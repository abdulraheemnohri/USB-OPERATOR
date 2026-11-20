# USB-OPERATOR

Universal Physical Device AI Operating Platform. Local-first device discovery, governed command planning, hardware adapters and remote operator foundations.

**Status: v0.6.0 development foundation.** This is not a production-ready universal hardware controller. Live device actuation remains disabled; simulator execution is available for demos.

## Implemented
- FastAPI backend, React/Vite dashboard and CLI host agent.
- USB descriptor and serial-port discovery; optional read-only HID enumeration.
- Optional BLE advertisement discovery (disabled by default; no pairing or writes).
- SQLite device inventory persistence and hash-chained audit integrity checks.
- Background cross-platform polling monitor for device arrival/departure.
- Strict JSON device profile validation; profiles remain inert and disabled.
- Strict read-only JSONL serial protocol client and ESP32 firmware example.
- Read-only Modbus TCP/RTU protocol primitives with transaction/CRC/range validation.
- Read-only SCPI serial query helper with a strict query allowlist.
- Simulator, capability checks, default-deny policy and approval workflow.
- Optional AI proposal adapter; AI cannot execute hardware commands.
- Android USB OTG enumeration and iOS paired-host dashboard scaffolds.
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

BLE discovery is opt-in: set USB_OPERATOR_ENABLE_BLE=true. The monitor interval is configured by USB_OPERATOR_HOTPLUG_INTERVAL.

## API
- GET /health, GET /v1/devices, GET /v1/policy
- POST /v1/discovery/scan
- GET /v1/monitor, GET /v1/profiles, GET /v1/audit?limit=100
- POST /v1/commands/plan, /v1/commands/{plan_id}/approve, /v1/commands/{plan_id}/execute

## Hardware support status
| Interface | Status |
|---|---|
| USB descriptors | Read-only discovery |
| Serial / ESP32 | Port discovery + standalone read-only JSONL client/firmware example; API control not enabled |
| HID | Read-only enumeration |
| BLE | Optional advertisement discovery; no pairing/control |
| Modbus TCP/RTU | Standalone read-only protocol primitives; no live device binding |
| SCPI | Allowlisted read-only serial query helper; no live device binding |
| Wi-Fi / Ethernet agents | Planned |
| Cameras / sensors / storage | Planned, not live-enabled |
| PLC / robotics / motor control | Planned, not live-enabled |
| Simulator | Demo commands; never physical actuation |

A protocol helper is not a complete hardware driver. Device register maps, scaling, identity binding, physical limits, bus configuration and read-back verification must be commissioned per model before connecting real equipment.

## Safety
Unknown actions are denied. Selected writes require operator approval; critical actions are blocked. Independent hardware interlocks and emergency stops remain mandatory. Do not expose the API beyond loopback without authentication, TLS, firewalling and a security review. Audit hashes are tamper-evident, not tamper-proof.

## Mobile and multi-computer
The host agent targets Windows, Linux and macOS. Android requires native USB Host permissions for direct OTG. iOS generic USB host access is limited; its companion primarily connects to a paired host agent. Multi-computer control will use authenticated agents, each enforcing local policy.

See docs/ARCHITECTURE.md, docs/SAFETY.md, docs/MOBILE.md, docs/PERSISTENCE_AND_AUDIT.md, docs/DEVICE_PROFILES.md, docs/HOTPLUG.md, docs/ESP32_JSONL_PROTOCOL.md and docs/INDUSTRIAL_PROTOCOLS.md.
