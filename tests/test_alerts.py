import pytest
from usb_operator.alerts import AlertRuleCreate, AlertService
from usb_operator.telemetry import TelemetryBatch, TelemetrySample, TelemetryService
from usb_operator.storage import SQLiteStore
from usb_operator.registry import DeviceRegistry
from usb_operator.models import Device, DeviceState, Transport

def setup():
    store = SQLiteStore(":memory:")
    registry = DeviceRegistry(store)
    registry.upsert(Device(id="meter-1", name="Meter", transport=Transport.NETWORK, state=DeviceState.CONNECTED))
    telemetry = TelemetryService(registry, store)
    alerts = AlertService(registry, store)
    return store, telemetry, alerts

def test_threshold_creates_alert_and_resolves_when_normal():
    _, telemetry, alerts = setup()
    rule = alerts.create_rule(AlertRuleCreate(device_id="meter-1", metric="voltage", operator="gt", threshold=250, unit="V", severity="critical"))
    assert rule["enabled"] is True
    telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="voltage", value=255, unit="V")]))
    active = alerts.list_alerts(status="active")
    assert len(active) == 1 and active[0]["severity"] == "critical"
    telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="voltage", value=240, unit="V")]))
    assert alerts.list_alerts(status="active") == []
    assert alerts.list_alerts(status="resolved")[0]["status"] == "resolved"

def test_alert_is_deduplicated_until_condition_clears():
    _, telemetry, alerts = setup()
    alerts.create_rule(AlertRuleCreate(device_id="meter-1", metric="temperature", operator="gte", threshold=80))
    for value in (81, 82, 83):
        telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="temperature", value=value)]))
    assert len(alerts.list_alerts()) == 1

def test_bad_quality_samples_do_not_trigger_alert():
    _, telemetry, alerts = setup()
    alerts.create_rule(AlertRuleCreate(device_id="meter-1", metric="current", operator="gt", threshold=10))
    telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="current", value=20, quality="bad")]))
    assert alerts.list_alerts() == []

def test_disabled_rule_does_not_trigger():
    _, telemetry, alerts = setup()
    rule = alerts.create_rule(AlertRuleCreate(device_id="meter-1", metric="voltage", operator="gt", threshold=250))
    alerts.set_enabled(rule["id"], False)
    telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="voltage", value=260)]))
    assert alerts.list_alerts() == []

def test_acknowledgement_and_rule_validation():
    _, telemetry, alerts = setup()
    with pytest.raises(LookupError):
        alerts.create_rule(AlertRuleCreate(device_id="unknown", metric="voltage", operator="gt", threshold=250))
    alerts.create_rule(AlertRuleCreate(device_id="meter-1", metric="voltage", operator="gt", threshold=250))
    telemetry.ingest(TelemetryBatch(samples=[TelemetrySample(device_id="meter-1", metric="voltage", value=260)]))
    alert = alerts.list_alerts()[0]
    assert alerts.acknowledge(alert["id"])["status"] == "acknowledged"
    assert alerts.list_alerts(status="acknowledged")
