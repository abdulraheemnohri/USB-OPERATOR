"""Cross-platform polling hot-plug monitor. Polling is deliberately read-only."""
import asyncio
class HotplugMonitor:
    def __init__(self,discovery,registry,audit,interval:float=5.0):
        self.discovery=discovery; self.registry=registry; self.audit=audit; self.interval=max(2.0,float(interval)); self._task=None; self._stop=None; self.last_scan_at=None; self.last_error=None; self.scans=0
    async def scan_once(self):
        from datetime import datetime,timezone
        before={d.id for d in self.registry.list() if d.state.value=="connected"}
        found=await self.discovery.scan(); scanned=set(self.discovery.last_scan_transports); present={d.id for d in found}
        disconnected=self.registry.mark_missing(scanned,present)
        added=[d for d in found if d.id not in before]
        if self.audit:
            for device in added: self.audit.record("device.connected",{"device_id":device.id,"transport":device.transport.value,"name":device.name})
            for device in disconnected: self.audit.record("device.disconnected",{"device_id":device.id,"transport":device.transport.value})
        self.scans+=1; self.last_scan_at=datetime.now(timezone.utc).isoformat(); self.last_error=None
        return {"connected":len(added),"disconnected":len(disconnected),"found":len(found),"devices":[d.model_dump(mode="json") for d in found],"scanned_transports":sorted(scanned),"adapter_errors":dict(self.discovery.last_scan_errors)}
    async def _run(self):
        while not self._stop.is_set():
            try: await self.scan_once()
            except Exception as exc: self.last_error=type(exc).__name__
            try: await asyncio.wait_for(self._stop.wait(),timeout=self.interval)
            except asyncio.TimeoutError: pass
    async def start(self):
        if self._task is None or self._task.done():
            self._stop=asyncio.Event(); self._task=asyncio.create_task(self._run(),name="usb-operator-hotplug")
    async def stop(self):
        if self._task and not self._task.done():
            if self._stop: self._stop.set()
            await self._task
        self._task=None
    def status(self): return {"running":bool(self._task and not self._task.done()),"interval_seconds":self.interval,"scans":self.scans,"last_scan_at":self.last_scan_at,"last_error":self.last_error}
