# Snapshot format version 1

`surfdiff snapshot capture.jsonl --out baseline.json` validates and replays the
entire input before writing. Output is UTF-8 JSON with ASCII escapes, two-space
indentation, sorted mapping keys, and one LF terminator. Existing output entries
are never replaced. Parent directories must exist and support hard links.
The packaged `schemas/snapshot-v1.json` defines the structural contract; check
also validates IDs, supported protocol/catalogs, final graphs, and data semantics.
Snapshot writing and baseline loading share bounds: 64 MiB, 1,000,000 JSON value
nodes, nesting depth 80 (including wrappers). Serialization fails before writing
if these bounds would make the output unusable as a baseline. Existing replay
limits still apply to data models, component counts, and surfaces.

Top-level fields: `snapshot_version: 1`, `protocol` containing `target: v0.9.1`
and the pinned `schema_revision`, and `surfaces`, a mapping keyed by surface ID.
Each surface has:

- `createSurface`: captured configuration; omitted `theme`/`sendDataModel`
  become `{}`/`false`.
- `components`: component IDs mapped to their final full definitions.
- `dataModel`: effective JSON data, initially `{}`.
- `undefinedDataPaths`: sorted escaped pointers to undefined array slots. These
  slots appear as null placeholders in dataModel; explicit null is not listed.

All active components are retained and checked, including unreachable ones.
Deleted surfaces disappear; delete/recreate starts fresh. Mapping insertion order
and batching do not affect output. Child/tab order, values, actions, bindings,
expressions, IDs, and catalog identifiers are preserved. There are no timestamps,
input paths, line numbers, or machine-specific fields. Numbers are not coerced;
catalog component defaults are not materialized.

## Data update policy

Omitted, empty, or `/` paths address the root (the A2UI convention). Other paths
are absolute RFC 6901 pointers: escapes decode once, invalid escapes fail, and
interior empty segments remain empty keys. Missing containers are created,
choosing an array when the next segment is a canonical non-negative integer.
Scalars cannot be traversed for writes; null intermediates can become containers.
Missing-target deletion is a no-op. Arrays grow with undefined slots, never shift
on deletion, and reject negative, leading-zero, nonnumeric, or oversized indices.
`-` is not a JSON Patch append operator.

Values replace targets, not merge them. Explicit null is preserved, including at
the root. Root deletion resets to `{}`. This follows the specification's
distinction between omitted and present JSON values. Some current SDK code
collapses null/deletion or normalizes empty pointer segments differently;
SurfaceDiff follows the pinned text and RFC escaping rather than copying those
renderer-specific discrepancies. See protocol compatibility for inspected paths.
