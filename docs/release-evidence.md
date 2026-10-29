# Release-readiness evidence — prepared 0.1.0

Date: 2026-10-29 (Asia/Karachi). Status: engineering verification in progress until
the final exact hosted commit is recorded in STATE.md; no publication or release.

## Previous-phase audit

Phase 3 started clean at 733bcbb and was independently audited. Its original 170
tests and hosted matrix passed. A Medium terminal control-injection issue was
reproduced and repaired before Phase 4. The repair's 172 tests and all local
checks passed and the milestone was pushed as 331b3c1. See phase3-audit.md.

## Phase 4 local results

Windows/Python 3.13.15, portable pinned development environment:

- 188 tests passed, 99.30% statement coverage. Adversarial additions exercise
  publication races, read-only/hard-link baselines, byte/shape boundaries,
  expression non-execution, and 10000 sparse slots round-tripped through check.
  Help/version now also return 2 on a closed pipe rather than shutdown code 120,
  with real subprocess regressions.
- Ruff lint/format, strict mypy for package and maintainer tools, pip check,
  wheel/sdist build, and metadata checks passed.
- Runtime audit: 5 packages, no known vulnerabilities or skipped entries.
  Windows development audit: 65 applicable packages, no known vulnerabilities or
  skipped entries. See security-review.md for scope and caveats.
- Fresh wheel/source installs succeeded separately in offline venvs outside
  the checkout. Version/entrypoint, schema hashes, commands/exits 0/1/2,
  baseline protection, and socket/DNS-blocked runtime operation passed.
- Two builds from the same checkout produced identical wheel and sdist digests.
  Repeat after final documentation changes; verify_artifacts.py writes the
  corresponding final dist/SHA256SUMS. This is same-platform reproducibility,
  not an unmeasured claim of identical bytes across operating systems.

Tests/artifact publication used native NTFS permissions because the local sandbox
denies hard links. The assertions were executed, not skipped or weakened. Local
Python 3.12/Linux was not fabricated; hosted jobs provide those results.

## Performance sanity observation

One local workload, with other development work active: 251 components, 1000 data
rows, 25 point updates, 36000-byte capture, 84516-byte snapshot. Observed replay
2.7927 s, equal check 5.1375 s, one-change check 4.4775 s. Results were verified
for correctness, including exactly one expected data path. These are observations,
not promises, throughput claims, performance thresholds, or representative hardware
benchmarks. The tool is bounded but not a hostile multi-tenant execution sandbox.

## Reproduction and final review

Commands are executable in README/releasing.md and the CI workflow. Package and
maintainer source are linted/typed; the main import package has no new runtime
dependency. Runtime/build locks include hashes, development lock has portable
markers/version pins. Advisory/tool versions and license provenance are recorded.
Release notes, contracts, architecture, limitations, contributing/security policy,
and the owner checklist were reviewed. No known Critical/High product defect was
reproduced after repairs; remaining limits are explicit in limitations.md.

Final matrix acceptance requires all four Windows/Linux Python 3.12/3.13 jobs,
including advisories, artifact installs/reproducibility, and performance checks,
to pass for the exact pushed implementation. STATE.md records that observed result;
this document must not be used to infer a green result before it exists.

Initial refreshed workflow 80f5d9c failed validation before jobs (run 40792546162).
Local parsing reproduced an unquoted colon-space in --only-binary=:all: at line
38. The value is now quoted and a safe YAML/scalar-command regression is retained.
The new parser is development-only and was added to the audited portable lock.
A further Windows-locale check reproduced Unicode diff failure on ASCII output;
escaped text fallback now preserves diff exit1 and exact JSON, with subprocess
regressions. A maintainer doc-edit helper's locale decoding was corrected using
explicit UTF-8; normal capture/baseline readers already decode UTF-8 explicitly.
The failed hosted run is not represented as acceptance; all gates are rerun.

Hosted run 40794299240 exposed an omitted Python 3.12 runtime dependency in
the lock generated using Python 3.13 defaults. Regeneration with explicit
--python-version 3.12 retains hash-pinned typing-extensions 4.16.0 below 3.13.
A marker regression and the full fresh-install matrix verify this correction.
Runtime audits cover five packages locally on 3.13 and six on 3.12.
