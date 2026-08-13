"""Graph assembly: Node construction, degrees, BFS depth, entry-spec parsing."""

from __future__ import annotations

import difflib
from collections import Counter, deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from flowcli.infer import infer_signatures
from flowcli.models import MODULE_QUALNAME, ModuleInfo, Node, UnresolvedCall, node_id
from flowcli.resolver import EXTERNAL, INTERNAL, ProjectIndex, ResolvedCall


@dataclass
class Graph:
    nodes: dict[str, Node]
    unresolved: list[UnresolvedCall] = field(default_factory=list)
    entry: str | None = None


def build_graph(index: ProjectIndex, resolved: list[ResolvedCall], include_external: bool = False) -> Graph:
    nodes = _make_nodes(index, resolved)
    unresolved = _apply_edges(nodes, resolved, include_external)
    unresolved.sort(key=lambda u: (u.caller, u.lineno, u.callee_expr))
    return Graph(nodes={nid: nodes[nid] for nid in sorted(nodes)}, unresolved=unresolved)


def apply_simulation(
    graph: Graph, index: ProjectIndex, resolved: list[ResolvedCall], entry_ids: list[str] | None = None
) -> list[list[str]]:
    """Run the static simulation and attach it to nodes. Returns the simulated call order."""
    from flowcli.simulate import module_entry_candidates, simulate

    signatures = {nid: node.signature for nid, node in graph.nodes.items() if node.signature}
    seeds = entry_ids or [nid for nid in module_entry_candidates(index) if nid in graph.nodes]
    records, events = simulate(index, resolved, signatures, seeds)
    for nid, record in records.items():
        node = graph.nodes.get(nid)
        if node is not None and (record["sites"] or any(s["types"] or s["values"] for s in record["args"].values())):
            node.simulated = record
    return [e for e in events if e[0] in graph.nodes and e[1] in graph.nodes]


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


def compute_depths(graph: Graph, entries: str | Sequence[str], max_depth: int | None = None) -> int:
    """BFS from one or more entry nodes; recursion is just a back-edge. Returns the unreachable count.

    Multiple entries (a module entry seeds every function in the file) all start at depth 0.
    With max_depth, nodes more than that many call-hops away stay depth=None
    (and get removed by prune_unreachable) — the brake against runaway scope.
    """
    ids = [entries] if isinstance(entries, str) else list(entries)
    missing = [nid for nid in ids if nid not in graph.nodes]
    if missing:
        raise ValueError(f"entry node(s) not in graph: {missing}")
    for node in graph.nodes.values():
        node.depth = None
    seen = set(ids)
    queue: deque[tuple[str, int]] = deque((nid, 0) for nid in ids)
    while queue:
        nid, depth = queue.popleft()
        graph.nodes[nid].depth = depth
        if max_depth is not None and depth >= max_depth:
            continue
        for callee in graph.nodes[nid].calls:
            if callee in graph.nodes and callee not in seen:
                seen.add(callee)
                queue.append((callee, depth + 1))
    graph.entry = ids[0] if len(ids) == 1 else None
    return sum(1 for node in graph.nodes.values() if node.depth is None)


def prune_unreachable(graph: Graph) -> int:
    """Drop every node compute_depths did not reach (depth is None). Returns the number removed.

    Scopes the whole report to the entry's call graph: nodes, edge references in both
    directions (a depth limit can leave surviving nodes pointing past the fence), and
    unresolved calls from pruned callers all go.
    """
    removed = {nid for nid, node in graph.nodes.items() if node.depth is None}
    if not removed:
        return 0
    graph.nodes = {nid: node for nid, node in graph.nodes.items() if nid not in removed}
    for node in graph.nodes.values():
        node.called_by = [c for c in node.called_by if c not in removed]
        node.calls = [c for c in node.calls if c not in removed]
        node.static_call_count = {k: v for k, v in node.static_call_count.items() if k not in removed}
    graph.unresolved = [u for u in graph.unresolved if u.caller not in removed]
    return len(removed)


def parse_entry_specs(specs: Sequence[str], index: ProjectIndex) -> tuple[str, list[str]]:
    """Resolve several entry specs at once into one combined (label, seed node ids)."""
    labels: list[str] = []
    ids: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        label, spec_ids = parse_entry_spec(spec, index)
        labels.append(label)
        for nid in spec_ids:
            if nid not in seen:
                seen.add(nid)
                ids.append(nid)
    if not ids:
        raise ValueError("no entry points resolved")
    if len(labels) == 1:
        return labels[0], sorted(ids)
    shown = ", ".join(labels[:3])
    if len(labels) > 3:
        shown += f", +{len(labels) - 3} more"
    return f"{len(labels)} entries: {shown}", sorted(ids)


def parse_entry_spec(spec: str, index: ProjectIndex) -> tuple[str, list[str]]:
    """Resolve an entry spec to (display label, seed node ids).

    'path/to/mod.py:qualname' / 'dotted.module:qualname' -> that one function.
    'path/to/mod.py' / 'dotted.module' (no qualname) -> every function the module defines.
    'path/to/dir' / 'dotted.package' -> every function in every module beneath it,
    subpackages included — the whole folder's ecosystem.
    """
    if ":" in spec:
        mod_part, qual = spec.rsplit(":", 1)
    else:
        mod_part, qual = spec, None

    if qual is None:
        subtree = _find_subtree(mod_part, index)
        if subtree is not None:
            return subtree

    module = _find_module(mod_part, index)
    if qual is None:
        ids = [node_id(module.name, q) for q in module.functions]
        if not ids:
            raise ValueError(f"module {module.name!r} defines no functions")
        return f"{module.name} (module)", ids
    if qual in module.functions:
        nid = node_id(module.name, qual)
        return nid, [nid]
    suggestions = difflib.get_close_matches(qual, list(module.functions), n=3)
    hint = f" (did you mean: {', '.join(suggestions)}?)" if suggestions else ""
    raise ValueError(f"entry function not found: {qual!r} in module {module.name!r}{hint}")


def _find_subtree(mod_part: str, index: ProjectIndex) -> tuple[str, list[str]] | None:
    """Directory or package entry: seed from every function beneath it. None if not a subtree."""
    trimmed = mod_part.rstrip("/\\")
    path = Path(trimmed)
    if path.is_dir():
        target = path.resolve()
        modules = [m for m in index.modules.values() if target in Path(m.file).resolve().parents]
        if not modules:
            raise ValueError(f"no parsed modules under directory: {mod_part!r}")
        label = f"{path.name}/"
    else:
        package = index.modules.get(trimmed)
        if package is None or not package.is_package:
            return None
        modules = [m for m in index.modules.values() if m.name == trimmed or m.name.startswith(f"{trimmed}.")]
        label = trimmed

    ids = sorted(node_id(m.name, q) for m in modules for q in m.functions)
    if not ids:
        raise ValueError(f"no functions defined under {mod_part!r}")
    return f"{label} ({len(modules)} modules)", ids


def _find_module(mod_part: str, index: ProjectIndex) -> ModuleInfo:
    module = None
    if mod_part.endswith(".py"):
        target = Path(mod_part).resolve()
        for m in index.modules.values():
            if Path(m.file).resolve() == target:
                module = m
                break
    else:
        module = index.modules.get(mod_part)
    if module is None:
        known = difflib.get_close_matches(mod_part, list(index.modules), n=3)
        hint = f" (did you mean: {', '.join(known)}?)" if known else ""
        raise ValueError(f"entry module not found: {mod_part!r}{hint}")
    return module
