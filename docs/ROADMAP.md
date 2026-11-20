# Roadmap

- [x] Core API, device models, registry and policy gateway.
- [x] USB descriptor and serial discovery; read-only HID and optional BLE discovery.
- [x] Simulator, approval-gated command planning and React dashboard foundation.
- [x] SQLite inventory persistence, hash-chained audit and polling hot-plug monitor.
- [x] Strict device profile manifest validation; profiles remain inert.
- [x] Read-only JSONL serial protocol client and ESP32 firmware example (not connected to live command API).
- [x] Read-only Modbus TCP/RTU protocol primitives with bounds, transaction and CRC validation (not live-bound).
- [x] Allowlisted read-only SCPI serial query helper (not live-bound).
- [ ] Signed profiles, trust/key rotation and verified hardware identity binding.
- [ ] Profile-driven, operator-approved live serial read-only API integration.
- [ ] Modbus device profiles, register maps, scaling and hardware-in-the-loop tests.
- [ ] Camera capture, sensor adapters and permission controls.
- [ ] Remote host-agent pairing, TLS and role-based access.
- [ ] Android USB permission flow and authenticated host connection.
- [ ] iOS paired-host dashboard with certificate validation.
- [ ] PLC/robotics integrations with independent safety systems.
- [ ] Signed release packages and platform installers.

A checked item means code exists in the repository; it does not imply certification or production hardware validation.
