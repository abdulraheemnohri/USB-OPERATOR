# USB-OPERATOR

Universal Physical Device AI Operating Platform. Local-first device discovery, governed command planning, hardware adapters and remote operator foundations.

**Status: v0.3.0 development foundation.** This is not yet a production-ready universal hardware controller. Live device actuation remains disabled; simulator execution is available for demos.

## Implemented
- FastAPI backend, React/Vite dashboard and CLI host agent.
- USB descriptor and serial-port discovery; optional read-only HID enumeration.
- Optional BLE advertisement discovery (disabled by default; no pairing or writes).
- SQLite device inventory persistence and hash-chained audit event integrity checks.
- Simulated ESP32 / Modbus meter, device registry and capability checks.
- Default-deny policy, expiring command plans and approval workflow.
- Optional OpenAI-compatible local/remote AI proposal adapter; AI cannot execute hardware actions.
- Android USB OTG enumeration scaffold and iOS paired-host dashboard scaffold.
- Pytest and GitHub Actions CI.

## Quick start — Windows PowerShell
    py -3.11 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    python -m pip install -e ".[dev,usb,hid,ble,ai]"
    usb-operator serve

Open http://127.0.0.1:8765/docs. In another terminal: cd frontend; npm install; npm run dev.

## Quick start — Linux / macOS
    python3.11 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e ".[dev,usb,hid,ble,ai]"
    usb-operator serve

BLE discovery is opt-in: set USB_OPERATOR_ENABLE_BLE=true before starting the service. Install Bluetooth system dependencies and grant OS Bluetooth permissions first.

## API
- GET /health, GET /v1/devices, GET /v1/policy
- POST /v1/discovery/scan
- GET /v1/audit?limit=100 (includes hash-chain verification)
- POST /v1/commands/plan
- POST /v1/commands/{plan_id}/approve
- POST /v1/commands/{plan_id}/execute

## Support status
| Interface | Status |
|---|---|
| USB descriptors | Read-only discovery |
| Serial / ESP32 / Arduino | Port discovery; protocol adapter and firmware pending |
| HID | Read-only enumeration |
| BLE | Optional advertisement discovery; no pairing/control |
| Wi-Fi / Ethernet | Planned host-agent transport |
| Cameras / sensors / storage | Planned, not live-enabled |
| Modbus / SCPI / robotics / PLC | Planned, not live-enabled |
| Simulator | Demo commands; never physical actuation |

USB enumeration is not device control. A VID/PID does not establish protocol or safe operating limits. Each live adapter needs an independently reviewed device profile, parameter schema, physical limits, timeout, read-back verification and hardware-in-the-loop tests.

## Safety
Unknown actions are denied. Read-only actions can run automatically. Selected writes require operator approval. Critical actions are blocked. Independent hardware interlocks and emergency stops remain mandatory. Do not expose the API beyond loopback without authentication, TLS, firewalling and a security review. The hash chain is tamper-evident, not tamper-proof.

## Mobile and multi-computer
The host agent targets Windows, Linux and macOS. Android needs native USB Host permissions for direct OTG access; iOS generic USB host access is limited and the companion primarily connects to a paired host agent. Multi-computer control will use authenticated agents, each enforcing its own local policy.

See docs/ARCHITECTURE.md, docs/SAFETY.md, docs/MOBILE.md, docs/PERSISTENCE_AND_AUDIT.md and docs/ROADMAP.md.
