# Structural comparison contract

`check` validates its baseline first, then the entire captured stream and final
state, and only then compares. It never writes either input. Exit 0 means equal
supported state, 1 means structural differences, and 2 means invalid/unsupported
input or incomplete processing. Every difference is a regression for this release;
there are no ignore filters, approvals, or automatic baseline updates.

Surface and component maps match by identity, not insertion order. Adding/removing
a surface or component produces one container report, not all its descendants.
Changing a component's type produces one report at its component field; resulting
property changes are summarized by that type change. Other properties compare
recursively using escaped pointers into snapshot state.

Exact reordering of the same child IDs or tab objects produces one
CHILD_ORDER_CHANGED report. Other arrays compare by index without heuristic
alignment; insertions can change later positions. Actions and references have
stable semantic codes, without duplicate derived reference reports. Effective
models compare structurally after restoring undefined slots; raw metadata paths
are not diffed separately. Explicit null, undefined slots, absent keys, and false
are distinct. Numbers compare by JSON numeric value, so 1 and 1.0 are equivalent;
booleans never equal numbers. Catalog IDs remain significant as captured.

Differences sort by escaped pointer string and code. This is lexicographic order
(e.g. index 10 sorts before index 2), not numeric or display order. At most 20,000
changes are supported. Exceeding that limit returns COMPARISON_LIMIT and code 2
with no partial change array. Baselines share snapshot byte/node/depth bounds and
must satisfy snapshot version 1, the pinned schema revision, and replay limits.
A separate 32 MiB budget covers serialized change payloads (including paths and
before/after values). This prevents a long ancestor key repeated across many
differences from inflating a small input into an unbounded report. Exceeding
either limit fails the whole comparison.

Text reports show counts, stable codes, and paths, without dumping application
values. JSON reports include before/after values and can contain sensitive data.
These are structural findings, not claims about visual appearance or severity.
See reports.md for the machine-readable format.
