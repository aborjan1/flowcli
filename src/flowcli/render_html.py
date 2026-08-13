"""Embed the merged graph into the self-contained interactive HTML page."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from flowcli.classes import ClassGraph
from flowcli.graph import Graph
from flowcli.models import Node
from flowcli.template_html import TEMPLATE

EXTERNAL_MODULE = "(external)"
LARGE_GRAPH_WARNING = 3000  # O(n^2) repulsion gets sluggish beyond this


def _module_of(node_id: str) -> str:
    return node_id.split(":", 1)[0] if ":" in node_id else EXTERNAL_MODULE


def _node_entry(n: Node, module_index: int) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": n.id,
        "m": module_index,
        "in": len(n.called_by),
        "out": len(n.calls),
        "file": n.file,
        "line": n.lineno,
        "depth": n.depth,
        "kind": n.kind,
        "flow": n.flow,
    }
    if n.signature is not None:
        entry["sig"] = {
            "p": [[p["name"], p.get("ann")] for p in n.signature["params"]],
            "r": n.signature["returns"],
            "inf": n.signature["inferred"],
        }
    if n.dynamic is not None:
        entry["dyn"] = {
            "n": n.dynamic.get("ncalls", 0),
            "a": n.dynamic.get("args", {}),
            "r": n.dynamic.get("returns", []),
            "s": n.dynamic.get("samples", []),
        }
    if n.simulated is not None:
        entry["sim"] = {
            "n": n.simulated.get("sites", 0),
            "a": {
                name: {"t": slot["types"], "v": slot["values"]}
                for name, slot in n.simulated.get("args", {}).items()
                if slot["types"] or slot["values"]
            },
        }
    return entry


def build_payload(graph: Graph, meta: dict[str, Any], runtime: dict[str, Any] | None = None) -> dict[str, Any]:
    ids = list(graph.nodes)  # already sorted
    idx = {nid: i for i, nid in enumerate(ids)}
    modules = sorted({_module_of(nid) for nid in ids})
    mod_idx = {m: i for i, m in enumerate(modules)}

    nodes = [_node_entry(graph.nodes[nid], mod_idx[_module_of(nid)]) for nid in ids]
    links = []
    for nid in ids:
        n = graph.nodes[nid]
        for callee, count in n.static_call_count.items():
            if callee in idx:
                links.append({"s": idx[nid], "t": idx[callee], "c": count})

    events = []
    if runtime:
        for pair in runtime.get("events", []):
            if len(pair) == 2 and pair[0] in idx and pair[1] in idx:
                events.append([idx[pair[0]], idx[pair[1]]])

    return {
        "meta": {
            "tool": meta.get("tool", "flowcli"),
            "root": meta.get("root", ""),
            "entry": meta.get("entry"),
            "entry_nodes": meta.get("entry_nodes", []),
            "has_runtime": bool(meta.get("has_runtime")),
            "entry_points": [
                {"id": e["id"], "kind": e["kind"], "why": e["why"]}
                for e in meta.get("entry_points", [])
                if e["id"] in idx
            ],
        },
        "modules": modules,
        "nodes": nodes,
        "links": links,
        "events": events,
    }


def _class_payload(class_graph: ClassGraph | None) -> dict[str, Any]:
    if class_graph is None or not class_graph.nodes:
        return {"nodes": [], "links": []}
    ids = sorted(class_graph.nodes)
    idx = {nid: i for i, nid in enumerate(ids)}
    nodes = []
    for nid in ids:
        n = class_graph.nodes[nid]
        nodes.append(
            {
                "id": n.id,
                "m": n.module,
                "name": n.name,
                "st": n.stereotype,
                "file": n.file,
                "line": n.lineno,
                "bases": n.bases,
                "ext": [
                    [name, idx.get(ref, -1) if ref else -1]
                    for name, ref in zip(n.bases, n.base_refs + [None] * len(n.bases))
                ],
                "f": [[f["name"], f["type"], idx.get(f["ref"], -1), f["value"]] for f in n.fields],
                "meth": [[m["name"], m["id"]] for m in n.methods],
            }
        )
    links = [
        {"s": idx[e.source], "t": idx[e.target], "k": e.kind, "l": e.label}
        for e in class_graph.edges
        if e.source in idx and e.target in idx
    ]
    return {"nodes": nodes, "links": links}


def render_html(
    graph: Graph,
    meta: dict[str, Any],
    out: Path,
    runtime: dict[str, Any] | None = None,
    class_graph: ClassGraph | None = None,
) -> None:
    if len(graph.nodes) > LARGE_GRAPH_WARNING:
        print(
            f"flowcli: warning: {len(graph.nodes)} nodes — the force layout may be slow above "
            f"{LARGE_GRAPH_WARNING}; consider --exclude to trim the graph",
            file=sys.stderr,
        )
    payload = build_payload(graph, meta, runtime)
    payload["classes"] = _class_payload(class_graph)
    # "</" -> "<\/" keeps any embedded string safe inside the <script> element and is valid JSON.
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    out.write_text(TEMPLATE.replace("__FLOWCLI_DATA__", data), encoding="utf-8")
