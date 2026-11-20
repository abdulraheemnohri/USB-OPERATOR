from ..models import Device,DeviceState,Transport
from .base import DeviceAdapter
class SimulatorAdapter(DeviceAdapter):
    transport="simulator"
    async def discover(self):
        return [Device(id="sim:esp32-lab",name="Simulated ESP32 Lab Board",transport=Transport.SIMULATOR,state=DeviceState.SIMULATED,capabilities=["identify","status","read","gpio_set"],metadata={"board":"ESP32","firmware":"usb-operator-demo","safe_demo":True}),Device(id="sim:modbus-meter",name="Simulated Modbus Energy Meter",transport=Transport.SIMULATOR,state=DeviceState.SIMULATED,capabilities=["identify","status","read"],metadata={"protocol":"Modbus RTU","safe_demo":True})]
    async def execute(self,device,action,parameters):
        if action in {"status","identify","read","list_capabilities"}: return {"ok":True,"device_id":device.id,"action":action,"data":{"simulated":True,"value":24.1 if action=="read" else "ready"}}
        if action=="gpio_set":
            pin=int(parameters.get("pin",-1))
            if not 0<=pin<=39: raise ValueError("GPIO pin must be between 0 and 39.")
            return {"ok":True,"simulated":True,"pin":pin,"value":bool(parameters.get("value"))}
        raise ValueError("Action is not supported by simulator.")
