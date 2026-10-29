# SurfaceDiff 1.0.0 — GitHub alpha release notes

Version: v1.0.0 at the owner's request, retaining the alpha/pre-release label.
This version does not claim production maturity or expand the MVP. Distribution
is GitHub-only; no PyPI upload. SurfaceDiff is independent/unofficial and has no
Google/A2UI endorsement. The earlier v0.1.0 alpha is historical.

## Included

- `validate`: bounded UTF-8 JSONL and pinned A2UI v0.9.1 Basic Catalog checks,
  lifecycle replay, effective data updates, and final graph integrity.
- `snapshot --out`: version 1 canonical active state, preserving IDs, order,
  actions/bindings, nulls, and undefined array slots, with no-overwrite output.
- `check --baseline`: deterministic structural differences, human/JSON reports,
  and exit 0 equal, 1 different, 2 invalid/unsupported/incomplete processing.
- Offline normal operation; expressions remain data and are never evaluated.
- Windows/Linux Python 3.12/3.13 CI, portable locks, hash-verified offline artifact
  installation proof, advisory checks, and documented security/resource bounds.

## Compatibility and limits

The pinned v0.9.1 schemas accept both v0.9 and v0.9.1 envelope labels. Only the
two documented Basic Catalog identifiers are supported. No v0.8, candidate v1.0,
arbitrary catalogs, renderer, model inference, function evaluation, auto-approval,
or baseline rewrite is included. Full definitions are required by the pinned
schema, even where SDKs accept type-omitting patches.

Structural equality is not visual equality. Arrays generally compare by index;
exact child/tab reorders are summarized. Added/removed containers and type changes
suppress redundant descendants. Reports and snapshots may contain sensitive data.
Resource limits can reject oversized inputs/comparisons and do not impose a wall
clock sandbox. Snapshot publication requires hard-link support and is not a
power-loss durability guarantee. See limitations.md, snapshots.md, reports.md,
and release-evidence.md for exact contracts and verified results.

## Observed v1.0.0 publication — 2026-10-30

Owner-approved GitHub alpha/pre-release is public:
https://github.com/asadabbas717/a2ui-surface-diff/releases/tag/v1.0.0

Tag v1.0.0 points to 507f4a5dde26981d586044143beb5187a7037c4a.
All four exact-commit hosted jobs passed:
https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40969929111

Local suite: 188 passed, 99.30% coverage; lint/format/types/pip check and fresh
offline wheel/source installations/repeated-build hashes passed. Downloaded the
three published assets and checked byte identity and SHA256SUMS against the
reviewed local build. Release API confirmed non-draft, pre-release=true and the
three expected asset names. No PyPI upload. The earlier v0.1.0 alpha is historical;
no published data was deleted. This supersedes earlier pending-release steps.
Remaining cache/external-copy privacy limitations are documented, not claimed
to be erased. Account-wide email privacy remains unchanged at owner request.
