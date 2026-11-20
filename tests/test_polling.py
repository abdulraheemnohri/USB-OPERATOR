import pytest
from usb_operator.polling import PollChannel, PollRequest, ReadOnlyPoller
from usb_operator.telemetry import TelemetryService
from usb_operator.storage import SQLiteStore
from usb_operator.registry import DeviceRegistry
from usb_operator.models import Device, DeviceState, Transport

class FakeModbus:
    async def read_registers(self, host, port, unit_id, start, count, function_code):
        assert (host, port, unit_id, start, count, function_code) == ("192.0.2.10", 502, 1, 10, 1, 3)
        return type("Result", (), {"registers": (2304,)})()

class FakeJSONL:
    async def execute(self, device, action, parameters):
        assert action == "read"
        return {"data": {"value": 24.5, "unit": "C"}}

@pytest.mark.asyncio
async def test_modbus_poll_converts_explicit_register_to_telemetry():
    store = SQLiteStore(":memory:")
    registry = DeviceRegistry(store)
    registry.upsert(Device(id="meter-1", name="Meter", transport=Transport.NETWORK, state=DeviceState.CONNECTED, location="192.0.2.10"))
    service = TelemetryService(registry, store)
    poller = ReadOnlyPoller(service, modbus_client=FakeModbus())
    request = PollRequest(protocol="modbus_tcp", channels=[PollChannel(metric="voltage", unit="V", address=10, scale=0.1)])
    result = await poller.poll("meter-1", request)
    assert result["accepted"] == 1
    assert service.latest("meter-1")[0]["value"] == 230.4

@pytest.mark.asyncio
async def test_jsonl_poll_reads_only_configured_channel():
    store = SQLiteStore(":memory:")
    registry = DeviceRegistry(store)
    registry.upsert(Device(id="esp-1", name="ESP32", transport=Transport.SERIAL, state=DeviceState.CONNECTED, location="COM4"))
    service = TelemetryService(registry, store)
    poller = ReadOnlyPoller(service, jsonl_client=FakeJSONL())
    result = await poller.poll("esp-1", PollRequest(protocol="esp32_jsonl", channels=[PollChannel(metric="temperature", channel="temp", unit="C")]))
    assert result["accepted"] == 1
    assert service.latest("esp-1")[0]["value"] == 24.5

def test_poll_request_rejects_write_function_codes():
    with pytest.raises(ValueError):
        PollChannel(metric="unsafe", address=1, function_code=6)

@pytest.mark.asyncio
async def test_modbus_poll_rejects_non_network_device():
    store = SQLiteStore(":memory:")
    registry = DeviceRegistry(store)
    registry.upsert(Device(id="serial-1", name="Serial", transport=Transport.SERIAL, location="COM4"))
    poller = ReadOnlyPoller(TelemetryService(registry, store), modbus_client=FakeModbus())
    with pytest.raises(PermissionError):
        await poller.poll("serial-1", PollRequest(protocol="modbus_tcp", channels=[PollChannel(metric="v", address=1)]))
