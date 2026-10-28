# SurfaceDiff

SurfaceDiff is an independent, unofficial Python CLI for structural regression
testing of captured A2UI interfaces. Its planned workflow records an approved
baseline and detects interface structure changes when models or prompts change.
It does not render interfaces or run a model. It is not endorsed by Google or
the A2UI maintainers.

**Current status: Phase 1 development preview (`0.1.0.dev1`).** Only `validate`
is implemented. It checks message syntax and supported Basic Catalog structure
using pinned official A2UI v0.9.1 schemas, which accept `v0.9` and `v0.9.1`.
It does not yet verify lifecycle, roots, or final references. Snapshot and check
commands are planned for Phases 2 and 3.

## Install and try

Python 3.12+ is required. From this source directory:

```console
python -m pip install .
```

Two-command demonstration using the supplied capture:

```console
surfdiff validate examples/hello.jsonl
surfdiff validate examples/hello.jsonl --format json
```

Example terminal output:

```text
PASS examples/hello.jsonl: 2 messages validated (syntax/catalog only).
```

Windows may display the path with backslashes. No package has been published;
the source installation above is the supported installation for this phase.

## CI use

After installing from source in a checkout, run:

```console
surfdiff validate examples/hello.jsonl --format json
```

Exit code 0 means syntax/catalog validation passed; 2 means invalid input,
unsupported input, or a processing error. Exit code 1 is reserved for valid
comparisons with differences in Phase 3. Invalid input never produces a pass.
Validation stops at the first error. JSON reports go to stdout; human-readable
input errors go to stderr. Argument usage errors use argparse's stderr output.

## Input and limitations

Input is UTF-8 JSONL without a BOM, one message per nonempty line. Message order
and physical line numbers are preserved. Duplicate object keys, non-finite
numbers, malformed JSON, unsupported catalogs, and unsupported versions fail.
Default limits: 16 MiB total, 1 MiB per physical line including its newline,
10,000 messages, nesting depth 64, and 100,000 JSON value nodes per message.
Root depth is zero; object keys do not count as value nodes.

Normal CLI operation uses local files only. Catalog IDs are identifiers, never
download targets. Captures and future snapshots may contain sensitive application
data; review them before committing.

See [compatibility](docs/protocol-compatibility.md),
[limitations](docs/limitations.md), [report format](docs/reports.md),
[architecture](docs/architecture.md), [development state](STATE.md),
and [roadmap](ROADMAP.md).

## Development

```console
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` in a POSIX shell, then:

```console
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m build --no-isolation
python -m twine check dist/*
```

Dependency ranges live in `pyproject.toml`; `requirements-dev.lock` records the
versions used for local Phase 1 verification. It is a version inventory rather
than a cross-platform, hash-verified lock. CI installs the declared ranges to
exercise compatibility.
