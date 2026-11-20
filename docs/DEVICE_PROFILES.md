# Device Profiles

A device profile is a declarative contract between an identified device and an adapter. Profiles must be reviewed before use and must never be generated directly into a live control path.

Required fields for a production profile:
- stable profile ID and version;
- supported VID/PID or vendor/product identity rules;
- transport and protocol name/version;
- explicit capabilities and action schemas;
- risk class, approval requirements and numeric limits;
- command timeout, retry policy and rate limit;
- safe-state behavior and verification/read-back operation;
- firmware compatibility and profile signature metadata.

The example profile is documentation/demo metadata only. It does not enable live GPIO writes.
