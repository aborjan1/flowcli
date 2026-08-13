"""Static signature and return-type inference.

Runs after parsing, over the project-wide index. Annotations are ground truth;
unannotated functions get their return types inferred from return expressions:
constants, constructor calls (-> the class), typed locals, and calls to other
functions whose return type is known — chained through a small fixpoint
(capped passes; cycles simply stop contributing, they never hang).
"""

from __future__ import annotations

from typing import Any

from flowcli.models import MODULE_QUALNAME, CallKind, FunctionInfo, ModuleInfo, RawCall, node_id
from flowcli.resolver import (
    INTERNAL,
    ProjectIndex,
    _resolve_class_ref,
    _resolve_one,
)

MAX_PASSES = 3
MAX_RETURN_TYPES = 5

Signatures = dict[str, dict[str, Any]]
RetLines = dict[str, dict[int, str]]


def infer_signatures(index: ProjectIndex) -> tuple[Signatures, RetLines]:
    """Return ({node_id: signature dict}, {node_id: {return lineno: type display}})."""
    entries: list[tuple[str, ModuleInfo, FunctionInfo]] = []
    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        for fn in mod.functions.values():
            if fn.qualname == MODULE_QUALNAME:
                continue
            entries.append((node_id(mod.name, fn.qualname), mod, fn))

    known: dict[str, set[str]] = {nid: set() for nid, _, _ in entries}
    annotated: set[str] = set()
    deps: dict[str, set[str]] = {}
    # per node: [(lineno, "type" | "dep", display-or-dep-id)] for annotating flow ret boxes
    line_recs: dict[str, list[tuple[int, str, str]]] = {}

    for nid, mod, fn in entries:
        if fn.returns_ann:
            known[nid].add(fn.returns_ann)
            annotated.add(nid)
        elif fn.is_generator:
            known[nid].add("Generator")
        for tag, value, lineno in fn.return_exprs:
            display, dep = _resolve_return_expr(index, mod, fn, tag, value)
            if display is not None:
                if nid not in annotated and not fn.is_generator:
                    known[nid].add(display)
                line_recs.setdefault(nid, []).append((lineno, "type", display))
            elif dep is not None:
                deps.setdefault(nid, set()).add(dep)
                line_recs.setdefault(nid, []).append((lineno, "dep", dep))
        if not fn.return_exprs and not fn.is_generator and nid not in annotated:
            known[nid].add("None")  # falls off the end

    for _ in range(MAX_PASSES):
        changed = False
        for nid, dep_ids in deps.items():
            if nid in annotated:
                continue
            for dep in dep_ids:
                new = known.get(dep, set()) - known[nid]
                if new:
                    known[nid] |= new
                    changed = True
        if not changed:
            break

    signatures: Signatures = {}
    ret_lines: RetLines = {}
    for nid, _mod, fn in entries:
        signatures[nid] = {
            "params": [dict(p) for p in fn.params],
            "returns": sorted(known[nid])[:MAX_RETURN_TYPES],
            "inferred": nid not in annotated,
        }
        per_line: dict[int, set[str]] = {}
        for lineno, kind, value in line_recs.get(nid, []):
            types = [value] if kind == "type" else sorted(known.get(value, set()))[:3]
            if types:
                per_line.setdefault(lineno, set()).update(types)
        if per_line:
            ret_lines[nid] = {lineno: " | ".join(sorted(types)) for lineno, types in per_line.items()}
    return signatures, ret_lines


def _resolve_return_expr(
    index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, tag: str, value: Any
) -> tuple[str | None, str | None]:
    """Resolve one return expression to (type display, None) or (None, dep node id) or (None, None)."""
    if tag == "const":
        return (value, None)
    if tag == "name":
        parts = fn.local_types.get(value)
        if not parts:
            return (None, None)
        ref = _resolve_class_ref(index, mod, parts)
        return (ref[1] if ref is not None else ".".join(parts), None)
    if tag == "call":
        return _resolve_return_call(index, mod, fn, tuple(value))
    return (None, None)  # "unknown": marks that a return exists, contributes no type


def _resolve_return_call(
    index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...]
) -> tuple[str | None, str | None]:
    if parts == ("cls",) and fn.class_qualname:
        return (fn.class_qualname, None)
    ref = _resolve_class_ref(index, mod, parts)
    if ref is not None:  # constructor call -> instance of that class
        return (ref[1], None)
    status, target, _reason = _resolve_one(index, mod, fn, _raw_call_for(parts, fn))
    if status != INTERNAL:
        return (None, None)
    if target.rpartition(":")[2].endswith("__init__"):  # constructor reached via alias/import
        cls = target.split(":", 1)[1].rsplit(".__init__", 1)[0]
        return (cls, None)
    return (None, target)  # depend on the callee's inferred return type


def _raw_call_for(parts: tuple[str, ...], fn: FunctionInfo) -> RawCall:
    hint = ".".join(parts)
    if len(parts) == 1:
        return RawCall(CallKind.NAME, parts, 0, hint)
    if parts[0] in ("self", "cls") and fn.class_qualname:
        if len(parts) == 2:
            kind = CallKind.SELF_ATTR if parts[0] == "self" else CallKind.CLS_ATTR
            return RawCall(kind, parts, 0, hint)
        return RawCall(CallKind.OPAQUE, parts, 0, hint)  # self.attr.method() chain
    return RawCall(CallKind.DOTTED, parts, 0, hint)
