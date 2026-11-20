# USB-OPERATOR

Universal Physical Device AI Operating Platform. Local-first discovery, governed command planning, telemetry ingestion, hardware adapters and operator tooling.

**Status: v0.7.0 development foundation.** Not a production-ready universal hardware controller. Live device actuation remains disabled; simulator execution is available for demos.

## Implemented
- FastAPI backend, React/Vite dashboard and CLI host agent.
- USB descriptor, serial-port and optional read-only HID discovery; optional BLE advertisements.
- SQLite device inventory, bounded telemetry history and hash-chained audit.
- Background polling hot-plug monitor and inert validated device profiles.
- Strict read-only ESP32 JSONL, Modbus TCP/RTU and SCPI protocol foundations.
- Telemetry validation, ingestion and query API (not yet connected to physical sensor polling).
- Simulator, capability checks, default-deny policy and approval workflow.
- Optional AI proposal adapter; AI cannot execute hardware commands.
- Android USB OTG and iOS companion starter scaffolds.
- Pytest and GitHub Actions CI.

## Windows PowerShell
    py -3.11 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    python -m pip install -e ".[dev,usb,hid,ble,ai]"
    usb-operator serve

Open http://127.0.0.1:8765/docs. Dashboard: cd frontend; npm install; npm run dev.

## API
- GET /health, GET /v1/devices, GET /v1/policy, GET /v1/monitor, GET /v1/profiles
- POST /v1/discovery/scan
- POST /v1/telemetry/ingest; GET /v1/telemetry/latest; GET /v1/telemetry/history/{device_id}
- GET /v1/audit
- POST /v1/commands/plan, /v1/commands/{plan_id}/approve, /v1/commands/{plan_id}/execute

## Hardware status
| Interface | Status |
|---|---|
| USB / serial / HID | Read-only discovery |
| BLE | Optional advertisements; no pairing or control |
| ESP32 JSONL | Standalone read-only client and firmware example |
| Modbus TCP/RTU | Standalone read-only protocol primitives; no live binding |
| SCPI | Allowlisted read-only query helper; no live binding |
| Telemetry | Ingestion/storage/query API; no physical sensor polling yet |
| Camera, storage, PLC, robotics, remote agents | Planned / not live-enabled |
| Simulator | Demo only; no physical actuation |

## Safety
Unknown actions are denied. Selected writes require operator approval; critical actions are blocked. Independent hardware interlocks and emergency stops remain mandatory. Do not expose beyond loopback without strong authentication, TLS, firewalling and security review. Audit hashes are tamper-evident, not tamper-proof. Telemetry is not a safety interlock.

See docs/TELEMETRY.md, docs/INDUSTRIAL_PROTOCOLS.md, docs/ARCHITECTURE.md and docs/SAFETY.md.
