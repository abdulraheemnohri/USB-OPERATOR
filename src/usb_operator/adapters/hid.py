"""Read-only HID enumeration. No keyboard injection or output reports are exposed."""
import asyncio
from ..models import Device,Transport
from .base import DeviceAdapter
class HIDAdapter(DeviceAdapter):
    transport="hid"
    async def discover(self):
        def scan():
            try: import hid
            except ImportError: return []
            found=[]
            try: items=hid.enumerate()
            except Exception: return []
            for item in items:
                vid=int(item.get("vendor_id") or 0); pid=int(item.get("product_id") or 0); path=item.get("path")
                path_text=path.decode(errors="replace") if isinstance(path,bytes) else str(path or "unknown")
                serial=item.get("serial_number") or None; product=item.get("product_string") or "HID device"
                found.append(Device(id=f"hid:{vid:04x}:{pid:04x}:{serial or path_text}",name=product,transport=Transport.HID,vendor_id=vid or None,product_id=pid or None,serial_number=serial,manufacturer=item.get("manufacturer_string"),product=product,location=path_text,capabilities=["identify","status"],metadata={"usage_page":item.get("usage_page"),"usage":item.get("usage"),"interface_number":item.get("interface_number")}))
            return found
        return await asyncio.to_thread(scan)
