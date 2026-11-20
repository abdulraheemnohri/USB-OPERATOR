import asyncio
from ..models import Device,Transport
from .base import DeviceAdapter
class USBAdapter(DeviceAdapter):
    transport="usb"
    async def discover(self):
        def scan():
            try: import usb.core
            except ImportError as exc: raise RuntimeError("USB discovery requires the optional 'usb' extra.") from exc
            result=[]
            for d in usb.core.find(find_all=True) or []:
                vid,pid=int(d.idVendor),int(d.idProduct)
                result.append(Device(id=f"usb:{vid:04x}:{pid:04x}:{getattr(d,'bus','na')}:{getattr(d,'address','na')}",name=f"USB device {vid:04X}:{pid:04X}",transport=Transport.USB,vendor_id=vid,product_id=pid,location=f"bus={getattr(d,'bus',None)} address={getattr(d,'address',None)}",capabilities=["identify","status"],metadata={"bus":getattr(d,"bus",None),"address":getattr(d,"address",None)}))
            return result
        return await asyncio.to_thread(scan)
