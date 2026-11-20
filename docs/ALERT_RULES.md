# Telemetry threshold rules and alerts

Threshold rules evaluate accepted telemetry samples with `quality=good`. Supported operators are `gt`, `gte`, `lt`, `lte`, `eq`, and `ne`; severities are `info`, `warning`, and `critical`. Rules are scoped to one registered device and metric. A maximum of 200 rules is enforced.

## API

All mutation endpoints require the operator token when `USB_OPERATOR_REMOTE_TOKEN` is configured.

- `POST /v1/alerts/rules` create a rule.
- `GET /v1/alerts/rules?device_id=meter-1` list rules.
- `POST /v1/alerts/rules/{rule_id}/enabled` with `{"enabled": false}` enable/disable.
- `GET /v1/alerts?status=active&limit=100` list alert history.
- `POST /v1/alerts/{alert_id}/acknowledge` acknowledge an active alert.

Example rule:

```json
{
  "device_id": "meter-1",
  "metric": "voltage_l1",
  "operator": "gt",
  "threshold": 250,
  "unit": "V",
  "severity": "warning",
  "enabled": true
}
```

An alert is opened when a good-quality sample violates the threshold. Repeated violating samples do not create duplicate active alerts. When a later good-quality sample returns to the non-violating side, the alert is resolved. Acknowledgement does not resolve an alert; it remains active until the condition clears.

These are monitoring notifications only. They are not protective relays, trip logic, emergency stops, or a substitute for certified electrical protection. Never use this feature as the sole protection for people, equipment, or installations.
