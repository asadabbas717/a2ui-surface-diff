import copy
import json
import subprocess
import sys
from dataclasses import replace
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from surface_diff.baseline import load_baseline
from surface_diff.cli import main
from surface_diff.comparison import check_file, compare_snapshots
from surface_diff.data_model import decode_model, encode_model
from surface_diff.diagnostics import InvalidInput
from surface_diff.snapshot import SNAPSHOT_LIMITS, serialize_snapshot, write_snapshot

FIXTURES = Path(__file__).parent / "fixtures"


def approved():
    return json.loads((FIXTURES / "baseline.json").read_text(encoding="utf-8"))


def saved(tmp_path, value):
    path = tmp_path / "baseline.json"
    path.write_bytes(serialize_snapshot(value))
    return path


def test_independent_fixture_roundtrip():
    snapshot = load_baseline(FIXTURES / "baseline.json")
    assert snapshot == approved()
    assert check_file(FIXTURES / "unchanged.jsonl", FIXTURES / "baseline.json").exit_code == 0


@pytest.mark.parametrize(
    "old,new,code,path",
    [
        ({"text": "Hello"}, {"text": "Changed"}, "PROPERTY_CHANGED", "text"),
        ({"text": "Hello"}, {"text": "Hello", "variant": "h1"}, "PROPERTY_ADDED", "variant"),
        ({"text": "Hello", "variant": "h1"}, {"text": "Hello"}, "PROPERTY_REMOVED", "variant"),
        ({"text": {"path": "/a"}}, {"text": {"path": "/b"}}, "PROPERTY_CHANGED", "text/path"),
    ],
)
def test_properties_bindings_and_nonmutation(old, new, code, path):
    before, after = approved(), approved()
    for snapshot, props in [(before, old), (after, new)]:
        snapshot["surfaces"]["s"]["components"]["root"] = {
            "id": "root",
            "component": "Text",
            **props,
        }
    originals = copy.deepcopy((before, after))
    changes = compare_snapshots(before, after)
    assert [(item.code, item.path) for item in changes] == [
        (code, "/surfaces/s/components/root/" + path)
    ]
    assert (before, after) == originals


def test_container_and_type_changes_are_not_duplicated():
    before, after = approved(), approved()
    after["surfaces"]["s"]["components"]["root"] = {"id": "root", "component": "Divider"}
    changes = compare_snapshots(before, after)
    assert len(changes) == 1 and changes[0].code == "COMPONENT_TYPE_CHANGED"
    assert changes[0].before == "Text" and changes[0].after == "Divider"
    added = copy.deepcopy(before)
    added["surfaces"]["other"] = copy.deepcopy(before["surfaces"]["s"])
    added["surfaces"]["other"]["createSurface"]["surfaceId"] = "other"
    assert [c.code for c in compare_snapshots(before, added)] == ["SURFACE_ADDED"]
    assert [c.code for c in compare_snapshots(added, before)] == ["SURFACE_REMOVED"]
    added = copy.deepcopy(before)
    added["surfaces"]["s"]["components"]["extra"] = {"id": "extra", "component": "Divider"}
    assert [c.code for c in compare_snapshots(before, added)] == ["COMPONENT_ADDED"]
    removed = compare_snapshots(added, before)
    assert [c.code for c in removed] == ["COMPONENT_REMOVED"]
    assert removed[0].as_dict()["after"] == {"state": "absent"}


def test_child_order_reference_and_action_paths():
    before, after = approved(), approved()
    for snapshot in (before, after):
        snapshot["surfaces"]["s"]["components"] = {
            "root": {"id": "root", "component": "Row", "children": ["a", "b"]},
            "a": {"id": "a", "component": "Divider"},
            "b": {"id": "b", "component": "Divider"},
        }
    after["surfaces"]["s"]["components"]["root"]["children"] = ["b", "a"]
    changes = compare_snapshots(before, after)
    assert len(changes) == 1 and changes[0].code == "CHILD_ORDER_CHANGED"
    assert changes[0].path.endswith("/children")
    for snapshot in (before, after):
        snapshot["surfaces"]["s"]["components"]["root"] = {
            "id": "root",
            "component": "Button",
            "child": "a",
            "action": {"event": {"name": "go"}},
        }
    after["surfaces"]["s"]["components"]["root"]["child"] = "b"
    after["surfaces"]["s"]["components"]["root"]["action"]["event"]["name"] = "stop"
    changes = compare_snapshots(before, after)
    assert [(c.code, c.path.split("/root/")[-1]) for c in changes] == [
        ("ACTION_CHANGED", "action/event/name"),
        ("REFERENCE_CHANGED", "child"),
    ]


