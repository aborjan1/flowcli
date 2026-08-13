"""Report emitters: report.json, report.md, and the terminal summary."""

from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from flowcli.classes import ClassGraph
from flowcli.graph import Graph
from flowcli.models import Node


def write_json(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph | None = None) -> None:
    payload: dict[str, Any] = {
        "meta": meta,
        "nodes": [asdict(node) for node in graph.nodes.values()],
        "unresolved": [asdict(u) for u in graph.unresolved],
    }
    if class_graph is not None:
        payload["classes"] = {
            "nodes": [asdict(n) for n in class_graph.nodes.values()],
            "edges": [asdict(e) for e in class_graph.edges],
        }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _loc(node: Node, root: str) -> str:
    if not node.file:
        return "—"
    try:
        rel = os.path.relpath(node.file, root)
    except ValueError:
        rel = node.file
    return f"{rel}:{node.lineno}"


def _by_out_degree(graph: Graph) -> list[Node]:
    return sorted(graph.nodes.values(), key=lambda n: (-len(n.calls), -len(n.called_by), n.id))


def write_markdown(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph | None = None) -> None:
    root = str(meta.get("root", ""))
    lines: list[str] = ["# flowcli report", ""]
    summary = (
        f"**{meta['module_count']}** modules · **{meta['node_count']}** nodes · "
        f"**{meta['edge_count']}** edges · **{meta['unresolved_count']}** unresolved calls"
    )
    if meta.get("entry"):
        summary += f" · entry `{meta['entry']}` ({meta['unreachable_count']} unreachable)"
    lines += [summary, "", "## Call graph", ""]

    lines += ["| Node | Kind | File:Line | Out | In | Depth |", "|---|---|---|---:|---:|---:|"]
    for node in _by_out_degree(graph):
        depth = "—" if node.depth is None else str(node.depth)
        lines.append(
            f"| `{node.id}` | {node.kind} | {_loc(node, root)} | {len(node.calls)} | {len(node.called_by)} | {depth} |"
        )

    lines += _most_called_section(graph)
    lines += _unreachable_section(graph, meta)
    lines += _signatures_section(graph)
    lines += _classes_section(class_graph)
    lines += _unresolved_section(graph)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _classes_section(class_graph: ClassGraph | None) -> list[str]:
    if class_graph is None or not class_graph.nodes:
        return []
    has_edges: dict[str, list[str]] = {}
    for edge in class_graph.edges:
        if edge.kind == "has":
            has_edges.setdefault(edge.source, []).append(f"{edge.label} → {edge.target.split(':', 1)[1]}")
    lines = ["", "## Classes", "", "| Class | Kind | Inherits | Properties | Holds |", "|---|---|---|---|---|"]
    for nid in sorted(class_graph.nodes):
        node = class_graph.nodes[nid]
        props = ", ".join(
            f"{f['name']}: {f['type']}" if f["type"] else f["name"] for f in node.fields[:6]
        ) or "—"
        if len(node.fields) > 6:
            props += f", … +{len(node.fields) - 6}"
        lines.append(
            f"| `{nid}` | {node.stereotype or 'class'} | {_cell(', '.join(node.bases)) or '—'} "
            f"| {_cell(props)} | {_cell(', '.join(has_edges.get(nid, []))) or '—'} |"
        )
    return lines


def _most_called_section(graph: Graph) -> list[str]:
    most_called = sorted(
        (n for n in graph.nodes.values() if n.called_by), key=lambda n: (-len(n.called_by), n.id)
    )[:10]
    if not most_called:
        return []
    lines = ["", "## Top 10 most-called", "", "| Node | In | Called by |", "|---|---:|---|"]
    for node in most_called:
        callers = ", ".join(f"`{c}`" for c in node.called_by[:5])
        if len(node.called_by) > 5:
            callers += f", … +{len(node.called_by) - 5}"
        lines.append(f"| `{node.id}` | {len(node.called_by)} | {callers} |")
    return lines


