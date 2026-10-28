# Protocol compatibility

Source: [official A2UI repository](https://github.com/a2ui-project/a2ui), revision
`4767c140e13b4d8952b92b3bef35b81121dc8810`, inspected 2026-10-29.
The [official specification](https://a2ui.org/specification/v0.9.1-a2ui/)
identifies v0.9.1 as current. SurfaceDiff targets that revision, not a floating
website version, v0.8, or candidate v1.0.

Vendored assets under `src/surface_diff/schemas` map to upstream:

| Local file | Upstream path |
| --- | --- |
| server_to_client.json | specification/v0_9_1/json/server_to_client.json |
| common_types.json | specification/v0_9_1/json/common_types.json |
| catalog.json | specification/v0_9_1/catalogs/basic/catalog.json |
| example.json | specification/v0_9_1/catalogs/basic/examples/00_simple-text.json |
| UPSTREAM_LICENSE | LICENSE |

`SHA256SUMS.json` records exact asset hashes. The protocol text is preserved at
`docs/upstream-protocol.md`. All upstream assets are Apache-2.0; the unmodified
license is retained. See root `NOTICE` for attribution and provenance.

The official schemas accept **both** `v0.9` and `v0.9.1` envelope versions.
Their canonical schema and catalog identifiers still contain `v0_9`. The v0.9.1
protocol documentation uses a `v0_9_1` catalog identifier in examples. SurfaceDiff
accepts exactly these two Basic Catalog identifiers:

- `https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json`
- `https://a2ui.org/specification/v0_9_1/catalogs/basic/catalog.json`

Both use the same pinned Basic Catalog schema. Unknown catalogs fail explicitly;
SurfaceDiff does not infer catalog contents or fetch a catalog ID.

Supported message syntax: `createSurface`, `updateComponents`, `updateDataModel`,
`deleteSurface`. Schema validation includes catalog components, theme, bindings,
and function/action structure. Phase 2 adds lifecycle, final roots/references/
cycles, and supported data updates.

Replay semantics: creation must precede updates/deletion; deleting
permits ID reuse; component lists add/update components rather than replace the
whole collection; intermediate unresolved references are permitted; data updates
replace the target, omitted value deletes, and omitted path or `/` targets the
root. Array deletion preserves slot position; snapshots distinguish undefined
slots from explicit null. See snapshots.md for pointer compatibility decisions.

Implementation paths inspected at that same revision:

- typescript/core/web_core/src/state/data-model.ts
- typescript/core/web_core/src/state/component-model.ts
- typescript/core/web_core/src/processing/message-processor.ts
- python/a2ui_core/src/a2ui/core/state/data_model.py

Component property assignments replace rather than deep-merge. Collection
updates retain other components. Some SDKs allow type-omitting patches despite
the official component schema requiring type/properties; this release follows
the schema contract. No candidate v1.0 behavior is implemented.

Phase 3 compares bindings, expressions, actions, and references structurally.
It does not evaluate functions or infer rendered appearance. Baseline protocol
target and immutable schema revision must match this implementation; incompatible
metadata fails with code 2 rather than being treated as a UI difference.
snapshot-v1.json and check-report-v1.json are SurfaceDiff-authored schemas,
distinct from the unmodified upstream assets in SHA256SUMS.json.
