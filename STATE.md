# SurfaceDiff development state

Updated: 2026-10-29 (Asia/Karachi).

## Current milestone and authorization

Phase 4 release-readiness implementation is complete locally, pending its exact
refreshed hosted matrix before final acceptance. Phases 1–3 are implemented and
independently audited. Target/local artifact version is 0.1.0, still unpublished.
There is no fifth feature phase. Branch main started clean/synchronized at
733bcbb51437c559a495b23c1eeadc95007964d3; unrelated user work was not changed.

Remote: https://github.com/asadabbas717/a2ui-surface-diff.git. The owner authorizes
commit/push of every milestone after checks pass. Tag/release/package upload,
visibility/security-setting changes remain unauthorized and were not performed.
Repository description, relevant topics, and Apache-2.0 license were verified and
preserved. PyPI and the three previously checked similar names returned 404;
this is not a reservation and must be rechecked before any publication.

## Phase 3 independent audit

See docs/phase3-audit.md: a Medium terminal control-injection defect was reproduced
and repaired. Human output now escapes controls/format characters/backslashes,
while printable Unicode and exact decoded JSON data are preserved. The repaired
suite passed 172 tests, 99.72% statement coverage, all lint/format/type/dependency/
build/metadata checks. Milestone 331b3c1 was committed/pushed before Phase 4.
No Critical/High defect was reproduced in the reviewed scope.

Historical implementation commits: 41355ec Phase 1, 08be30a Phase 1 repair,
476bda7 Phase 2, 57c9426 Phase 2 repair, c3ffc6b Phase 3, 733bcbb CI evidence.
Their exact hosted evidence and defects are retained in the phase audit docs.
Historical green runs do not substitute for the new Phase 4 matrix.

## Phase 4 delivered

- Portable exact development lock with platform markers, replacing the Windows
  version inventory. Runtime/backend locks also include published artifact hashes.
  Generator: uv 0.13.6 in a maintainer-only environment. No new runtime dependency.
- Current advisory checks: runtime 5 packages and local Windows development 65
  applicable packages, no known vulnerability entries or skipped packages. CI
  audits both locks on each target to include Linux-only development markers.
- Runtime/build license provenance and upstream attribution review documented in
  docs/security-review.md; no relicensing or new vendored third-party code.
- Hardened publication races, read-only/hard-link baseline aliases, exact byte and
  decoded-shape boundaries, expression non-execution, and sparse index10000
  round-trip. Normal commands remain offline and never rewrite approved baselines.
- Fixed a reproduced closed-pipe defect in argparse help/version: shutdown code
  120 is replaced with processing-error code 2, tested as real subprocesses.
- Maintainer tools verify fresh separate wheel/source installs offline, installed
  package origin/version/assets, commands/exits, baseline protection, blocked
  socket/DNS calls, and same-checkout repeated-build digests. Successful proof
  writes final dist/SHA256SUMS. Tools reject -O so assertions cannot be stripped.
- Modest performance workload with correctness assertions and observed timings,
  not speed thresholds/claims. Detailed observations in docs/release-evidence.md.
- Reviewed immutable checkout v7.0.1/setup-python v7.1.0 pins, Node24 runtimes,
  contents:read permissions and disabled credential persistence. CI now includes
  advisories, performance observation, and fresh/reproducible artifact proof.
- Complete README/contributing/security/changelog, architecture/contracts,
  limitations, maintainer procedure, release notes/checklist, and evidence.

## Verification performed locally