@pytest.mark.parametrize(
    "old,new,expected",
    [
        (1, True, True),
        (False, 0, True),
        (1, 1.0, False),
        ({"x": [1]}, {"x": [True]}, True),
        ([], {}, True),
    ],
)
def test_json_type_aware_equality(old, new, expected):
    before, after = approved(), approved()
    before["surfaces"]["s"]["dataModel"] = old
    after["surfaces"]["s"]["dataModel"] = new
    assert bool(compare_snapshots(before, after)) is expected


def test_tab_order_is_one_change():
    before, after = approved(), approved()
    tabs = [{"title": "A", "child": "a"}, {"title": "B", "child": "b"}]
    for snapshot, entries in [(before, tabs), (after, list(reversed(tabs)))]:
        snapshot["surfaces"]["s"]["components"] = {
            "root": {"id": "root", "component": "Tabs", "tabs": entries},
            "a": {"id": "a", "component": "Divider"},
            "b": {"id": "b", "component": "Divider"},
        }
    changes = compare_snapshots(before, after)
    assert len(changes) == 1
    assert changes[0].code == "CHILD_ORDER_CHANGED"
    assert changes[0].path == "/surfaces/s/components/root/tabs"
    assert compare_snapshots(before, before) == ()


def test_readme_checkout_workflow(tmp_path):
    examples = Path(__file__).parent.parent / "examples"
    baseline = tmp_path / "checkout.json"
    assert main(["snapshot", str(examples / "checkout-before.jsonl"), "--out", str(baseline)]) == 0
    result = check_file(examples / "checkout-after.jsonl", baseline)
    assert result.exit_code == 1
    assert [(c.code, c.path) for c in result.changes] == [
        ("COMPONENT_REMOVED", "/surfaces/checkout/components/buy"),
        ("COMPONENT_REMOVED", "/surfaces/checkout/components/buy-label"),
        ("REFERENCE_CHANGED", "/surfaces/checkout/components/root/children/1"),
    ]


def test_data_paths_absence_arrays_and_undefined():
    before, after = approved(), approved()
    before["surfaces"]["s"]["dataModel"] = {"a/~": None, "arr": [None, 1]}
    after["surfaces"]["s"]["dataModel"] = {"arr": [None, 2, 3]}
    after["surfaces"]["s"]["undefinedDataPaths"] = ["/arr/0"]
    changes = compare_snapshots(before, after)
    assert [(c.code, c.path) for c in changes] == [
        ("DATA_CHANGED", "/surfaces/s/dataModel/arr/0"),
        ("DATA_CHANGED", "/surfaces/s/dataModel/arr/1"),
        ("DATA_ADDED", "/surfaces/s/dataModel/arr/2"),
        ("DATA_REMOVED", "/surfaces/s/dataModel/a~1~0"),
    ]
    assert changes[0].as_dict()["before"]["value"] is None
    assert changes[0].as_dict()["after"] == {"state": "undefined"}
    assert not any("undefinedDataPaths" in c.path for c in changes)
    added = compare_snapshots(approved(), after)
    assert added[0].as_dict()["after"]["undefined_paths"] == ["/0"]


def test_compare_order_and_creation_properties():
    before, after = approved(), approved()
    after["surfaces"]["s"]["createSurface"]["theme"] = {"z": 1, "a": 2}
    first = compare_snapshots(before, after)
    after["surfaces"]["s"]["createSurface"]["theme"] = {"a": 2, "z": 1}
    assert [c.as_dict() for c in first] == [c.as_dict() for c in compare_snapshots(before, after)]
    assert [c.path for c in first] == sorted(c.path for c in first)


