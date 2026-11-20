# Universal Telemetry Engine

This milestone introduces a normalized telemetry schema, validated ingestion and bounded history queries.

## API
- `POST /v1/telemetry/ingest` — authenticated host-side ingestion, max 100 samples per batch.
- `GET /v1/telemetry/latest?device_id=...` — latest samples grouped by query result.
- `GET /v1/telemetry/history/{device_id}?metric=voltage&limit=100` — bounded history.

Samples require a known connected or simulated device, simple metric identifier, finite numeric value, bounded unit/quality/source and a sane timestamp. Unknown or disconnected devices are rejected. SQLite retains the most recent 10,000 samples. This is an ingestion/storage layer, not yet a live hardware sensor driver; it does not poll Modbus/SCPI or decode vendor register maps.

## Example (PowerShell)
```powershell
$body = @{ samples = @(@{ device_id = "sim:modbus-meter"; metric = "voltage_l1"; value = 230.4; unit = "V"; quality = "good" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/v1/telemetry/ingest -ContentType "application/json" -Body $body
Invoke-RestMethod http://127.0.0.1:8765/v1/telemetry/latest
```

Keep the host bound to loopback. For remote deployment configure a strong operator token and TLS reverse proxy. Do not use telemetry as a protective relay or safety interlock.
