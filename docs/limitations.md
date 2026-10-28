# Current limitations

Phase 2 validates supported syntax, lifecycle, data updates, roots, final
references, and cycles. snapshot records final active state. check/comparison
remain Phase 3 work. A complete-message truncation that leaves coherent state
cannot be detected without an application-level completion signal.

Only the pinned Basic Catalog is supported. Custom catalogs, v0.8, candidate
v1.0, rendering, function evaluation, and dynamic binding resolution are excluded.
Templates are checked for their component definition, not instantiated. Unreachable
components are retained and checked. Sharing children among parents is allowed.

Batches partially update the collection; each supplied definition must satisfy
the official full component schema. Type-omitting patches accepted by some SDKs
are not accepted by these schemas. Omitted properties on repeated definitions
are removed; nested properties are not merged. Component defaults are not added.
Surface theme/sendDataModel defaults are normalized; catalog IDs stay as captured.
See snapshots.md for exact pointer and undefined-slot semantics.

Snapshots contain potentially sensitive data. Review before committing. Error
paths/file names may contain identifiers even though error messages omit values.
Resource limits bound state growth, not execution wall time. Repeated large
updates and schema combinators can be expensive. This is not a multi-tenant sandbox.
Atomic snapshot publication requires hard-link support (e.g. NTFS/ext4). Denied
operations fail without replacing baselines. This does not guarantee durability
against power loss.

Local verification uses Windows/Python 3.13. Original Phase 1 hosted CI passed
Ubuntu 3.12/3.13 but failed Windows due to a repaired test-path defect. New hosted
results remain pending. Package publication and releases remain unauthorized.
