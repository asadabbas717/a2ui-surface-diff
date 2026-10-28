# Validation report version 1

`validate --format json` emits one JSON object on stdout and returns 0 on pass or
2 on invalid/unsupported input. Processing stops at the first failure; a failure
always has status `error`, even after earlier messages passed.

| Field | Meaning |
| --- | --- |
| report_version | Integer 1 |
| command | `validate` |
| status | `passed` or `error` |
| scope | `message_syntax_and_basic_catalog` |
| source | Input path as supplied through pathlib; not a snapshot field |
| messages_checked | Number of messages successfully validated before stopping |
| diagnostics | Ordered array, empty on pass, one entry on input error |

Diagnostics have `code` (stable identifier), `message` (human guidance), `line`
(physical 1-based JSONL line or null for file-level errors), and `path` (escaped
JSON Pointer into the message, or empty for whole-message/file errors).

Codes: `INPUT_IO`, `INPUT_ENCODING`, `EMPTY_INPUT`, `INPUT_SIZE`, `LINE_SIZE`,
`MESSAGE_LIMIT`, `INPUT_COMPLEXITY`, `INVALID_JSON`, `UNSUPPORTED_VERSION`,
`UNSUPPORTED_CATALOG`, `SCHEMA_INVALID`.

Reports sort object keys for reproducibility. Paths may reflect local input paths;
reports are not canonical snapshots. Usage errors and catastrophic resource
exhaustion write text to stderr and return 2, including in JSON mode. They never
emit a successful report. Comparison reports will be defined in Phase 3.
