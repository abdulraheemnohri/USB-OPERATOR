import pytest
from usb_operator.adapters.hid import HIDAdapter
from usb_operator.adapters.ble import BLEAdapter
@pytest.mark.asyncio
async def test_hid_discovery_returns_list_without_optional_driver():
 result=await HIDAdapter().discover(); assert isinstance(result,list)
@pytest.mark.asyncio
async def test_ble_discovery_returns_list_or_graceful_empty():
 result=await BLEAdapter().discover(); assert isinstance(result,list)
