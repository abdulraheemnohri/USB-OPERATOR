# USB-OPERATOR

**Universal Physical Device AI Operating Platform** — local-first device discovery, governed command planning, hardware adapters and remote operator foundations.

> Status: v0.2.0 development foundation. This repository is not yet a production-ready universal hardware controller. Live control is intentionally limited; the included simulator is safe for demos.

## What exists now
- FastAPI backend and React/Vite dashboard.
- Read-only USB descriptor discovery (optional PyUSB/libusb) and serial-port discovery.
- Device registry and simulated ESP32 / Modbus meter.
- Policy engine: default deny, read-only allowlist, explicit approvals for selected writes, hard blocks for critical actions.
- Command planning with expiring plans and approval workflow.
- Optional OpenAI-compatible local/remote AI proposal adapter. AI proposals do not execute hardware commands.
- Pytest unit tests for policy and simulated command execution.

## Quick start (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,usb]"
usb-operator serve
```
Open http://127.0.0.1:8765/docs. In another terminal:
```powershell
cd frontend
npm install
npm run dev
```

## Quick start (Linux / macOS)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,usb]"
usb-operator serve
```
Then run the frontend with `cd frontend && npm install && npm run dev`.

## API
- `GET /health`
- `GET /v1/devices`
- `POST /v1/discovery/scan`
- `GET /v1/policy`
- `POST /v1/commands/plan`
- `POST /v1/commands/{plan_id}/approve`
- `POST /v1/commands/{plan_id}/execute`

## Hardware support status
| Interface | Current status |
|---|---|
| USB descriptors | Optional PyUSB discovery, read-only |
| Serial / ESP32 / Arduino | Serial-port discovery; device firmware protocol still required |
| HID | Dependency slot / adapter planned |
| BLE / Wi-Fi / Ethernet | Architecture planned; not implemented as device drivers |
| Camera / GPIO / storage | Planned adapters; not enabled for live operation |
| Modbus / SCPI / robotics | Planned protocol adapters; no live actuation yet |
| Simulator | Implemented demo devices and simulated commands |

USB enumeration and control are different capabilities. A VID/PID does not prove what a device can safely do. Device profiles must explicitly define protocol, commands, parameter schemas, limits and verification behavior.

## Safety model
- Default-deny for unknown actions.
- Read-only actions may run automatically.
- Actuating / writing actions require an operator approval.
- Critical actions are blocked in the default policy.
- Hardware emergency stops, fuses, contactors, safety PLCs and interlocks remain independent of this software.
- Do not expose the API to a network without authentication, TLS, firewall rules and a security review. Default bind is loopback.

## Cross-platform and mobile strategy
The Python host agent is intended for Windows, Linux and macOS. Android requires a native USB Host/OTG companion and explicit Android USB permission. iOS cannot offer unrestricted generic USB access; use supported accessory protocols and network-connected host agents. Mobile clients should connect to an authenticated host agent, not assume direct access to every USB class.

## Development
See [ARCHITECTURE.md](docs/ARCHITECTURE.md), [SAFETY.md](docs/SAFETY.md), [MOBILE.md](docs/MOBILE.md), and [ROADMAP.md](docs/ROADMAP.md).
