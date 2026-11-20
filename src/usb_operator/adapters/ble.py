"""Optional BLE advertisement discovery; does not pair, connect or write characteristics."""
from ..models import Device,Transport
from .base import DeviceAdapter
class BLEAdapter(DeviceAdapter):
    transport="ble"
    async def discover(self):
        try: from bleak import BleakScanner
        except ImportError as exc: raise RuntimeError("BLE discovery requires the optional 'ble' extra.") from exc
        devices=await BleakScanner.discover(timeout=4.0,return_adv=True); found=[]
        for address,pair in devices.items():
            device,adv=pair; name=device.name or adv.local_name or "BLE device"
            found.append(Device(id=f"ble:{address}",name=name,transport=Transport.BLE,capabilities=["identify","status"],metadata={"address":address,"rssi":adv.rssi,"service_uuids":adv.service_uuids,"manufacturer_data_keys":[str(k) for k in adv.manufacturer_data.keys()]}))
        return found
