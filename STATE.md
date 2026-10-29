# SurfaceDiff development state

Updated: 2026-10-30 (Asia/Karachi).

## Current state

All four engineering phases are complete. Owner requested version v1.0.0 after
explicitly approving GitHub alpha upload/publication. Keep the alpha/pre-release
label and GitHub-only distribution; no PyPI upload or visibility change.
The v0.1.0 alpha was published immediately before this version request:
https://github.com/asadabbas717/a2ui-surface-diff/releases/tag/v0.1.0
It points to 82bb2254493458ec268873dbb601572a9c7c7564, whose four-job hosted
matrix passed: https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40969133820
Do not relabel a 0.1.0 wheel as 1.0.0. Version metadata, tests, verifier, artifact
names and CI paths now target 1.0.0 and must pass before its GitHub publication.

## Privacy holds resolved

Private vulnerability reporting enabled and confirmed through owner-authenticated
GitHub. SECURITY.md links to the private report form. Existing secret scanning
and push protection remain enabled. Owner authorized main-history email repair:
13 original commit trees were verified identical, author/committer emails changed
to no-reply, and one invalidated initial signature removed. Remote replacement
used exact force-with-lease. A fresh remote clone verified private commit emails
throughout normal history. Ignored local recovery bundle/mapping remain in .tmp;
never upload them. Re-clone or carefully rebase old clones; do not merge old
history back. Historical SHA/CI references in audits describe original evidence.
Cached commits, old workflow refs and external copies may still retain metadata;
no claim of total erasure is made. See docs/privacy-review.md.

Owner explicitly declined GitHub account-wide email privacy. Leave that setting
unchanged. Future web edits/merges may expose configured email; SurfaceDiff local
commits use no-reply. No credentials, login addresses or notification settings
were changed. Normal runtime remains offline. Real captures/reports can contain
sensitive data; ignored local paths are safeguards, not complete protection.

## Verification and continuity

Previous accepted suite: 188 tests, 99.30% coverage (714/719), Ruff lint/format,
strict mypy (14 modules), pip check, runtime/development audits, CLI smokes,
performance sanity, wheel/source build and metadata checks, fresh separate offline
installs, schema checks, and identical same-platform repeat-build hashes.
Pinned upstream 4767c140e13b4d8952b92b3bef35b81121dc8810 and vendored raw
hashes/notices remain unchanged. No runtime dependency or MVP feature expansion.
Detailed historical phase audits, security/compatibility decisions, commands,
limits and artifact proof are in docs/phase*-audit.md, docs/release-evidence.md,
docs/security-review.md, docs/releasing.md and docs/limitations.md.

## Next required step

Run version-1.0.0 local gates and artifact/privacy checks, commit/push the tested
milestone, and verify all Windows/Linux Python 3.12/3.13 CI jobs for that exact
commit. Publish only the reviewed 1.0.0 wheel/source/SHA256SUMS to the approved
GitHub alpha release; verify remote asset hashes, tag commit and pre-release flag.
Record actual release and CI URLs after observing them. Preserve the historical
v0.1.0 release and tag rather than deleting published data without approval.
No fifth phase, PyPI upload, paid service or unsolicited feature work.