Windows, Python 3.13.15. Native NTFS permissions were necessary for hard links;
assertions were executed, not skipped/weakened. Project-local TEMP/TMP were used
because the sandbox default temporary directory restricts pip build files.

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest --basetemp=.tmp/phase4-encoding-repair --cov-report=xml
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pip check
.venv\Scripts\python -m pip_audit --strict --disable-pip --require-hashes -r requirements-runtime.lock --format json --output .tmp/runtime-audit.json --progress-spinner off
.venv\Scripts\python -m pip_audit --strict --disable-pip --no-deps -r requirements-dev.lock --format json --output .tmp/development-audit.json --progress-spinner off
.venv\Scripts\python tools/performance_sanity.py
.venv\Scripts\python -m build --no-isolation
.venv\Scripts\python -m twine check dist/a2ui_surface_diff-0.1.0*
.venv\Scripts\python -m pip download --only-binary=:all: --require-hashes -r requirements-runtime.lock -r requirements-build.lock --dest .tmp/wheelhouse
.venv\Scripts\python tools/verify_artifacts.py --wheel dist/a2ui_surface_diff-0.1.0-py3-none-any.whl --sdist dist/a2ui_surface_diff-0.1.0.tar.gz --wheelhouse .tmp/wheelhouse
git diff --check
```

Final suite: 187 passed; 99.30% statement coverage (714/719). Uncredited statements
are the module entrypoint and argparse termination handling exercised in child
processes. Ruff lint/format, strict mypy (14 package/tool modules), pip check,
artifact metadata and advisory checks passed. Fresh offline artifact installs and
repeated-build digests passed; repeat with final docs before pushing the tested
milestone. See release-evidence.md and releasing.md for scope/commands.

## Contracts and remaining limits

Pinned upstream revision: 4767c140e13b4d8952b92b3bef35b81121dc8810; upstream hashes
and notices unchanged. Supports official v0.9/v0.9.1 envelopes and two documented
Basic Catalog IDs, with explicit SDK/schema/null/pointer differences. No v0.8,
v1.0, custom catalogs, rendering, model calls, evaluation, or auto-approvals.
Snapshot wrapper1, validation report2, check report1 are unchanged. Consumers
select report contracts by command/version. Booleans differ from numbers; numeric
1 and 1.0 compare equal. Absent/null/undefined remain distinct. JSON can contain
sensitive application values; text has controls escaped.

Capture limits: 16 MiB, 1 MiB per physical line, 10000 messages, 100000 nodes and
depth64/message. Replay: 1000 active surfaces, 20000 components, combined model
nodes200000/depth64, max array index10000. Snapshot/baseline: 64 MiB, 1M nodes,
depth80. Comparison: 20000 changes and 32 MiB serialized change-payload budget;
incomplete analysis fails with code2, never a partial successful comparison.

Remaining explicit limits: no wall-time sandbox or power-loss durability, required
hard-link support, positional array diffing, no complete-message truncation signal,
and no exhaustive verification of newer Python/platform/dependency combinations.
Nested schema guidance/heuristic alignment remain optional future improvements,
not known Critical/High defects or promised phase-five scope. Advisory results are
dated evidence, not a guarantee of vulnerability absence. See limitations.md.

## Exact next step

Commit/push the tested Phase 4 milestone, inspect all four refreshed hosted jobs,
repair any failure, and record actual commit/run evidence. Only then mark Phase 4
accepted. After all four phases, await owner artifact/release review; confirm a
private security reporting channel and obtain explicit publication/tag/release
approval. Recheck package name and advisories immediately before any authorized
publication. Do not publish or invent another development phase automatically.

## Phase 4 repair before acceptance

80f5d9c6e1476689a4c7f65f70c8a0a2b62d5777 failed workflow validation before jobs
(run 40792546162). An unquoted colon-space was reproduced as YAML ScannerError
at line38, quoted, and covered by a safe parser/scalar-run regression. PyYAML
6.0.3 is development-only; 65 applicable Windows development packages audited
with no known vulnerability entries or skips. A Windows-locale test also found
that valid Unicode diff paths failed on ASCII output. Escaped text fallback and
exact JSON now preserve proper exit1; subprocess regressions cover both formats.
A doc-update helper was corrected to explicit UTF-8 and affected text repaired.
All gates and artifact proof are rerun before pushing this repair; the initial
failed workflow is not acceptance.
