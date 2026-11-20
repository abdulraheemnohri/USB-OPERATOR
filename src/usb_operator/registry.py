from threading import RLock
from .models import Device,DeviceState
class DeviceRegistry:
    def __init__(self,store=None):
        self._items={}; self._lock=RLock(); self.store=store
        if store:
            for item in store.load_devices(): self._items[item.id]=item
    def upsert(self,device:Device):
        with self._lock: self._items[device.id]=device
        if self.store: self.store.save_device(device)
        return device
    def get(self,device_id):
        with self._lock: return self._items.get(device_id)
    def list(self):
        with self._lock: return sorted(self._items.values(),key=lambda x:x.name.casefold())
    def remove(self,device_id):
        with self._lock: removed=self._items.pop(device_id,None) is not None
        if removed and self.store: self.store.remove_device(device_id)
        return removed
    def mark_missing(self,scanned_transports:set[str],present_ids:set[str]):
        changed=[]
        with self._lock:
            for device_id,device in list(self._items.items()):
                if device.transport.value in scanned_transports and device_id not in present_ids and device.state!=DeviceState.DISCONNECTED:
                    updated=device.model_copy(update={"state":DeviceState.DISCONNECTED})
                    self._items[device_id]=updated; changed.append(updated)
        if self.store:
            for device in changed: self.store.save_device(device)
        return changed