@pytest.mark.parametrize(
    "raw,code",
    [
        (b"", "BASELINE_INVALID"),
        (b"{", "BASELINE_INVALID"),
        (b'{"x":1,"x":2}', "BASELINE_INVALID"),
        (b'{"x":NaN}', "BASELINE_INVALID"),
        (b'{"x":1e999}', "BASELINE_INVALID"),
        (b"[]", "BASELINE_INVALID"),
        (b"null", "BASELINE_INVALID"),
        (b"\xff", "BASELINE_INVALID"),
        (b"\xef\xbb\xbf{}", "BASELINE_INVALID"),
        (b'{"x":"\\ud800"}', "BASELINE_INVALID"),
        (b'{"snapshot_version":true}', "BASELINE_UNSUPPORTED"),
        (b'{"snapshot_version":1.0}', "BASELINE_UNSUPPORTED"),
        (b'{"snapshot_version":2}', "BASELINE_UNSUPPORTED"),
    ],
)
def test_malformed_baselines(tmp_path, raw, code):
    path = tmp_path / "bad.json"
    path.write_bytes(raw)
    with pytest.raises(InvalidInput) as error:
        load_baseline(path)
    assert error.value.diagnostic.code == code
    assert path.read_bytes() == raw


@pytest.mark.parametrize(
    "defect",
    [
        "metadata",
        "extra",
        "surface-id",
        "component-id",
        "component-type",
        "references",
        "root",
        "catalog",
        "undefined-object",
        "undefined-missing",
        "undefined-nonnull",
        "undefined-duplicate",
    ],
)
def test_invalid_baseline_state(tmp_path, defect):
    value = approved()
    surface = value["surfaces"]["s"]
    if defect == "metadata":
        value["protocol"]["schema_revision"] = "unknown"
    elif defect == "extra":
        value["extra"] = 1
    elif defect == "surface-id":
        surface["createSurface"]["surfaceId"] = "wrong"
    elif defect == "component-id":
        surface["components"]["root"]["id"] = "wrong"
    elif defect == "component-type":
        surface["components"]["root"]["component"] = "Invented"
    elif defect == "references":
        surface["components"]["root"] = {"id": "root", "component": "Card", "child": "missing"}
    elif defect == "root":
        surface["components"] = {}
    elif defect == "catalog":
        surface["createSurface"]["catalogId"] = "custom"
    else:
        surface["dataModel"] = [None]
        surface["undefinedDataPaths"] = ["/0"]
        if defect == "undefined-object":
            surface["dataModel"] = {"0": None}
        elif defect == "undefined-missing":
            surface["undefinedDataPaths"] = ["/1"]
        elif defect == "undefined-nonnull":
            surface["dataModel"] = [1]
        elif defect == "undefined-duplicate":
            surface["undefinedDataPaths"] = ["/0", "/0"]
    path = saved(tmp_path, value)
    before = path.read_bytes()
    with pytest.raises(InvalidInput) as error:
        load_baseline(path)
    assert error.value.diagnostic.code.startswith("BASELINE_")
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "paths", [["relative"], ["/~2"], ["/0/deep"], ["/01"], ["/1"], ["/" + "/".join(["a"] * 65)]]
)
def test_bad_undefined_paths(paths):
    with pytest.raises(InvalidInput):
        decode_model([None], paths)


def test_undefined_roundtrip_empty_keys_and_duplicates():
    data, paths = {"": {"a/b": [None, None]}}, ["//a~1b/1"]
    assert encode_model(decode_model(data, paths)) == (data, paths)
    with pytest.raises(InvalidInput, match="unique"):
        decode_model([None], ["/0", "/0"])


def test_baseline_io_size_and_complexity(tmp_path, monkeypatch):
    with pytest.raises(InvalidInput, match="Cannot read"):
        load_baseline(tmp_path / "missing")
    path = saved(tmp_path, approved())
    monkeypatch.setattr(
        "surface_diff.baseline.SNAPSHOT_LIMITS", replace(SNAPSHOT_LIMITS, file_bytes=8)
    )
    with pytest.raises(InvalidInput) as error:
        load_baseline(path)
    assert error.value.diagnostic.code == "BASELINE_LIMIT"
    monkeypatch.setattr("surface_diff.baseline.SNAPSHOT_LIMITS", replace(SNAPSHOT_LIMITS, nodes=3))
    with pytest.raises(InvalidInput, match="node limit"):
        load_baseline(path)


