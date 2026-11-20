# Roadmap

- [x] Repository audit and development branch.
- [x] Core API, device models, registry and policy gateway.
- [x] USB descriptor and serial discovery.
- [x] Simulator and approval-gated command planning.
- [x] React dashboard foundation and architecture documentation.
- [x] SQLite device inventory persistence.
- [x] Hash-chained audit events and integrity verification endpoint.
- [x] Read-only HID enumeration adapter.
- [x] Optional BLE advertisement discovery (opt-in; no pairing or writes).
- [x] Cross-platform polling hot-plug monitor with per-adapter failure isolation.
- [x] Strict device profile manifest validation and diagnostics endpoint (profiles inert by default).
- [x] Strict read-only JSONL serial protocol client and ESP32 firmware example (not wired to live command API).
- [ ] Signed device profiles and trust/key rotation.
- [ ] Native OS event-driven hot-plug backends.
- [ ] Reviewed profile-to-device identity binding and live read-only serial API integration.
- [ ] Modbus RTU/TCP and SCPI read-only integrations.
- [ ] Camera capture and sensor adapters with permission controls.
- [ ] Remote host agent pairing, TLS and role-based access.
- [ ] Android USB permission flow and authenticated host connection.
- [ ] iOS paired-host dashboard with certificate validation.
- [ ] Hardware-in-the-loop test suite and signed release packages.

A checkbox is marked complete only when code exists in this repository; roadmap items are not implied to be implemented.
