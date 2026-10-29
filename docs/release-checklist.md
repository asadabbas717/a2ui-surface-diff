# Owner release checklist — prepared 0.1.0

Engineering preparation is complete only after the exact Phase 4 implementation
commit passes the refreshed four-job hosted matrix. See STATE.md for the observed
result, release-evidence.md for local proof, and releasing.md for commands.

## Engineering gates

- [x] Audit Phase 3; repair terminal control injection and retain regression tests.
- [x] Keep the agreed MVP/identity, pinned protocol assets, and Apache-2.0 notices.
- [x] Exercise adversarial boundaries, source/baseline protection, concurrent
  writers, sparse arrays, and expression non-execution.
- [x] Portable development lock; hash-locked runtime/backend installs.
- [x] Runtime/build license provenance and current advisory review; no ignored CVEs.
- [x] Performance sanity workload with correctness assertions and honest observations.
- [x] Build wheel/source artifacts; verify metadata, repeat-build digests, and fresh
  separate offline installations with runtime network calls blocked.
- [x] Complete README, contributing/security/changelog, architecture, compatibility,
  limitations, snapshot/comparison/report contracts, release notes, and evidence.
- [x] Exact implementation 02bd7ca passed Ubuntu/Windows Python 3.12/3.13 CI,
  run 40794910578; all four jobs and artifact/advisory gates succeeded.
- [x] Existing repository description/topics/license inspected and preserved.
  PyPI and the three previously checked similar names returned 404 on 2026-10-29.

## Owner review follow-up — GitHub only

- [x] Delegated limitations/artifact/checksum/privacy review; see privacy-review.md.
- [x] Owner prohibits PyPI uploads; package-name reservation is not needed.
- [ ] Confirm a private security reporting channel or GitHub reporting configuration.
- [ ] Resolve existing public commit-email exposure before a GitHub release.
  Future local commits use the no-reply identity. Do not rewrite history silently.
- [ ] GitHub release held pending privacy items; no PyPI or visibility changes.
- [ ] After any authorized publication, verify the real remote version/artifacts
  and record actual URLs. Do not invent release links or claim an upload in advance.

No paid infrastructure, publishing credentials/workflow, automatic baseline
approval, or release automation is included. All four engineering phases end at
owner review; subsequent work is a final audit or a new owner-scoped request.
