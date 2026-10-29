# Release-readiness evidence — 1.0.0 alpha

Date: 2026-10-29 (Asia/Karachi). Status: all four engineering phases accepted;
no publication or release. Hosted implementation evidence is recorded below.

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

## Observed hosted acceptance

Implementation 02bd7ca5c96ac585a22a1b94f2830ab00418d21a passed all four jobs:
https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40794910578

Ubuntu/Windows and Python 3.12/3.13 each passed 188 tests and every configured
gate, including both advisory checks and fresh/reproducible artifact proof.
Same-platform repeat builds were identical; cross-platform archive hash identity
is not claimed. Final local artifacts and dist/SHA256SUMS are regenerated after
this documentation update. No tag, release, or package publication occurred.

## Observed v1.0.0 publication — 2026-10-30

Owner-approved GitHub alpha/pre-release is public:
https://github.com/asadabbas717/a2ui-surface-diff/releases/tag/v1.0.0

Tag v1.0.0 points to 507f4a5dde26981d586044143beb5187a7037c4a.
All four exact-commit hosted jobs passed:
https://github.com/asadabbas717/a2ui-surface-diff/actions/runs/40969929111

Local suite: 188 passed, 99.30% coverage; lint/format/types/pip check and fresh
offline wheel/source installations/repeated-build hashes passed. Downloaded the
three published assets and checked byte identity and SHA256SUMS against the
reviewed local build. Release API confirmed non-draft, pre-release=true and the
three expected asset names. No PyPI upload. The earlier v0.1.0 alpha is historical;
no published data was deleted. This supersedes earlier pending-release steps.
Remaining cache/external-copy privacy limitations are documented, not claimed
to be erased. Account-wide email privacy remains unchanged at owner request.
