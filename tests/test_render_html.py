from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from flowcli.graph import Graph, apply_runtime
from flowcli.models import Node
from flowcli.render_html import build_payload, render_html

DATA_RE = re.compile(r'<script id="flowcli-data" type="application/json">(.*?)</script>', re.S)


def extract_payload(html: str) -> dict[str, Any]:
    match = DATA_RE.search(html)
    assert match, "embedded data script not found"
    return json.loads(match.group(1))


def test_payload_roundtrip(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {"root": "x"}, out)
    payload = extract_payload(out.read_text(encoding="utf-8"))
    assert len(payload["nodes"]) == len(sample_graph.nodes)
    assert len(payload["links"]) == sum(len(n.calls) for n in sample_graph.nodes.values())
    count = len(payload["nodes"])
    for link in payload["links"]:
        assert 0 <= link["s"] < count
        assert 0 <= link["t"] < count
        assert link["c"] >= 1


def test_payload_modules_and_degrees(sample_graph: Graph) -> None:
    payload = build_payload(sample_graph, {})
    assert "sampleproj.helpers" in payload["modules"]
    by_id = {n["id"]: n for n in payload["nodes"]}
    util_b = by_id["sampleproj.helpers:util_b"]
    assert util_b["in"] == len(sample_graph.nodes["sampleproj.helpers:util_b"].called_by)
    assert payload["modules"][util_b["m"]] == "sampleproj.helpers"


def test_explore_mode_controls_present(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    html = out.read_text(encoding="utf-8")
    assert "Expand all" in html
    assert "Collapse all" in html
    assert "expandModule" in html
    assert "revealCallees" in html
    assert 'id="panel"' in html
    assert "renderFlow" in html
    assert "__FLOWCLI_DATA__" not in html


def test_boot_reveals_nothing(sample_graph: Graph, tmp_path: Path) -> None:
    """entry_nodes is a scope, not an anchor — a directory entry seeds it with the whole package."""
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    html = out.read_text(encoding="utf-8")
    assert "data.meta.entry_nodes" not in html  # nothing is surfaced before the first click
    assert "function ensureVisible" in html
    assert "function revealCallees" in html


def test_payload_includes_flow(sample_graph: Graph) -> None:
    payload = build_payload(sample_graph, {})
    by_id = {n["id"]: n for n in payload["nodes"]}
    flow = by_id["sampleproj.helpers:fact"]["flow"]
    assert flow[0]["t"] == "if"
    assert by_id["sampleproj.helpers:util_a"]["flow"][0]["calls"] == ["sampleproj.helpers:util_b"]


def test_payload_sig_dyn_and_events(sample_graph: Graph) -> None:
    runtime = {
        "functions": {
            "sampleproj.helpers:util_a": {"ncalls": 2, "args": {}, "returns": ["int"], "samples": []},
        },
        "events": [
            ["sampleproj.helpers:util_a", "sampleproj.helpers:util_b"],
            ["bogus:x", "bogus:y"],
        ],
    }
    apply_runtime(sample_graph, runtime)
    payload = build_payload(sample_graph, {"has_runtime": True}, runtime)
    by_id = {n["id"]: n for n in payload["nodes"]}
    fact = by_id["sampleproj.helpers:fact"]
    assert fact["sig"] == {"p": [["n", None]], "r": ["int"], "inf": True}
    assert "sig" not in by_id["sampleproj.app:<module>"]
    util_a = by_id["sampleproj.helpers:util_a"]
    assert util_a["dyn"]["n"] == 2
    assert "dyn" not in fact
    ids = [n["id"] for n in payload["nodes"]]
    assert payload["events"] == [[ids.index("sampleproj.helpers:util_a"), ids.index("sampleproj.helpers:util_b")]]
    assert payload["meta"]["has_runtime"] is True


def test_template_v2_markers(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    html = out.read_text(encoding="utf-8")
    for marker in (
        "fmarch",
        "prefers-reduced-motion",
        "enterFocus",
        "layoutLayers",
        "legend-restore",
        "measureHeader",
        "Top-down",
        "recomputeFocus",
        "st-play",
        "applyStep",
        "roundRect",
        "drawEdge",
        "Entry points",
        "topbar",
        "rebuildTrail",
        "TRAIL_ALPHA",
        "st-hist",
        "prettyId",
        "drawClass",
        "measureClass",
        "vtab",
        "clickClassRow",
        "buildClassTree",
        "renderClassPanel",
        "data-ckey",
        "clipText",
    ):
        assert marker in html, marker


def test_class_payload_embedded(sample_index, tmp_path: Path) -> None:
    from flowcli.classes import build_class_graph
    from flowcli.graph import build_graph
    from flowcli.resolver import resolve_all

    graph = build_graph(sample_index, resolve_all(sample_index))
    out = tmp_path / "graph.html"
    render_html(graph, {}, out, class_graph=build_class_graph(sample_index))
    payload = extract_payload(out.read_text(encoding="utf-8"))
    ids = [c["id"] for c in payload["classes"]["nodes"]]
    assert "sampleproj.models:Engine" in ids
    engine = payload["classes"]["nodes"][ids.index("sampleproj.models:Engine")]
    assert engine["bases"] == ["Base"]
    assert engine["ext"] == [["Base", ids.index("sampleproj.models:Base")]]  # expandable inline
    assert any(link["k"] == "inherits" for link in payload["classes"]["links"])


def test_class_payload_empty_without_graph(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    payload = extract_payload(out.read_text(encoding="utf-8"))
    assert payload["classes"] == {"nodes": [], "links": []}


def test_palette_is_fixed_not_generated(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    html = out.read_text(encoding="utf-8")
    assert "#3987e5" in html  # documented categorical slot 1
    assert "137.508" not in html  # no golden-angle hue generation


def test_entry_points_reach_payload(sample_graph: Graph) -> None:
    meta = {
        "entry_points": [
            {"id": "sampleproj.app:main", "kind": "main", "why": "named main()"},
            {"id": "gone:x", "kind": "root", "why": "pruned"},
        ]
    }
    payload = build_payload(sample_graph, meta)
    assert payload["meta"]["entry_points"] == [{"id": "sampleproj.app:main", "kind": "main", "why": "named main()"}]


def test_payload_carries_simulation(sample_index, tmp_path: Path) -> None:
    from flowcli.graph import apply_simulation, build_graph
    from flowcli.resolver import resolve_all

    resolved = resolve_all(sample_index)
    graph = build_graph(sample_index, resolved)
    events = apply_simulation(graph, sample_index, resolved, ["sampleproj.app:main"])
    payload = build_payload(graph, {}, {"events": events})
    by_id = {n["id"]: n for n in payload["nodes"]}
    assert by_id["sampleproj.helpers:fact"]["sim"]["a"]["n"]["v"] == ["5"]
    assert payload["events"]  # simulated call order drives replay without any runtime data


def test_no_network_references(sample_graph: Graph, tmp_path: Path) -> None:
    out = tmp_path / "graph.html"
    render_html(sample_graph, {}, out)
    html = out.read_text(encoding="utf-8")
    assert "http://" not in html
    assert "https://" not in html


def test_script_close_escaped(tmp_path: Path) -> None:
    node = Node(id="m:f", file="weird</script>.py", lineno=1)
    graph = Graph(nodes={"m:f": node})
    out = tmp_path / "graph.html"
    render_html(graph, {}, out)
    html = out.read_text(encoding="utf-8")
    payload = extract_payload(html)  # would fail if the literal </script> broke the element
    assert payload["nodes"][0]["file"] == "weird</script>.py"
