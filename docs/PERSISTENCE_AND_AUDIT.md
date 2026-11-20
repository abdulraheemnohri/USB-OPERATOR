# Persistence and audit

USB-OPERATOR stores discovered device metadata in SQLite and restores it at startup. Device state in this inventory is last-known metadata, not proof that a device is currently connected; run discovery to refresh.

The audit table is append-only through the application API and each record contains the previous record hash plus its own SHA-256 digest. The API exposes verification status. This is tamper-evident, not tamper-proof: a privileged attacker able to rewrite the database and recompute the entire chain can alter it. Production deployments should export signed checkpoints to a separate protected system.

Audit payloads deliberately omit raw command parameter values by default. Keep credentials, personal data, and sensitive device telemetry out of audit events.
