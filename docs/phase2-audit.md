# Phase 2 independent audit — 2026-10-29

Starting revision: `476bda703b5d9c65d25c3b232a7271ced8af6916`, clean `main`
synchronized with origin. Original local suite: 100 tests passed, 98.90% coverage.
All four jobs of [hosted run 40783646327](https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40783646327)
passed (Ubuntu/Windows, Python 3.12/3.13), including packaging and CLI smoke checks.

## Findings and repairs

- **Medium, repaired:** deleting an absent descendant of a null intermediate
  created a container (`{"a": null}` became `{"a": {}}`). Return the detached
  unchanged model when deletion encounters null. Regressions cover objects,
  arrays, deeper paths, source non-mutation, and identical final snapshot bytes.
- **Medium, repaired:** stdout writes occurred outside the CLI exception boundary.
  A closed output stream raised an uncaught OSError rather than returning the
  documented processing-error code 2. Include rendering in the execution boundary;
  retain resource/input exceptions and add a closed-output regression test.
- **Low, deferred:** repeated updates copy/traverse the entire bounded data model.
  There are no performance guarantees; measure in Phase 4 before optimizing.
- **Low, documented:** snapshot publication requires hard links and does not
  guarantee durability against power loss. This is an explicit supported-filesystem
  constraint rather than a silent overwrite fallback.

Reviewed replay's collection/definition update boundaries, roots, progressive and
final references, template/reference field coverage against the pinned catalog,
iterative cycle detection, ID reuse, pointer escaping, null/undefined distinction,
state bounds, source detachment, output safety, offline schema registry, packaging,
report versioning, tests, and contributor documentation. No Critical/High defect
was reproduced. SDK/schema differences remain explicitly documented, not inferred
away from the high coverage number.

## Repaired-phase verification

Executed with `.venv\Scripts\python` on Windows/Python 3.13.15:

```text
-m pytest --basetemp=.tmp/phase2-audit-repaired --cov-report=xml
-m ruff check .
-m ruff format --check .
-m mypy
-m pip check
-m build --no-isolation
-m twine check dist/*
```

105 tests passed; 99.57% statement coverage; lint, formatting, strict typing,
dependency consistency, wheel/sdist build, and artifact metadata checks passed.
Tests used native NTFS permissions because the sandbox denies hard-link creation.
No vulnerability scanner is configured; no vulnerability-scan result is claimed.
Verdict: **PASS after repairs** for Phase 2 local acceptance. Historical hosted
success applies to the starting revision; repaired hosted verification is tracked
separately. The owner authorized committing/pushing each tested milestone.
