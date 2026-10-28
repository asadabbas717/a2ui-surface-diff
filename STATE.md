# Development state

Updated: 2026-10-29 (Asia/Karachi).

## Status

**Phase 1 complete locally.** Phases 2–4 have not started. Development package
version: `0.1.0.dev1`; target release remains `0.1.0`.

At Phase 1 completion, the workspace had started empty and was not a Git repository. No existing work was
overwritten. No repository was initialized, no commit was made, and no remote
repository, push, release, package publication, or visibility change occurred.
This describes the initial implementation session; see the synchronization update below.

## GitHub synchronization update

The owner subsequently authorized committing and pushing Phase 1 to
`https://github.com/asadabbas717/a2ui-surface-diff.git`.
The owner-created repository is public and already contains initial commit
`64eb4c20497fbc11f7a709fceb8689491280c69e` with an Apache-2.0 LICENSE.
Local Git was initialized and that history fetched for preservation. The Phase 1
commit is prepared as its descendant on `main`, with generated environments,
caches, temporary data, and build artifacts excluded. This authorization covers
commit/push, not package publication or a release. Hosted CI remains unverified
until its actual result is inspected.
The remote's standard Apache-2.0 root LICENSE is preserved; the full unmodified
upstream license remains in the vendored assets. Git attributes preserve pinned
asset bytes across Windows checkouts so their integrity hashes remain valid.

## Completed work

- Installable src-layout package with Hatchling and the `surfdiff` entry point.
- Strict, bounded, streaming UTF-8 JSONL loader with physical line diagnostics.
- Unmodified, pinned official v0.9.1 schemas and Apache-2.0 attribution.
- Offline envelope and Basic Catalog validation; explicit unsupported versions
  and catalog errors; deterministic text/JSON reports with a declared scope.
- Parser, schema, integration, CLI subprocess, non-mutation, integrity, input
  limit, and no-network tests.
- Ruff, strict mypy, coverage gate, and read-only Windows/Linux 3.12/3.13 CI matrix.
- Documentation skeletons, realistic executable example, and release checklist.

## Decisions and upstream findings

- Pinned revision: `4767c140e13b4d8952b92b3bef35b81121dc8810`.
- Official schemas accept both `v0.9` and `v0.9.1`. Canonical schema IDs retain
  `v0_9`. Accept the two Basic Catalog IDs used by the pinned schema/docs.
- Register a local alias for the envelope's relative catalog reference. The
  registry's default retrieval fails closed; no runtime schema downloads.
- Follow actual schema behavior: extra theme keys are allowed. Component
  properties still follow their official schema restrictions.
- Stop on first failure and count only successfully checked messages. Do not
  expose raw schema errors that may embed captured application values.
- Keep lifecycle/references/replay out of Phase 1 and expose the validation scope
  in help, successful text output, JSON reports, and documentation.
- Use metadata 2.4 explicitly because Hatchling 1.33's default 2.5 was rejected
  by the installed Twine 6.2 metadata checker.
- Local dependency versions are recorded in `requirements-dev.lock`; this is a
  Windows verification inventory, not a portable hash-locked installation.

## Names and remote preparation

Authenticated GitHub login: `asadabbas717` (connected GitHub tool).
GitHub API lookup of `asadabbas717/a2ui-surface-diff` returned HTTP 404.
PyPI JSON lookups for `a2ui-surface-diff`, `surfacediff`, `surface-diff`, and
`a2ui-diff` returned HTTP 404. These are preliminary availability checks, not
reservations or an exhaustive trademark/confusable-name review. Recheck before
publication. Preserve the requested identity.

Upstream repository root contains LICENSE and no NOTICE file. The license is
vendored; provenance and exact asset hashes are retained. CI action pins were
checked against official tags: checkout v4.2.2 and setup-python v5.6.0.
Proposed remote description/topics are recorded in the release checklist and
will be configured only after explicit authorization to create the remote.

## Local verification evidence

Platform: Windows, Python 3.13.15. The commands below were executed from the
workspace. PowerShell used a project-local temporary directory because the
sandbox's default pip temporary directory produced a permission error:

```powershell
$env:TEMP = Join-Path (Get-Location) '.tmp'
$env:TMP = $env:TEMP
```

Environment/source installation:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python -m venv .tmp\install-env
.tmp\install-env\Scripts\python -m pip install .
```

Build/test dependencies were installed separately before editable installation;
the fresh install-env source installation fetched its own isolated build and
runtime dependencies and succeeded. An initial no-isolation editable attempt
needed Hatchling's `editables` helper; it is now included in the dev extra.

Final code quality commands:

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pytest --basetemp=.tmp/pytest-verified
```

Results: **53 passed**, **98.90% statement coverage** (180/182 statements).
Only the two `__main__.py` statements were not credited by in-process coverage;
module entry point behavior is exercised in subprocess tests. Ruff and format
checks pass; strict mypy passes for all six package modules. Early test failures
were investigated against upstream: extra theme fields are allowed, and decoder
recursion limits vary by interpreter. Expectations now reflect those facts.

Packaging and command checks:

```powershell
.venv\Scripts\python -m build --no-isolation
.venv\Scripts\python -m twine check dist/*
.venv\Scripts\surfdiff validate examples/hello.jsonl
.venv\Scripts\surfdiff validate examples/hello.jsonl --format json
.venv\Scripts\surfdiff --help
.venv\Scripts\surfdiff --version
.venv\Scripts\python -m pip freeze --exclude-editable
```

Wheel and sdist build and metadata checks pass. The build creates its wheel from
the sdist. Archive inspection confirms schemas, upstream license, root LICENSE,
and NOTICE in the wheel and excludes virtual environments and temporary files.
Both demonstration commands pass and report two messages. Help/version work.

The built wheel was then installed into `install-env` with:

```powershell
.tmp\install-env\Scripts\python -m pip install --no-index --no-deps --force-reinstall dist/a2ui_surface_diff-0.1.0.dev1-py3-none-any.whl
```

From `.tmp` (outside the source checkout), the installed `surfdiff` entry point
validated `../examples/hello.jsonl` successfully. A Python smoke check confirmed
the import came from that environment's `site-packages`, validated with socket
creation blocked, and verified every installed vendored asset hash. Final source
and archive review found no accidental runtime network calls or input writes.

## Known limitations and pending work

No known Phase 1 release-blocking defect remains in the implemented scope.
This is a development preview, not the complete v0.1.0 product.

- Validation is message syntax/catalog validation only. It does not yet check
  surface lifecycle, roots, final references, or effective data model paths.
- Schema-valid complete-message-boundary truncation cannot yet be detected.
- Custom catalogs, v0.8, and candidate v1.0 fail; expressions are never evaluated.
- Resource limits are finite but do not provide a wall-time sandbox.
- Linux, Python 3.12, and hosted CI have not been run. CI is configured only;
  no hosted success is claimed.
- The owner has now supplied the GitHub repository and authorized commit/push.
  The PyPI name remains unreserved; package publication remains unauthorized.

## Exact next step

Wait for owner instruction to start Phase 2. Then inspect this state, roadmap,
and architecture; investigate upstream partial-component and JSON Pointer/array
deletion semantics; define replay acceptance cases; implement lifecycle, final
references, and canonical snapshots together. Do not begin Phase 2 automatically.
