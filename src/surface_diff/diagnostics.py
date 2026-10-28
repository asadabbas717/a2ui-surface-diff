"""Stable, content-safe diagnostics shared by input and schema validation."""

from dataclasses import asdict, dataclass
from typing import Any


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
            "report_version": 1,
            "command": "validate",
            "status": "passed" if self.valid else "error",
            "scope": "message_syntax_and_basic_catalog",
            "source": self.source,
            "messages_checked": self.messages_checked,
            "diagnostics": [asdict(item) for item in self.diagnostics],
        }
