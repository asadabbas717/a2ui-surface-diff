# SurfaceDiff development state

Updated: 2026-10-29 (Asia/Karachi).

## Current status and authorization

Current iteration starts clean at 733bcbb. Phase 3 is independently reviewed;
terminal control injection in human output was repaired (172 tests, 99.72%
coverage; all configured checks pass). See docs/phase3-audit.md. The owner has
authorized Phase 4 after this acceptance and commit/push of tested milestones.
The remainder of this state records the preceding Phase 3 milestone until Phase 4
updates replace it. Package publication/releases remain unauthorized.

Phases 1–3 are complete locally. Phase 4 has not started. Development version:
0.1.0.dev3; target release remains 0.1.0. Branch: main. This iteration started
clean and synchronized at 476bda703b5d9c65d25c3b232a7271ced8af6916. No unrelated
user changes were present or removed.

Remote: https://github.com/asadabbas717/a2ui-surface-diff.git.
The owner explicitly authorized commit/push of every milestone after its checks
pass. The Phase 2 audit repair was committed/pushed as
57c9426a21355c8fc48eb10b622d797a4b1f812b. Phase 3 was committed/pushed as
c3ffc6ba306938213ccd8ef32918d1672e729d4e. Hosted run 40786664420 passed all four
Ubuntu/Windows, Python 3.12/3.13 jobs for that exact implementation commit.
This follow-up continuity commit changes documentation only.
No package publication, release, or visibility change is authorized or performed.

## Previous-phase audit

See docs/phase2-audit.md. Two Medium defects were repaired: absent deletion
through a null intermediate changed state, and stdout rendering bypassed the
CLI failure boundary. Nulls now remain unchanged on absent-descendant deletion;
output failures return processing-error code 2. During Phase 3, explicit flush
and failed-stream closure also fixed buffered shutdown behavior, verified with a
real closed-pipe subprocess. No Critical/High defect was reproduced in the audit.

Repaired Phase 2 local evidence: 105 tests, 99.57% statement coverage, and all
lint/format/type/dependency/build/metadata checks passed. Its hosted run
40784042065 passed all four Ubuntu/Windows, Python 3.12/3.13 jobs. Original Phase 2
run 40783646327 also passed all four jobs. Original Phase 1 run 40781697398 failed
Windows on an entrypoint test-path defect fixed in 08be30a; the historical failure
is retained in docs/phase1-audit.md rather than represented as current success.

## Phase 3 delivered

- check CLI: validate baseline first, replay/validate candidate, compare final
  supported state. Exit 0 equal, 1 differences, 2 invalid/incomplete processing.
- Read-only bounded strict JSON baseline parsing, duplicate/nonfinite/Unicode
  rejection, wrapper schema, exact version/protocol metadata checks, matching
  surface/component IDs, official schema checks, graph/state/undefined-slot checks.
- Deterministic structural paths and codes for surfaces, components/types,
  properties, actions, child/tab ordering, references, and effective data.
- Added/removed containers and component type changes suppress descendant noise.
  Arrays compare by index; exact child/tab reorders produce a single change.
- JSON-aware equality: booleans differ from numbers; 1 and 1.0 compare equal.
  Null, absent properties, and undefined array slots remain distinct.
- Text output contains concise codes/paths; versioned JSON reports contain
  explicit before/after value states. Sensitive values may be present in JSON.
- SurfaceDiff-authored snapshot-v1.json and check-report-v1.json contracts,
  independent baseline/no-difference/regression fixtures, realistic checkout demo,
  CI check smoke command, and documentation updates.
- Strict parsing shared between JSONL and snapshots. No new dependencies.

## Architecture and compatibility decisions

baseline.py composes existing official schema validation and replay integrity
checks, then returns canonical state. comparison.py owns read-only diff/report
logic. analysis/replay/data_model/snapshot retain their earlier responsibilities.
No rendering, network access, expression evaluation, automatic approvals, filters,
plugins, custom catalogs, or candidate v1.0 features were added.

Pinned upstream revision: 4767c140e13b4d8952b92b3bef35b81121dc8810. Vendored assets,
hashes, and license notices are unchanged. New SurfaceDiff schemas are separate
from upstream hash entries. Both official v0.9/v0.9.1 envelope versions and the two
documented Basic Catalog IDs remain supported. Captured catalog IDs are significant.
SDK/schema/null/pointer differences remain explicit in protocol-compatibility.md
and snapshots.md. Component collection upserts retain other components; each full
definition replaces properties. Dynamic values and bindings compare structurally.

