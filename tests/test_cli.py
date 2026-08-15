from __future__ import annotations

import json
from pathlib import Path

import pytest

from flowcli.cli import main


def test_path_only_defaults_to_map(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out)]) == 0  # no "map" subcommand
    assert (out / "report.json").is_file()
    assert (out / "graph.html").is_file()


def test_path_plus_file_entry(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "helpers.py", "-o", str(out), "--formats", "json"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sampleproj.helpers (module)"
    assert data["meta"]["module_count"] == 8  # whole package parsed, then scoped
    assert {n["id"] for n in data["nodes"]} == {
        "sampleproj.helpers:fact",
        "sampleproj.helpers:outer",
        "sampleproj.helpers:outer.inner",
        "sampleproj.helpers:ping",
        "sampleproj.helpers:pong",
        "sampleproj.helpers:util_a",
        "sampleproj.helpers:util_b",
    }


def test_path_plus_folder_entry(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "sub", "-o", str(out), "--formats", "json"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sub/ (2 modules)"
    ids = {n["id"] for n in data["nodes"]}
    assert "sampleproj.sub.worker:work" in ids
    # scoped to what that folder reaches — helpers.util_b is called by work(), ping is not
    assert "sampleproj.helpers:util_b" in ids
    assert "sampleproj.helpers:ping" not in ids


def test_multiple_entries_as_arguments(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(
        [
            str(sampleproj_path),
            "app.py:main",
            "helpers.py:ping",
            "-o",
            str(out),
            "--formats",
            "json",
        ]
    )
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"].startswith("2 entries: ")
    ids = {n["id"] for n in data["nodes"]}
    assert {"sampleproj.app:main", "sampleproj.helpers:ping", "sampleproj.helpers:pong"} <= ids
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["sampleproj.app:main"]["depth"] == 0
    assert by_id["sampleproj.helpers:ping"]["depth"] == 0  # both seeds start at 0


def test_multiple_entries_comma_separated(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main([str(sampleproj_path), "app.py:main,helpers.py:ping", "-o", str(out), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert len(data["meta"]["entry_nodes"]) == 2


def test_mixed_entry_kinds(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main([str(sampleproj_path), "sub", "app.py:main", "-o", str(out), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in data["nodes"]}
    assert "sampleproj.sub.worker:work" in ids
    assert "sampleproj.app:main" in ids


def test_path_plus_function_entry(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "app.py:main", "-o", str(out), "--formats", "json"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sampleproj.app:main"


def test_dotted_entry_still_works(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "sampleproj.app:main", "-o", str(out), "--formats", "json"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sampleproj.app:main"


def test_entry_points_suggested_when_no_entry(
    tmp_path: Path, sampleproj_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out), "--formats", "json"]) == 0
    printed = capsys.readouterr().out
    assert "suggested entry points" in printed
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    ids = {e["id"] for e in data["meta"]["entry_points"]}
    assert "sampleproj.app:main" in ids


def test_classes_in_report_by_default(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out), "--formats", "json,md"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    ids = {c["id"] for c in data["classes"]["nodes"]}
    assert {"sampleproj.models:Base", "sampleproj.models:Engine"} <= ids
    assert any(e["kind"] == "inherits" for e in data["classes"]["edges"])
    assert data["meta"]["class_count"] == len(ids)
    assert "## Classes" in (out / "report.md").read_text(encoding="utf-8")


def test_no_classes_flag(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out), "--formats", "json", "--no-classes"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert "classes" not in data
    assert data["meta"]["class_count"] == 0


def test_simulation_on_by_default(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out), "--formats", "json"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["simulated"] is True
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["sampleproj.helpers:fact"]["simulated"]["args"]["n"]["values"] == ["5"]


def test_no_simulate_flag(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main([str(sampleproj_path), "-o", str(out), "--formats", "json", "--no-simulate"]) == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["simulated"] is False
    assert all(n["simulated"] is None for n in data["nodes"])


def test_map_end_to_end(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main(["map", str(sampleproj_path), "-o", str(out)]) == 0
    assert (out / "report.json").is_file()
    assert (out / "report.md").is_file()
    assert (out / "graph.html").is_file()
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["module_count"] == 8
    assert data["meta"]["entry"] is None
    ids = [n["id"] for n in data["nodes"]]
    assert "sampleproj.app:main" in ids
    assert ids == sorted(ids)
    assert all(n["dynamic"] is None for n in data["nodes"])


def test_map_with_entry_scopes_to_call_graph(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path), "sampleproj.app:main", "-o", str(out), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sampleproj.app:main"
    assert data["meta"]["scoped"] is True
    assert data["meta"]["unreachable_count"] > 0
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["sampleproj.app:main"]["depth"] == 0
    assert by_id["sampleproj.helpers:util_a"]["depth"] == 1
    assert "sampleproj.helpers:ping" not in by_id  # outside the entry's call graph -> pruned
    assert all(n["depth"] is not None for n in data["nodes"])


def test_map_module_entry_whole_file(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path), "sampleproj.helpers", "-o", str(out), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["entry"] == "sampleproj.helpers (module)"
    assert len(data["meta"]["entry_nodes"]) == 7
    ids = {n["id"] for n in data["nodes"]}
    assert ids == {
        "sampleproj.helpers:fact",
        "sampleproj.helpers:outer",
        "sampleproj.helpers:outer.inner",
        "sampleproj.helpers:ping",
        "sampleproj.helpers:pong",
        "sampleproj.helpers:util_a",
        "sampleproj.helpers:util_b",
    }


def test_map_entry_depth_limit(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(
        [
            "map",
            str(sampleproj_path),
            "sampleproj.app:<module>",
            "-o",
            str(out),
            "--depth",
            "1",
            "--formats",
            "json",
        ]
    )
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["depth_limit"] == 1
    ids = {n["id"] for n in data["nodes"]}
    assert ids == {"sampleproj.app:<module>", "sampleproj.app:main"}


def test_map_entry_keep_unreachable(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(
        [
            "map",
            str(sampleproj_path),
            "sampleproj.app:main",
            "-o",
            str(out),
            "--keep-unreachable",
            "--formats",
            "json",
        ]
    )
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["scoped"] is False
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["sampleproj.helpers:ping"]["depth"] is None  # kept, depth-annotated as unreachable


def test_map_include_external(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path), "-o", str(out), "--include-external", "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in data["nodes"]}
    assert "os.path.join" in ids


def test_formats_filter(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    assert main(["map", str(sampleproj_path), "-o", str(out), "--formats", "json"]) == 0
    assert (out / "report.json").is_file()
    assert not (out / "report.md").exists()
    assert not (out / "graph.html").exists()


def test_exclude_flag(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path), "-o", str(out), "--exclude", "sub/*", "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in data["nodes"]}
    assert not any(nid.startswith("sampleproj.sub.worker:") for nid in ids)


def test_single_file_map(tmp_path: Path, sampleproj_path: Path) -> None:
    out = tmp_path / "out"
    rc = main(["map", str(sampleproj_path / "helpers.py"), "-o", str(out), "--formats", "json"])
    assert rc == 0
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["module_count"] == 1


def test_bad_path_exit_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["map", str(tmp_path / "nope")]) == 1
    assert "not found" in capsys.readouterr().err


def test_no_python_files_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert main(["map", str(empty), "-o", str(tmp_path / "out")]) == 2


def test_bad_entry_exit_1(tmp_path: Path, sampleproj_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["map", str(sampleproj_path), "sampleproj.app:nope", "-o", str(tmp_path / "out")])
    assert rc == 1
    assert "entry" in capsys.readouterr().err


def test_unknown_format_exit_1(tmp_path: Path, sampleproj_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["map", str(sampleproj_path), "-o", str(tmp_path / "out"), "--formats", "pdf"]) == 1


def test_quiet_suppresses_summary(tmp_path: Path, sampleproj_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["map", str(sampleproj_path), "-o", str(tmp_path / "out"), "-q", "--formats", "json"])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_summary_printed_by_default(tmp_path: Path, sampleproj_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["map", str(sampleproj_path), "-o", str(tmp_path / "out"), "--formats", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "modules" in out
    assert "wrote json" in out


def test_syntax_error_file_skipped_with_warning(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "good.py").write_text("def f():\n    pass\n", encoding="utf-8")
    (tmp_path / "bad.py").write_text("def (\n", encoding="utf-8")
    out = tmp_path / "out"
    assert main(["map", str(tmp_path), "-o", str(out), "--formats", "json", "-q"]) == 0
    assert "skipping" in capsys.readouterr().err
    data = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert len(data["meta"]["skipped_files"]) == 1


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert "flowcli" in capsys.readouterr().out
