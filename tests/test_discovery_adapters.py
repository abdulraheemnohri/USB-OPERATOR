import importlib.util
import pytest
from usb_operator.adapters.hid import HIDAdapter
from usb_operator.adapters.ble import BLEAdapter

@pytest.mark.asyncio
async def test_hid_discovery_handles_optional_driver_explicitly():
 if importlib.util.find_spec("hid") is None:
  with pytest.raises(RuntimeError,match="optional 'hid' extra"): await HIDAdapter().discover()
 else:
  assert isinstance(await HIDAdapter().discover(),list)

@pytest.mark.asyncio
async def test_ble_discovery_handles_optional_driver_explicitly():
 if importlib.util.find_spec("bleak") is None:
  with pytest.raises(RuntimeError,match="optional 'ble' extra"): await BLEAdapter().discover()
 else:
  assert isinstance(await BLEAdapter().discover(),list)
