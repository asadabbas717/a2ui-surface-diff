# SurfaceDiff development state

Updated: 2026-10-30 (Asia/Karachi).

## Current state

All four engineering phases are complete. Owner-approved v1.0.0 is published
as a GitHub alpha/pre-release, with matching package/CLI/artifact metadata:
https://github.com/asadabbas717/a2ui-surface-diff/releases/tag/v1.0.0

Release tag v1.0.0 is fixed at 507f4a5dde26981d586044143beb5187a7037c4a.
Its four-job Windows/Linux Python 3.12/3.13 matrix passed:
https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40969929111

Release API confirmed draft=false, prerelease=true, and exactly three uploaded
assets: 1.0.0 wheel, 1.0.0 source archive and SHA256SUMS. Downloaded all three
from the public release and verified byte identity against the reviewed local
build and the manifest. GitHub adds its two source-code downloads separately.
No PyPI upload, paid service, visibility change or runtime feature expansion.
The earlier v0.1.0 alpha remains historical; it was published immediately before
the owner's version change. No published release/tag was deleted or retargeted.
This documentation follow-up does not change the immutable release commit/assets.

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

## Verified release artifacts

- a2ui_surface_diff-1.0.0-py3-none-any.whl:
  a213cd2269c9a8981485f84f4d6474043ba5f7af9aa82c23065d9eec18894e1f
- a2ui_surface_diff-1.0.0.tar.gz:
  f7edbbeee5b43017c78f5d1578c026a971e4f543125f6eb9a9304e51f5017179

## Next required step

No release hold or development phase remains. Use the GitHub alpha within its
documented scope and report vulnerabilities privately. Retain the owner-selected
account privacy setting and never upload real captures or local recovery data.
Future work requires a concrete owner request; no automatic release, history
rewrite, PyPI publication, or feature expansion. Keep tag v1.0.0 immutable.
