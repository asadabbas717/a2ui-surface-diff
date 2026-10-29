"""A correctness-first workload observation, not a benchmark or speed guarantee."""

import json
import tempfile
import time
from pathlib import Path

from surface_diff.analysis import analyze_file
from surface_diff.comparison import check_file
from surface_diff.snapshot import write_snapshot
from surface_diff.validation import BASIC_CATALOGS


def main() -> None:
    if not __debug__:
        raise RuntimeError(
            "Sanity verification requires assertions; run without -O/PYTHONOPTIMIZE."
        )
    root = Path(__file__).resolve().parents[1] / ".tmp"
    root.mkdir(exist_ok=True)
    timings: dict[str, float | int] = {"components": 251, "data_rows": 1000, "point_updates": 25}
    with tempfile.TemporaryDirectory(dir=root, prefix="performance-") as directory:
        work = Path(directory).resolve()
        assert work.is_relative_to(root.resolve()) and work != root.resolve()
        capture, baseline = work / "capture.jsonl", work / "baseline.json"
        components = [
            {"id": "root", "component": "Column", "children": [f"t{i}" for i in range(250)]}
        ]
        components.extend(
            {"id": f"t{i}", "component": "Text", "text": f"Item {i}"} for i in range(250)
        )
        messages = [
            {
                "version": "v0.9.1",
                "createSurface": {"surfaceId": "s", "catalogId": sorted(BASIC_CATALOGS)[0]},
            },
            {"version": "v0.9.1", "updateComponents": {"surfaceId": "s", "components": components}},
            {
                "version": "v0.9.1",
                "updateDataModel": {
                    "surfaceId": "s",
                    "value": {"rows": [{"name": str(i)} for i in range(1000)]},
                },
            },
        ]
        messages.extend(
            {
                "version": "v0.9.1",
                "updateDataModel": {
                    "surfaceId": "s",
                    "path": f"/rows/{i}/name",
                    "value": f"updated-{i}",
                },
            }
            for i in range(25)
        )
        capture.write_text("\n".join(json.dumps(item) for item in messages), encoding="utf-8")
        start = time.perf_counter()
        analysis = analyze_file(capture)
        assert analysis.report.valid and analysis.snapshot is not None
        timings["replay_seconds"] = round(time.perf_counter() - start, 4)
        write_snapshot(baseline, analysis.snapshot)
        start = time.perf_counter()
        assert check_file(capture, baseline).exit_code == 0
        timings["equal_check_seconds"] = round(time.perf_counter() - start, 4)
        with capture.open("a", encoding="utf-8") as stream:
            stream.write(
                "\n"
                + json.dumps(
                    {
                        "version": "v0.9.1",
                        "updateDataModel": {
                            "surfaceId": "s",
                            "path": "/rows/12/name",
                            "value": "changed",
                        },
                    }
                )
            )
        start = time.perf_counter()
        result = check_file(capture, baseline)
        assert result.exit_code == 1 and len(result.changes) == 1
        assert result.changes[0].path == "/surfaces/s/dataModel/rows/12/name"
        timings["changed_check_seconds"] = round(time.perf_counter() - start, 4)
        timings["capture_bytes"] = capture.stat().st_size
        timings["snapshot_bytes"] = baseline.stat().st_size
    print(json.dumps(timings, sort_keys=True))


if __name__ == "__main__":
    main()
