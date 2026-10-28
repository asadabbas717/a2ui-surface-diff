import copy
import json
import os
import socket
import subprocess
import sys
import sysconfig
from importlib.resources import files
from pathlib import Path

import pytest

from surface_diff import __version__
from surface_diff.cli import main
from surface_diff.loader import Limits
from surface_diff.validation import BASIC_CATALOGS, make_validator, validate_file

CATALOG = sorted(BASIC_CATALOGS)[0]
CREATE = {"version": "v0.9.1", "createSurface": {"surfaceId": "main", "catalogId": CATALOG}}
TEXT = {
    "version": "v0.9.1",
    "updateComponents": {
        "surfaceId": "main",
        "components": [{"id": "root", "component": "Text", "text": "Hello"}],
    },
}


def write_stream(tmp_path, messages):
    path = tmp_path / "input.jsonl"
    path.write_text("\n".join(json.dumps(m) for m in messages) + "\n", encoding="utf-8")
    return path


def test_official_example_and_no_network(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Validation attempted network access")

    monkeypatch.setattr(socket, "socket", forbidden)
    example = json.loads(files("surface_diff").joinpath("schemas/example.json").read_text())
    report = validate_file(write_stream(tmp_path, example["messages"]))
    assert report.valid and report.messages_checked == 2


@pytest.mark.parametrize("version", ["v0.9", "v0.9.1"])
@pytest.mark.parametrize("catalog", sorted(BASIC_CATALOGS))
def test_versions_and_catalogs(tmp_path, version, catalog):
    create = copy.deepcopy(CREATE)
    create["version"] = version
    create["createSurface"]["catalogId"] = catalog
    assert validate_file(write_stream(tmp_path, [create, TEXT])).valid


@pytest.mark.parametrize(
    "message,code",
    [
        ({"version": "v1.0"}, "UNSUPPORTED_VERSION"),
        ({"version": None}, "UNSUPPORTED_VERSION"),
        ({"version": []}, "UNSUPPORTED_VERSION"),
        ({"version": "v0.8"}, "UNSUPPORTED_VERSION"),
        ({}, "SCHEMA_INVALID"),
        ([], "SCHEMA_INVALID"),
        (None, "SCHEMA_INVALID"),
        ({"createSurface": CREATE["createSurface"]}, "SCHEMA_INVALID"),
        ({**CREATE, "extra": True}, "SCHEMA_INVALID"),
        ({**CREATE, "deleteSurface": {"surfaceId": "main"}}, "SCHEMA_INVALID"),
        (
            {
                "version": "v0.9",
                "createSurface": {"surfaceId": "s", "catalogId": "https://evil.test/catalog"},
            },
            "UNSUPPORTED_CATALOG",
        ),
        (
            {"version": "v0.9", "createSurface": {"surfaceId": 1, "catalogId": CATALOG}},
            "SCHEMA_INVALID",
        ),
        (
            {"version": "v0.9", "updateComponents": {"surfaceId": "s", "components": []}},
            "SCHEMA_INVALID",
        ),
        (
            {
                "version": "v0.9",
                "updateComponents": {
                    "surfaceId": "s",
                    "components": [{"id": "r", "component": "Invented"}],
                },
            },
            "SCHEMA_INVALID",
        ),
        (
            {
                "version": "v0.9",
                "updateComponents": {
                    "surfaceId": "s",
                    "components": [{"id": "r", "component": "Text"}],
                },
            },
            "SCHEMA_INVALID",
        ),
    ],
)
def test_invalid_messages(tmp_path, message, code):
    report = validate_file(write_stream(tmp_path, [message]))
    assert not report.valid
    assert report.diagnostics[0].code == code
    assert report.diagnostics[0].line == 1


@pytest.mark.parametrize(
    "raw,code",
    [
        (b"", "EMPTY_INPUT"),
        (b" \n\r\n", "EMPTY_INPUT"),
        (b'{"version":', "INVALID_JSON"),
        (b"\xff\n", "INPUT_ENCODING"),
        (b"\xef\xbb\xbf{}", "INVALID_JSON"),
        (b'{"x":1,"x":2}', "INVALID_JSON"),
        (b'{"x":NaN}', "INVALID_JSON"),
        (b'{"x":Infinity}', "INVALID_JSON"),
        (b'{"x":1e999}', "INVALID_JSON"),
        (b'{"x":"\\ud800"}', "INVALID_JSON"),
        (b'{"\\ud800":0}', "INVALID_JSON"),
    ],
)
def test_bad_bytes(tmp_path, raw, code):
    path = tmp_path / "bad.jsonl"
    path.write_bytes(raw)
    assert validate_file(path).diagnostics[0].code == code


def test_extreme_nesting_rejected(tmp_path):
    path = tmp_path / "deep.jsonl"
    path.write_bytes(b"[" * 2000 + b"]" * 2000)
    # Decoder recursion thresholds differ by Python build. Either rejection
    # must be a processing error, never successful validation.
    report = validate_file(path)
    assert not report.valid
    assert report.diagnostics[0].code in {"INVALID_JSON", "INPUT_COMPLEXITY"}


@pytest.mark.parametrize(
    "limits,messages,code",
    [
        (Limits(file_bytes=4), [CREATE], "INPUT_SIZE"),
        (Limits(line_bytes=4), [CREATE], "LINE_SIZE"),
        (Limits(messages=1), [CREATE, TEXT], "MESSAGE_LIMIT"),
        (Limits(depth=1), [CREATE], "INPUT_COMPLEXITY"),
        (Limits(nodes=2), [CREATE], "INPUT_COMPLEXITY"),
    ],
)
def test_limits(tmp_path, limits, messages, code):
    assert validate_file(write_stream(tmp_path, messages), limits).diagnostics[0].code == code


def test_read_failure(tmp_path):
    assert validate_file(tmp_path / "missing").diagnostics[0].code == "INPUT_IO"
    assert validate_file(tmp_path).diagnostics[0].code == "INPUT_IO"
    assert validate_file(Path("bad\x00path")).diagnostics[0].code == "INPUT_IO"


def test_function_validation(tmp_path):
    text = copy.deepcopy(TEXT)
    text["updateComponents"]["components"][0]["text"] = {
        "call": "formatString",
        "args": {"value": "Hello"},
        "returnType": "string",
    }
    assert validate_file(write_stream(tmp_path, [CREATE, text])).valid
    text["updateComponents"]["components"][0]["text"]["call"] = "unknown"
    assert not validate_file(write_stream(tmp_path, [CREATE, text])).valid


def test_local_schema_integrity():
    import hashlib

    assets = files("surface_diff").joinpath("schemas")
    manifest = json.loads(assets.joinpath("SHA256SUMS.json").read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256(assets.joinpath(name).read_bytes()).hexdigest() == digest


def test_all_envelopes_and_blank_lines(tmp_path):
    messages = [
        CREATE,
        TEXT,
        {"version": "v0.9", "updateDataModel": {"surfaceId": "main", "value": {"user": "Alice"}}},
        {"version": "v0.9", "deleteSurface": {"surfaceId": "main"}},
    ]
    path = write_stream(tmp_path, messages)
    path.write_bytes(b"\n" + path.read_bytes() + b" \n")
    before = path.read_bytes()
    first = validate_file(path)
    assert first.valid and first.messages_checked == 4
    assert first.as_dict() == validate_file(path).as_dict()
    assert path.read_bytes() == before


def test_stops_on_error_and_reports_physical_line(tmp_path):
    path = write_stream(tmp_path, [CREATE])
    path.write_bytes(path.read_bytes() + b"\n{\n")
    report = validate_file(path)
    assert report.messages_checked == 1
    assert report.diagnostics[0].line == 3


def test_catalog_theme_and_bound_properties(tmp_path):
    text = copy.deepcopy(TEXT)
    text["updateComponents"]["components"][0]["text"] = {"path": "/greeting"}
    assert validate_file(write_stream(tmp_path, [CREATE, text])).valid
    text["updateComponents"]["components"][0]["unexpected"] = "secret-value"
    report = validate_file(write_stream(tmp_path, [CREATE, text]))
    assert not report.valid
    assert "secret-value" not in json.dumps(report.as_dict())
    create = copy.deepcopy(CREATE)
    create["createSurface"]["theme"] = {"unknown": "secret-value"}
    # The official theme schema permits extra keys; do not invent constraints.
    assert validate_file(write_stream(tmp_path, [create])).valid
    create["createSurface"]["theme"] = "invalid"
    assert not validate_file(write_stream(tmp_path, [create])).valid


def test_schema_validation_non_mutating():
    original = copy.deepcopy(TEXT)
    make_validator().validate(TEXT)
    assert original == TEXT


def test_phase_one_scope_explicit(tmp_path):
    # Lifecycle and final references intentionally require Phase 2.
    report = validate_file(write_stream(tmp_path, [TEXT]))
    assert report.valid
    assert report.as_dict()["scope"] == "message_syntax_and_basic_catalog"


def test_cli_output(tmp_path, capsys):
    path = write_stream(tmp_path, [CREATE, TEXT])
    assert main([str_arg for str_arg in ["validate", str(path)]]) == 0
    assert "syntax/catalog only" in capsys.readouterr().out
    path.write_text("{", encoding="utf-8")
    assert main(["validate", str(path)]) == 2
    captured = capsys.readouterr()
    assert not captured.out and "INVALID_JSON" in captured.err
    assert main(["validate", str(path), "--format", "json"]) == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "error" and data["report_version"] == 1
    assert not captured.err


def test_resource_failure(tmp_path, monkeypatch, capsys):
    def exhausted(path):
        raise RecursionError

    monkeypatch.setattr("surface_diff.cli.validate_file", exhausted)
    assert main(["validate", str(tmp_path)]) == 2
    assert "incomplete" in capsys.readouterr().err


@pytest.mark.parametrize(
    "args,exit_code",
    [
        (["--help"], 0),
        (["--version"], 0),
        ([], 2),
        (["snapshot"], 2),
        (["validate", "--format", "xml"], 2),
    ],
)
def test_cli_subprocess(args, exit_code):
    result = subprocess.run(
        [sys.executable, "-m", "surface_diff", *args], capture_output=True, text=True, check=False
    )
    assert result.returncode == exit_code
    if args == ["--version"]:
        assert __version__ in result.stdout


def test_installed_entrypoint(tmp_path):
    path = write_stream(tmp_path, [CREATE, TEXT])
    command = Path(sysconfig.get_path("scripts")) / (
        "surfdiff.exe" if os.name == "nt" else "surfdiff"
    )
    result = subprocess.run(
        [str(command), "validate", str(path), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["messages_checked"] == 2


@pytest.mark.parametrize("whitespace", ["\u00a0", "\u2003", "\v", "\f"])
def test_non_json_whitespace_is_not_a_blank_line(tmp_path, whitespace):
    path = write_stream(tmp_path, [CREATE])
    with path.open("a", encoding="utf-8") as stream:
        stream.write(whitespace + "\n")
    report = validate_file(path)
    assert not report.valid
    assert report.diagnostics[0].code == "INVALID_JSON"
    assert report.diagnostics[0].line == 2
