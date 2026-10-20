"""Graph assembly: nodes from the index, edges from resolved calls, then optional enrichment."""

from __future__ import annotations

from collections import Counter

from flowcli.analysis.index import ProjectIndex
from flowcli.analysis.infer import infer_signatures
from flowcli.analysis.model import MODULE_QUALNAME, node_id
from flowcli.analysis.resolver import EXTERNAL, INTERNAL, ResolvedCall
from flowcli.analysis.simulate import module_entry_candidates, simulate
from flowcli.graph.model import Graph, Node, UnresolvedCall


def build_graph(index: ProjectIndex, resolved: list[ResolvedCall], include_external: bool = False) -> Graph:
    nodes = _make_nodes(index, resolved)
    unresolved = _apply_edges(nodes, resolved, include_external)
    unresolved.sort(key=lambda u: (u.caller, u.lineno, u.callee_expr))
    return Graph(nodes={nid: nodes[nid] for nid in sorted(nodes)}, unresolved=unresolved)


def _make_nodes(index: ProjectIndex, resolved: list[ResolvedCall]) -> dict[str, Node]:
    calls_by_caller: dict[str, list[tuple[int, str]]] = {}
    for rc in resolved:
        if rc.status == INTERNAL:
            calls_by_caller.setdefault(rc.caller, []).append((rc.lineno, rc.target))
    signatures, ret_lines = infer_signatures(index)

    nodes: dict[str, Node] = {}
    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        for fn in mod.functions.values():
            nid = node_id(mod.name, fn.qualname)
            if fn.qualname == MODULE_QUALNAME:
                kind = "module"
            elif fn.class_qualname:
                kind = "method"
            else:
                kind = "function"
            _annotate_flow(fn.flow, calls_by_caller.get(nid, []))
            _annotate_ret_types(fn.flow, ret_lines.get(nid, {}))
            nodes[nid] = Node(
                id=nid,
                file=fn.file,
                lineno=fn.lineno,
                kind=kind,
                decorators=list(fn.decorators),
                flow=fn.flow,
                signature=signatures.get(nid),
            )
    return nodes


def _apply_edges(nodes: dict[str, Node], resolved: list[ResolvedCall], include_external: bool) -> list[UnresolvedCall]:
    unresolved: list[UnresolvedCall] = []
    counts: dict[str, Counter[str]] = {}
    for rc in resolved:
        if rc.status == INTERNAL:
            counts.setdefault(rc.caller, Counter())[rc.target] += 1
        elif rc.status == EXTERNAL and include_external:
            if rc.target not in nodes:
                nodes[rc.target] = Node(id=rc.target, file="", lineno=0, kind="external")
            counts.setdefault(rc.caller, Counter())[rc.target] += 1
        elif rc.status == EXTERNAL:
            unresolved.append(UnresolvedCall(rc.caller, rc.target, rc.lineno, "external"))
        else:
            unresolved.append(UnresolvedCall(rc.caller, rc.target, rc.lineno, rc.reason))

    for caller, ctr in counts.items():
        node = nodes[caller]
        node.static_call_count = dict(sorted(ctr.items()))
        node.calls = sorted(ctr)
        for callee in ctr:
            nodes[callee].called_by.append(caller)
    for node in nodes.values():
        node.called_by.sort()
    return unresolved


def _annotate_flow(flow: list[dict], calls: list[tuple[int, str]]) -> None:
    """Attach resolved call targets to flow nodes by line range (idempotent — assigns, never appends)."""
    for item in flow:
        start = item.get("line", 0)
        if item["t"] in ("stmt", "ret"):
            end = item.get("end", start)
            item["calls"] = sorted({t for ln, t in calls if start <= ln <= end})
            continue
        head_end = item.get("head_end", start)
        item["calls"] = sorted({t for ln, t in calls if start <= ln <= head_end})
        for key in ("then", "else", "body", "final"):
            if key in item:
                _annotate_flow(item[key], calls)
        for handler in item.get("handlers", []):
            _annotate_flow(handler["body"], calls)
        for case in item.get("cases", []):
            _annotate_flow(case["body"], calls)


def _annotate_ret_types(flow: list[dict], line_map: dict[int, str]) -> None:
    """Attach inferred branch return types to flow 'ret' nodes (idempotent — assigns, never appends)."""
    if not line_map:
        return
    for item in flow:
        if item["t"] == "ret":
            rt = line_map.get(item.get("line", 0))
            if rt:
                item["rt"] = rt
            continue
        for key in ("then", "else", "body", "final"):
            if key in item:
                _annotate_ret_types(item[key], line_map)
        for handler in item.get("handlers", []):
            _annotate_ret_types(handler["body"], line_map)
        for case in item.get("cases", []):
            _annotate_ret_types(case["body"], line_map)


def apply_runtime(graph: Graph, runtime: dict) -> int:
    """Fill Node.dynamic from a flowcli-run runtime.json dict. Returns the matched-node count."""
    matched = 0
    for nid, record in runtime.get("functions", {}).items():
        node = graph.nodes.get(nid)
        if node is not None:
            node.dynamic = record
            matched += 1
    return matched


def apply_simulation(
    graph: Graph, index: ProjectIndex, resolved: list[ResolvedCall], entry_ids: list[str] | None = None
) -> list[list[str]]:
    """Run the static simulation and attach it to nodes. Returns the simulated call order."""
    signatures = {nid: node.signature for nid, node in graph.nodes.items() if node.signature}
    seeds = entry_ids or [nid for nid in module_entry_candidates(index) if nid in graph.nodes]
    records, events = simulate(index, resolved, signatures, seeds)
    for nid, record in records.items():
        node = graph.nodes.get(nid)
        if node is not None and (record["sites"] or any(s["types"] or s["values"] for s in record["args"].values())):
            node.simulated = record
    return [e for e in events if e[0] in graph.nodes and e[1] in graph.nodes]
