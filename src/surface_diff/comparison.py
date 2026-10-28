"""Deterministic structural comparisons and CI reports; no baseline writes."""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from surface_diff.analysis import analyze_file
from surface_diff.baseline import load_baseline
from surface_diff.data_model import MISSING, decode_model, encode_model, pointer
from surface_diff.diagnostics import Diagnostic, InvalidInput

MAX_CHANGES = 20_000
MAX_CHANGE_BYTES = 32 * 1024 * 1024


class Absent(Enum):
    VALUE = "absent"


ABSENT = Absent.VALUE


def _side(value: Any) -> dict[str, Any]:
    if value is ABSENT:
        return {"state": "absent"}
    if value is MISSING:
        return {"state": "undefined"}
    encoded, undefined = encode_model(value)
    return {"state": "value", "value": encoded, "undefined_paths": undefined}


@dataclass(frozen=True)
class Change:
    code: str
    path: str
    before: Any
    after: Any

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "path": self.path,
            "before": _side(self.before),
            "after": _side(self.after),
        }


def _kind(value: Any) -> Any:
    if type(value) in (int, float):
        return "number"
    return type(value)


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> tuple[Change, ...]:
    """Compare already validated snapshots. Containers stop at added/removed/type changes."""
    changes: list[Change] = []
    change_bytes = 0

    def emit(code: str, parts: list[str], old: Any, new: Any) -> None:
        nonlocal change_bytes
        if len(changes) >= MAX_CHANGES:
            raise InvalidInput(
                Diagnostic("COMPARISON_LIMIT", "Change limit exceeded; comparison is incomplete.")
            )
        path_length = sum(len(part) + part.count("~") + part.count("/") + 1 for part in parts)
        if path_length > MAX_CHANGE_BYTES:
            raise InvalidInput(
                Diagnostic(
                    "COMPARISON_LIMIT", "Change payload budget exceeded; comparison is incomplete."
                )
            )
        change = Change(code, pointer(parts), old, new)
        change_bytes += len(json.dumps(change.as_dict(), ensure_ascii=True).encode("utf-8"))
        if change_bytes > MAX_CHANGE_BYTES:
            raise InvalidInput(
                Diagnostic(
                    "COMPARISON_LIMIT", "Change payload budget exceeded; comparison is incomplete."
                )
            )
        changes.append(change)

    def walk(old: Any, new: Any, parts: list[str], domain: str, relative: list[str]) -> None:
        operation = "ADDED" if old is ABSENT else "REMOVED" if new is ABSENT else "CHANGED"
        if old is not ABSENT and new is not ABSENT and _kind(old) == _kind(new):
            if isinstance(old, dict):
                for key in sorted(old.keys() | new.keys()):
                    walk(
                        old.get(key, ABSENT),
                        new.get(key, ABSENT),
                        [*parts, key],
                        domain,
                        [*relative, key],
                    )
                return
            if isinstance(old, list):
                if (
                    domain == "PROPERTY"
                    and relative == ["children"]
                    and all(isinstance(item, str) for item in [*old, *new])
                    and old != new
                    and sorted(old) == sorted(new)
                ):
                    emit("CHILD_ORDER_CHANGED", parts, old, new)
                    return
                if domain == "PROPERTY" and relative == ["tabs"]:
                    old_tabs = [json.dumps(item, sort_keys=True) for item in old]
                    new_tabs = [json.dumps(item, sort_keys=True) for item in new]
                    if old_tabs != new_tabs and sorted(old_tabs) == sorted(new_tabs):
                        emit("CHILD_ORDER_CHANGED", parts, old, new)
                        return
                for index in range(max(len(old), len(new))):
                    walk(
                        old[index] if index < len(old) else ABSENT,
                        new[index] if index < len(new) else ABSENT,
                        [*parts, str(index)],
                        domain,
                        [*relative, str(index)],
                    )
                return
            if old == new:
                return
        code = f"{domain}_{operation}"
        if domain == "PROPERTY" and relative and relative[0] == "action":
            code = "ACTION_CHANGED"
        elif (
            domain == "PROPERTY"
            and relative
            and (
                relative[0] in ("children", "child", "trigger", "content")
                or (relative[0] == "tabs" and relative[-1] == "child")
            )
        ):
            code = "REFERENCE_CHANGED"
        emit(code, parts, old, new)

    old_surfaces, new_surfaces = before["surfaces"], after["surfaces"]
    for surface_id in sorted(old_surfaces.keys() | new_surfaces.keys()):
        parts = ["surfaces", surface_id]
        if surface_id not in old_surfaces:
            emit("SURFACE_ADDED", parts, ABSENT, new_surfaces[surface_id])
            continue
        if surface_id not in new_surfaces:
            emit("SURFACE_REMOVED", parts, old_surfaces[surface_id], ABSENT)
            continue
        old_surface, new_surface = old_surfaces[surface_id], new_surfaces[surface_id]
        walk(
            old_surface["createSurface"],
            new_surface["createSurface"],
            [*parts, "createSurface"],
            "PROPERTY",
            [],
        )
        old_components, new_components = old_surface["components"], new_surface["components"]
        for component_id in sorted(old_components.keys() | new_components.keys()):
            component_parts = [*parts, "components", component_id]
            if component_id not in old_components:
                emit("COMPONENT_ADDED", component_parts, ABSENT, new_components[component_id])
            elif component_id not in new_components:
                emit("COMPONENT_REMOVED", component_parts, old_components[component_id], ABSENT)
            elif (
                old_components[component_id]["component"]
                != new_components[component_id]["component"]
            ):
                emit(
                    "COMPONENT_TYPE_CHANGED",
                    [*component_parts, "component"],
                    old_components[component_id]["component"],
                    new_components[component_id]["component"],
                )
            else:
                walk(
                    old_components[component_id],
                    new_components[component_id],
                    component_parts,
                    "PROPERTY",
                    [],
                )
        walk(
            decode_model(old_surface["dataModel"], old_surface["undefinedDataPaths"]),
            decode_model(new_surface["dataModel"], new_surface["undefinedDataPaths"]),
            [*parts, "dataModel"],
            "DATA",
            [],
        )
    return tuple(sorted(changes, key=lambda change: (change.path, change.code)))


