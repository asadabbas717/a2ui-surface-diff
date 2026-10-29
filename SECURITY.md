# Security

Treat captures as untrusted and potentially sensitive. Review them before
committing or sharing. Normal validation never executes expressions or fetches
schemas. Resource limits are documented in README and limitations.
Baselines are also untrusted: check validates bounded strict JSON, protocol
metadata, catalog structure, references, and undefined-slot metadata before
comparison. It never opens the baseline for writing. JSON comparison reports
include before/after application values; review them before uploading CI logs.

Do not post credentials or sensitive captures in public issues. Private
vulnerability reporting is enabled for this public repository. Use
[Report a vulnerability](https://github.com/asadabbas717/a2ui-surface-diff/security/advisories/new)
to send security findings privately to the maintainers. Include a minimal
synthetic reproduction; do not attach unrelated personal data or credentials.
No personal contact address is required or published by this policy.

Distribution is limited to GitHub by owner instruction. Local credential files
and common output folders are ignored by default; already tracked files and
explicit forced additions are not protected by ignore rules.
