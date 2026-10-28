"""Ordered replay and final-state integrity checks for the pinned Basic Catalog."""

import copy
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

from surface_diff.data_model import (
    MAX_MODEL_NODES,
    MISSING,
    bound_model,
    encode_model,
    pointer,
    update_model,
)
from surface_diff.diagnostics import Diagnostic, InvalidInput
from surface_diff.validation import OPERATIONS, SCHEMA_REVISION

MAX_SURFACES = 1_000
MAX_COMPONENTS = 20_000


@dataclass
class Surface:
    creation: dict[str, Any]
    line: int
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    component_lines: dict[str, int] = field(default_factory=dict)
    data: Any = field(default_factory=dict)
    data_nodes: int = 1


def references(component: dict[str, Any]) -> Iterator[tuple[str, list[str]]]:
    """All structural reference fields in the pinned Basic Catalog, excluding IDs/bindings."""
    kind = component["component"]
    if kind in ("Row", "Column", "List"):
        children = component["children"]
        if isinstance(children, list):
            for index, child in enumerate(children):
                yield child, ["children", str(index)]
        else:
            yield children["componentId"], ["children", "componentId"]
    elif kind in ("Card", "Button"):
        yield component["child"], ["child"]
    elif kind == "Modal":
        yield component["trigger"], ["trigger"]
        yield component["content"], ["content"]
    elif kind == "Tabs":
        for index, tab in enumerate(component["tabs"]):
            yield tab["child"], ["tabs", str(index), "child"]


def _problem(code: str, message: str, line: int, parts: list[str]) -> InvalidInput:
    return InvalidInput(Diagnostic(code, message, line, pointer(parts)))


class Replay:
    """Session-local state; no I/O, schema downloads, rendering, or expression evaluation."""

    def __init__(self) -> None:
        self.surfaces: dict[str, Surface] = {}

    def apply(self, message: dict[str, Any], line: int) -> None:
        """Apply a schema-valid message. Incoming definitions are detached before storage."""
        operation = next(op for op in OPERATIONS if op in message)
        payload = message[operation]
        surface_id = payload["surfaceId"]
        if operation == "createSurface":
            if surface_id in self.surfaces:
                raise _problem(
                    "SURFACE_EXISTS",
                    "Delete the active surface before recreating it.",
                    line,
                    [operation, "surfaceId"],
                )
            if len(self.surfaces) >= MAX_SURFACES:
                raise _problem("STATE_LIMIT", "Active surface limit exceeded.", line, [operation])
            if sum(item.data_nodes for item in self.surfaces.values()) >= MAX_MODEL_NODES:
                raise _problem(
                    "STATE_LIMIT",
                    "Combined active data models exceed the node limit.",
                    line,
                    [operation],
                )
            self.surfaces[surface_id] = Surface(copy.deepcopy(payload), line)
            return
        if surface_id not in self.surfaces:
            raise _problem(
                "SURFACE_MISSING",
                "Create the surface before updating or deleting it.",
                line,
                [operation, "surfaceId"],
            )
        surface = self.surfaces[surface_id]
        if operation == "deleteSurface":
            del self.surfaces[surface_id]
        elif operation == "updateComponents":
            batch: dict[str, dict[str, Any]] = {}
            for index, component in enumerate(payload["components"]):
                if component["id"] in batch:
                    raise _problem(
                        "COMPONENT_DUPLICATE",
                        "Component IDs must be unique within one update batch.",
                        line,
                        [operation, "components", str(index), "id"],
                    )
                batch[component["id"]] = copy.deepcopy(component)
            total = sum(len(item.components) for item in self.surfaces.values())
            if total + len(batch.keys() - surface.components.keys()) > MAX_COMPONENTS:
                raise _problem("STATE_LIMIT", "Active component limit exceeded.", line, [operation])
            surface.components.update(batch)
            surface.component_lines.update(dict.fromkeys(batch, line))
        else:
            try:
                updated = update_model(
                    surface.data, payload.get("path", "/"), payload.get("value", MISSING)
                )
                nodes = bound_model(updated)
                total_nodes = sum(item.data_nodes for item in self.surfaces.values())
                if total_nodes - surface.data_nodes + nodes > MAX_MODEL_NODES:
                    raise InvalidInput(
                        Diagnostic(
                            "STATE_LIMIT", "Combined active data models exceed the node limit."
                        )
                    )
                surface.data, surface.data_nodes = updated, nodes
            except InvalidInput as error:
                raise _problem(
                    error.diagnostic.code, error.diagnostic.message, line, [operation, "path"]
                ) from error

    def finish(self) -> dict[str, Any]:
        """Check final graphs iteratively and return a detached canonical snapshot value."""
        result: dict[str, Any] = {}
        for surface_id, surface in sorted(self.surfaces.items()):
            base = ["surfaces", surface_id, "components"]
            if "root" not in surface.components:
                raise _problem(
                    "ROOT_MISSING",
                    "Active surface requires a component with ID 'root'.",
                    surface.line,
                    base,
                )
            graph: dict[str, list[str]] = {}
            for component_id, component in sorted(surface.components.items()):
                graph[component_id] = []
                for target, path in references(component):
                    if target not in surface.components:
                        raise _problem(
                            "REFERENCE_MISSING",
                            "Final component reference has no definition on this surface.",
                            surface.component_lines[component_id],
                            [*base, component_id, *path],
                        )
                    graph[component_id].append(target)
            colors: dict[str, int] = {}
            for start in graph:
                stack = [(start, False)]
                while stack:
                    node, exiting = stack.pop()
                    if exiting:
                        colors[node] = 2
                        continue
                    if colors.get(node) == 1:
                        raise _problem(
                            "REFERENCE_CYCLE",
                            "Final component graph contains a cycle.",
                            surface.component_lines[node],
                            [*base, node],
                        )
                    if colors.get(node) == 2:
                        continue
                    colors[node] = 1
                    stack.append((node, True))
                    stack.extend((target, False) for target in reversed(graph[node]))
            data, undefined = encode_model(surface.data)
            creation = copy.deepcopy(surface.creation)
            creation.setdefault("theme", {})
            creation.setdefault("sendDataModel", False)
            result[surface_id] = {
                "createSurface": creation,
                "components": copy.deepcopy(surface.components),
                "dataModel": data,
                "undefinedDataPaths": undefined,
            }
        return {
            "snapshot_version": 1,
            "protocol": {"target": "v0.9.1", "schema_revision": SCHEMA_REVISION},
            "surfaces": result,
        }


def replay(messages: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Pure replay API for already schema-validated messages."""
    state = Replay()
    for line, message in enumerate(messages, 1):
        state.apply(message, line)
    return state.finish()
