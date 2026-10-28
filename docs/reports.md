# Validation report version 2

validate --format json emits one object on stdout and returns 0 on success or 2
on invalid/unsupported input. It stops at the first failure; successfully applied
earlier messages never turn incomplete analysis into a pass.

| Field | Meaning |
| --- | --- |
| report_version | Integer 2 |
| command | validate |
| status | passed or error |
| scope | schemas_lifecycle_and_final_references |
| source | Input path as supplied through pathlib |
| messages_checked | Number of messages successfully applied |
| diagnostics | Ordered array, empty on pass, one entry on error |

Diagnostics have code, human guidance in message, physical 1-based line (or null
for file errors), and path: an escaped pointer into the input message or final
snapshot state, or empty for file errors. Final diagnostics sort by surface ID,
component ID, and catalog reference order. Final failures carry the associated
creation/component update line and can occur after all messages were applied.

Codes: INPUT_IO, INPUT_ENCODING, EMPTY_INPUT, INPUT_SIZE, LINE_SIZE, MESSAGE_LIMIT,
INPUT_COMPLEXITY, INVALID_JSON, UNSUPPORTED_VERSION, UNSUPPORTED_CATALOG,
SCHEMA_INVALID, SURFACE_EXISTS, SURFACE_MISSING, ROOT_MISSING, COMPONENT_DUPLICATE,
REFERENCE_MISSING, REFERENCE_CYCLE, DATA_PATH, STATE_LIMIT.
Snapshot output errors use OUTPUT_EXISTS/OUTPUT_IO on stderr.

Object keys are sorted. Reports can include local file paths; snapshots never do.
Usage errors and catastrophic resource/output failures use stderr text and code 2,
including in JSON mode. Version 2 explicitly changes Phase 1 report version 1's
syntax-only scope. Comparison reports are Phase 3 work.
