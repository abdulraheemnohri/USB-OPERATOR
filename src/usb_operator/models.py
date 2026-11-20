from datetime import datetime,timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel,Field
def utcnow(): return datetime.now(timezone.utc)
class Transport(StrEnum):
    USB="usb"; SERIAL="serial"; HID="hid"; BLE="ble"; NETWORK="network"; SIMULATOR="simulator"; CAMERA="camera"; GPIO="gpio"; UNKNOWN="unknown"
class DeviceState(StrEnum):
    CONNECTED="connected"; DISCONNECTED="disconnected"; SIMULATED="simulated"; DEGRADED="degraded"
class Device(BaseModel):
    id:str; name:str; transport:Transport; state:DeviceState=DeviceState.CONNECTED
    vendor_id:int|None=None; product_id:int|None=None; serial_number:str|None=None
    manufacturer:str|None=None; product:str|None=None; location:str|None=None
    capabilities:list[str]=Field(default_factory=list); metadata:dict[str,Any]=Field(default_factory=dict); last_seen:datetime=Field(default_factory=utcnow)
class CommandRequest(BaseModel):
    device_id:str; action:str=Field(min_length=1,max_length=80); parameters:dict[str,Any]=Field(default_factory=dict); reason:str=Field(default="",max_length=500)
class CommandPlan(BaseModel):
    id:str; device_id:str; action:str; parameters:dict[str,Any]; risk:str; status:str; explanation:str; created_at:datetime=Field(default_factory=utcnow); expires_at:datetime
