# Security

Treat captures as untrusted and potentially sensitive. Review them before
committing or sharing. Normal validation never executes expressions or fetches
schemas. Resource limits are documented in README and limitations.
Baselines are also untrusted: check validates bounded strict JSON, protocol
metadata, catalog structure, references, and undefined-slot metadata before
comparison. It never opens the baseline for writing. JSON comparison reports
include before/after application values; review them before uploading CI logs.

Do not post credentials or sensitive captures in public issues. Until a public
repository with private reporting is configured, report security concerns
privately to the repository owner using an existing trusted contact channel.
No public security contact has been established for this unreleased project.
