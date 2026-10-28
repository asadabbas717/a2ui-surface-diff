"""Bounded JSON Pointer upserts; absence is distinct from explicit JSON null."""

import copy
import re
from enum import Enum
from typing import Any

from surface_diff.diagnostics import Diagnostic, InvalidInput


class Absent(Enum):
    VALUE = "undefined"


MISSING = Absent.VALUE
MAX_ARRAY_INDEX = 10_000
MAX_MODEL_NODES = 200_000
MAX_MODEL_DEPTH = 64


def pointer(parts: list[str]) -> str:
    return "".join("/" + part.replace("~", "~0").replace("/", "~1") for part in parts)


def _bad(message: str) -> InvalidInput:
    return InvalidInput(Diagnostic("DATA_PATH", message))


def _tokens(path: str) -> list[str]:
    if path in ("", "/"):
        return []
    if not path.startswith("/") or re.search(r"~(?![01])", path):
        raise _bad("Expected an absolute JSON Pointer with valid ~0/~1 escapes.")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]
    if len(parts) > MAX_MODEL_DEPTH:
        raise _bad("Data path exceeds the supported depth limit.")
    return parts


def _index(token: str) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]*", token):
        raise _bad("Array paths require a non-negative canonical integer index.")
    if len(token) > 5 or int(token) > MAX_ARRAY_INDEX:
        raise _bad("Array index exceeds the supported maximum of 10000.")
    return int(token)


def bound_model(value: Any) -> int:
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if count > MAX_MODEL_NODES or depth > MAX_MODEL_DEPTH:
            raise InvalidInput(
                Diagnostic("STATE_LIMIT", "Effective data model exceeds node/depth limits.")
            )
        if isinstance(item, dict):
            pending.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            pending.extend((child, depth + 1) for child in item)
    return count


def update_model(root: Any, path: str, value: Any = MISSING) -> Any:
    """Return a detached updated model; leave the caller's model unchanged on error."""
    parts = _tokens(path)
    if not parts:
        result = {} if value is MISSING else copy.deepcopy(value)
        bound_model(result)
        return result
    result = copy.deepcopy(root)
    if result is None or result is MISSING:
        if value is MISSING:
            return result
        result = {}
    current = result
    for position, token in enumerate(parts):
        last = position == len(parts) - 1
        if isinstance(current, dict):
            key: str | int = token
            old = current.get(token, MISSING)
        elif isinstance(current, list):
            key = _index(token)
            old = current[key] if key < len(current) else MISSING
        else:
            if value is MISSING:
                return result
            raise _bad("Cannot traverse a primitive data-model value.")
        if value is MISSING and old is MISSING:
            return result  # Removing an absent path does not create containers.
        if last:
            if isinstance(current, dict):
                if value is MISSING:
                    current.pop(token, None)
                else:
                    current[token] = copy.deepcopy(value)
            else:
                index = int(key)
                current.extend([MISSING] * max(0, index + 1 - len(current)))
                current[index] = copy.deepcopy(value)
            break
        if old is MISSING or old is None:
            if value is MISSING:
                return result  # A descendant of null is absent; do not materialize it.
            child: Any = [] if re.fullmatch(r"0|[1-9][0-9]*", parts[position + 1]) else {}
            if isinstance(current, dict):
                current[token] = child
            else:
                index = int(key)
                current.extend([MISSING] * max(0, index + 1 - len(current)))
                current[index] = child
            old = child
        current = old
    bound_model(result)
    return result


def encode_model(value: Any) -> tuple[Any, list[str]]:
    """Use null placeholders plus separate paths to preserve undefined array slots."""
    undefined: list[str] = []

    def encode(item: Any, parts: list[str]) -> Any:
        if item is MISSING:
            undefined.append(pointer(parts))
            return None
        if isinstance(item, dict):
            return {key: encode(child, [*parts, key]) for key, child in sorted(item.items())}
        if isinstance(item, list):
            return [encode(child, [*parts, str(index)]) for index, child in enumerate(item)]
        return item

    result = encode(value, [])
    return result, sorted(undefined)


def decode_model(value: Any, undefined_paths: list[str]) -> Any:
    """Restore undefined slots from snapshot metadata using RFC pointers, not A2UI root paths."""
    result = copy.deepcopy(value)
    if len(set(undefined_paths)) != len(undefined_paths):
        raise _bad("Undefined slot paths must be unique.")
    for path in undefined_paths:
        if path.count("/") > MAX_MODEL_DEPTH:
            raise _bad("Undefined slot path exceeds the model depth limit.")
        if not path.startswith("/") or re.search(r"~(?![01])", path):
            raise _bad("Undefined slot metadata requires escaped absolute JSON Pointers.")
        parts = [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]
        current = result
        for index, token in enumerate(parts):
            if isinstance(current, list):
                key = _index(token)
                if key >= len(current):
                    raise _bad("Undefined slot path does not exist.")
                if index == len(parts) - 1:
                    if current[key] is not None:
                        raise _bad("Undefined slots require null array placeholders.")
                    current[key] = MISSING
                    break
                current = current[key]
            elif isinstance(current, dict) and token in current:
                current = current[token]
            else:
                raise _bad("Undefined slot path does not exist.")
        else:
            raise _bad("Undefined slot paths must terminate at an array element.")
    return result
