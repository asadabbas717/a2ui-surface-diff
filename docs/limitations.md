# Supported scope and limitations for prepared 0.1.0

The three commands validate/replay supported streams, record canonical snapshots,
and compare final structural state against a validated baseline. These are
structural checks, not rendering or visual appearance checks. The pinned A2UI
v0.9.1 schema revision accepts v0.9/v0.9.1 message labels and exactly the two
documented Basic Catalog IDs. Unsupported versions/catalogs fail explicitly.

- Custom catalogs, v0.8, candidate v1.0, model inference, rendering, function
  evaluation, dynamic binding resolution, automatic approval, and ignore filters
  are excluded. Templates are checked for their definition, not instantiated.
- Full component definitions must satisfy the official schema; SDK-specific
  type-omitting patches are unsupported. Collection upserts retain other IDs;
  supplied definitions replace properties instead of deep-merging them.
- Unreachable components remain checked; shared children are permitted. Final
  roots/references/cycles are validated after progressive messages complete.
- Coherent truncation ending on complete messages cannot be detected without an
  application completion signal. No external session state is assumed.
- Explicit null/undefined/deletion and pointer conventions are documented in
  snapshots.md, including differences from some SDK implementations.
- Arrays generally compare by index. Exact child/tab reorders are summarized;
  added/removed containers and component type changes suppress descendant noise.
  Catalog identifiers remain significant. No cross-version migration is provided.
- Input/state/snapshot/comparison budgets are finite and documented in README,
  snapshots.md, and comparison.md. They do not impose wall-time isolation;
  repeated model copies and schema combinators can be expensive.
- Snapshot publication requires hard-link support (e.g. NTFS/ext4). Denied or
  unsupported publication fails without replacing entries. Atomic publication
  does not guarantee durability against power loss.
- Snapshots and JSON reports can contain sensitive application data. Human text
  escapes terminal controls/backslashes; JSON preserves exact decoded values.
- Tested targets are the hosted Ubuntu/Windows Python 3.12/3.13 matrix and local
  Windows/Python 3.13.15. Other Python versions, platforms, and all dependency
  combinations permitted by the ranges have not been exhaustively verified.
- The locked set is reproducible and audited as recorded, not a promise about
  future vulnerabilities. Development pins lack artifact hashes; runtime/backend
  installation hashes are enforced. See security-review.md and releasing.md.

Detailed nested schema-error guidance and heuristic array alignment are deferred,
not known Critical/High blockers or promises of another feature phase. No tag,
GitHub release, package publication, security-setting, or visibility change was
performed. Owner approval and reporting-channel confirmation remain publication
steps in release-checklist.md.
