# Hot-plug monitoring

A background polling monitor runs inside the host agent and reports newly discovered and disconnected devices. The polling interval is configured with USB_OPERATOR_HOTPLUG_INTERVAL (minimum two seconds). Only transports whose adapter scan completed successfully are reconciled, preventing an unavailable optional driver from falsely disconnecting its devices.

Polling is cross-platform and read-only. It is not an OS-native interrupt/event driver and detection latency depends on the configured interval. BLE advertisements can disappear temporarily; use a longer interval or a future transport-specific presence policy before treating BLE absence as a physical disconnect.
