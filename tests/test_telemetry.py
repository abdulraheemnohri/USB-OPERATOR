import pytest
from usb_operator.telemetry import TelemetryBatch,TelemetrySample,TelemetryService
from usb_operator.storage import SQLiteStore
from usb_operator.registry import DeviceRegistry
from usb_operator.adapters.simulator import SimulatorAdapter
from usb_operator.models import DeviceState
@pytest.mark.asyncio
async def test_telemetry_ingest_and_query(tmp_path):
 store=SQLiteStore(str(tmp_path/"telemetry.db")); registry=DeviceRegistry(store); device=(await SimulatorAdapter().discover())[1]; registry.upsert(device); service=TelemetryService(registry,store)
 batch=TelemetryBatch(samples=[TelemetrySample(device_id=device.id,metric="voltage",value=230.5,unit="V")]); assert service.ingest(batch)["accepted"]==1
 assert service.latest(device.id)[0]["metric"]=="voltage"
 assert service.history(device.id,"voltage")[0]["value"]==230.5

def test_metric_name_rejects_injection():
 with pytest.raises(ValueError): TelemetrySample(device_id="d",metric="voltage;DROP TABLE",value=2)

def test_non_finite_values_rejected():
 with pytest.raises(ValueError): TelemetrySample(device_id="d",metric="voltage",value=float("nan"))
@pytest.mark.asyncio
async def test_unknown_device_rejected():
 service=TelemetryService(DeviceRegistry(),SQLiteStore(":memory:"))
 with pytest.raises(LookupError): service.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="missing",metric="voltage",value=1)]))

def test_memory_store_persists_across_operations():
 store=SQLiteStore(":memory:"); store.record("test",{"ok":True}); assert store.list_audit()[0]["event"]=="test"
 sample={"device_id":"sim:test","metric":"voltage","value":230.0,"unit":"V","quality":"good","recorded_at":"2026-11-20T00:00:00+00:00","source":"test"}
 store.record_telemetry(sample); assert store.latest_telemetry()[0]["value"]==230.0
