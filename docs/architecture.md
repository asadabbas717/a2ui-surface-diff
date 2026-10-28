# Architecture

`cli.py` owns argument parsing, output, and exit codes. `loader.py` streams bounded
binary lines, decodes UTF-8, parses strict JSON, and bounds decoded complexity.
`validation.py` applies the pinned schemas through a closed `referencing`
registry. `diagnostics.py` owns immutable diagnostics and versioned reports.

The validator validates each message independently and stops on the first
failure. `messages_checked` counts only messages that completed validation.
There is no replay state in Phase 1. Surface and component maps, final references,
and effective data model semantics will be introduced together in Phase 2.

Schemas remain unmodified. An in-memory alias resolves the envelope's relative
`catalog.json` reference to the upstream Basic Catalog. Resource retrieval always
raises for an unknown URI. Component properties and function-call syntax are
schema checked, never evaluated. Exceptions are caught at input boundaries;
diagnostics avoid embedding input values or raw schema error strings.
