# SurfaceDiff

SurfaceDiff is an independent, unofficial Python CLI for structural regression
testing of captured A2UI interfaces. Its workflow records an approved
baseline and detects interface structure changes when models or prompts change.
It does not render interfaces or run a model. It is not endorsed by Google or
the A2UI maintainers.

**Current status: `0.1.0` prepared locally; not published.** `validate`,
`snapshot`, and `check` are implemented. They validate pinned official A2UI v0.9.1 schemas
(accepting `v0.9` and `v0.9.1` messages), replay captures, and verify lifecycle,
roots, and final references, then compare captured state against an approved
snapshot. Tested targets are Windows/Linux with Python 3.12/3.13; see
[release evidence](docs/release-evidence.md) for verified checks and limitations.

## Privacy and distribution

Distribution is GitHub-only; this project is not published to PyPI. Normal CLI
commands work offline and do not upload captures or reports. Snapshots and JSON
reports can contain application data; keep real data in the ignored `local-data/`
folder. Credential files and common local output folders are ignored as a guard
against accidental staging, not a guarantee against sharing sensitive files.
Use only synthetic or carefully redacted examples in public issues and CI.
See [privacy review](docs/privacy-review.md) for the current release hold.

## Install and try

Python 3.12+ is required. From this source directory:

```console
python -m pip install .
```

Two-command demonstration using the supplied capture:

```console
surfdiff snapshot examples/checkout-before.jsonl --out baseline.json
surfdiff check examples/checkout-after.jsonl --baseline baseline.json
```

Example terminal output:

```text
Snapshot written: baseline.json
DIFF examples/checkout-after.jsonl: 3 structural changes.
  COMPONENT_REMOVED /surfaces/checkout/components/buy
  COMPONENT_REMOVED /surfaces/checkout/components/buy-label
  REFERENCE_CHANGED /surfaces/checkout/components/root/children/1
```

Human text escapes literal backslashes and terminal control characters. JSON
reports preserve exact decoded paths/values. No package has been published;
the source installation above is the supported installation for this phase.
Snapshot output must be a new path in an existing directory. Existing files,
including the capture, are never overwritten. Rename a previous demo baseline
yourself before repeating the snapshot command.
The second capture loses the purchase button and its label. Its check exits 1,
so CI detects the structural regression. No rendering or visual inference occurs.

## CI use

After reviewing and committing your baseline, use `check` in CI. To test the
unchanged capture against the baseline generated above:

```console
surfdiff check examples/checkout-before.jsonl --baseline baseline.json --format json
```

Exit code 0 means a check found no differences (or validation passed), 1 means
a valid comparison found differences, and 2 means invalid/unsupported input or
an incomplete/failed operation. Check never writes its baseline or input.
Validation stops at the first error. JSON reports go to stdout; human-readable
input errors go to stderr. Argument usage errors use argparse's stderr output.

## Input and limitations

Input is UTF-8 JSONL without a BOM, one message per nonempty line. Message order
and physical line numbers are preserved. Duplicate object keys, non-finite
numbers, malformed JSON, unsupported catalogs, and unsupported versions fail.
Default limits: 16 MiB total, 1 MiB per physical line including its newline,
10,000 messages, nesting depth 64, and 100,000 JSON value nodes per message.
Root depth is zero; object keys do not count as value nodes.
Replay limits: 1,000 active surfaces, 20,000 total active components, 200,000
combined effective data-model nodes, model depth 64, and maximum array index
10,000. These are safety bounds, not performance claims.

Normal CLI operation uses local files only. Catalog IDs are identifiers, never
download targets. Captures, snapshots, and JSON diffs may contain sensitive application
data; review them before committing.

See [compatibility](docs/protocol-compatibility.md),
[limitations](docs/limitations.md), [report format](docs/reports.md),
[architecture](docs/architecture.md), [development state](STATE.md),
and [roadmap](ROADMAP.md). See [snapshot format](docs/snapshots.md) for canonical
output and the representation of deleted array slots versus explicit null.

## Development

```console
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` in a POSIX shell, then:

```console
python -m pip install -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pip check
python -m pip_audit --strict --disable-pip --require-hashes -r requirements-runtime.lock --progress-spinner off
python -m build --no-isolation
python -m twine check dist/*
```

Dependency ranges live in `pyproject.toml`. `requirements-dev.lock` now pins a
portable development environment with platform markers. Runtime and source-build
locks also pin artifact hashes; they are exercised by fresh offline installations
in CI. See [maintainer instructions](docs/releasing.md) for regeneration,
artifact verification, and the explicit approval required before publication.
