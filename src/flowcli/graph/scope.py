"""Scope a graph to what an entry point reaches: BFS depths, then pruning."""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence

from flowcli.graph.model import Graph


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
