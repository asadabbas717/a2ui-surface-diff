"""Canonical serialization and atomic output publication without overwrites."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from surface_diff.diagnostics import Diagnostic, InvalidInput


def serialize_snapshot(snapshot: dict[str, Any]) -> bytes:
    return (
        json.dumps(snapshot, sort_keys=True, ensure_ascii=True, allow_nan=False, indent=2) + "\n"
    ).encode("utf-8")


def write_snapshot(path: Path, snapshot: dict[str, Any]) -> None:
    data = serialize_snapshot(snapshot)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=".surfdiff-", delete=False
        ) as stream:
            temporary = stream.name
            stream.write(data)
        # A hard link publishes a complete file atomically, failing if any
        # entry (including a dangling symlink) already occupies the destination.
        os.link(temporary, path)
    except FileExistsError as error:
        raise InvalidInput(
            Diagnostic("OUTPUT_EXISTS", "Output exists; choose a new baseline path.")
        ) from error
    except (OSError, ValueError) as error:
        raise InvalidInput(
            Diagnostic(
                "OUTPUT_IO",
                "Cannot write snapshot; check the parent directory and hard-link support.",
            )
        ) from error
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