def _unreachable_section(graph: Graph, meta: dict[str, Any]) -> list[str]:
    if not meta.get("entry"):
        return []
    lines = ["", f"## Unreachable from `{meta['entry']}`", ""]
    if meta.get("scoped"):
        lines.append(
            f"_{meta['unreachable_count']} function(s) outside this call graph were pruned from the report "
            "(rerun with --keep-unreachable to include them)._"
        )
        return lines
    unreachable = [n.id for n in graph.nodes.values() if n.depth is None]
    lines += [f"- `{nid}`" for nid in unreachable] if unreachable else ["_None — every node is reachable._"]
    return lines


def _signatures_section(graph: Graph) -> list[str]:
    sig_nodes = [n for n in graph.nodes.values() if n.signature is not None]
    if not sig_nodes:
        return []
    lines = ["", "## Signatures", "", "| Node | Signature | Returns | Data flow |", "|---|---|---|---|"]
    for node in sig_nodes:
        lines.append(f"| `{node.id}` | `({_params_str(node)})` | `{_returns_str(node)}` | {_runtime_str(node)} |")
    return lines


def _unresolved_section(graph: Graph) -> list[str]:
    if not graph.unresolved:
        return []
    reasons = Counter(u.reason for u in graph.unresolved)
    lines = ["", "## Unresolved calls", ""]
    lines += [f"- **{reason}**: {count}" for reason, count in reasons.most_common()]
    top = Counter(u.callee_expr for u in graph.unresolved).most_common(15)
    lines += ["", "| Callee expression | Occurrences |", "|---|---:|"]
    lines += [f"| `{expr}` | {count} |" for expr, count in top]
    return lines


def _cell(text: str) -> str:
    return text.replace("|", "/")  # pipes break Markdown table cells even inside code spans


def _params_str(node: Node) -> str:
    sig = node.signature or {}
    parts = []
    for p in sig.get("params", []):
        item = p["name"]
        if p.get("ann"):
            item += f": {p['ann']}"
        if p.get("default"):
            item += f"={p['default']}"
        parts.append(item)
    return _cell(", ".join(parts))


def _returns_str(node: Node) -> str:
    sig = node.signature or {}
    returns = sig.get("returns", [])
    if not returns:
        return "?"
    text = _cell(", ".join(returns))
    return f"~{text}" if sig.get("inferred") else text


def _runtime_str(node: Node) -> str:
    if node.dynamic:
        observed = ", ".join(node.dynamic.get("returns", [])) or "?"
        return _cell(f"{node.dynamic.get('ncalls', 0)}× observed · {observed}")
    if node.simulated:
        bits = []
        for name, slot in node.simulated.get("args", {}).items():
            if slot["values"]:
                bits.append(f"{name}={'/'.join(slot['values'][:2])}")
            elif slot["types"]:
                bits.append(f"{name}:{slot['types'][0]}")
        sites = node.simulated.get("sites", 0)
        detail = ", ".join(bits[:3]) if bits else "no args"
        return _cell(f"~{sites} site(s) · {detail}")
    return "—"


def print_summary(graph: Graph, meta: dict[str, Any]) -> None:
    print(
        f"flowcli: {meta['module_count']} modules, {meta['node_count']} nodes, "
        f"{meta['edge_count']} edges, {meta['unresolved_count']} unresolved"
    )
    if meta.get("entry"):
        tail = " — pruned" if meta.get("scoped") else ""
        print(f"entry: {meta['entry']} ({meta['unreachable_count']} unreachable{tail})")
    if meta.get("has_runtime"):
        print(f"runtime: {meta.get('runtime_matched', 0)}/{meta.get('runtime_total', 0)} functions observed")
    top = _by_out_degree(graph)[:5]
    if top:
        width = max(len(n.id) for n in top)
        print("top by out-degree:")
        for node in top:
            print(f"  {node.id:<{width}}  out={len(node.calls)} in={len(node.called_by)}")
    if meta.get("skipped_files"):
        print(f"skipped {len(meta['skipped_files'])} unparseable file(s), see report.json meta")
