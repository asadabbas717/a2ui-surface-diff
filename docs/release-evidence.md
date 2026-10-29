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

- 184 tests passed, 99.30% statement coverage. Adversarial additions exercise
  publication races, read-only/hard-link baselines, byte/shape boundaries,
  expression non-execution, and 10000 sparse slots round-tripped through check.
  Help/version now also return 2 on a closed pipe rather than shutdown code 120,
  with real subprocess regressions.
- Ruff lint/format, strict mypy for package and maintainer tools, pip check,
  wheel/sdist build, and metadata checks passed.
- Runtime audit: 5 packages, no known vulnerabilities or skipped entries.
  Windows development audit: 64 applicable packages, no known vulnerabilities or
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
