from fastapi.testclient import TestClient
from usb_operator.api.app import app, registry
from usb_operator.models import Device, DeviceState, Transport

def test_alert_rule_and_lifecycle_api():
    device_id = "api-alert-meter"
    registry.upsert(Device(id=device_id, name="API Test Meter", transport=Transport.NETWORK, state=DeviceState.CONNECTED))
    with TestClient(app) as client:
        created = client.post("/v1/alerts/rules", json={"device_id":device_id,"metric":"voltage","operator":"gt","threshold":250,"unit":"V","severity":"critical"})
        assert created.status_code == 200
        rule = created.json()
        assert rule["enabled"] is True
        assert client.get("/v1/alerts/rules", params={"device_id":device_id}).json()["rules"]
        ingest = client.post("/v1/telemetry/ingest", json={"samples":[{"device_id":device_id,"metric":"voltage","value":255,"unit":"V","quality":"good"}]})
        assert ingest.status_code == 200
        assert len(ingest.json()["opened_alerts"]) == 1
        active = client.get("/v1/alerts", params={"status":"active"}).json()["alerts"]
        assert active and active[0]["device_id"] == device_id
        ack = client.post(f"/v1/alerts/{active[0]['id']}/acknowledge")
        assert ack.status_code == 200
        assert ack.json()["status"] == "acknowledged"
        disabled = client.post(f"/v1/alerts/rules/{rule['id']}/enabled", json={"enabled":False})
        assert disabled.status_code == 200 and disabled.json()["enabled"] is False
    registry.remove(device_id)

def test_alert_api_rejects_invalid_metric():
    with TestClient(app) as client:
        response = client.post("/v1/alerts/rules", json={"device_id":"missing","metric":"bad;metric","operator":"gt","threshold":1})
        assert response.status_code == 422
