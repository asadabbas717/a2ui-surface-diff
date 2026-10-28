import copy
import json
import subprocess
import sys

import pytest

from surface_diff.analysis import analyze_file, validate_file
from surface_diff.cli import main
from surface_diff.data_model import MISSING, encode_model, update_model
from surface_diff.diagnostics import InvalidInput
from surface_diff.replay import Replay, replay
from surface_diff.snapshot import serialize_snapshot, write_snapshot
from surface_diff.validation import BASIC_CATALOGS

CATALOG = sorted(BASIC_CATALOGS)[0]


def message(operation, surface="s", **fields):
    return {"version": "v0.9.1", operation: {"surfaceId": surface, **fields}}


def create(surface="s"):
    return message("createSurface", surface, catalogId=CATALOG)


def components(*items, surface="s"):
    return message("updateComponents", surface, components=list(items))


def text(id="root", **fields):
    return {"id": id, "component": "Text", "text": "Hello", **fields}


def capture(tmp_path, messages):
    path = tmp_path / "capture.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in messages), encoding="utf-8")
    return path


def test_progressive_updates_preserve_collection_and_replace_definition(tmp_path):
    messages = [
        create(),
        components({"id": "root", "component": "Column", "children": ["late"]}),
        components(text("late", variant="h1")),
        components(text("late", text="updated")),
    ]
    original = copy.deepcopy(messages)
    path = capture(tmp_path, messages)
    analysis = analyze_file(path)
    assert analysis.report.valid
    surface = analysis.snapshot["surfaces"]["s"]
    assert set(surface["components"]) == {"root", "late"}
    assert surface["components"]["late"] == text("late", text="updated")
    assert "variant" not in surface["components"]["late"]
    assert messages == original
    snapshot = replay(messages)
    snapshot["surfaces"]["s"]["components"]["late"]["text"] = "changed"
    assert messages == original


@pytest.mark.parametrize(
    "messages,code",
    [
        ([create(), create()], "SURFACE_EXISTS"),
        ([components(text())], "SURFACE_MISSING"),
        ([message("deleteSurface")], "SURFACE_MISSING"),
        ([message("updateDataModel", value={})], "SURFACE_MISSING"),
        ([create()], "ROOT_MISSING"),
        ([create(), components(text(), text())], "COMPONENT_DUPLICATE"),
        (
            [create(), components({"id": "root", "component": "Card", "child": "absent"})],
            "REFERENCE_MISSING",
        ),
        (
            [create(), components({"id": "root", "component": "Card", "child": "root"})],
            "REFERENCE_CYCLE",
        ),
    ],
)
def test_lifecycle_failures(tmp_path, messages, code):
    analysis = analyze_file(capture(tmp_path, messages))
    assert not analysis.report.valid and analysis.snapshot is None
    assert analysis.report.diagnostics[0].code == code
    assert analysis.report.diagnostics[0].line is not None


def test_reuse_multiple_surfaces_and_deleted_invalid_graph(tmp_path):
    messages = [
        create(),
        components({"id": "root", "component": "Card", "child": "missing"}),
        create("other"),
        components(text(text="other"), surface="other"),
        message("deleteSurface"),
        create(),
        components(text()),
    ]
    snapshot = analyze_file(capture(tmp_path, messages)).snapshot
    assert set(snapshot["surfaces"]) == {"s", "other"}
    assert snapshot["surfaces"]["s"]["components"] == {"root": text()}
    assert replay([create(), message("deleteSurface")])["surfaces"] == {}


@pytest.mark.parametrize(
    "component,targets",
    [
        ({"id": "root", "component": "Row", "children": ["a", "b"]}, ["a", "b"]),
        (
            {"id": "root", "component": "List", "children": {"componentId": "a", "path": "/rows"}},
            ["a"],
        ),
        ({"id": "root", "component": "Modal", "trigger": "a", "content": "b"}, ["a", "b"]),
        ({"id": "root", "component": "Tabs", "tabs": [{"title": "A", "child": "a"}]}, ["a"]),
        (
            {
                "id": "root",
                "component": "Button",
                "child": "a",
                "action": {"event": {"name": "go"}},
            },
            ["a"],
        ),
    ],
)
def test_catalog_reference_shapes(tmp_path, component, targets):
    stream = [create(), components(component), components(*(text(target) for target in targets))]
    assert validate_file(capture(tmp_path, stream)).valid
    stream.pop()
    report = validate_file(capture(tmp_path, stream))
    assert report.diagnostics[0].code == "REFERENCE_MISSING"
    assert report.diagnostics[0].path.startswith("/surfaces/s/components/root/")


def test_final_reference_checks_all_components_and_dag(tmp_path):
    root = {"id": "root", "component": "Row", "children": ["a", "b"]}
    a = {"id": "a", "component": "Card", "child": "leaf"}
    b = {"id": "b", "component": "Card", "child": "leaf"}
    stream = [create(), components(root, a, b, text("leaf"))]
    assert validate_file(capture(tmp_path, stream)).valid
    stream += [components({"id": "orphan", "component": "Card", "child": "absent"})]
    assert validate_file(capture(tmp_path, stream)).diagnostics[0].code == "REFERENCE_MISSING"


