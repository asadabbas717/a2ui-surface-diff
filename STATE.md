# SurfaceDiff development state

Updated: 2026-10-29 (Asia/Karachi).

## Current status

Phase 1 independently audited and repaired; Phase 2 audited and repaired.
Phases 3 and 4 have not started. Development version: 0.1.0.dev2; target 0.1.0.
Branch: main. The iteration started clean at 41355ec910ca9bc6df5572f225798c8c5a9e6cf9.
No unrelated user work was present or removed.

Remote: https://github.com/asadabbas717/a2ui-surface-diff.git.
Original Phase 1 was pushed as 41355ec. The local audit repair commit is
08be30ada503c6855c410f6dd877afe514e74006. The Phase 2 commit containing this
state records the next implementation. This iteration creates local commits;
new commits have not been pushed. No package publication, release, or visibility
change occurred. The owner-created initial history and Apache-2.0 license remain.

## Previous-phase audit

See docs/phase1-audit.md for severity, reproduction, repairs, and evidence.
Two Medium findings were repaired: non-JSON whitespace lines could be skipped,
and the entrypoint test assumed the wrong Windows script directory outside a
venv. Four whitespace regression cases and the retained installed-executable
subprocess test cover the corrections. No Critical/High issue was reproduced.
Phase 1 local acceptance: PASS after repairs, 57 tests, 98.90% statement coverage,
lint/format/mypy/build/metadata all passed. Commit 08be30a isolates the repairs.

Hosted evidence was read, not inferred: run 40781697398 for original 41355ec
passed Ubuntu 3.12/3.13, but Windows 3.12/3.13 failed the incorrect script-path
test. This is historical evidence, not verification of the repaired/new commits.
Hosted Phase 2 run 40783646327 passed all Windows/Linux 3.12/3.13 jobs at
476bda7. Only Windows/Python 3.13.15 is available for local execution.

## Phase 2 delivered

- Streaming schema validation composed with session-local stateful replay.
- Surface creation/deletion, duplicate/missing lifecycle checks, clean ID reuse,
  independent surfaces, component collection upserts, duplicate-batch checks.
- Bounded effective data-model upserts, root replacement/deletion, null values,
  escaped JSON Pointers, empty interior segments, implicit containers/arrays,
  non-shifting deleted array slots, primitive traversal errors.
- Progressive references; final roots/references/template targets and cycles
  checked across all active components with iterative graph traversal.
- Canonical snapshot version 1, preserving identities, actions, bindings,
  expressions, array order, surface configuration, and effective model values.
- snapshot CLI with complete-file atomic publication and no overwrite.
- validate now checks replay/final state. Validation report version 2 explicitly
  declares the stronger scope instead of silently changing version 1 semantics.
- Added replay/data-model/analysis/snapshot modules, behavioral tests, snapshot
  documentation, and a snapshot smoke command in the CI matrix.

## Protocol and design decisions

Pinned official revision: 4767c140e13b4d8952b92b3bef35b81121dc8810.
Vendored schemas/licenses/example and exact byte hashes are unchanged. Git
attributes preserve their bytes. Both v0.9 and v0.9.1 messages are accepted,
as the official schemas require; two documented Basic Catalog IDs are accepted.
Unknown catalogs fail closed. Runtime has no network calls or expression execution.

Inspected pinned protocol text and TypeScript/Python implementation paths are
listed in docs/protocol-compatibility.md. Collection updates retain untouched
components. Each supplied definition replaces that component's properties and
must satisfy the official schema. SDK type-omitting patches are unsupported
because the pinned schemas require complete definitions.

The protocol text distinguishes explicit null from omitted values. Null remains
a value, including at root; root deletion resets to {}. Some SDK implementations
collapse null/deletion or drop empty pointer segments. We follow the protocol text
and RFC pointer escaping, with A2UI's special / root convention, and document the
renderer discrepancies. Arrays preserve undefined slots via null placeholders
plus undefinedDataPaths, avoiding collision with arbitrary captured JSON objects.

