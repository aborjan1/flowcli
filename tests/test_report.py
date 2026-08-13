from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flowcli.graph import Graph, compute_depths
from flowcli.report import write_json, write_markdown


def fixed_meta(graph: Graph, **overrides: Any) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "tool": "flowcli",
        "version": "0.1.0",
        "schema_version": 1,
        "root": "/tmp/fixed",
        "generated_at": "2026-08-12T00:00:00+00:00",
        "module_count": 8,
        "node_count": len(graph.nodes),
        "edge_count": sum(len(n.calls) for n in graph.nodes.values()),
        "entry": None,
        "unreachable_count": 0,
        "include_external": False,
        "skipped_files": [],
        "unresolved_count": len(graph.unresolved),
    }
    meta.update(overrides)
    return meta


def test_json_schema(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    write_json(sample_graph, fixed_meta(sample_graph), out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(data) == {"meta", "nodes", "unresolved"}
    for key in ("tool", "version", "schema_version", "root", "generated_at", "module_count", "entry"):
        assert key in data["meta"]
    ids = [n["id"] for n in data["nodes"]]
    assert ids == sorted(ids)
    assert all(n["dynamic"] is None for n in data["nodes"])
    node_keys = set(data["nodes"][0])
    assert {"id", "file", "lineno", "calls", "called_by", "depth", "static_call_count", "dynamic", "kind"} <= node_keys
    assert all({"caller", "callee_expr", "lineno", "reason"} == set(u) for u in data["unresolved"])


def test_json_deterministic(sample_graph: Graph, tmp_path: Path) -> None:
    meta = fixed_meta(sample_graph)
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    write_json(sample_graph, meta, a)
    write_json(sample_graph, meta, b)
    assert a.read_bytes() == b.read_bytes()


def test_md_sorted_by_out_degree(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    write_markdown(sample_graph, fixed_meta(sample_graph), out)
    lines = out.read_text(encoding="utf-8").splitlines()
    header_idx = lines.index("| Node | Kind | File:Line | Out | In | Depth |")
    first_row = lines[header_idx + 2]
    expected = max(sample_graph.nodes.values(), key=lambda n: (len(n.calls), len(n.called_by)))
    assert f"`{expected.id}`" in first_row


def test_md_unreachable_section_only_with_entry(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    write_markdown(sample_graph, fixed_meta(sample_graph), out)
    assert "Unreachable" not in out.read_text(encoding="utf-8")

    unreachable = compute_depths(sample_graph, "sampleproj.app:main")
    meta = fixed_meta(sample_graph, entry="sampleproj.app:main", unreachable_count=unreachable)
    write_markdown(sample_graph, meta, out)
    text = out.read_text(encoding="utf-8")
    assert "## Unreachable from `sampleproj.app:main`" in text
    assert "`sampleproj.helpers:ping`" in text


def test_md_signatures_section(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    write_markdown(sample_graph, fixed_meta(sample_graph), out)
    text = out.read_text(encoding="utf-8")
    assert "## Signatures" in text
    assert "| `sampleproj.helpers:fact` | `(n)` | `~int` | — |" in text


def test_summary_runtime_line(sample_graph: Graph, capsys) -> None:
    from flowcli.report import print_summary

    meta = fixed_meta(sample_graph, has_runtime=True, runtime_matched=3, runtime_total=5)
    print_summary(sample_graph, meta)
    assert "runtime: 3/5 functions observed" in capsys.readouterr().out


def test_md_unresolved_sections(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    write_markdown(sample_graph, fixed_meta(sample_graph), out)
    text = out.read_text(encoding="utf-8")
    assert "## Unresolved calls" in text
    assert "**external**" in text
    assert "`os.path.join`" in text
