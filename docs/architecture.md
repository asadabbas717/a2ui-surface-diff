# Architecture

cli.py owns argument parsing, output, and exit codes. loader.py streams bounded
UTF-8 JSONL. validation.py yields schema-valid messages through a closed registry.
analysis.py composes these checks with replay.py and immutable diagnostics.

Replay has session-local surface maps. Component definitions replace by ID,
retaining components absent from the batch. Final graph checks cover roots,
references (including templates/tabs), and cycles across all active components.
References may be unresolved during replay. Iterative graph traversal supports
long graphs without consuming the Python call stack.

data_model.py implements bounded pointer upserts and an undefined sentinel.
Null is a value; omitted values delete object keys or leave undefined array slots.
Updates detach caller data. snapshot.py serializes sorted mappings and publishes
a complete temporary file through a no-overwrite hard link in the output folder.
Hard-link support is required; output failures return 2.

The pure replay() API expects schema-validated messages; file callers use
analyze_file()/validate_file() from analysis.py. No expressions are evaluated,
no runtime catalog/schema fetch occurs, and diagnostics avoid raw input values.
Input and effective state are bounded, but this is not a wall-time sandbox.

baseline.py reads a bounded strict JSON document, checks the snapshot wrapper,
reuses official component validation and replay integrity checks, restores
undefined slots, and returns canonical state. comparison.py performs read-only
comparison and builds a separate CheckReport. Missing object properties and
undefined array slots have distinct internal sentinels. JSON booleans never
compare equal to numbers; numeric representations such as 1/1.0 do compare equal.
Added/removed containers and component type changes stop descendant reporting.
All output paths are escaped pointers sorted lexicographically. The comparison
limit fails the entire operation rather than returning a partial successful diff.
