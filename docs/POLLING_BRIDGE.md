# Read-only protocol-to-telemetry polling bridge

This milestone connects the existing read-only Modbus TCP and ESP32 JSONL clients to validated telemetry ingestion.

## API

`POST /v1/devices/{device_id}/telemetry/poll` (operator token required)

Example Modbus TCP body (the network device must already be discovered/registered and its `location` must contain the configured host or host:port):

```json
{
  "protocol": "modbus_tcp",
  "unit_id": 1,
  "timeout": 2,
  "channels": [
    {"metric": "voltage_l1", "unit": "V", "address": 0, "function_code": 3, "scale": 0.1}
  ]
}
```

Example ESP32 JSONL body:

```json
{
  "protocol": "esp32_jsonl",
  "channels": [
    {"metric": "temperature", "unit": "C", "channel": "temperature"}
  ]
}
```

Every mapping is explicit. Modbus polling reads one configured register per metric; the bridge does not assume a vendor register map, data type, scaling, or byte order. Confirm the exact meter manual and register map before using real equipment. The example address above is illustrative, not an Eastron SDM630 register assignment.

ESP32 polling only invokes the protocol's `read` action for named channels. Neither path exposes writes, GPIO control, relay control, or arbitrary commands. Requests are bounded to 32 channels, validated read function codes and bounded timeouts. Telemetry remains monitoring data, not a protective relay or safety interlock.

The current bridge is a manually triggered API operation, not a continuous background polling scheduler. No physical device has been tested by CI; tests use fake protocol clients.
