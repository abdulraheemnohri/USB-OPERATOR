import pytest
from usb_operator.models import Device,DeviceState,Transport
from usb_operator.registry import DeviceRegistry
from usb_operator.services.hotplug import HotplugMonitor
class FakeDiscovery:
 last_scan_transports={"serial"}
 last_scan_errors={}
 async def scan(self): return []
@pytest.mark.asyncio
async def test_hotplug_marks_only_scanned_missing_devices_disconnected():
 registry=DeviceRegistry(); serial=Device(id="serial:COM7",name="Board",transport=Transport.SERIAL); usb=Device(id="usb:1234",name="USB",transport=Transport.USB)
 registry.upsert(serial); registry.upsert(usb); monitor=HotplugMonitor(FakeDiscovery(),registry,None,2); result=await monitor.scan_once()
 assert result["disconnected"]==1; assert registry.get("serial:COM7").state==DeviceState.DISCONNECTED; assert registry.get("usb:1234").state==DeviceState.CONNECTED
