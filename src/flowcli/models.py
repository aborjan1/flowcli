"""Data types shared across the flowcli pipeline."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

MODULE_QUALNAME = "<module>"


class CallKind(enum.Enum):
    NAME = "name"  # f()
    DOTTED = "dotted"  # a.b.f() — root is a plain name, not self/cls
    SELF_ATTR = "self"  # self.f()
    CLS_ATTR = "cls"  # cls.f()
    SUPER_ATTR = "super"  # super().f()
    OPAQUE = "opaque"  # call on a call result, subscript, lambda, deep self chain, ...


# One argument at a call site: (keyword or None, kind, payload).
# kind: "lit" (payload = (repr, typename)) | "name" | "call" (payload = dotted parts)
#     | "selfattr" | "star" | "unknown"
ArgAtom = tuple[str | None, str, Any]


@dataclass
class RawCall:
    kind: CallKind
    parts: tuple[str, ...]
    lineno: int
    repr_hint: str
    args: tuple[ArgAtom, ...] = ()


@dataclass
class FunctionInfo:
    qualname: str  # "f", "Class.m", "outer.inner", or "<module>"
    module: str
    file: str
    lineno: int
    class_qualname: str | None = None  # nearest enclosing class, None for free functions
    raw_calls: list[RawCall] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    flow: list[dict[str, Any]] = field(default_factory=list)  # nested control-flow tree (see parser._flow_of_body)
    local_types: dict[str, tuple[str, ...]] = field(default_factory=dict)  # var -> dotted type-expr parts
    params: list[dict[str, str | None]] = field(default_factory=list)  # {"name","ann","default"} display strings
    returns_ann: str | None = None  # return annotation display, ground truth when present
    returns_ann_parts: tuple[str, ...] = ()
    return_exprs: list[tuple[str, Any, int]] = field(default_factory=list)  # ("const"|"call"|"name"|"unknown", v, line)
    is_generator: bool = False


@dataclass
class ClassInfo:
    qualname: str
    module: str
    lineno: int
    bases: list[tuple[str, ...]] = field(default_factory=list)  # dotted parts of each resolvable base expr
    base_reprs: list[str] = field(default_factory=list)  # display strings, incl. unresolvable bases
    methods: dict[str, str] = field(default_factory=dict)  # method name -> function qualname
    attr_types: dict[str, tuple[str, ...]] = field(default_factory=dict)  # self.<attr> -> dotted type parts
    fields: list[dict[str, Any]] = field(default_factory=list)  # {name, ann, parts, value, source, lineno}
    decorators: list[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    name: str  # dotted module name
    file: str
    is_package: bool  # file is an __init__.py
    imports: dict[str, str] = field(default_factory=dict)  # bound local name -> absolute dotted target
    star_imports: list[str] = field(default_factory=list)  # absolute dotted modules star-imported
    functions: dict[str, FunctionInfo] = field(default_factory=dict)  # qualname -> info
    classes: dict[str, ClassInfo] = field(default_factory=dict)  # qualname -> info
    has_main_guard: bool = False  # contains `if __name__ == "__main__":`


@dataclass
class ParseFailure:
    file: str
    error: str


@dataclass
class UnresolvedCall:
    caller: str  # node id
    callee_expr: str
    lineno: int
    reason: str  # external | unknown-name | instance-attr | opaque | not-found-in-hierarchy


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


def node_id(module: str, qualname: str) -> str:
    return f"{module}:{qualname}"
