import asyncio
from serial.tools import list_ports
from ..models import Device,Transport
from .base import DeviceAdapter
class SerialAdapter(DeviceAdapter):
    transport="serial"
    async def discover(self):
        def scan():
            found=[]
            for p in list_ports.comports():
                found.append(Device(id=f"serial:{p.device}",name=p.description or p.device,transport=Transport.SERIAL,location=p.device,manufacturer=p.manufacturer,product=p.product,serial_number=p.serial_number,metadata={"vid":p.vid,"pid":p.pid,"hwid":p.hwid},capabilities=["identify","status","read"]))
            return found
        return await asyncio.to_thread(scan)
