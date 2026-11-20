import json
import pytest
from usb_operator.protocols.jsonl import PROTOCOL,build_request,parse_response

def test_builds_read_only_request():
 raw=build_request("read",{"channel":"temperature"}); item=json.loads(raw); assert item["protocol"]==PROTOCOL and item["action"]=="read"

def test_rejects_actuation_action():
 with pytest.raises(PermissionError): build_request("gpio_set",{"pin":2,"value":True})

def test_rejects_invalid_channel():
 with pytest.raises(ValueError): build_request("read",{"channel":"temperature;gpio_set"})

def test_parses_correlated_response():
 raw=json.dumps({"protocol":PROTOCOL,"id":"abc","ok":True,"data":{"temperature_c":27.5}}).encode()+b"\n"
 assert parse_response(raw,"abc")["data"]["temperature_c"]==27.5

@pytest.mark.parametrize("raw",[b"",b"not-json\n",b"{}\n",b"{\"protocol\":\"wrong\",\"id\":\"x\",\"ok\":true,\"data\":{}}\n"])
def test_rejects_malformed_or_wrong_protocol(raw):
 with pytest.raises(ValueError): parse_response(raw,"x")

def test_rejects_mismatched_request_id():
 raw=json.dumps({"protocol":PROTOCOL,"id":"other","ok":True,"data":{}}).encode()+b"\n"
 with pytest.raises(ValueError,match="correlation"): parse_response(raw,"expected")
