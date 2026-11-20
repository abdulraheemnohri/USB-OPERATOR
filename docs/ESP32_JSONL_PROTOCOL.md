# ESP32 JSONL protocol — read-only starter

Protocol ID: usb-operator-jsonl/1. Transport: USB serial at 115200 baud. Each request and response is one UTF-8 JSON object terminated by LF. Every response echoes the request ID. Host parsing rejects malformed, oversized, wrong-version and mismatched-ID frames.

Supported firmware actions:
- identify — returns board and firmware identity
- status — returns readiness and uptime
- read — returns a named, explicitly supported telemetry channel

The Python client only permits those three read-only actions. GPIO writes, relay switching, firmware flashing, reset, and motor commands are intentionally absent. This firmware is a protocol example, not a certified industrial controller. GPIO34 is an ADC input on common ESP32 boards; verify the exact board pinout and electrical limits before wiring anything.

## Build
Install Arduino IDE or Arduino CLI and the ArduinoJson library. Open examples/firmware/esp32-jsonl-readonly/esp32-jsonl-readonly.ino, select the exact ESP32 board, and upload. Use a safe low-voltage analog source only within the board's documented input range.

## Example request
    {"protocol":"usb-operator-jsonl/1","id":"abc123","action":"status","parameters":{}}

## Example response
    {"protocol":"usb-operator-jsonl/1","id":"abc123","ok":true,"data":{"status":"ready","uptime_ms":1000}}

The serial client is not connected to the general command execution endpoint yet. Hardware profile binding, device identity verification, per-action policy enforcement, hardware-in-the-loop testing and operator approval UI must be completed before any live serial integration is enabled.
