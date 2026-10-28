# Changelog

## 0.1.0.dev3 — unreleased

- Phase 2 audit: preserve null when deleting absent descendants; return code 2
  on output-stream failures. Repaired milestone passes hosted CI.
- Phase 3: strict read-only baseline validation, deterministic structural diffs,
  `check`, exit codes 0/1/2, and versioned text/JSON comparison reports.
- Distinguish booleans/numbers and absent/undefined/null values, summarize
  container/type/order changes without redundant descendant reports, and reject
  incomplete comparisons. Add checkout regression fixtures and report schemas.

## 0.1.0.dev2 — unreleased

- Audit repairs: reject non-JSON whitespace lines; locate Windows scripts using
  sysconfig rather than assuming they are beside the interpreter.
- Phase 2: bounded replay, lifecycle, component upserts, data pointers,
  progressive/final references, cycle detection, and canonical snapshots.
- Add `snapshot --out` with atomic no-overwrite output; validation now checks
  final supported state and emits report version 2.

## 0.1.0.dev1 — unreleased

- Phase 1: installable `surfdiff validate`, strict bounded JSONL input, pinned
  offline A2UI v0.9.1/Basic Catalog schema checks, text and JSON diagnostics.
- Initial tests, lint/type/coverage tooling, and baseline CI configuration.
- Replay, snapshots, and structural comparisons remain planned.
