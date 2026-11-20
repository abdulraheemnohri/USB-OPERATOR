"""Allowlisted, read-only SCPI query protocol helper."""
from __future__ import annotations
import re
ALLOWED_QUERIES={"*IDN?","*OPC?","SYST:ERR?","MEAS:VOLT?","MEAS:CURR?","MEAS:POW?","MEAS:FREQ?","READ?"}
def validate_scpi_query(command:str)->str:
    if not isinstance(command,str): raise TypeError("SCPI query must be text")
    normalized=command.strip().upper()
    if len(normalized)>40 or not re.fullmatch(r"[A-Z0-9:*?._-]+",normalized): raise ValueError("Invalid SCPI query syntax")
    if normalized not in ALLOWED_QUERIES: raise PermissionError("SCPI command is not in the read-only query allowlist")
    if not normalized.endswith("?"): raise PermissionError("SCPI write commands are forbidden")
    return normalized
class SCPISerialClient:
    def __init__(self,baudrate:int=9600,timeout:float=1.0): self.baudrate=baudrate; self.timeout=max(.1,min(float(timeout),3.0))
    async def query(self,port:str,command:str):
        import asyncio
        query=validate_scpi_query(command)
        if not isinstance(port,str) or not port or len(port)>256 or any(c in port for c in "\r\n\0"): raise ValueError("Invalid serial port")
        return await asyncio.to_thread(self._query_sync,port,query)
    def _query_sync(self,port,query):
        import serial
        with serial.Serial(port,self.baudrate,timeout=self.timeout,write_timeout=self.timeout) as connection:
            connection.reset_input_buffer(); connection.write((query+"\n").encode("ascii")); connection.flush()
            response=connection.read_until(b"\n",1024)
        if not response or len(response)>=1024: raise TimeoutError("SCPI response missing or too large")
        return {"query":query,"response":response.decode("ascii",errors="replace").strip()}
