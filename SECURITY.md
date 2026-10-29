# Security

Treat captures as untrusted and potentially sensitive. Review them before
committing or sharing. Normal validation never executes expressions or fetches
schemas. Resource limits are documented in README and limitations.
Baselines are also untrusted: check validates bounded strict JSON, protocol
metadata, catalog structure, references, and undefined-slot metadata before
comparison. It never opens the baseline for writing. JSON comparison reports
include before/after application values; review them before uploading CI logs.

Do not post credentials or sensitive captures in public issues. The repository is public. Private vulnerability reporting has not
been verified from an authenticated administrator session. Use an existing trusted
private contact channel until it is confirmed. If none exists, a public issue may
ask for a private channel, but must contain no vulnerability details, captures,
credentials, or personal information. No personal email address is published here.

Distribution is limited to GitHub by owner instruction. Local credential files
and common output folders are ignored by default; already tracked files and
explicit forced additions are not protected by ignore rules.
