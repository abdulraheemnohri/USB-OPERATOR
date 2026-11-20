from threading import RLock
from .models import Device
class DeviceRegistry:
    def __init__(self): self._items={}; self._lock=RLock()
    def upsert(self,device:Device):
        with self._lock: self._items[device.id]=device
        return device
    def get(self,device_id):
        with self._lock: return self._items.get(device_id)
    def list(self):
        with self._lock: return sorted(self._items.values(),key=lambda x:x.name.casefold())
    def remove(self,device_id):
        with self._lock: return self._items.pop(device_id,None) is not None
