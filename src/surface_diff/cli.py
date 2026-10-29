"""Small public command line interface."""

import argparse
import json
import sys
from contextlib import suppress
from pathlib import Path

from surface_diff import __version__
from surface_diff.analysis import analyze_file
from surface_diff.comparison import check_file
from surface_diff.diagnostics import InvalidInput, terminal_text
from surface_diff.snapshot import write_snapshot


def _print_text(message: str, *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    rendered = terminal_text(message).encode(encoding, errors="backslashreplace").decode(encoding)
    print(rendered, file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="surfdiff", description="Offline A2UI structural tooling."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate", help="Validate schemas, lifecycle, and final Basic Catalog references."
    )
    validate.add_argument("input", type=Path)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    snapshot = commands.add_parser("snapshot", help="Write a canonical final-state snapshot.")
    snapshot.add_argument("input", type=Path)
    snapshot.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("check", help="Compare final state with an approved snapshot.")
    check.add_argument("input", type=Path)
    check.add_argument("--baseline", type=Path, required=True)
    check.add_argument("--format", choices=("text", "json"), default="text")
    try:
        try:
            args = parser.parse_args(argv)
        except SystemExit:
            # Help/version terminate inside argparse; flush before leaving
            # so a closed pipe still follows the processing-error boundary.
            sys.stdout.flush()
            raise
        result = _execute(args)
        sys.stdout.flush()
        return result
    except (RecursionError, MemoryError):
        _print_text(
            "surfdiff: processing resource limit exceeded; analysis incomplete.", error=True
        )
        return 2
    except InvalidInput as error:
        _print_text(f"surfdiff: {error.diagnostic.code}: {error.diagnostic.message}", error=True)
        return 2
    except (OSError, UnicodeError, ValueError):
        # Close a failed buffered stream so interpreter shutdown cannot retry
        # the write and replace our processing-error exit code (e.g. with 120).
        with suppress(OSError, UnicodeError, ValueError):
            sys.stdout.close()
        _print_text("surfdiff: output processing failed; analysis incomplete.", error=True)
        return 2


def _execute(args: argparse.Namespace) -> int:
    if args.command == "check":
        comparison = check_file(args.input, args.baseline)
        if args.format == "json":
            print(json.dumps(comparison.as_dict(), ensure_ascii=True, sort_keys=True))
        elif comparison.diagnostics:
            for item in comparison.diagnostics:
                line = f":{item.line}" if item.line is not None else ""
                _print_text(
                    f"{comparison.diagnostic_source}{line}: {item.code} "
                    f"{item.path}: {item.message}",
                    error=True,
                )
        elif comparison.changes:
            _print_text(f"DIFF {comparison.source}: {len(comparison.changes)} structural changes.")
            for change in comparison.changes:
                _print_text(f"  {change.code} {change.path}")
        else:
            _print_text(f"PASS {comparison.source}: no structural differences.")
        return comparison.exit_code
    analysis = analyze_file(args.input)
    report = analysis.report
    if args.command == "snapshot" and report.valid:
        assert analysis.snapshot is not None
        write_snapshot(args.out, analysis.snapshot)
        _print_text(f"Snapshot written: {args.out}")
        return 0
    if getattr(args, "format", "text") == "json":
        print(json.dumps(report.as_dict(), ensure_ascii=True, sort_keys=True))
    elif report.valid:
        _print_text(
            f"PASS {report.source}: {report.messages_checked} messages validated "
            "(schemas/lifecycle/final references)."
        )
    else:
        for diagnostic in report.diagnostics:
            line = f":{diagnostic.line}" if diagnostic.line is not None else ""
            _print_text(
                f"{report.source}{line}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}",
                error=True,
            )
    return 0 if report.valid else 2
