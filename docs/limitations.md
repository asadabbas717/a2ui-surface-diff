# Current limitations

Phase 1 validates individual message syntax and Basic Catalog structure only.
It does not detect updates before creation, duplicate active surfaces, missing
roots, dangling final references, invalid data-model pointer application, cycles,
or truncation that happens to end on a complete message boundary. A stream with
valid syntax may therefore be unusable at runtime. Empty captures and truncated
JSON messages fail. Snapshot and check commands are not implemented yet.

Only the pinned Basic Catalog is supported. Runtime custom catalogs, function
evaluation, binding resolution, rendering, legacy v0.8, and candidate v1.0 are
unsupported. Progressive references are left alone until final-state validation
is implemented in Phase 2.

Limits bound file bytes and decoded shape, not execution wall time. JSON Schema
combinators can be expensive on adversarial inputs; this is not a sandbox for
hostile multi-tenant workloads. Error output omits message values, but structural
paths and file names can contain sensitive identifiers.

Local verification uses Windows/Python 3.13. Linux and Python 3.12 are configured
in CI, pending hosted verification. The owner has supplied the GitHub repository
and authorized a Phase 1 commit/push. No package publication or release is authorized.
