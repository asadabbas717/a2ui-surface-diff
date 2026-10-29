# SurfaceDiff 0.1.0 — prepared release notes

Status: local artifacts prepared, not published or released. This is the first
small public-facing release candidate for owner review, not a production maturity
claim. SurfaceDiff is independent/unofficial and has no Google/A2UI endorsement.

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
