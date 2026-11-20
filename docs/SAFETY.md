# Safety and Governance

## Default policy
- Allow automatic: identify, status, read, list_capabilities, capture_preview.
- Require explicit approval: write, gpio_set, relay_set, motor_move, restart, firmware_update, network_config, storage_write.
- Block by default: firmware_flash, erase_storage, format_storage, unlock, disable_safety, bypass_interlock, mains_switch, motor_unbounded.
- Unknown actions: deny.

## Mandatory safeguards before production
1. Device-specific profiles with strict parameter schemas and physical range limits.
2. Independent hardware emergency stop and safe-state design.
3. Operator identity, short-lived approvals and immutable audit records.
4. Command timeouts, rate limits, idempotency and disconnect handling.
5. Read-back verification and explicit failure states.
6. No raw shell, arbitrary USB control transfers or unrestricted HID injection from AI output.
7. Firmware updates require signed images, compatibility checks, recovery path and separate authorization.
8. Test against simulators and hardware-in-the-loop fixtures before enabling a live adapter.

This software is not a safety-rated controller and must not be used as the sole protection for machinery, mains electricity, life-safety equipment or hazardous processes.
