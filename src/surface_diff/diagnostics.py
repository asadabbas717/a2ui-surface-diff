"""Stable, content-safe diagnostics shared by input and schema validation."""

import unicodedata
from dataclasses import asdict, dataclass
from typing import Any


def terminal_text(value: str) -> str:
    """Escape terminal controls and backslashes without altering machine-readable data."""
    return "".join(
        char.encode("unicode_escape").decode("ascii")
        if char == "\\" or unicodedata.category(char) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        else char
        for char in value
    )


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    line: int | None = None
    path: str = ""


class InvalidInput(Exception):
    def __init__(self, diagnostic: Diagnostic) -> None:
        self.diagnostic = diagnostic
        super().__init__(diagnostic.message)


@dataclass(frozen=True)
class Report:
    source: str
    messages_checked: int
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.diagnostics

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_version": 2,
            "command": "validate",
            "status": "passed" if self.valid else "error",
            "scope": "schemas_lifecycle_and_final_references",
            "source": self.source,
            "messages_checked": self.messages_checked,
            "diagnostics": [asdict(item) for item in self.diagnostics],
        }
