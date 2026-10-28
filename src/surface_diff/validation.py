"""Offline validation against unmodified pinned upstream schemas.

Phase 1 checks message syntax and Basic Catalog structure only. Lifecycle and
final-reference verification belong to the replay phase.
"""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from surface_diff.diagnostics import Diagnostic, InvalidInput, Report
from surface_diff.loader import DEFAULT_LIMITS, Limits, load_jsonl

SCHEMA_REVISION = "4767c140e13b4d8952b92b3bef35b81121dc8810"
BASIC_CATALOGS = frozenset(
    f"https://a2ui.org/specification/{version}/catalogs/basic/catalog.json"
    for version in ("v0_9", "v0_9_1")
)
OPERATIONS = ("createSurface", "updateComponents", "updateDataModel", "deleteSurface")


def make_validator() -> Draft202012Validator:
    assets = files("surface_diff").joinpath("schemas")
    schemas = [
        json.loads(assets.joinpath(name).read_text(encoding="utf-8"))
        for name in ("server_to_client.json", "common_types.json", "catalog.json")
    ]
    registry: Registry[Any] = Registry()  # Default retrieval raises; never fetches.
    for schema in schemas:
        resource = Resource.from_contents(schema)
        registry = registry.with_resource(schema["$id"], resource)
        # The envelope references catalog.json beside itself; upstream gives
        # the actual catalog a different canonical $id. Register that alias.
        if "catalogId" in schema:
            registry = registry.with_resource(
                "https://a2ui.org/specification/v0_9/catalog.json", resource
            )
    return Draft202012Validator(schemas[0], registry=registry)


def _pointer(parts: Any) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def validate_file(path: Path, limits: Limits = DEFAULT_LIMITS) -> Report:
    validator = make_validator()
    checked = 0
    try:
        for line, message in load_jsonl(path, limits):
            if (
                isinstance(message, dict)
                and "version" in message
                and message["version"] not in ("v0.9", "v0.9.1")
            ):
                return Report(
                    str(path),
                    checked,
                    (
                        Diagnostic(
                            "UNSUPPORTED_VERSION", "Expected v0.9 or v0.9.1.", line, "/version"
                        ),
                    ),
                )
            if isinstance(message, dict) and isinstance(message.get("createSurface"), dict):
                catalog = message["createSurface"].get("catalogId")
                if isinstance(catalog, str) and catalog not in BASIC_CATALOGS:
                    return Report(
                        str(path),
                        checked,
                        (
                            Diagnostic(
                                "UNSUPPORTED_CATALOG",
                                "Only the pinned Basic Catalog is supported.",
                                line,
                                "/createSurface/catalogId",
                            ),
                        ),
                    )
            # Select the official branch only when the envelope is unambiguous.
            # This avoids oneOf errors about unrelated message types.
            operations = [op for op in OPERATIONS if isinstance(message, dict) and op in message]
            selected = validator
            if len(operations) == 1:
                definition = operations[0][0].upper() + operations[0][1:] + "Message"
                selected = validator.evolve(
                    schema={"$ref": f"{validator.schema['$id']}#/$defs/{definition}"}
                )
            error = next(selected.iter_errors(message), None)
            if error is not None:
                location = _pointer(error.absolute_path)
                # Do not echo schema error.message: it may contain application secrets.
                diagnostic = Diagnostic(
                    "SCHEMA_INVALID",
                    f"Message fails official schema rule '{error.validator}'; "
                    "check required fields, types, and Basic Catalog properties.",
                    line,
                    location,
                )
                return Report(str(path), checked, (diagnostic,))
            checked += 1
    except InvalidInput as error:
        return Report(str(path), checked, (error.diagnostic,))
    return Report(str(path), checked)