def test_snapshot_output_obeys_baseline_read_limits(tmp_path, monkeypatch):
    output = tmp_path / "output.json"
    monkeypatch.setattr(
        "surface_diff.snapshot.SNAPSHOT_LIMITS", replace(SNAPSHOT_LIMITS, file_bytes=8)
    )
    with pytest.raises(InvalidInput) as error:
        write_snapshot(output, approved())
    assert error.value.diagnostic.code == "SNAPSHOT_LIMIT" and not output.exists()
    monkeypatch.setattr("surface_diff.snapshot.SNAPSHOT_LIMITS", replace(SNAPSHOT_LIMITS, depth=1))
    with pytest.raises(InvalidInput) as error:
        write_snapshot(output, approved())
    assert error.value.diagnostic.code == "SNAPSHOT_LIMIT" and not output.exists()


def test_incomplete_comparison_never_returns_diff_success(tmp_path, monkeypatch):
    value = approved()
    value["surfaces"]["s"]["components"]["root"].update(text="Different", variant="h1")
    baseline = saved(tmp_path, value)
    monkeypatch.setattr("surface_diff.comparison.MAX_CHANGES", 1)
    result = check_file(FIXTURES / "unchanged.jsonl", baseline)
    assert result.exit_code == 2
    assert result.diagnostics[0].code == "COMPARISON_LIMIT"
    assert result.changes == ()


def test_long_paths_and_payload_budget_prevent_oversized_reports(monkeypatch):
    before, after = approved(), approved()
    long_key = "ancestor" * 100
    before["surfaces"]["s"]["dataModel"] = {long_key: {str(i): 0 for i in range(10)}}
    after["surfaces"]["s"]["dataModel"] = {long_key: {str(i): 1 for i in range(10)}}
    monkeypatch.setattr("surface_diff.comparison.MAX_CHANGE_BYTES", 2000)
    with pytest.raises(InvalidInput, match="payload budget"):
        compare_snapshots(before, after)
    monkeypatch.setattr("surface_diff.comparison.MAX_CHANGE_BYTES", 20)
    with pytest.raises(InvalidInput, match="payload budget"):
        compare_snapshots(before, after)


@pytest.mark.parametrize(
    "fixture,exit_code,status",
    [("unchanged.jsonl", 0, "passed"), ("regression.jsonl", 1, "different")],
)
def test_cli_reports_and_never_mutates_inputs(tmp_path, fixture, exit_code, status, capsys):
    baseline = saved(tmp_path, approved())
    source = tmp_path / fixture
    source.write_bytes((FIXTURES / fixture).read_bytes())
    original = (source.read_bytes(), baseline.read_bytes())
    args = ["check", str(source), "--baseline", str(baseline)]
    assert main(args) == exit_code
    output = capsys.readouterr()
    assert ("no structural differences" if exit_code == 0 else "PROPERTY_CHANGED") in output.out
    assert output.err == ""
    assert main([*args, "--format", "json"]) == exit_code
    report = json.loads(capsys.readouterr().out)
    assert report["report_version"] == 1 and report["command"] == "check"
    assert report["status"] == status and report["diagnostics"] == []
    assert original == (source.read_bytes(), baseline.read_bytes())


