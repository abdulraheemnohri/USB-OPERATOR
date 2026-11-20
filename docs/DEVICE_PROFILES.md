# Device profile manifests

Profiles are strict JSON manifests validated by Pydantic. Unknown fields, undeclared actions, duplicate capabilities, unsafe read-only approval combinations and invalid ranges are rejected. The API only lists profiles; it does not activate them or bind them to live hardware.

Each profile should declare a stable ID/version, transport, protocol, identity hints, capabilities and action metadata. Profiles in the sample directory remain disabled. A profile is not a driver: production activation still requires a reviewed protocol adapter, explicit physical limits, timeouts, read-back verification and hardware-in-the-loop tests.

The current loader reads JSON files from USB_OPERATOR_PROFILES_DIR (default examples/profiles). Do not load profile directories writable by untrusted users.