def test_long_graph_does_not_use_python_recursion():
    items = [
        {"id": "root" if i == 0 else str(i), "component": "Card", "child": str(i + 1)}
        for i in range(1500)
    ]
    snapshot = replay([create(), components(*items, text("1500"))])
    assert len(snapshot["surfaces"]["s"]["components"]) == 1501


def test_cross_surface_reference_is_unresolved(tmp_path):
    stream = [
        create(),
        create("other"),
        components(text("shared"), text(), surface="other"),
        components({"id": "root", "component": "Card", "child": "shared"}),
    ]
    assert validate_file(capture(tmp_path, stream)).diagnostics[0].code == "REFERENCE_MISSING"


def test_component_type_change_and_data_updates_across_surfaces(tmp_path):
    messages = [
        create(),
        create("other"),
        components(text()),
        components(text(), surface="other"),
        message("updateDataModel", value={"old": 1}),
        message("updateDataModel", "other", path="/keep", value=None),
        message("updateDataModel", value={"new": 2}),
        components({"id": "root", "component": "Divider"}),
    ]
    analysis = analyze_file(capture(tmp_path, messages))
    assert analysis.report.valid
    surfaces = analysis.snapshot["surfaces"]
    assert surfaces["s"]["components"]["root"] == {"id": "root", "component": "Divider"}
    assert surfaces["s"]["dataModel"] == {"new": 2}
    assert surfaces["other"]["dataModel"] == {"keep": None}
    assert surfaces["other"]["undefinedDataPaths"] == []


def test_final_diagnostics_sort_by_identity(tmp_path):
    invalid = {"id": "root", "component": "Card", "child": "absent"}
    stream = [
        create("z"),
        components(invalid, surface="z"),
        create("a/~"),
        components(invalid, surface="a/~"),
    ]
    report = validate_file(capture(tmp_path, stream))
    assert report.diagnostics[0].path == "/surfaces/a~1~0/components/root/child"


def test_multi_node_cycle(tmp_path):
    stream = [
        create(),
        components(
            {"id": "root", "component": "Card", "child": "a"},
            {"id": "a", "component": "Card", "child": "root"},
        ),
    ]
    assert validate_file(capture(tmp_path, stream)).diagnostics[0].code == "REFERENCE_CYCLE"


def test_model_escapes_empty_segments_null_and_deletion():
    original = {"items": [1, None, 3], "a/b": {"~x": 0}}
    updated = update_model(original, "/a~1b/~0x", None)
    assert updated["a/b"]["~x"] is None
    assert original["a/b"]["~x"] == 0
    updated = update_model(updated, "/items/1")
    data, undefined = encode_model(updated)
    assert data["items"] == [1, None, 3] and undefined == ["/items/1"]
    updated = update_model(updated, "/a~1b/~0x")
    assert updated["a/b"] == {}
    assert update_model({}, "/a//b", 4) == {"a": {"": {"b": 4}}}
    assert update_model({}, "/~01", True) == {"~1": True}
    assert update_model({}, "/__proto__/safe", 1) == {"__proto__": {"safe": 1}}


@pytest.mark.parametrize("path", ["", "/"])
def test_root_replacement_and_omitted_value(path):
    assert update_model({"a": 1}, path, [1, 2]) == [1, 2]
    assert update_model({"a": 1}, path, None) is None
    assert update_model({"a": 1}, path) == {}


def test_upsert_array_growth_and_absent_deletion():
    root = update_model({}, "/users/2/name", "Ada")
    assert root == {"users": [MISSING, MISSING, {"name": "Ada"}]}
    data, undefined = encode_model(root)
    assert data == {"users": [None, None, {"name": "Ada"}]}
    assert undefined == ["/users/0", "/users/1"]
    assert update_model({}, "/absent/path") == {}
    assert update_model([1], "/100") == [1]
    assert update_model({"a": None}, "/a/0", 2) == {"a": [2]}
    assert update_model(None, "/a", 1) == {"a": 1}
    assert update_model(None, "/absent") is None
    assert update_model(3, "/absent") == 3
    assert update_model({"a": 1}, "/a/absent") == {"a": 1}


@pytest.mark.parametrize(
    "root,path",
    [
        ({}, "relative"),
        ({}, "/bad~2"),
        ({}, "/trailing~"),
        ([], "/-"),
        ([], "/01"),
        ([], "/-1"),
        ([], "/10001"),
        ([], "/9999999999999999999999"),
        (1, "/a"),
        ({"a": 1}, "/a/b"),
        ({}, "/" + "/".join(["a"] * 65)),
    ],
)
def test_bad_model_paths_do_not_mutate(root, path):
    before = copy.deepcopy(root)
    with pytest.raises(InvalidInput, match=".") as error:
        update_model(root, path, 2)
    assert error.value.diagnostic.code == "DATA_PATH"
    assert root == before


