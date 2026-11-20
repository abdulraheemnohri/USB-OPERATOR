"""Strict, read-only USB-OPERATOR JSON Lines serial protocol client."""
from __future__ import annotations
import asyncio,json,re,secrets
from typing import Any
PROTOCOL="usb-operator-jsonl/1"
READ_ONLY_ACTIONS={"identify","status","read"}
MAX_FRAME_BYTES=8192
_CHANNEL=re.compile(r"^[A-Za-z0-9_.-]{1,32}$")
def build_request(action:str,parameters:dict[str,Any]|None=None,request_id:str|None=None)->bytes:
    if action not in READ_ONLY_ACTIONS: raise PermissionError("Serial JSONL client permits read-only actions only.")
    params=parameters or {}
    if action in {"identify","status"} and params: raise ValueError(f"{action} does not accept parameters")
    if action=="read":
        if set(params)-{"channel"}: raise ValueError("Unsupported read parameter")
        channel=params.get("channel","default")
        if not isinstance(channel,str) or not _CHANNEL.fullmatch(channel): raise ValueError("Invalid telemetry channel")
        params={"channel":channel}
    envelope={"protocol":PROTOCOL,"id":request_id or secrets.token_hex(8),"action":action,"parameters":params}
    return (json.dumps(envelope,separators=(",",":"),ensure_ascii=True)+"\n").encode("utf-8")
def parse_response(frame:bytes,expected_id:str)->dict[str,Any]:
    if not frame or len(frame)>MAX_FRAME_BYTES or not frame.endswith(b"\n"): raise ValueError("Invalid or oversized JSONL response frame")
    try: data=json.loads(frame.decode("utf-8").strip())
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValueError("Malformed JSONL response") from exc
    if not isinstance(data,dict): raise ValueError("Response must be a JSON object")
    if data.get("protocol")!=PROTOCOL: raise ValueError("Unsupported device protocol version")
    if data.get("id")!=expected_id: raise ValueError("Response correlation ID mismatch")
    if not isinstance(data.get("ok"),bool): raise ValueError("Response is missing boolean ok field")
    if data["ok"] and not isinstance(data.get("data"),dict): raise ValueError("Successful response must include an object data field")
    if not data["ok"] and not isinstance(data.get("error"),str): raise ValueError("Failed response must include an error message")
    return data
class SerialJSONLClient:
    def __init__(self,baudrate:int=115200,timeout:float=1.0):
        self.baudrate=baudrate; self.timeout=max(0.1,min(float(timeout),3.0))
    async def execute(self,device,action:str,parameters:dict|None=None):
        if device.transport.value!="serial": raise ValueError("JSONL adapter requires a serial device")
        if not device.location: raise ValueError("Serial device has no port location")
        request=build_request(action,parameters); request_id=json.loads(request)["id"]
        return await asyncio.to_thread(self._exchange,device,action,request,request_id)
    def _exchange(self,device,action,request,request_id):
        import serial
        with serial.Serial(device.location,self.baudrate,timeout=self.timeout,write_timeout=self.timeout) as port:
            port.reset_input_buffer(); port.write(request); port.flush()
            frame=port.read_until(b"\n",MAX_FRAME_BYTES+1)
        response=parse_response(frame,request_id)
        if not response["ok"]: raise RuntimeError(response["error"][:200])
        return {"ok":True,"device_id":device.id,"action":action,"data":response["data"]}
