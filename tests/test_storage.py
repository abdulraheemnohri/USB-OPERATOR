from usb_operator.storage import SQLiteStore
from usb_operator.registry import DeviceRegistry
from usb_operator.models import Device,Transport

def test_devices_persist_between_registry_instances(tmp_path):
 path=str(tmp_path/"state.db"); store=SQLiteStore(path); registry=DeviceRegistry(store); d=Device(id="usb:test",name="Test",transport=Transport.USB,capabilities=["identify"]); registry.upsert(d)
 restored=DeviceRegistry(SQLiteStore(path)); assert restored.get("usb:test").name=="Test"

def test_audit_chain_verifies_and_detects_tampering(tmp_path):
 store=SQLiteStore(str(tmp_path/"audit.db")); store.record("test.event",{"value":1}); store.record("test.event",{"value":2}); assert store.verify_audit()["valid"]
 with store._connect() as db: db.execute("UPDATE audit SET payload='{}' WHERE seq=1")
 assert not store.verify_audit()["valid"]
