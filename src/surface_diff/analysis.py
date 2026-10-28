"""Compose streaming schema validation, replay, and final-state verification."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from surface_diff.diagnostics import InvalidInput, Report
from surface_diff.loader import DEFAULT_LIMITS, Limits
from surface_diff.replay import Replay
from surface_diff.validation import validated_messages


@dataclass(frozen=True)
class Analysis:
    report: Report
    snapshot: dict[str, Any] | None


def analyze_file(path: Path, limits: Limits = DEFAULT_LIMITS) -> Analysis:
    state = Replay()
    checked = 0
    try:
        for line, message in validated_messages(path, limits):
            state.apply(message, line)
            checked += 1
        snapshot = state.finish()
    except InvalidInput as error:
        return Analysis(Report(str(path), checked, (error.diagnostic,)), None)
    return Analysis(Report(str(path), checked), snapshot)


def validate_file(path: Path, limits: Limits = DEFAULT_LIMITS) -> Report:
    return analyze_file(path, limits).report
