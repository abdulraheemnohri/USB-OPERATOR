import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    app_name:str="USB-OPERATOR"
    host:str=os.getenv("USB_OPERATOR_HOST","127.0.0.1")
    port:int=int(os.getenv("USB_OPERATOR_PORT","8765"))
    database_path:str=os.getenv("USB_OPERATOR_DB","data/usb-operator.db")
    policy_mode:str=os.getenv("USB_OPERATOR_POLICY","policy")
    remote_token:str=os.getenv("USB_OPERATOR_REMOTE_TOKEN","")
    enable_ble:bool=os.getenv("USB_OPERATOR_ENABLE_BLE","false").lower() in {"1","true","yes"}
    cors_origins:tuple[str,...]=tuple(x.strip() for x in os.getenv("USB_OPERATOR_CORS","http://localhost:5173").split(",") if x.strip())
settings=Settings()
