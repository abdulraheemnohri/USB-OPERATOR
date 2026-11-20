import asyncio
from ..adapters.serial import SerialAdapter
from ..adapters.usb import USBAdapter
from ..adapters.hid import HIDAdapter
from ..adapters.ble import BLEAdapter
from ..adapters.simulator import SimulatorAdapter
class DiscoveryService:
    def __init__(self,registry,include_simulator=True,enable_ble=False):
        self.registry=registry; self.adapters=[SerialAdapter(),USBAdapter(),HIDAdapter()]
        if enable_ble: self.adapters.append(BLEAdapter())
        if include_simulator: self.adapters.append(SimulatorAdapter())
    async def scan(self):
        batches=await asyncio.gather(*(a.discover() for a in self.adapters),return_exceptions=True); found=[]
        for batch in batches:
            if isinstance(batch,Exception): continue
            for device in batch: self.registry.upsert(device); found.append(device)
        return found
