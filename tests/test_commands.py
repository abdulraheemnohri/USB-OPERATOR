import pytest
from usb_operator.models import CommandRequest
from usb_operator.policy import SafetyPolicy
from usb_operator.registry import DeviceRegistry
from usb_operator.services.commands import CommandService
from usb_operator.adapters.simulator import SimulatorAdapter
@pytest.mark.asyncio
async def test_simulated_read_executes():
 r=DeviceRegistry(); d=(await SimulatorAdapter().discover())[0]; r.upsert(d); s=CommandService(r,SafetyPolicy()); p=s.plan(CommandRequest(device_id=d.id,action="read")); result=await s.execute(p.id); assert result["ok"] and result["data"]["simulated"]
@pytest.mark.asyncio
async def test_gpio_requires_approval():
 r=DeviceRegistry(); d=(await SimulatorAdapter().discover())[0]; r.upsert(d); s=CommandService(r,SafetyPolicy()); p=s.plan(CommandRequest(device_id=d.id,action="gpio_set",parameters={"pin":2,"value":True}))
 with pytest.raises(PermissionError): await s.execute(p.id)
 s.approve(p.id); assert (await s.execute(p.id))["ok"]
def test_unknown_device_cannot_be_planned():
 with pytest.raises(LookupError): CommandService(DeviceRegistry(),SafetyPolicy()).plan(CommandRequest(device_id="missing",action="read"))
