# Phase 1 independent audit — 2026-10-29

Starting revision: `41355ec910ca9bc6df5572f225798c8c5a9e6cf9`, clean `main`.
Scope: packaging, strict bounded JSONL, offline pinned schema validation,
validate CLI, tests, documentation, and baseline CI. Replay was not yet required.

## Findings

- **Medium, repaired:** Unicode `strip()` skipped lines containing non-JSON
  whitespace after valid messages. Restrict blank-line detection to JSON's
  four whitespace characters. Four regression cases now reject these lines
  with physical line numbers rather than reporting success.
- **Medium, repaired:** the installed-entrypoint test assumed scripts reside
  beside `python.exe`. This broke both hosted Windows jobs outside a venv.
  Use `sysconfig.get_path('scripts')`; retain the actual subprocess assertion.
- **Low, deferred:** human schema diagnostics identify a line/path/rule but can
  offer more specific guidance for nested catalog failures.
- **Low, documented:** dependency ranges plus a Windows version inventory are
  not a portable hash-locked install. Full reproducibility hardening is Phase 4.
- **Low, deferred:** CI action pins use older Node runtimes; hosted runners
  reported forced Node 24 execution. The actions ran; update after review in
  Phase 4 rather than changing unrelated infrastructure during replay work.

No Critical/High finding was reproduced. Schema IDs, catalog aliases, closed
resource retrieval, duplicate keys, numeric/Unicode handling, size/shape limits,
non-mutation, packaging assets, and declared syntax-only scope were inspected.
No input evaluation or runtime download path was found. Meaningful stateful
checks were intentionally absent in Phase 1, not assumed to exist from coverage.

## Verification and verdict

Windows/Python 3.13.15, using `.venv\Scripts\python`:

```text
-m pytest --basetemp=.tmp/audit-repaired
-m ruff check .
-m ruff format --check .
-m mypy
-m build --no-isolation
-m twine check dist/*
```

57 tests passed; 98.90% statement coverage; lint, format, strict typing, build,
and both artifact metadata checks passed. Verdict: **PASS after repairs for
Phase 1's local acceptance criteria**.

Hosted run [40781697398](https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40781697398)
was inspected: Ubuntu 3.12/3.13 passed; Windows 3.12/3.13 failed only the
incorrect executable path test (52 passed, 1 failed in the inspected 3.12 log).
These are results for the original revision, not the repaired code. Repaired
hosted results are still pending; no new hosted success is claimed.