def test_check_errors_json_stderr_and_nonmutation(tmp_path, capsys):
    source = tmp_path / "invalid.jsonl"
    source.write_text("{", encoding="utf-8")
    baseline = saved(tmp_path, approved())
    original = baseline.read_bytes()
    assert main(["check", str(source), "--baseline", str(baseline)]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "INVALID_JSON" in output.err
    assert main(["check", str(source), "--baseline", str(baseline), "--format", "json"]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "error" and report["changes"] == []
    assert report["diagnostics"][0]["file"] == str(source)
    assert (
        main(["check", str(source), "--baseline", str(tmp_path / "missing"), "--format", "json"])
        == 2
    )
    report = json.loads(capsys.readouterr().out)
    assert report["diagnostics"][0]["code"] == "BASELINE_IO"
    assert baseline.read_bytes() == original
    assert main(["check", str(baseline), "--baseline", str(baseline)]) == 2
    assert baseline.read_bytes() == original


@pytest.mark.parametrize(
    "fixture,code", [("unchanged.jsonl", 0), ("regression.jsonl", 1), ("absent.jsonl", 2)]
)
def test_check_cli_subprocess(fixture, code):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "surface_diff",
            "check",
            str(FIXTURES / fixture),
            "--baseline",
            str(FIXTURES / "baseline.json"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == code, result.stderr
    assert json.loads(result.stdout)["command"] == "check"


def test_buffered_cli_output_failure_keeps_exit_two():
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "surface_diff",
            "check",
            str(FIXTURES / "unchanged.jsonl"),
            "--baseline",
            str(FIXTURES / "baseline.json"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None and process.stderr is not None
    process.stdout.close()
    error = process.stderr.read().decode("utf-8")
    assert process.wait(timeout=20) == 2
    assert "output processing failed" in error


def test_check_does_not_contact_network(monkeypatch):
    import socket

    def blocked(*args, **kwargs):
        pytest.fail("Network access attempted")

    monkeypatch.setattr(socket, "socket", blocked)
    assert check_file(FIXTURES / "regression.jsonl", FIXTURES / "baseline.json").exit_code == 1


def test_untrusted_terminal_controls_are_escaped_but_json_paths_are_exact(tmp_path, capsys):
    value = approved()
    key = "\x1b[2J\nFAKE PASS\u0085\u202e"
    value["surfaces"]["s"]["dataModel"] = {key: 0}
    baseline = saved(tmp_path, value)
    capture = tmp_path / "capture.jsonl"
    update = {"version": "v0.9.1", "updateDataModel": {"surfaceId": "s", "value": {key: 1}}}
    capture.write_text(
        (FIXTURES / "unchanged.jsonl").read_text() + "\n" + json.dumps(update), encoding="utf-8"
    )
    args = ["check", str(capture), "--baseline", str(baseline)]
    assert main(args) == 1
    output = capsys.readouterr().out
    assert len(output.splitlines()) == 2
    assert not any(control in output for control in ("\x1b", "\x85", "\u202e"))
    assert "\\x1b[2J\\nFAKE PASS" in output
    assert main([*args, "--format", "json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["changes"][0]["path"] == "/surfaces/s/dataModel/" + key


def test_terminal_escape_representation_is_unambiguous():
    from surface_diff.diagnostics import terminal_text

    assert terminal_text("\n") == "\\n"
    assert terminal_text("\\n") == "\\\\n"
    assert terminal_text("café اردو") == "café اردو"
    assert terminal_text("\u2028\u2066\r") == "\\u2028\\u2066\\r"


@pytest.mark.parametrize("fixture", ["unchanged.jsonl", "regression.jsonl", "absent.jsonl"])
def test_stable_report_schema(fixture):
    schema = json.loads(files("surface_diff").joinpath("schemas/check-report-v1.json").read_text())
    Draft202012Validator.check_schema(schema)
    report = check_file(FIXTURES / fixture, FIXTURES / "baseline.json").as_dict()
    Draft202012Validator(schema).validate(report)


def test_new_snapshot_matches_check_contract(tmp_path):
    baseline = tmp_path / "fresh.json"
    assert main(["snapshot", str(FIXTURES / "unchanged.jsonl"), "--out", str(baseline)]) == 0
    assert main(["check", str(FIXTURES / "unchanged.jsonl"), "--baseline", str(baseline)]) == 0
    assert main(["check", str(FIXTURES / "regression.jsonl"), "--baseline", str(baseline)]) == 1


def test_surface_deletion_and_empty_baseline_comparison(tmp_path):
    capture = tmp_path / "deleted.jsonl"
    first = (FIXTURES / "unchanged.jsonl").read_text().splitlines()[0]
    capture.write_text(
        first + '\n{"version":"v0.9.1","deleteSurface":{"surfaceId":"s"}}\n', encoding="utf-8"
    )
    removed = check_file(capture, FIXTURES / "baseline.json")
    assert removed.exit_code == 1
    assert [change.code for change in removed.changes] == ["SURFACE_REMOVED"]
    empty = approved()
    empty["surfaces"] = {}
    baseline = saved(tmp_path, empty)
    added = check_file(FIXTURES / "unchanged.jsonl", baseline)
    assert added.exit_code == 1
    assert [change.code for change in added.changes] == ["SURFACE_ADDED"]
