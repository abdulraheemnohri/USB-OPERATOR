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
        self.last_scan_transports=set(); self.last_scan_errors={}
    async def scan(self):
        batches=await asyncio.gather(*(a.discover() for a in self.adapters),return_exceptions=True); found=[]
        self.last_scan_transports=set(); self.last_scan_errors={}
        for adapter,batch in zip(self.adapters,batches):
            if isinstance(batch,Exception): self.last_scan_errors[adapter.transport]=type(batch).__name__; continue
            self.last_scan_transports.add(adapter.transport)
            for device in batch: self.registry.upsert(device); found.append(device)
        return found
