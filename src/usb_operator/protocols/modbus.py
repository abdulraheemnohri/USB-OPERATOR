"""Read-only Modbus TCP/RTU protocol primitives. No write function codes are exposed."""
from __future__ import annotations
import asyncio,secrets,struct
from dataclasses import dataclass
MAX_READ_REGISTERS=125
@dataclass(frozen=True)
class ModbusReadResult:
    unit_id:int
    function_code:int
    start_address:int
    registers:tuple[int,...]

def validate_read(unit_id:int,start_address:int,count:int,function_code:int=3):
    if not 0<=unit_id<=247: raise ValueError("Modbus unit ID must be 0..247")
    if not 0<=start_address<=65535: raise ValueError("Start address must be 0..65535")
    if not 1<=count<=MAX_READ_REGISTERS or start_address+count>65536: raise ValueError("Register count/address range is invalid")
    if function_code not in (3,4): raise PermissionError("Only read holding/input registers (FC03/FC04) are supported")

def parse_tcp_response(frame:bytes,transaction_id:int,unit_id:int,function_code:int,count:int)->tuple[int,...]:
    if len(frame)<9: raise ValueError("Modbus TCP response is truncated")
    tid,protocol,length=struct.unpack(">HHH",frame[:6])
    if tid!=transaction_id: raise ValueError("Modbus transaction ID mismatch")
    if protocol!=0: raise ValueError("Invalid Modbus protocol identifier")
    if length!=len(frame)-6 or length<3: raise ValueError("Invalid Modbus MBAP length")
    if frame[6]!=unit_id: raise ValueError("Modbus unit ID mismatch")
    fc=frame[7]
    if fc==(function_code|0x80): raise RuntimeError(f"Modbus exception response code {frame[8] if len(frame)>8 else -1}")
    if fc!=function_code: raise ValueError("Unexpected Modbus function code")
    byte_count=frame[8]
    if byte_count!=count*2 or len(frame)!=9+byte_count: raise ValueError("Modbus register byte count mismatch")
    return tuple(struct.unpack(">"+("H"*count),frame[9:]))

class ModbusTCPReadClient:
    def __init__(self,timeout:float=2.0): self.timeout=max(.2,min(float(timeout),5.0))
    async def read_registers(self,host:str,port:int,unit_id:int,start_address:int,count:int,function_code:int=3)->ModbusReadResult:
        validate_read(unit_id,start_address,count,function_code)
        if not host or len(host)>253 or any(c in host for c in "\r\n/\\"): raise ValueError("Invalid host")
        if not 1<=int(port)<=65535: raise ValueError("Invalid TCP port")
        tid=secrets.randbelow(65536); pdu=struct.pack(">BHH",function_code,start_address,count); frame=struct.pack(">HHHB",tid,0,len(pdu)+1,unit_id)+pdu
        reader,writer=await asyncio.wait_for(asyncio.open_connection(host,int(port)),self.timeout)
        try:
            writer.write(frame); await asyncio.wait_for(writer.drain(),self.timeout)
            header=await asyncio.wait_for(reader.readexactly(7),self.timeout)
            _,_,length=struct.unpack(">HHH",header[:6])
            if length<3 or length>252: raise ValueError("Invalid Modbus TCP response length")
            body=await asyncio.wait_for(reader.readexactly(length-1),self.timeout)
            registers=parse_tcp_response(header+body,tid,unit_id,function_code,count)
            return ModbusReadResult(unit_id,function_code,start_address,registers)
        finally:
            writer.close()
            try: await writer.wait_closed()
            except Exception: pass

def modbus_crc16(data:bytes)->int:
    crc=0xFFFF
    for byte in data:
        crc^=byte
        for _ in range(8): crc=(crc>>1)^0xA001 if crc&1 else crc>>1
    return crc

def build_rtu_read_request(unit_id:int,start_address:int,count:int,function_code:int=3)->bytes:
    validate_read(unit_id,start_address,count,function_code)
    payload=struct.pack(">BBHH",unit_id,function_code,start_address,count); crc=modbus_crc16(payload)
    return payload+struct.pack("<H",crc)

def parse_rtu_read_response(frame:bytes,unit_id:int,function_code:int,count:int)->tuple[int,...]:
    if len(frame)<5: raise ValueError("Modbus RTU response is truncated")
    if modbus_crc16(frame[:-2])!=struct.unpack("<H",frame[-2:])[0]: raise ValueError("Modbus RTU CRC mismatch")
    if frame[0]!=unit_id: raise ValueError("Modbus RTU unit ID mismatch")
    if frame[1]==(function_code|0x80): raise RuntimeError(f"Modbus RTU exception code {frame[2]}")
    if frame[1]!=function_code or frame[2]!=count*2 or len(frame)!=5+count*2: raise ValueError("Invalid Modbus RTU response")
    return tuple(struct.unpack(">"+("H"*count),frame[3:-2]))
