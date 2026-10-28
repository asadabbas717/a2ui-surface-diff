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
    args = parser.parse_args(argv)
    try:
        result = _execute(args)
        sys.stdout.flush()
        return result
    except (RecursionError, MemoryError):
        print("surfdiff: processing resource limit exceeded; analysis incomplete.", file=sys.stderr)
        return 2
    except InvalidInput as error:
        print(
            terminal_text(f"surfdiff: {error.diagnostic.code}: {error.diagnostic.message}"),
            file=sys.stderr,
        )
        return 2
    except (OSError, UnicodeError, ValueError):
        # Close a failed buffered stream so interpreter shutdown cannot retry
        # the write and replace our processing-error exit code (e.g. with 120).
        with suppress(OSError, UnicodeError, ValueError):
            sys.stdout.close()
        print("surfdiff: output processing failed; analysis incomplete.", file=sys.stderr)
        return 2


def _execute(args: argparse.Namespace) -> int:
    if args.command == "check":
        comparison = check_file(args.input, args.baseline)
        if args.format == "json":
            print(json.dumps(comparison.as_dict(), ensure_ascii=True, sort_keys=True))
        elif comparison.diagnostics:
            for item in comparison.diagnostics:
                line = f":{item.line}" if item.line is not None else ""
                print(
                    terminal_text(
                        f"{comparison.diagnostic_source}{line}: {item.code} "
                        f"{item.path}: {item.message}"
                    ),
                    file=sys.stderr,
                )
        elif comparison.changes:
            print(
                terminal_text(
                    f"DIFF {comparison.source}: {len(comparison.changes)} structural changes."
                )
            )
            for change in comparison.changes:
                print(terminal_text(f"  {change.code} {change.path}"))
        else:
            print(terminal_text(f"PASS {comparison.source}: no structural differences."))
        return comparison.exit_code
    analysis = analyze_file(args.input)
    report = analysis.report
    if args.command == "snapshot" and report.valid:
        assert analysis.snapshot is not None
        write_snapshot(args.out, analysis.snapshot)
    if args.command == "snapshot" and report.valid:
        print(terminal_text(f"Snapshot written: {args.out}"))
        return 0
    if getattr(args, "format", "text") == "json":
        print(json.dumps(report.as_dict(), ensure_ascii=True, sort_keys=True))
    elif report.valid:
        print(
            terminal_text(
                f"PASS {report.source}: {report.messages_checked} messages validated "
                "(schemas/lifecycle/final references)."
            )
        )
    else:
        for diagnostic in report.diagnostics:
            line = f":{diagnostic.line}" if diagnostic.line is not None else ""
            print(
                terminal_text(
                    f"{report.source}{line}: {diagnostic.code} "
                    f"{diagnostic.path}: {diagnostic.message}"
                ),
                file=sys.stderr,
            )
    return 0 if report.valid else 2