def test_model_and_state_limits(monkeypatch):
    monkeypatch.setattr("surface_diff.data_model.MAX_MODEL_NODES", 3)
    with pytest.raises(InvalidInput, match="node/depth"):
        update_model({}, "/a", [1, 2, 3])
    monkeypatch.setattr("surface_diff.data_model.MAX_MODEL_DEPTH", 2)
    with pytest.raises(InvalidInput, match="node/depth"):
        update_model({}, "/", {"a": {"b": {"c": 1}}})
    state = Replay()
    state.apply(create(), 1)
    monkeypatch.setattr("surface_diff.replay.MAX_SURFACES", 1)
    with pytest.raises(InvalidInput, match="surface limit"):
        state.apply(create("other"), 2)
    monkeypatch.setattr("surface_diff.replay.MAX_COMPONENTS", 1)
    with pytest.raises(InvalidInput, match="component limit"):
        state.apply(components(text(), text("a")), 3)
    monkeypatch.setattr("surface_diff.replay.MAX_MODEL_NODES", 1)
    with pytest.raises(InvalidInput, match="Combined"):
        state.apply(message("updateDataModel", value=[1]), 4)
    monkeypatch.setattr("surface_diff.replay.MAX_SURFACES", 2)
    with pytest.raises(InvalidInput, match="Combined"):
        state.apply(create("another"), 5)


def test_stateful_model_error_reports_message_path(tmp_path):
    stream = [create(), components(text()), message("updateDataModel", path="bad", value=1)]
    report = validate_file(capture(tmp_path, stream))
    assert report.diagnostics[0].code == "DATA_PATH"
    assert report.diagnostics[0].line == 3
    assert report.diagnostics[0].path == "/updateDataModel/path"


def test_snapshot_equivalent_streams_and_order_preservation():
    root = {"id": "root", "component": "Row", "children": ["b", "a"]}
    first = [
        create(),
        components(root, text("a"), text("b")),
        message("updateDataModel", value={"b": 2, "a": 1}),
    ]
    second = [
        create(),
        components(text("b")),
        components(text("a"), root),
        message("updateDataModel", value={"a": 1, "b": 2}),
    ]
    assert serialize_snapshot(replay(first)) == serialize_snapshot(replay(second))
    assert replay(first)["surfaces"]["s"]["components"]["root"]["children"] == ["b", "a"]
    assert b"timestamp" not in serialize_snapshot(replay(first))


def test_snapshot_cli_success_no_clobber_and_no_input_changes(tmp_path, capsys):
    source = capture(
        tmp_path,
        [
            create(),
            components(text()),
            message("updateDataModel", value=[None, 1]),
            message("updateDataModel", path="/1"),
        ],
    )
    before = source.read_bytes()
    output = tmp_path / "baseline.json"
    assert main(["snapshot", str(source), "--out", str(output)]) == 0
    saved = output.read_bytes()
    assert json.loads(saved)["surfaces"]["s"]["undefinedDataPaths"] == ["/1"]
    assert saved.endswith(b"\n") and b"\r\n" not in saved
    assert main(["snapshot", str(source), "--out", str(output)]) == 2
    assert "OUTPUT_EXISTS" in capsys.readouterr().err
    assert output.read_bytes() == saved and source.read_bytes() == before
    assert main(["snapshot", str(source), "--out", str(source)]) == 2
    assert source.read_bytes() == before
    assert not list(tmp_path.glob(".surfdiff-*"))


def test_snapshot_invalid_stream_never_writes(tmp_path, capsys):
    path = capture(tmp_path, [create()])
    output = tmp_path / "out.json"
    assert main(["snapshot", str(path), "--out", str(output)]) == 2
    assert not output.exists()
    assert "ROOT_MISSING" in capsys.readouterr().err


def test_snapshot_write_error_and_atomic_publish_failure(tmp_path, monkeypatch, capsys):
    source = capture(tmp_path, [create(), components(text())])
    assert main(["snapshot", str(source), "--out", str(tmp_path / "missing" / "out")]) == 2
    assert "OUTPUT_IO" in capsys.readouterr().err

    def fail(*args):
        raise OSError("No hard-link support")

    monkeypatch.setattr("surface_diff.snapshot.os.link", fail)
    with pytest.raises(InvalidInput, match="hard-link"):
        write_snapshot(tmp_path / "failed", replay([create(), components(text())]))
    assert not (tmp_path / "failed").exists()
    assert not list(tmp_path.glob(".surfdiff-*"))


def test_snapshot_cli_subprocess_deterministic(tmp_path):
    source = capture(tmp_path, [create(), components(text())])
    results = []
    for index in range(2):
        output = tmp_path / f"baseline-{index}.json"
        result = subprocess.run(
            [sys.executable, "-m", "surface_diff", "snapshot", str(source), "--out", str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        results.append(output.read_bytes())
    assert results[0] == results[1]
