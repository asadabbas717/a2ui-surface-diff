# Dependency, license, and security review — 2026-10-29

Scope: prepared SurfaceDiff 0.1.0, its pinned protocol assets, locked runtime
dependencies, build tools, development tooling, normal CLI boundaries, and CI.
This is a dated engineering record, not a promise about future advisories.

## Runtime inventory

Installed distribution metadata and published project links were inspected:

| Package | Locked version | Declared license | Upstream |
| --- | --- | --- | --- |
| attrs | 26.1.0 | MIT | https://github.com/python-attrs/attrs |
| jsonschema | 4.26.0 | MIT | https://github.com/python-jsonschema/jsonschema |
| jsonschema-specifications | 2025.9.1 | MIT | https://github.com/python-jsonschema/jsonschema-specifications |
| referencing | 0.37.0 | MIT | https://github.com/python-jsonschema/referencing |
| rpds-py | 2026.9.1 | MIT | https://github.com/crate-py/rpds |

The SurfaceDiff wheel contains its own Python package, schemas, and license
notices, not copies of these dependency packages. Runtime dependencies are
installed separately from the exact hash-locked artifacts. Build-only metadata:
hatchling 1.33.0 MIT; packaging 26.3 Apache-2.0 OR BSD-2-Clause; pathspec 1.1.1
MPL-2.0; pluggy 1.7.0 MIT; tomlkit 0.15.2 MIT; trove-classifiers 2026.9.21.13
Apache license classifier. Build/development tools are not runtime requirements.
Project license remains Apache-2.0; no relicensing or new vendoring was performed.

Pinned A2UI files still match SHA256SUMS.json at revision
4767c140e13b4d8952b92b3bef35b81121dc8810. UPSTREAM_LICENSE is retained verbatim
(including its unrelated upstream MIT appendix); root LICENSE and NOTICE are
preserved. New SurfaceDiff-authored schemas are identified separately in the
compatibility documentation. No Google/A2UI endorsement is claimed.

## Advisory checks

Using [PyPA pip-audit](https://github.com/pypa/pip-audit) 2.10.1 against current
public advisory data:

- Runtime hash lock: 5 packages, 0 known vulnerability entries, 0 skipped entries.
- Development lock on local Windows/Python 3.13: 65 applicable packages,
  0 known vulnerability entries, 0 skipped entries. Linux-only markers are
  exercised by the hosted Linux matrix, not claimed from this Windows run.

Exact commands are in releasing.md and CI. No ignore-vulnerability flags or
automatic upgrade/fix flags were used. The development audit warns that its
version-only lock lacks artifact hashes; runtime/build installation hashes are
enforced separately. Stale audit-cache entries were ignored/refetched by the tool,
not skipped advisory checks. A successful advisory lookup is not a malware scan,
source audit of every dependency, or guarantee that no vulnerability exists.

## Product/CI boundaries reviewed

- Strict bounded JSON, duplicate/nonfinite/invalid Unicode rejection, offline
  schema registry, explicit catalogs/versions, and lifecycle/final-state checks.
- No eval/exec, pickle loading, shell subprocess, network request, or schema
  download in the import package. Expressions remain uninterpreted data.
- Read-only baseline loading, explicit absent/undefined/null states, finite
  diff/state budgets, no partial successful report, and exact JSON paths.
- Escaped human terminal controls, concise text output, exact JSON machine data,
  closed-pipe error behavior, and warning that JSON diffs can expose application data.
- Atomic no-overwrite output, tested concurrent writers, hard-link aliases,
  read-only baselines, failed publication cleanup, and source non-mutation.
- Immutable CI action pins reviewed against official release tags/action.yml:
  [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
  (`3d3c42e5aac5ba805825da76410c181273ba90b1`) and
  [setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0)
  (`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`), both Node 24.
  Permissions remain contents:read; credential persistence is disabled. No
  publishing token, paid service, upload workflow, or automatic approval was added.

Remaining boundaries: no wall-time sandbox, arbitrary catalogs or expression
evaluation, and no power-loss durability guarantee. GitHub repository description
and relevant owner-configured topics were verified and preserved. PyPI returned
404 for a2ui-surface-diff and the three previously checked similar names; this
does not reserve a name. Private security reporting should be confirmed by the
owner before publication; no account/security setting was silently changed.

PyYAML 6.0.3 (MIT metadata) is development-only, for a regression check of
workflow YAML grammar and scalar run commands; it is not imported by the CLI.
An initial workflow failed before jobs due to an unquoted colon in a pip flag.
Local parser reproduction identified the fault; quoting and regression checks
repair it without removing a gate. Human output also falls back to escaped
Unicode when a limited output encoding cannot represent a valid identifier;
JSON paths and semantic exit codes remain exact.

Python 3.12 also requires typing-extensions 4.16.0 (PSF-2.0 metadata),
hash-pinned with its Python marker. Local Python 3.13 runtime audits omit this
inapplicable dependency; hosted Python 3.12 audits and fresh installs include it.