Bounds: input 16 MiB, physical line 1 MiB, 10000 messages, decoded message depth 64
and 100,000 value nodes. Replay: 1,000 active surfaces, 20,000 total active components,
200,000 combined data-model nodes, model depth 64, maximum array index 10,000. There is no
wall-time sandbox. Source values are copied before state changes. Graph traversal
is iterative and covers unreachable active components too; shared children are
allowed. Dynamic templates are checked, not evaluated. Component defaults are
not materialized; creation theme/sendDataModel defaults are normalized.

Snapshot output uses a same-directory temporary file plus os.link to publish
without replacing any existing entry. NTFS/ext4 support this; unsupported or
denied links fail with OUTPUT_IO. No partial destination is published. The local
sandbox denies hard links, so native-permission test execution was required.
The sandbox run's two output failures were investigated, not hidden or skipped;
the native run passed every assertion. Atomic publication does not promise
power-loss durability. Snapshot/report formats are documented under docs/.

## Verification evidence for Phase 2

Commands executed from the project, with .venv\Scripts\python:

```powershell
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m pytest --basetemp=.tmp/phase2-acceptance --cov-report=xml
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pip check
.venv\Scripts\python -m build --no-isolation
.venv\Scripts\python -m twine check dist/*
git diff --check
```

Test execution used native filesystem permissions. **100 passed**, **98.90%**
statement coverage (451/456). Uncredited statements are the subprocess module
entry point and an output-error boundary. Strict mypy passes all ten modules;
Ruff lint/format and dependency consistency pass. Wheel/sdist build and metadata
checks pass; no vulnerability scanner is configured or claimed. The dev dependency
version inventory remains requirements-dev.lock, not a portable hash lock.

The earlier source install and artifact checks are preserved in docs/phase1-audit.md
and commit history. New artifact smoke execution installs the Phase 2 wheel into
.tmp/install-env and invokes it outside the checkout, validates and snapshots the
example, compares snapshot bytes, checks version, and verifies no network access.

## Remaining limitations and next step

No known Critical/High defect remains in implemented Phase 2 scope. This remains
a development preview, not a completed regression-comparison product.

- check/structural comparison and comparison JSON reports are Phase 3.
- Repaired/new hosted Windows/Linux 3.12/3.13 CI is still pending.
- SDK-specific partial definitions, custom catalogs, rendering, binding/function
  execution, v0.8 and candidate v1.0 are unsupported.
- Complete-message truncation leaving coherent state cannot be detected.
- Snapshot publication needs hard-link support. Limits do not guarantee wall time.
- Lower-priority schema-error guidance, portable dependency locking, and CI action
  runtime refresh remain deferred to Phase 4; see the audit.
- PyPI names were initially checked with 404 results but are unreserved; recheck
  before any owner-authorized publication. Package publication remains unauthorized.

Exact next step: await the owner's next iteration instruction. Then audit Phase 2
before implementing only Phase 3: structural diff/check, stable comparison reports,
exit1 for valid differences, exit2 for errors, and strict baseline non-mutation.
Do not start Phase 3 automatically or publish/release anything.

## Current iteration: Phase 2 audit repair milestone

The owner has now authorized Phase 3 after review and commit/push of every tested
milestone. Phase 2 and the earlier audit were already pushed before this iteration.
The iteration started clean and synchronized at 476bda7. The independent Phase 2
audit repaired null-descendant deletion and the stdout exception boundary; see
docs/phase2-audit.md. Repaired local evidence: 105 tests, 99.57% coverage, all
configured lint/format/type/dependency/build/metadata checks pass. This tested
repair milestone is committed/pushed before starting Phase 3. Publication and
releases remain unauthorized. The previous next-step text is historical; the
current next step is Phase 3 implementation only.
