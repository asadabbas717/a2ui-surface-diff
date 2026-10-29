import copy
import importlib.metadata
import json
import os
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
import yaml
from packaging.requirements import Requirement

from surface_diff import __version__
from surface_diff.analysis import analyze_file
from surface_diff.comparison import check_file
from surface_diff.diagnostics import InvalidInput
from surface_diff.loader import Limits, load_jsonl
from surface_diff.snapshot import serialize_snapshot, write_snapshot

FIXTURES = Path(__file__).parent / "fixtures"


def approved():
    return json.loads((FIXTURES / "baseline.json").read_text(encoding="utf-8"))


def test_distribution_metadata_matches_code():
    assert importlib.metadata.version("a2ui-surface-diff") == __version__ == "1.0.0"


def test_runtime_lock_retains_python312_conditional_dependency():
    path = Path(__file__).parent.parent / "requirements-runtime.lock"
    lines = path.read_text(encoding="utf-8").splitlines()
    dependency = Requirement(
        next(line.rstrip(" " + chr(92)) for line in lines if line.startswith("typing-extensions=="))
    )
    assert dependency.marker is not None
    assert dependency.marker.evaluate({"python_full_version": "3.12.15"})
    assert not dependency.marker.evaluate({"python_full_version": "3.13.15"})


def test_ci_workflow_is_valid_yaml_with_scalar_commands():
    path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "run" in step:
                assert isinstance(step["run"], str)


@pytest.mark.parametrize("report_format", ["text", "json"])
def test_unicode_paths_survive_ascii_output(tmp_path, report_format):
    key = "اردو"
    value = approved()
    value["surfaces"]["s"]["dataModel"] = {key: 0}
    baseline = tmp_path / "baseline.json"
    baseline.write_bytes(serialize_snapshot(value))
    capture = tmp_path / "unicode.jsonl"
    update = {"version": "v0.9.1", "updateDataModel": {"surfaceId": "s", "value": {key: 1}}}
    capture.write_text(
        (FIXTURES / "unchanged.jsonl").read_text(encoding="utf-8") + "\n" + json.dumps(update),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "surface_diff",
            "check",
            str(capture),
            "--baseline",
            str(baseline),
            "--format",
            report_format,
        ],
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1 and result.stderr == b""
    text = result.stdout.decode("ascii")
    if report_format == "json":
        assert json.loads(text)["changes"][0]["path"] == "/surfaces/s/dataModel/" + key
    else:
        assert "DATA_CHANGED" in text and "\\u0627\\u0631\\u062f\\u0648" in text


@pytest.mark.parametrize("argument", ["--help", "--version"])
def test_argparse_output_closed_pipe_returns_two(argument):
    process = subprocess.Popen(
        [sys.executable, "-m", "surface_diff", argument],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None and process.stderr is not None
    process.stdout.close()
    error = process.stderr.read().decode("utf-8")
    assert process.wait(timeout=20) == 2
    assert "output processing failed" in error


def test_concurrent_snapshot_publish_has_one_winner(tmp_path):
    first, second = approved(), approved()
    second["surfaces"]["s"]["components"]["root"]["text"] = "second"
    output = tmp_path / "contested.json"
    barrier = Barrier(2)

    def publish(snapshot):
        barrier.wait(timeout=20)
        try:
            write_snapshot(output, snapshot)
            return "written"
        except InvalidInput as error:
            return error.diagnostic.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(publish, [first, second]))
    assert sorted(results) == ["OUTPUT_EXISTS", "written"]
    assert output.read_bytes() in (serialize_snapshot(first), serialize_snapshot(second))
    assert not list(tmp_path.glob(".surfdiff-*"))


def test_existing_hardlink_and_readonly_baseline_are_preserved(tmp_path):
    baseline = tmp_path / "approved.json"
    baseline.write_bytes(serialize_snapshot(approved()))
    original = baseline.read_bytes()
    alias = tmp_path / "alias.json"
    os.link(baseline, alias)
    baseline.chmod(stat.S_IREAD)
    try:
        assert check_file(FIXTURES / "unchanged.jsonl", baseline).exit_code == 0
        assert check_file(FIXTURES / "regression.jsonl", alias).exit_code == 1
        with pytest.raises(InvalidInput, match="Output exists"):
            write_snapshot(alias, approved())
        assert baseline.read_bytes() == alias.read_bytes() == original
    finally:
        baseline.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_capture_boundary_limits_are_bytes_not_characters(tmp_path):
    path = tmp_path / "boundary.jsonl"
    raw = '{"ß":[1]}\n'.encode()
    path.write_bytes(raw)
    limits = Limits(file_bytes=len(raw), line_bytes=len(raw), messages=1, depth=2, nodes=3)
    assert list(load_jsonl(path, limits)) == [(1, {"ß": [1]})]
    assert path.read_bytes() == raw


@pytest.mark.parametrize(
    "field,code",
    [
        ("file_bytes", "INPUT_SIZE"),
        ("line_bytes", "LINE_SIZE"),
        ("depth", "INPUT_COMPLEXITY"),
        ("nodes", "INPUT_COMPLEXITY"),
    ],
)
def test_one_over_boundary_is_rejected(tmp_path, field, code):
    from dataclasses import replace

    path = tmp_path / "over.jsonl"
    raw = b'{"a":[1]}\n'
    path.write_bytes(raw)
    limits = Limits(file_bytes=len(raw), line_bytes=len(raw), messages=1, depth=2, nodes=3)
    limits = replace(limits, **{field: getattr(limits, field) - 1})
    with pytest.raises(InvalidInput) as error:
        list(load_jsonl(path, limits))
    assert error.value.diagnostic.code == code


def test_expressions_are_data_and_never_execute(tmp_path, monkeypatch):
    import socket

    marker = tmp_path / "must-not-exist"
    expression = "${__import__('pathlib').Path(" + repr(str(marker)) + ").write_text('unsafe')}"
    messages = [
        json.loads(line) for line in (FIXTURES / "unchanged.jsonl").read_text().splitlines()
    ]
    messages[1]["updateComponents"]["components"][0]["text"] = {
        "call": "formatString",
        "args": {"value": expression},
        "returnType": "string",
    }
    original = copy.deepcopy(messages)
    capture = tmp_path / "expression.jsonl"
    capture.write_text("\n".join(json.dumps(message) for message in messages), encoding="utf-8")

    def blocked(*args, **kwargs):
        pytest.fail("Runtime attempted network access")

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    result = analyze_file(capture)
    assert result.report.valid
    assert (
        result.snapshot["surfaces"]["s"]["components"]["root"]["text"]["args"]["value"]
        == expression
    )
    assert not marker.exists() and messages == original


def test_sparse_array_limit_roundtrips_through_baseline(tmp_path):
    lines = (FIXTURES / "unchanged.jsonl").read_text()
    update = {
        "version": "v0.9.1",
        "updateDataModel": {"surfaceId": "s", "path": "/items/10000", "value": "last"},
    }
    capture = tmp_path / "sparse.jsonl"
    capture.write_text(lines + "\n" + json.dumps(update), encoding="utf-8")
    result = analyze_file(capture)
    assert result.report.valid
    assert len(result.snapshot["surfaces"]["s"]["undefinedDataPaths"]) == 10000
    assert result.snapshot["surfaces"]["s"]["dataModel"]["items"][-1] == "last"
    baseline = tmp_path / "sparse.json"
    write_snapshot(baseline, result.snapshot)
    original = baseline.read_bytes()
    assert check_file(capture, baseline).exit_code == 0
    assert baseline.read_bytes() == original
