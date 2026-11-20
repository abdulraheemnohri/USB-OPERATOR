# Architecture

## Core principle
AI is a planner, never the hardware authority. All proposed operations pass through typed device profiles, the policy gateway, authorization and a transport adapter.

## Layers
1. Clients: React dashboard, desktop shell, Android/iOS companions.
2. Host agent/API: local FastAPI service; future remote agents use mutually authenticated channels.
3. AI planner: local or remote OpenAI-compatible provider; emits suggestions only.
4. Policy gateway: default-deny, action classification, approval and audit.
5. Device registry: stable IDs, transport, descriptors, capabilities and health.
6. Hardware abstraction: USB, Serial, HID, BLE, network, GPIO and camera adapters.
7. Protocol plugins: ESP32 framed serial protocol, Modbus RTU/TCP, SCPI, vendor SDKs and robotics APIs.
8. Physical equipment: hardware interlocks and emergency stops remain authoritative.

## Device identity
Use transport + stable OS path + VID/PID + serial number where available. Never trust a display name as identity. USB descriptors are metadata, not a protocol specification.

## Capability profiles
Each profile should declare supported actions, JSON schemas, risk class, required permissions, timeout, rate limit, preconditions and post-execution verification. Unknown capabilities are unavailable.

## Hybrid AI
Local endpoint is attempted first. A remote endpoint is optional fallback. Only user-approved, redacted context should leave the host. AI output is untrusted input and must be schema-validated.

## Multi-computer topology
Each computer runs a host agent and owns its directly attached hardware. A central console discovers agents over an authenticated network. The agent enforces local policy even if the console or AI is compromised.
