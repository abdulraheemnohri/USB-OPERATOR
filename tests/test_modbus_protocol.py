import struct
import pytest
from usb_operator.protocols.modbus import validate_read,parse_tcp_response,build_rtu_read_request,parse_rtu_read_response,modbus_crc16

def test_validate_read_only_range():
 validate_read(1,0,125,3)
 with pytest.raises(PermissionError): validate_read(1,0,1,6)
 with pytest.raises(ValueError): validate_read(1,65535,2,3)

def test_parse_modbus_tcp_registers():
 tid=0x1234; regs=(230,15,500); data=struct.pack(">HHH",*regs); frame=struct.pack(">HHHBB",tid,0,3+len(data),1,3)+bytes([len(data)])+data
 assert parse_tcp_response(frame,tid,1,3,3)==regs

def test_tcp_transaction_mismatch_rejected():
 frame=struct.pack(">HHHBBB",2,0,3,1,3,2)+bytes([0,1])
 with pytest.raises(ValueError,match="transaction"): parse_tcp_response(frame,1,1,3,1)

def test_rtu_request_has_valid_crc_and_is_read_only():
 frame=build_rtu_read_request(1,0x10,2,4); assert modbus_crc16(frame[:-2])==struct.unpack("<H",frame[-2:])[0]; assert frame[1]==4

def test_rtu_response_parses_registers():
 body=bytes([1,3,4,0,10,0,20]); frame=body+struct.pack("<H",modbus_crc16(body)); assert parse_rtu_read_response(frame,1,3,2)==(10,20)

def test_rtu_crc_error_rejected():
 body=bytes([1,3,2,0,1]); frame=body+bytes([0,0])
 with pytest.raises(ValueError,match="CRC"): parse_rtu_read_response(frame,1,3,1)
