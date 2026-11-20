# Mobile and Remote Clients

## Android
Build a native Kotlin companion using Android USB Host APIs and USB permission intents for supported OTG devices. A companion may also connect to a host agent over HTTPS. Android permission is per device/session and some USB classes require vendor SDKs.

## iOS
Do not promise generic USB host access. Support a companion dashboard over HTTPS/WebSocket and accessory integrations that use Apple-supported accessory frameworks/protocols. A nearby computer agent can own the USB device and expose a restricted API.

## Other computers
Run one host agent per Windows/Linux/macOS machine. Bind to loopback by default. Remote mode requires TLS, authentication, explicit pairing, network allowlists and local policy enforcement. Never forward raw USB access over an unauthenticated socket.
