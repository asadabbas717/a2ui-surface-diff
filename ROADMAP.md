# Roadmap

Implement one phase at a time. Owner instruction is required to start the next.

Phase 1: independently audited and repaired; local acceptance passed (see
`docs/phase1-audit.md`). The owner has authorized the next single phase.
Phase 2: audited and repaired; local acceptance passes. The original Phase 2
revision passed the full hosted matrix; see `docs/phase2-audit.md`.
The owner has authorized Phase 3 and committing/pushing tested milestones.
Phase 3 is complete and pushed as c3ffc6b. Hosted run 40786664420 passed the
full Windows/Linux and Python 3.12/3.13 matrix.
Phase 3 has now passed independent review after a terminal-output repair; see
`docs/phase3-audit.md`. The owner authorizes the next single phase and tested pushes.

Phase 4 is complete and accepted after the repairs recorded in STATE.md.
Implementation 02bd7ca passed all four refreshed hosted jobs (run 40794910578),
188 tests per target, audits, and fresh/reproducible artifact checks. All four
phases are complete. Next: owner artifact/release review and explicit permission
before any publishing/tag/release action; no fifth phase is implied.

## Phase 4 scope and acceptance

Harden the existing MVP only: adversarial/error/output tests, performance sanity
checks, runtime dependency/license/vulnerability review, universal dependency
locks, fresh wheel/sdist installation checks, complete documentation/release notes,
and a verified Windows/Linux Python 3.12/3.13 CI matrix with reviewed action pins.
Keep runtime offline, existing schemas/CLI/report formats stable, and no overwrite
or automatic approval path. No feature expansion, publication, tags, or releases.

Accept only with executed reproducible tests and artifact evidence, no known
Critical/High release blocker, accurate compatibility limitations, a current
security/dependency review, complete release checklist, and exact next owner step.
Risks: platform markers/wheels, offline source builds, advisory freshness, action
runtime changes, resource costs, filesystem guarantees, and overclaiming readiness.

## Phase 3 scope and acceptance

Add read-only baseline validation, deterministic structural comparison, check
CLI, concise text reports, and a stable JSON comparison report. Preserve exact
paths and meaningful ordering; do not evaluate expressions or report visual
changes. Added/removed containers and type changes must avoid redundant reports.
Accept: identical/equivalent state exits 0, differences exit 1, all malformed or
unsupported inputs and incomplete comparisons exit 2. Validate baseline structure,
protocol metadata, IDs, references, bounds, and undefined-slot metadata before
comparison. Baseline and capture bytes remain unchanged on every check outcome.
Run unit/integration/CLI, coverage, lint, format, types, dependency, packaging,
artifact-installation, and available CI verification. No Phase 4 implementation.

Risks: boolean/number equality, array ordering and absence, unsafe/malformed
baselines, misleading duplicate diagnostics, and unbounded report size. Use strict
bounded JSON parsing, semantic baseline checks, explicit value states, stable
sorting, and an explicit failure when comparison limits prevent a complete result.

## Phase 2 scope and acceptance

Implement schema-validated replay, lifecycle checks, independent surfaces,
component collection upserts, bounded JSON Pointer data updates, progressive
references with final graph checks, and deterministic versioned snapshots.
Expose `snapshot <capture> --out <new-path>`; strengthen validate to include
replay/final-state checks. Do not implement comparison/check or release work.

Acceptance: equivalent message batching/mapping order yields identical snapshot
bytes; deletion/recreation resets state; arrays distinguish null and deleted slots;
final references/roots/cycles fail predictably; source inputs are unchanged;
existing output is never replaced; no expression evaluation/network occurs;
tests, coverage, lint, format, typing, and artifact checks pass locally.

Risks: SDK/schema disagreement about component patches and null/JSON Pointer
behavior; sparse-array serialization; state-growth attacks; filesystem-dependent
atomic output. Decisions are documented in protocol-compatibility.md and
snapshots.md. Hosted cross-platform verification remains a separate evidence item.

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

## Post-phase owner review — 2026-10-30

Owner requires GitHub-only distribution and delegates privacy review. Safe
follow-up safeguards are recorded in docs/privacy-review.md and STATE.md. All
four phases remain complete. First release is held for private-reporting account
access and the existing public commit-email exposure; no PyPI upload, visibility
change, history rewrite, or fifth phase is authorized by this follow-up.
