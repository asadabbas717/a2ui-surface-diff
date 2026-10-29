# Privacy and distribution review — 2026-10-30

Owner instruction: review on the owner's behalf, protect personal/application
information, and keep distribution on GitHub. No PyPI upload is authorized.
All four engineering phases remain complete; this is an owner-review follow-up.

## Review performed

Started clean on main at 4eeef55854ba1b0e51b7b170a1ba112fe9bc19cb.
Reviewed tracked paths, synthetic examples/fixtures, packaging metadata, ignored
outputs, CI permissions/logging, commit metadata, and prepared artifact members.
Scanned 148 reachable historical file blobs with patterns for private keys,
common GitHub/AWS/Google credentials, quoted credential assignments, and local
home paths. No credential pattern matched. Home-path matches were generic
synthetic protocol/test strings, not the owner's local home. This targeted scan
is not an exhaustive secret-detection or absence-of-sensitive-data guarantee.

The previously verified wheel has 26 files and the source archive has 64 files.
Neither contains .git, .venv, .tmp, or .env directories/files. The original
SHA256SUMS entries matched both files. Package metadata contains no author email.
Bundled official schema/license/protocol assets and attribution are preserved.
Public GitHub repository visibility already existed and was not changed.
No existing GitHub releases were listed at review time.

## Repairs and safe defaults

Future commits in this local repository use the owner's GitHub no-reply identity
instead of a personal email. This repository-local setting does not change other
projects or old commits. Credentials and common local application data/output
paths now have ignore rules. Already tracked files and git add -f bypass ignores;
use local-data/ for real captures and never paste them into public issues/logs.
The runtime remains offline. Maintainer dependency audits send package metadata
to advisory services; no captures/baselines are sent by those audit commands.

Distribution documentation now explicitly forbids PyPI uploads. No public
release, tag, visibility change, new credential, or history rewrite was made.
Only tested source/documentation commits are pushed under existing authorization.

## Initial release holds (historical findings)

Existing public commit metadata contains the owner's personal email. The actual
address is intentionally not copied here. A no-reply configuration prevents new
exposure but does not remove old metadata. Rewriting public history changes
commit identifiers and can disrupt clones; it requires a separate, explicit
owner decision. Even rewriting cannot guarantee removal from existing copies.

The connected GitHub tools cannot change repository security settings. The
available browser is not signed into GitHub; the settings page returned a
signed-out 404, so private vulnerability reporting could not be verified or
enabled. Do not treat that 404 as proof the feature is disabled. An authenticated
owner session is needed to inspect and enable it if necessary.

Safe current outcome: keep the existing GitHub source repository, push checked
privacy safeguards, and hold the first release. No technical knowledge or new
phase is required from the owner; resolve these specific account/history items
before deciding to publish reviewed artifacts on GitHub.

## Resolution with owner authorization — 2026-10-30

The owner provided a signed-in GitHub session and authorized changes to resolve
the holds. Private vulnerability reporting was enabled and GitHub confirmed the
setting was saved. Existing secret scanning and push protection were confirmed
enabled and preserved. SECURITY.md now links to the private report form.

The 13-commit main history was reconstructed with the owner's GitHub no-reply
identity in author/committer metadata. Every commit's tree was checked identical
to its original tree; no code, tests, messages, timestamps, or user files were
changed by that operation. One signature on the initial commit was removed
because the changed metadata invalidates it. A verified recovery bundle and SHA
mapping remain only in ignored .tmp; do not upload either. Remote replacement
uses an exact force-with-lease expectation, rejecting concurrent changes.

Previously recorded commit identifiers and CI runs in audit documents describe
the original historical checks. Rewritten identifiers differ; new CI must pass
for the final main revision. Existing clones should re-clone or carefully rebase,
never merge old history back. Normal main ancestry is reviewed for personal email
again after the push. Cached old commit URLs, old workflow refs, forks, and other
people's clones may still retain metadata; no claim of total erasure is made.
GitHub Support controls server-side cache removal. This residual limitation is
recorded rather than represented as a release blocker that code can eliminate.

The owner explicitly declined changing GitHub's account-wide email-privacy
setting. It remains unchanged. Future web edits/merges may therefore use the
account's configured email; local SurfaceDiff commits use no-reply. No login,
notification email, authentication credentials, or repository visibility changed.

Repository release holds are resolved after the checked main history is pushed.
Distribution remains GitHub-only. Prepare a reviewed draft first; a draft is not
a public release. Do not upload real captures, private backups, or environments.
