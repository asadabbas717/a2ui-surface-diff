# Maintainer verification and release procedure

These commands prepare local artifacts, not a publication. Never create a tag,
GitHub release, PyPI upload, or visibility change without explicit owner approval.
The existing owner authorization covers tested commits/pushes only.

## Reproduce the development environment

Use Python 3.12 or 3.13, create/activate a venv as in README, then:

```console
python -m pip install -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python -m pip check
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pip_audit --strict --disable-pip --require-hashes -r requirements-runtime.lock --progress-spinner off
python tools/performance_sanity.py
```

The audit queries public advisory services using package names/versions, never
captures or baselines. It is maintainer/CI tooling, not normal CLI behavior. No
known advisory is not a guarantee of vulnerability absence; audit fresh before
publishing. Performance output is one observed workload, not a speed guarantee.

## Build, verify, and install artifacts offline

```console
python -m build --no-isolation
python -m twine check dist/*
python -m pip download --only-binary=:all: --require-hashes -r requirements-runtime.lock -r requirements-build.lock --dest .tmp/wheelhouse
python tools/verify_artifacts.py --wheel dist/a2ui_surface_diff-0.1.0-py3-none-any.whl --sdist dist/a2ui_surface_diff-0.1.0.tar.gz --wheelhouse .tmp/wheelhouse
```

The verifier rebuilds from the same checkout, compares both artifact digests,
creates two fresh venvs outside the source package, installs hash-locked runtime
wheels without an index, and installs the wheel and source archive separately.
The source environment also gets the hash-locked backend. Package imports must
come from that venv. Schema hashes, version, installed entrypoint, commands and
exit codes, baseline protection, and blocked network access are exercised.
Successful verification writes `dist/SHA256SUMS`; generated outputs stay ignored.

Byte reproducibility is checked within each same-platform job/checkout using
locked tooling; no cross-platform byte identity is asserted. Normalize text
according to `.gitattributes`. The wheel does not bundle runtime dependencies.
Normal source installation may resolve newer packages within declared ranges;
the tested/reproducible set is the supplied runtime lock.

## Regenerate locks intentionally

The recorded generator is uv 0.13.6. Install it in an isolated maintainer venv,
then run (the invocation is the same on Windows/Linux):

```console
python -m pip install uv==0.13.6
uv pip compile pyproject.toml --python-version 3.12 --universal --generate-hashes --no-header -o requirements-runtime.lock
uv pip compile tools/build-requirements.in --python-version 3.12 --universal --generate-hashes --no-header -o requirements-build.lock
uv pip compile pyproject.toml --extra dev --python-version 3.12 --universal --no-header -o requirements-dev.lock
```

Review the diff, licenses, and advisories, then rerun all checks and the hosted
matrix. Runtime/build locks contain hashes for published platform artifacts.
The development lock pins versions/markers but does not promise artifact hashes.
Lock maintenance is not performed by normal CLI commands. No new runtime
dependency was added during release hardening.

## Owner's final publication decisions

Review the release checklist, limitations, and exact CI commit; recheck PyPI name
availability (404 does not reserve it). Confirm a private security reporting
channel and approve any desired tag/release/upload explicitly. There are no
publish credentials, upload workflow, automatic approval, or release automation
in this repository. Follow-up work after all four phases is an audit or a new
owner-scoped request, not an invented fifth phase.
