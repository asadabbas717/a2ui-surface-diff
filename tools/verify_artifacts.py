"""Rebuild and install each local artifact in fresh, offline environments."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import contextlib, hashlib, importlib.metadata, io, json, pathlib, socket, sys
from importlib.resources import files
def denied(*args, **kwargs):
    raise AssertionError("normal CLI attempted network access")
socket.socket = socket.create_connection = socket.getaddrinfo = denied
import surface_diff
from surface_diff.cli import main
package_path = pathlib.Path(surface_diff.__file__).resolve()
assert package_path.is_relative_to(pathlib.Path(sys.prefix).resolve())
assert surface_diff.__version__ == importlib.metadata.version("a2ui-surface-diff") == "0.1.0"
assets = files("surface_diff").joinpath("schemas")
for name, digest in json.loads(assets.joinpath("SHA256SUMS.json").read_text()).items():
    assert hashlib.sha256(assets.joinpath(name).read_bytes()).hexdigest() == digest
for name in ("snapshot-v1.json", "check-report-v1.json"):
    assert assets.joinpath(name).is_file()
base = pathlib.Path("baseline.json")
source = pathlib.Path("before.jsonl")
after = pathlib.Path("after.jsonl")
catalog = "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
create = {"version":"v0.9.1","createSurface":{"surfaceId":"s","catalogId":catalog}}
update = {"version":"v0.9.1","updateComponents":{
    "surfaceId":"s","components":[{"id":"root","component":"Text","text":"Hello"}]}}
source.write_text(json.dumps(create)+"\n"+json.dumps(update), encoding="utf-8")
update["updateComponents"]["components"][0]["text"] = "Changed"
after.write_text(json.dumps(create)+"\n"+json.dumps(update), encoding="utf-8")
bad = pathlib.Path("invalid.jsonl")
bad.write_text("{", encoding="utf-8")
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    assert main(["validate",str(source)]) == 0
    assert main(["snapshot",str(source),"--out",str(base)]) == 0
    original = base.read_bytes()
    assert main(["check",str(source),"--baseline",str(base),"--format","json"]) == 0
    assert main(["check",str(after),"--baseline",str(base),"--format","json"]) == 1
    assert main(["check",str(bad),"--baseline",str(base),"--format","json"]) == 2
    assert main(["snapshot",str(source),"--out",str(base)]) == 2
assert base.read_bytes() == original
print("installed package, schemas, offline CLI and exits 0/1/2: PASS")
"""


def run(command: list[str], cwd: Path) -> str:
    environment = {**os.environ, "PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
    result = subprocess.run(
        command, cwd=cwd, env=environment, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command!r}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    if not __debug__:
        raise RuntimeError(
            "Artifact verification requires assertions; run without -O/PYTHONOPTIMIZE."
        )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, default=ROOT / ".tmp")
    args = parser.parse_args()
    artifacts = [args.wheel.resolve(), args.sdist.resolve()]
    wheelhouse = args.wheelhouse.resolve()
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    evidence: dict[str, str] = {}
    with tempfile.TemporaryDirectory(dir=work, prefix="artifact-check-") as directory:
        temporary = Path(directory).resolve()
        assert temporary.is_relative_to(work) and temporary != work
        rebuilt = temporary / "rebuilt"
        run([sys.executable, "-m", "build", "--no-isolation", "--outdir", str(rebuilt)], ROOT)
        for index, artifact in enumerate(artifacts):
            if digest(artifact) != digest(rebuilt / artifact.name):
                raise RuntimeError(f"Repeated build differs: {artifact.name}")
            environment = temporary / f"env-{index}"
            venv.EnvBuilder(with_pip=True).create(environment)
            scripts = environment / ("Scripts" if os.name == "nt" else "bin")
            python = scripts / ("python.exe" if os.name == "nt" else "python")
            common = [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--find-links",
                str(wheelhouse),
            ]
            run(
                [*common, "--require-hashes", "-r", str(ROOT / "requirements-runtime.lock")],
                temporary,
            )
            if artifact.name.endswith(".tar.gz"):
                run(
                    [*common, "--require-hashes", "-r", str(ROOT / "requirements-build.lock")],
                    temporary,
                )
            run(
                [*common, "--no-deps", "--no-build-isolation", "--no-cache-dir", str(artifact)],
                temporary,
            )
            run([str(python), "-m", "pip", "check"], temporary)
            probe = temporary / f"probe-{index}"
            probe.mkdir()
            run([str(python), "-c", PROBE], probe)
            command = scripts / ("surfdiff.exe" if os.name == "nt" else "surfdiff")
            if run([str(command), "--version"], probe).strip() != "surfdiff 0.1.0":
                raise RuntimeError("Installed entrypoint version mismatch")
            evidence[artifact.name] = digest(artifact)
    manifest = "".join(f"{checksum}  {name}\n" for name, checksum in sorted(evidence.items()))
    (artifacts[0].parent / "SHA256SUMS").write_text(manifest, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {"status": "passed", "repeated_builds": "identical", "sha256": evidence}, sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
