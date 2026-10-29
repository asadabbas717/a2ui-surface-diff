# Changelog

## 1.0.0 — GitHub alpha, 2026-10-30

- Owner-selected version `v1.0.0`, with matching package/CLI metadata, build
  verification, filenames, and CI. The alpha/pre-release label is retained;
  this version number does not expand the MVP or claim production maturity.
- Private vulnerability reporting enabled; main commit email metadata repaired
  with all original source trees preserved. Local no-reply identity and ignored
  credential/application-data folders reduce future accidental exposure.
- GitHub-only distribution; no PyPI upload. Cached or external copies of old
  commits may retain original metadata; account-wide email settings remain as
  explicitly chosen by the owner.

## 0.1.0 — GitHub alpha, 2026-10-30

- Offline A2UI v0.9.1 validation/replay, canonical snapshots, structural checks,
  stable machine reports, and CI exit codes 0/1/2.
- Phase 3 audit: escape terminal control/format characters in human output while
  retaining exact JSON paths and printable Unicode.
- Phase 4: portable dependency locks, hash-verified runtime/build dependencies,
  advisory audit, fresh offline wheel/source installation proof, repeat-build
  digest verification, output race/boundary hardening tests, and performance
  sanity tooling. Refresh immutable CI action pins to Node 24.
- Return processing-error code 2 for closed help/version output pipes rather than
  interpreter shutdown code 120.
- Published as the initial GitHub alpha before the owner requested v1.0.0.
  Development previews below were never published; no PyPI upload occurred.

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
