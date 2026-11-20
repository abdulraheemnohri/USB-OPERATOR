# Alert Center and Dashboard (v0.10.0)

The dashboard now includes a monitoring-only Alert Center, threshold-rule controls, telemetry history chart, and latest-reading list.

## Alert workflow
1. Select a registered device and define a metric threshold.
2. Choose a comparator (gt, gte, lt, lte, eq, ne) and severity.
3. The backend evaluates only telemetry with quality good.
4. Repeated violations are deduplicated while an alert remains active or acknowledged.
5. Operators can acknowledge active alerts. A later good sample that clears the condition resolves the alert.

## Dashboard connection
- API base: VITE_API_URL, default http://127.0.0.1:8765.
- The optional operator token is held in React component memory only; it is not written to localStorage or cookies.
- If a remote token is configured on the backend, enter it in the dashboard before protected operations.
- Keep the API bound to loopback for local use. Remote deployments require TLS, a strong token, firewall controls and an authenticated reverse proxy.

## Telemetry chart
The chart uses GET /v1/telemetry/history/{device_id}?metric=... and plots up to 100 samples returned by the API. It is a lightweight SVG visualization with no charting dependency.

## Safety boundary
Alerts are operational monitoring features only. They are not protective relays, safety PLCs, electrical trip logic, emergency stops or certified interlocks. Never use this dashboard as the sole protection for mains, motors, machinery or people.
