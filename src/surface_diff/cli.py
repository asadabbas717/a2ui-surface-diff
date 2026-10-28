"""Small public command line interface."""

import argparse
import json
import sys
from pathlib import Path

from surface_diff import __version__
from surface_diff.validation import validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="surfdiff", description="Offline A2UI structural tooling."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate", help="Validate message syntax and Basic Catalog structure (Phase 1)."
    )
    validate.add_argument("input", type=Path)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        report = validate_file(args.input)
    except (RecursionError, MemoryError):
        print("surfdiff: processing resource limit exceeded; analysis incomplete.", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report.as_dict(), ensure_ascii=True, sort_keys=True))
    elif report.valid:
        print(
            f"PASS {report.source}: {report.messages_checked} messages validated "
            "(syntax/catalog only)."
        )
    else:
        for diagnostic in report.diagnostics:
            line = f":{diagnostic.line}" if diagnostic.line is not None else ""
            print(
                f"{report.source}{line}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}",
                file=sys.stderr,
            )
    return 0 if report.valid else 2
