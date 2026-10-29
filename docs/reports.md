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
syntax-only scope. Comparison reports use their own versioned contract below.


# Comparison report version 1

The packaged schemas/check-report-v1.json is the machine-readable contract for
check --format json. Validate reports remain command=validate/report_version=2;
consumers must dispatch on both command and version.

| Field | Meaning |
| --- | --- |
| report_version | Integer 1 |
| command | check |
| status | passed, different, or error |
| source | Captured JSONL path |
| baseline | Approved snapshot path |
| messages_checked | Successfully applied candidate messages; 0 if baseline failed first |
| changes | Sorted complete differences; empty on pass or processing error |
| diagnostics | Empty on valid comparisons; one error with code/message/line/path/file otherwise |

A change has code, path (escaped pointer into snapshot state), before, and after.
Each side is either {"state":"absent"}, {"state":"undefined"}, or
{"state":"value","value":JSON,"undefined_paths":[]}.
undefined_paths contains sorted pointers relative to that side's value when it
contains nested undefined array slots represented by null placeholders. A JSON
null itself is state=value/value=null, never absent or undefined.

Stable change codes:
SURFACE_ADDED, SURFACE_REMOVED, COMPONENT_ADDED, COMPONENT_REMOVED,
COMPONENT_TYPE_CHANGED, PROPERTY_ADDED, PROPERTY_REMOVED, PROPERTY_CHANGED,
ACTION_CHANGED, CHILD_ORDER_CHANGED, REFERENCE_CHANGED,
DATA_ADDED, DATA_REMOVED, DATA_CHANGED.

Check adds BASELINE_IO, BASELINE_LIMIT, BASELINE_INVALID, BASELINE_UNSUPPORTED,
and COMPARISON_LIMIT diagnostics to the capture validation codes. Snapshot
serialization adds SNAPSHOT_LIMIT before publishing oversized/deep output.
Error diagnostics identify the affected file explicitly; malformed multiline
baseline JSON includes its line when known. No partial changes accompany an error.

Text comparison errors go to stderr. Text success/differences and all regular
JSON reports go to stdout. Usage, catastrophic resource exhaustion, or output
stream failure uses stderr and exit 2, consistent with existing CLI boundaries.
JSON before/after values can contain application data; review before sharing.
Human-readable output escapes control/format characters and literal backslashes
in untrusted paths and names. This prevents terminal escape injection and forged
lines; machine-readable JSON retains exact decoded paths and values.
The complete change payload budget is 32 MiB in addition to the 20,000-change
limit. Output is flushed inside the CLI failure boundary; a closed output pipe
returns 2 rather than an interpreter-shutdown flush code, including help/version.