Snapshot wrapper version remains 1; validation report remains version 2. Check
reports use command=check/report_version=1, with passed/different/error status.
Consumers dispatch on command and version. Error reports contain no partial diff.
Snapshots/baselines: 64 MiB, 1M value nodes, depth 80 including wrappers. The writer
checks the same bounds so it does not publish an unreadable baseline. Existing
capture/replay limits remain: 16 MiB stream, 1 MiB physical line, 10000 messages,
100,000 message nodes/depth 64, 1,000 active surfaces, 20,000 active components,
200,000 combined model nodes/depth 64, maximum array index 10,000.

Comparisons stop with code 2 at 20000 changes or a 32 MiB serialized change-payload
budget. The budget prevents long repeated ancestor keys from multiplying report
memory use. Paths sort lexicographically after JSON Pointer escaping, then by code;
index 10 precedes 2. Undefined data slots are restored before comparing and are not
reported twice through raw undefinedDataPaths metadata. Added/removed containers
and type changes are intentionally summarized. Other arrays use positional
comparison without speculative alignment. See comparison.md and reports.md.

## Executed verification

Local platform: Windows/Python 3.13.15. Project-local TEMP/TMP were used for pip
and builds because the sandbox default temp directory has permission restrictions.
Tests run with native NTFS permissions because snapshot hard links are denied in
the sandbox; tests were not skipped or assertions weakened.

```powershell
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest --basetemp=.tmp/phase3-final --cov-report=xml
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pip check
.venv\Scripts\python -m build --no-isolation
.venv\Scripts\python -m twine check dist/*
.tmp\install-env\Scripts\python -m pip install --no-index --no-deps --force-reinstall dist/a2ui_surface_diff-0.1.0.dev3-py3-none-any.whl
git diff --check
```

170 tests passed; 99.72% statement coverage (706/708). Only the two module entry
statements were not credited in-process; module/installed entrypoints are exercised
as subprocesses. Ruff lint/format, strict mypy (12 modules), dependency consistency,
wheel/sdist build and metadata checks all pass. No vulnerability scanner is
configured or claimed. A first new test expected pre-escape key order; inspection
confirmed the implementation's specified escaped-path order, and the exact
expectation was corrected rather than weakening the ordering assertion.

Installed-wheel smoke checks ran outside the checkout using .tmp/install-env:
the real README snapshot/check workflow, exit codes 0/1/2, report JSON Schema,
version, baseline/capture byte preservation, and direct checks with socket creation
blocked all passed. Wheel inspection confirms both authored schemas and new
modules; sdist includes comparison fixtures/docs and excludes environments/temp.
The release-quality dependency inventory remains requirements-dev.lock; it is a
Windows version inventory, not a portable hash lock. Dependencies did not change.

## Remaining risks, deferred work, exact next step

No known Critical/High defect remains in implemented Phase 3 scope. This is still
a development preview pending Phase 4 release-readiness hardening.

- Phase 3 implementation CI is verified: run 40786664420 at c3ffc6b, all four
  matrix jobs successful, including tests, lint/format/types, CLI smoke, build,
  and metadata checks. This does not imply release readiness or publication.
- Snapshots need hard-link support (e.g. NTFS/ext4); denied/unsupported publication
  fails without replacing existing entries. Atomicity is not power-loss durability.
- No wall-time sandbox or performance promise. Repeated model updates copy state.
- SDK-specific type-omitting patches, arbitrary catalogs, evaluation, rendering,
  v0.8 and candidate v1.0 remain unsupported. Coherent complete-message truncation
  cannot be detected without an external completion signal.
- Array alignment, detailed nested schema-error guidance, portable dependency
  locking, dependency/license/security review, and CI action runtime refresh are
  deferred; no MVP expansion is implied. JSON diff reports can contain sensitive data.
- PyPI naming was initially checked but remains unreserved; recheck before any
  owner-authorized publication. Keep Apache-2.0 and independent/unofficial identity.

Exact next step: await the owner's next iteration instruction. Then audit Phase 3 before implementing
only Phase 4 hardening/release preparation. Do not publish, release, change visibility,
or automatically start Phase 4.
