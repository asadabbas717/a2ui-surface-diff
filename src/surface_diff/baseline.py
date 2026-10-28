"""Read-only, bounded loading and semantic validation of saved baselines."""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from surface_diff.data_model import decode_model
from surface_diff.diagnostics import Diagnostic, InvalidInput
from surface_diff.loader import parse_json
from surface_diff.replay import Replay
from surface_diff.snapshot import SNAPSHOT_LIMITS
from surface_diff.validation import BASIC_CATALOGS, SCHEMA_REVISION, make_validator


def _invalid(message: str, path: str = "") -> InvalidInput:
    return InvalidInput(Diagnostic("BASELINE_INVALID", message, path=path))


def load_baseline(path: Path) -> dict[str, Any]:
    """Return a canonical, fully checked snapshot; never open the baseline for writes."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(SNAPSHOT_LIMITS.file_bytes + 1)
    except (OSError, ValueError) as error:
        raise InvalidInput(Diagnostic("BASELINE_IO", "Cannot read baseline file.")) from error
    if len(raw) > SNAPSHOT_LIMITS.file_bytes:
        raise InvalidInput(Diagnostic("BASELINE_LIMIT", "Baseline exceeds the 64 MiB byte limit."))
    try:
        snapshot = parse_json(raw.decode("utf-8"), SNAPSHOT_LIMITS)
    except UnicodeError as error:
        raise _invalid("Baseline must be UTF-8 JSON without a BOM.") from error
    except InvalidInput as error:
        raise InvalidInput(
            Diagnostic("BASELINE_INVALID", error.diagnostic.message, error.diagnostic.line)
        ) from error
    if isinstance(snapshot, dict) and "snapshot_version" in snapshot:
        if type(snapshot["snapshot_version"]) is not int or snapshot["snapshot_version"] != 1:
            raise InvalidInput(
                Diagnostic(
                    "BASELINE_UNSUPPORTED", "Expected snapshot version 1.", path="/snapshot_version"
                )
            )
        protocol = snapshot.get("protocol")
        if isinstance(protocol, dict) and (
            protocol.get("target") != "v0.9.1" or protocol.get("schema_revision") != SCHEMA_REVISION
        ):
            raise InvalidInput(
                Diagnostic(
                    "BASELINE_UNSUPPORTED",
                    "Baseline protocol or schema revision is incompatible.",
                    path="/protocol",
                )
            )
    schema = json.loads(
        files("surface_diff").joinpath("schemas/snapshot-v1.json").read_text(encoding="utf-8")
    )
    if not Draft202012Validator(schema).is_valid(snapshot):
        raise _invalid("Baseline does not satisfy snapshot version 1 structure.")
    validator = make_validator()
    state = Replay()
    try:
        for surface_id, surface in sorted(snapshot["surfaces"].items()):
            creation = surface["createSurface"]
            if creation["surfaceId"] != surface_id:
                raise _invalid("Surface mapping key must match its surfaceId.")
            if any(component.get("id") != key for key, component in surface["components"].items()):
                raise _invalid("Component mapping key must match its component ID.")
            messages = [
                {"version": "v0.9.1", "createSurface": creation},
                {
                    "version": "v0.9.1",
                    "updateDataModel": {"surfaceId": surface_id, "value": surface["dataModel"]},
                },
            ]
            if surface["components"]:
                messages.append(
                    {
                        "version": "v0.9.1",
                        "updateComponents": {
                            "surfaceId": surface_id,
                            "components": list(surface["components"].values()),
                        },
                    }
                )
            for message in messages:
                if not validator.is_valid(message):
                    raise _invalid(
                        "Baseline surface or component fails the pinned official schema."
                    )
                # The envelope schema treats catalog IDs as strings; apply the
                # same supported-catalog restriction as captured streams.
                if "createSurface" in message and creation["catalogId"] not in BASIC_CATALOGS:
                    raise _invalid("Baseline uses an unsupported catalog.")
                state.apply(message, 1)
            state.surfaces[surface_id].data = decode_model(
                surface["dataModel"], surface["undefinedDataPaths"]
            )
        return state.finish()
    except InvalidInput as error:
        if error.diagnostic.code == "BASELINE_INVALID":
            raise
        raise _invalid(
            "Baseline has invalid lifecycle, references, data, or undefined slot metadata.",
            error.diagnostic.path,
        ) from error
