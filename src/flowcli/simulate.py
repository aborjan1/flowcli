"""Simulated execution: infer what data flows through each function, without running anything.

A static stand-in for a debugger session. Call-site arguments are bound to the
callee's parameters and propagated across the graph: literals carry their value
(`fact(5)` → `n = 5`), names carry their declared/inferred type, nested calls
carry the callee's return type. Iterated to a fixpoint so values travel several
hops from the entry point.

Also produces a simulated *call order* — a depth-first walk from the entry in
source-line order — so the replay animation works on code that can never be run
locally (device scripts, hardware-bound services).
"""

from __future__ import annotations

from typing import Any

from flowcli.models import MODULE_QUALNAME, CallKind, FunctionInfo, ModuleInfo, node_id
from flowcli.resolver import INTERNAL, ProjectIndex, ResolvedCall, _resolve_class_ref
from flowcli.resolver import _resolve_one as resolve_one

MAX_PASSES = 3
MAX_VALUES = 4  # distinct literal values kept per parameter
MAX_TYPES = 4
MAX_EVENTS = 2000
IMPLICIT_FIRST = ("self", "cls")


class _Site:
    """One resolved call site, pre-bound for repeated propagation passes."""

    __slots__ = ("caller", "target", "lineno", "pairs")

    def __init__(self, caller: str, target: str, lineno: int, pairs: list[tuple[str, tuple[str, Any]]]) -> None:
        self.caller = caller
        self.target = target
        self.lineno = lineno
        self.pairs = pairs  # [(callee param name, arg atom)]


def simulate(
    index: ProjectIndex,
    resolved: list[ResolvedCall],
    signatures: dict[str, dict[str, Any]],
    entry_ids: list[str] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[list[str]]]:
    """Return ({node_id: simulated record}, [[caller, callee], ...] simulated call order)."""
    fns = _function_index(index)
    sites = [s for s in (_bind_site(rc, fns) for rc in resolved if rc.status == INTERNAL) if s is not None]

    records: dict[str, dict[str, Any]] = {}
    for nid, fn in fns.items():
        params = {
            p["name"]: {"types": [], "values": [], "from": []}
            for p in fn.params
            if p["name"] not in IMPLICIT_FIRST
        }
        records[nid] = {"args": params, "returns": list(signatures.get(nid, {}).get("returns", [])), "sites": 0}

    for nid in entry_ids or []:
        _seed_entry(records.get(nid), fns.get(nid))

    for _ in range(MAX_PASSES):
        changed = False
        for site in sites:
            rec = records.get(site.target)
            if rec is None:
                continue
            for param, atom in site.pairs:
                slot = rec["args"].get(param)
                if slot is None:
                    continue
                types, value = _eval_atom(index, fns, records, signatures, site.caller, atom)
                if _absorb(slot, types, value, site.caller):
                    changed = True
        if not changed:
            break

    counts: dict[str, int] = {}
    for site in sites:
        counts[site.target] = counts.get(site.target, 0) + 1
    for nid, rec in records.items():
        rec["sites"] = counts.get(nid, 0)
        for slot in rec["args"].values():
            slot["types"] = sorted(slot["types"])
            slot["from"] = sorted(set(slot["from"]))[:5]

    return records, _simulated_events(sites, entry_ids or [])


def _function_index(index: ProjectIndex) -> dict[str, FunctionInfo]:
    out: dict[str, FunctionInfo] = {}
    for mod_name in sorted(index.modules):
        for fn in index.modules[mod_name].functions.values():
            out[node_id(mod_name, fn.qualname)] = fn
    return out


def _bind_site(rc: ResolvedCall, fns: dict[str, FunctionInfo]) -> _Site | None:
    """Map a call site's argument atoms onto the callee's parameter names."""
    callee = fns.get(rc.target)
    if callee is None or rc.call is None:
        return None
    names = [p["name"] for p in callee.params]
    if names and names[0] in IMPLICIT_FIRST:
        names = names[1:]  # bound method / constructor: receiver is implicit
    if rc.call.kind is CallKind.OPAQUE:
        return None

    pairs: list[tuple[str, tuple[str, Any]]] = []
    pos = 0
    for keyword, kind, payload in rc.call.args:
        if kind == "star":
            break  # *args / **kwargs make positional binding unknowable past this point
        if keyword is not None:
            if keyword in names:
                pairs.append((keyword, (kind, payload)))
            continue
        if pos < len(names):
            name = names[pos]
            if name.startswith("*"):
                break
            pairs.append((name, (kind, payload)))
        pos += 1
    return _Site(rc.caller, rc.target, rc.lineno, pairs)


