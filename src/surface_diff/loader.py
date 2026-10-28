"""Strict, streaming JSONL reader with fixed resource limits."""

import json
import math
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

from surface_diff.diagnostics import Diagnostic, InvalidInput


@dataclass(frozen=True)
class Limits:
    file_bytes: int = 16 * 1024 * 1024
    line_bytes: int = 1024 * 1024
    messages: int = 10_000
    depth: int = 64
    nodes: int = 100_000


DEFAULT_LIMITS = Limits()


def fail(code: str, message: str, line: int | None = None) -> NoReturn:
    raise InvalidInput(Diagnostic(code, message, line))


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate object key")
        result[key] = value
    return result


def _constant(value: str) -> NoReturn:
    raise ValueError("Non-finite number")


def _check_shape(value: Any, limits: Limits, line: int) -> None:
    pending = [(value, 0)]
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if depth > limits.depth or nodes > limits.nodes:
            fail("INPUT_COMPLEXITY", "Message exceeds nesting or node limit.", line)
        if isinstance(current, dict):
            pending.extend((item, depth + 1) for item in current.values())
            for key in current:
                try:
                    key.encode("utf-8")
                except UnicodeEncodeError:
                    fail("INVALID_JSON", "JSON object keys must contain valid Unicode.", line)
        elif isinstance(current, list):
            pending.extend((item, depth + 1) for item in current)
        elif isinstance(current, float) and not math.isfinite(current):
            fail("INVALID_JSON", "JSON numbers must be finite.", line)
        elif isinstance(current, str):
            try:
                current.encode("utf-8")
            except UnicodeEncodeError:
                fail("INVALID_JSON", "JSON strings must contain valid Unicode scalar values.", line)


def load_jsonl(path: Path, limits: Limits = DEFAULT_LIMITS) -> Iterator[tuple[int, Any]]:
    """Yield physical line numbers and parsed values; stop at the first input error."""
    try:
        with path.open("rb") as stream:
            total = count = line = 0
            while raw := stream.readline(limits.line_bytes + 1):
                line += 1
                total += len(raw)
                if total > limits.file_bytes:
                    fail("INPUT_SIZE", "Input exceeds total byte limit.", line)
                if len(raw) > limits.line_bytes:
                    fail("LINE_SIZE", "Input line exceeds byte limit.", line)
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    fail("INPUT_ENCODING", "Expected UTF-8 input without a byte-order mark.", line)
                if not text.strip(" \t\r\n"):
                    continue
                count += 1
                if count > limits.messages:
                    fail("MESSAGE_LIMIT", "Input exceeds message count limit.", line)
                try:
                    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
                except json.JSONDecodeError as error:
                    fail("INVALID_JSON", f"Malformed JSON at column {error.colno}.", line)
                except (ValueError, RecursionError):
                    fail("INVALID_JSON", "Invalid JSON: duplicate key, number, or nesting.", line)
                _check_shape(value, limits, line)
                yield line, value
            if not count:
                fail("EMPTY_INPUT", "Input contains no messages.")
    except (OSError, ValueError):
        fail("INPUT_IO", "Cannot read input file.")
