from __future__ import annotations

import json
from pathlib import Path

import pytest

from flowcli.cli import main

SCRIPT = (
    "def helper(n):\n"
    "    return n + 1\n"
    "\n"
    "def main():\n"
    "    total = 0\n"
    "    for i in range(3):\n"
    "        total += helper(i)\n"
    "    return total\n"
    "\n"
    "main()\n"
)


def write_script(tmp_path: Path, name: str = "prog.py", body: str = SCRIPT) -> Path:
    script = tmp_path / name
    script.write_text(body, encoding="utf-8")
    return script


def test_run_script_end_to_end(tmp_path: Path) -> None:
    script = write_script(tmp_path)
    out = tmp_path / "out"
    assert main(["run", "--no-map", "-o", str(out), str(script)]) == 0
    data = json.loads((out / "runtime.json").read_text(encoding="utf-8"))
    assert data["meta"]["mode"] == "script"
    assert data["meta"]["exit"] == 0
    fns = data["functions"]
    assert list(fns) == sorted(fns)
    assert fns["prog:helper"]["ncalls"] == 3
    assert fns["prog:helper"]["args"]["n"] == ["int"]
    assert fns["prog:helper"]["returns"] == ["int"]
    assert "prog:<module>" in fns
    assert ["prog:main", "prog:helper"] in data["events"]


def test_run_passes_argv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    script = write_script(tmp_path, "argv_prog.py", "import sys\nprint('ARGS:' + ','.join(sys.argv[1:]))\n")
    out = tmp_path / "out"
    assert main(["run", "-q", "--no-map", "-o", str(out), str(script), "alpha", "beta"]) == 0
    assert "ARGS:alpha,beta" in capsys.readouterr().out


def test_run_dash_m_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "mod_run.py").write_text("def go():\n    return 5\n\ngo()\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "out"
    assert main(["run", "--no-map", "-o", str(out), "--", "-m", "mod_run"]) == 0
    data = json.loads((out / "runtime.json").read_text(encoding="utf-8"))
    assert data["meta"]["mode"] == "module"
    assert "mod_run:go" in data["functions"]


def test_run_no_samples(tmp_path: Path) -> None:
    script = write_script(tmp_path)
    out = tmp_path / "out"
    assert main(["run", "--no-samples", "--no-map", "-o", str(out), str(script)]) == 0
    data = json.loads((out / "runtime.json").read_text(encoding="utf-8"))
    assert all(rec["samples"] == [] for rec in data["functions"].values())


def test_run_crashing_script_still_writes_runtime(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    script = write_script(tmp_path, "boom.py", "def f():\n    raise ValueError('boom')\n\nf()\n")
    out = tmp_path / "out"
    assert main(["run", "--no-map", "-o", str(out), str(script)]) == 1
    data = json.loads((out / "runtime.json").read_text(encoding="utf-8"))
    assert data["meta"]["exit"] == 1
    assert "boom:f" in data["functions"]
    assert "ValueError" in capsys.readouterr().err


def test_run_maps_by_default(tmp_path: Path) -> None:
    script = write_script(tmp_path)
    out = tmp_path / "out"
    assert main(["run", "-o", str(out), str(script)]) == 0
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["meta"]["has_runtime"] is True
    by_id = {n["id"]: n for n in report["nodes"]}
    assert by_id["prog:helper"]["dynamic"]["ncalls"] == 3
    assert by_id["prog:helper"]["signature"]["params"][0]["name"] == "n"


def test_run_no_map_only_writes_runtime(tmp_path: Path) -> None:
    script = write_script(tmp_path)
    out = tmp_path / "out"
    assert main(["run", "--no-map", "-o", str(out), str(script)]) == 0
    assert (out / "runtime.json").is_file()
    assert not (out / "report.json").exists()


def test_run_missing_target_exit_1(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["run"]) == 1
    assert "no program" in capsys.readouterr().err


def test_map_runtime_merge_counts(tmp_path: Path, sampleproj_path: Path) -> None:
    runtime = tmp_path / "runtime.json"
    runtime.write_text(
        json.dumps(
            {
                "meta": {},
                "functions": {
                    "sampleproj.helpers:util_b": {"ncalls": 4, "args": {}, "returns": ["int"], "samples": []},
                    "nosuch:fn": {"ncalls": 1, "args": {}, "returns": [], "samples": []},
                },
                "events": [],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path), "-o", str(out), "--runtime", str(runtime), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["runtime_total"] == 2
    assert data["meta"]["runtime_matched"] == 1
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["sampleproj.helpers:util_b"]["dynamic"]["ncalls"] == 4


def test_map_runtime_missing_file_exit_1(tmp_path: Path, sampleproj_path: Path) -> None:
    rc = main(["map", str(sampleproj_path), "-o", str(tmp_path / "o"), "--runtime", str(tmp_path / "nope.json")])
    assert rc == 1


def test_runtime_json_deterministic(tmp_path: Path) -> None:
    script = write_script(tmp_path)
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    assert main(["run", "-q", "--no-map", "-o", str(out_a), str(script)]) == 0
    assert main(["run", "-q", "--no-map", "-o", str(out_b), str(script)]) == 0
    data_a = json.loads((out_a / "runtime.json").read_text(encoding="utf-8"))
    data_b = json.loads((out_b / "runtime.json").read_text(encoding="utf-8"))
    data_a["meta"].pop("generated_at")
    data_b["meta"].pop("generated_at")
    assert data_a == data_b
