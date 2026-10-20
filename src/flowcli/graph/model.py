"""The merged call graph: one Node per function, plus the calls that could not be pinned down."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    """One entry in the merged graph. `dynamic` stays None in v1; the v2 profiler fills it in."""

    id: str  # "dotted.module:qualname" for internal, plain dotted path for external
    file: str
    lineno: int
    calls: list[str] = field(default_factory=list)
    called_by: list[str] = field(default_factory=list)
    depth: int | None = None  # min distance from --entry, None without one / unreachable
    static_call_count: dict[str, int] = field(default_factory=dict)
    dynamic: dict[str, Any] | None = None
    kind: str = "function"  # function | method | module | external
    decorators: list[str] = field(default_factory=list)
    flow: list[dict[str, Any]] = field(default_factory=list)  # control-flow tree; stmt nodes carry resolved "calls"
    signature: dict[str, Any] | None = None  # {"params": [...], "returns": [types], "inferred": bool}
    simulated: dict[str, Any] | None = None  # inferred data flow: {"args": {p: {...}}, "returns": [...], "sites": n}


@dataclass
class UnresolvedCall:
    caller: str  # node id
    callee_expr: str
    lineno: int
    reason: str  # external | unknown-name | instance-attr | opaque | not-found-in-hierarchy


@dataclass
class Graph:
    nodes: dict[str, Node]
    unresolved: list[UnresolvedCall] = field(default_factory=list)
    entry: str | None = None