def _seed_entry(rec: dict[str, Any] | None, fn: FunctionInfo | None) -> None:
    """Entry points have no caller — seed their parameters from annotations."""
    if rec is None or fn is None:
        return
    for p in fn.params:
        slot = rec["args"].get(p["name"])
        if slot is None:
            continue
        if p.get("ann"):
            _absorb(slot, [str(p["ann"])], None, "(entry)")
        if p.get("default"):
            _absorb(slot, [], str(p["default"]), "(default)")


def _absorb(slot: dict[str, Any], types: list[str], value: str | None, source: str) -> bool:
    changed = False
    for t in types:
        if t and t not in slot["types"] and len(slot["types"]) < MAX_TYPES:
            slot["types"].append(t)
            changed = True
    if value is not None and value not in slot["values"] and len(slot["values"]) < MAX_VALUES:
        slot["values"].append(value)
        changed = True
    if changed and source not in slot["from"]:
        slot["from"].append(source)
    return changed


def _eval_atom(
    index: ProjectIndex,
    fns: dict[str, FunctionInfo],
    records: dict[str, dict[str, Any]],
    signatures: dict[str, dict[str, Any]],
    caller_id: str,
    atom: tuple[str, Any],
) -> tuple[list[str], str | None]:
    """What is known about one argument expression, evaluated in the caller's scope."""
    kind, payload = atom
    if kind == "lit":
        value, tname = payload
        return ([tname], value)
    caller = fns.get(caller_id)
    if caller is None:
        return ([], None)
    mod = index.modules.get(caller.module)
    if mod is None:
        return ([], None)

    if kind == "name":
        local = caller.local_types.get(payload)
        if local:
            ref = _resolve_class_ref(index, mod, local)
            return ([ref[1] if ref else ".".join(local)], None)
        known = records.get(caller_id, {}).get("args", {}).get(payload)
        if known:  # forwarding one of the caller's own parameters
            return (list(known["types"]), known["values"][0] if known["values"] else None)
        return ([], None)
    if kind == "selfattr":
        if caller.class_qualname:
            ci = mod.classes.get(caller.class_qualname)
            parts = ci.attr_types.get(payload) if ci else None
            if parts:
                ref = _resolve_class_ref(index, mod, parts)
                return ([ref[1] if ref else ".".join(parts)], None)
        return ([], None)
    if kind == "call":
        return (_returns_of_call(index, mod, caller, signatures, tuple(payload)), None)
    return ([], None)


def _returns_of_call(
    index: ProjectIndex,
    mod: ModuleInfo,
    caller: FunctionInfo,
    signatures: dict[str, dict[str, Any]],
    parts: tuple[str, ...],
) -> list[str]:
    ref = _resolve_class_ref(index, mod, parts)
    if ref is not None:
        return [ref[1]]  # constructor call -> an instance of that class
    from flowcli.infer import _raw_call_for  # local import: infer imports models only

    status, target, _ = resolve_one(index, mod, caller, _raw_call_for(parts, caller))
    if status != INTERNAL:
        return []
    return list(signatures.get(target, {}).get("returns", []))[:MAX_TYPES]


def _simulated_events(sites: list[_Site], entry_ids: list[str]) -> list[list[str]]:
    """Depth-first walk from the entries in source-line order — a plausible execution trace."""
    out_edges: dict[str, list[tuple[int, str]]] = {}
    for site in sites:
        out_edges.setdefault(site.caller, []).append((site.lineno, site.target))
    for edges in out_edges.values():
        edges.sort()

    roots = list(entry_ids)
    if not roots:
        callees = {t for edges in out_edges.values() for _, t in edges}
        roots = sorted(set(out_edges) - callees) or sorted(out_edges)[:1]

    events: list[list[str]] = []
    for root in roots:
        _walk(root, out_edges, set(), events)
        if len(events) >= MAX_EVENTS:
            break
    return events[:MAX_EVENTS]


def _walk(node: str, out_edges: dict[str, list[tuple[int, str]]], stack: set[str], events: list[list[str]]) -> None:
    if len(events) >= MAX_EVENTS or node in stack:
        return  # cycle guard: recursion is shown once, not unrolled
    stack.add(node)
    for _lineno, target in out_edges.get(node, []):
        if len(events) >= MAX_EVENTS:
            break
        events.append([node, target])
        _walk(target, out_edges, stack, events)
    stack.discard(node)


def module_entry_candidates(index: ProjectIndex) -> list[str]:
    """Fallback entries when none was given: module-level code, then `main`-ish functions."""
    out: list[str] = []
    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        if MODULE_QUALNAME in mod.functions:
            out.append(node_id(mod_name, MODULE_QUALNAME))
        for qual in ("main", "run"):
            if qual in mod.functions:
                out.append(node_id(mod_name, qual))
    return out