@dataclass(frozen=True)
class CheckReport:
    source: str
    baseline: str
    messages_checked: int
    changes: tuple[Change, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    diagnostic_source: str | None = None

    @property
    def exit_code(self) -> int:
        return 2 if self.diagnostics else 1 if self.changes else 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_version": 1,
            "command": "check",
            "status": "error" if self.diagnostics else "different" if self.changes else "passed",
            "source": self.source,
            "baseline": self.baseline,
            "messages_checked": self.messages_checked,
            "changes": [change.as_dict() for change in self.changes],
            "diagnostics": [
                {**asdict(item), "file": self.diagnostic_source} for item in self.diagnostics
            ],
        }


def check_file(source: Path, baseline: Path) -> CheckReport:
    try:
        approved = load_baseline(baseline)
    except InvalidInput as error:
        return CheckReport(
            str(source),
            str(baseline),
            0,
            diagnostics=(error.diagnostic,),
            diagnostic_source=str(baseline),
        )
    analysis = analyze_file(source)
    if not analysis.report.valid:
        return CheckReport(
            str(source),
            str(baseline),
            analysis.report.messages_checked,
            diagnostics=analysis.report.diagnostics,
            diagnostic_source=str(source),
        )
    assert analysis.snapshot is not None
    try:
        changes = compare_snapshots(approved, analysis.snapshot)
    except InvalidInput as error:
        return CheckReport(
            str(source),
            str(baseline),
            analysis.report.messages_checked,
            diagnostics=(error.diagnostic,),
            diagnostic_source=str(source),
        )
    return CheckReport(str(source), str(baseline), analysis.report.messages_checked, changes)
