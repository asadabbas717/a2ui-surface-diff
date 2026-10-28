# Roadmap

Implement one phase at a time. Owner instruction is required to start the next.

1. **Foundation and validation:** packaging, bounded strict JSONL, pinned offline
   official schema validation, validate CLI, tests, lint, typing, baseline CI.
2. **Replay and snapshots:** surface/component lifecycle, data model pointer
   semantics, progressive/final references, canonical snapshots, snapshot CLI.
3. **Diff and reports:** structural comparisons, check CLI, stable paths,
   regression exit codes, baseline protection, CI integration fixtures.
4. **Hardening and release:** adversarial audit, Windows/Linux and 3.12/3.13
   verification, complete docs, artifact installation, dependency/license review,
   explicit owner approval before remote creation/publication/visibility changes.

## Phase 1 plan

Inspect the empty workspace and installed Python; verify names and upstream
schemas/license; vendor exact assets at an immutable revision; create a small
CLI and strict streaming reader; resolve all schema references locally; reject
unsupported catalogs explicitly; add high-value parser/schema/CLI tests; run
format, lint, type, coverage, build, and installation checks; record evidence.

Acceptance: source installation exposes `surfdiff`; official examples validate;
malformed/unsupported input returns 2 with file and physical line diagnostics;
resource limits fail predictably; runtime requires no network; tests and quality
checks pass. Lifecycle validation remains explicitly deferred to Phase 2.
