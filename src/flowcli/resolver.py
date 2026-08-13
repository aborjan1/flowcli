"""Pass 2: resolve raw calls against the project-wide symbol index."""

from __future__ import annotations

import builtins
from dataclasses import dataclass

from flowcli.models import MODULE_QUALNAME, CallKind, FunctionInfo, ModuleInfo, RawCall, node_id

BUILTIN_NAMES = frozenset(dir(builtins))

INTERNAL = "internal"
EXTERNAL = "external"
UNRESOLVED = "unresolved"


@dataclass
class ResolvedCall:
    caller: str  # node id
    lineno: int
    status: str  # internal | external | unresolved
    target: str  # node id (internal), dotted path (external), or callee expr (unresolved)
    reason: str = ""  # unresolved only
    call: RawCall | None = None  # the originating call site (argument atoms for simulation)


class ProjectIndex:
    def __init__(self, modules: dict[str, ModuleInfo]) -> None:
        self.modules = modules

    def module_for(self, dotted: str) -> str | None:
        """Longest known-module prefix of a dotted path."""
        parts = dotted.split(".")
        for i in range(len(parts), 0, -1):
            cand = ".".join(parts[:i])
            if cand in self.modules:
                return cand
        return None


def resolve_all(index: ProjectIndex) -> list[ResolvedCall]:
    out: list[ResolvedCall] = []
    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        for fn in mod.functions.values():
            caller = node_id(mod.name, fn.qualname)
            for call in fn.raw_calls:
                status, target, reason = _resolve_one(index, mod, fn, call)
                out.append(
                    ResolvedCall(
                        caller=caller,
                        lineno=call.lineno,
                        status=status,
                        target=target,
                        reason=reason,
                        call=call,
                    )
                )
    return out


Outcome = tuple[str, str, str]  # (status, target, reason)


def _internal(target_id: str) -> Outcome:
    return (INTERNAL, target_id, "")


def _external(dotted: str) -> Outcome:
    return (EXTERNAL, dotted, "")


def _unresolved(expr: str, reason: str) -> Outcome:
    return (UNRESOLVED, expr, reason)


def _resolve_one(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall) -> Outcome:
    if call.kind is CallKind.NAME:
        return _resolve_name(index, mod, fn, call)
    if call.kind is CallKind.DOTTED:
        return _resolve_dotted(index, mod, fn, call)
    if call.kind in (CallKind.SELF_ATTR, CallKind.CLS_ATTR, CallKind.SUPER_ATTR):
        if fn.class_qualname is None:
            return _unresolved(call.repr_hint, "instance-attr")
        method = call.parts[-1]
        target = resolve_method(
            index, mod.name, fn.class_qualname, method, skip_self=call.kind is CallKind.SUPER_ATTR
        )
        if target:
            return _internal(target)
        return _unresolved(call.repr_hint, "not-found-in-hierarchy")
    # OPAQUE
    if call.parts and call.parts[0] in ("self", "cls"):
        if len(call.parts) == 3 and call.parts[0] == "self" and fn.class_qualname:
            resolved = _resolve_self_attr_chain(index, mod, fn.class_qualname, call)
            if resolved is not None:
                return resolved
        return _unresolved(call.repr_hint, "instance-attr")
    return _unresolved(call.repr_hint, "opaque")


def _resolve_self_attr_chain(index: ProjectIndex, mod: ModuleInfo, class_qualname: str, call: RawCall) -> Outcome | None:
    """self.db.update() where the enclosing class (or a parsed base) types `db` as a parsed class."""
    attr, method = call.parts[1], call.parts[2]
    found = _find_attr_type(index, mod.name, class_qualname, attr)
    if found is None:
        return None
    decl_module, type_parts = found
    decl_mod = index.modules.get(decl_module)
    if decl_mod is None:
        return None
    ref = _resolve_class_ref(index, decl_mod, type_parts)  # resolves in the declaring module's namespace
    if ref is None:
        return None  # attribute typed as something we never parsed (sqlite3.Connection, ...) — stays unresolved
    target = resolve_method(index, ref[0], ref[1], method)
    return _internal(target) if target else _unresolved(call.repr_hint, "not-found-in-hierarchy")


def _find_attr_type(
    index: ProjectIndex,
    module: str,
    class_qualname: str,
    attr: str,
    _seen: set[tuple[str, str]] | None = None,
) -> tuple[str, tuple[str, ...]] | None:
    """Locate self.<attr>'s recorded type parts in the class or its parsed bases: (declaring_module, parts)."""
    if _seen is None:
        _seen = set()
    key = (module, class_qualname)
    if key in _seen:
        return None
    _seen.add(key)
    mod = index.modules.get(module)
    if mod is None:
        return None
    ci = mod.classes.get(class_qualname)
    if ci is None:
        return None
    if attr in ci.attr_types:
        return (module, ci.attr_types[attr])
    for base_parts in ci.bases:
        ref = _resolve_class_ref(index, mod, base_parts)
        if ref is not None:
            found = _find_attr_type(index, ref[0], ref[1], attr, _seen)
            if found is not None:
                return found
    return None


def _resolve_name(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall) -> Outcome:
    """Resolution order: enclosing scopes -> module symbols -> imports -> star imports -> builtins."""
    name = call.parts[0]

    if name == "cls" and fn.class_qualname:  # cls() in a classmethod -> own constructor
        target = resolve_method(index, mod.name, fn.class_qualname, "__init__")
        return _internal(target) if target else _unresolved(call.repr_hint, "not-found-in-hierarchy")
    if name == "self":
        return _unresolved(call.repr_hint, "instance-attr")

    scoped = _resolve_enclosing_scope(index, mod, fn, name, call.repr_hint)
    if scoped is not None:
        return scoped
    if name in mod.functions:
        return _internal(node_id(mod.name, name))
    if name in mod.classes:
        return _constructor(index, mod.name, name, call.repr_hint)
    return _resolve_name_imported(index, mod, name, call.repr_hint)


def _resolve_enclosing_scope(
    index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, name: str, hint: str
) -> Outcome | None:
    """Innermost-out over enclosing function scopes; class scopes don't leak into method bodies."""
    if fn.qualname == MODULE_QUALNAME:
        return None
    segments = fn.qualname.split(".")
    for i in range(len(segments), 0, -1):
        prefix = ".".join(segments[:i])
        if prefix in mod.classes:
            continue
        cand = f"{prefix}.{name}"
        if cand in mod.functions:
            return _internal(node_id(mod.name, cand))
        if cand in mod.classes:
            return _constructor(index, mod.name, cand, hint)
    return None


def _resolve_name_imported(index: ProjectIndex, mod: ModuleInfo, name: str, hint: str) -> Outcome:
    if name in mod.imports:
        return _resolve_absolute(index, mod.imports[name], hint)
    for star_mod in mod.star_imports:  # declaration order
        m = index.modules.get(star_mod)
        if m is None:
            continue
        if name in m.functions:
            return _internal(node_id(star_mod, name))
        if name in m.classes:
            return _constructor(index, star_mod, name, hint)
    if name in BUILTIN_NAMES:
        return _external(f"builtins.{name}")
    return _unresolved(hint, "unknown-name")


def _resolve_dotted(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall) -> Outcome:
    parts = call.parts
    root = parts[0]

    local = _resolve_local_class_dotted(index, mod, parts, call.repr_hint)
    if local is not None:
        return local

    typed = _resolve_typed_local(index, mod, fn, parts, call.repr_hint)
    if typed is not None:
        return typed

    if root in mod.imports:
        dotted = ".".join((mod.imports[root], *parts[1:]))
        return _resolve_absolute(index, dotted, call.repr_hint)

    if root in mod.classes or root in mod.functions:
        return _unresolved(call.repr_hint, "unknown-name")
    return _unresolved(call.repr_hint, "instance-attr")  # attribute call on a local value


def _resolve_typed_local(
    index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...], hint: str
) -> Outcome | None:
    """Typed local variable: `gen: Generator` param, `x: Foo = ...`, or `x = Foo()`.

    Only fires when the named type resolves to a *parsed* class — stdlib/third-party
    types (e.g. pathlib.Path) find no class and fall through to instance-attr.
    """
    if parts[0] not in fn.local_types or len(parts) != 2:
        return None
    ref = _resolve_class_ref(index, mod, fn.local_types[parts[0]])
    if ref is None:
        return None
    target = resolve_method(index, ref[0], ref[1], parts[1])
    return _internal(target) if target else _unresolved(hint, "not-found-in-hierarchy")


def _resolve_local_class_dotted(
    index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...], hint: str
) -> Outcome | None:
    """ClassName() / Class.method() / Outer.Inner() naming a class defined in this module."""
    dotted = ".".join(parts)
    if dotted in mod.classes:
        return _constructor(index, mod.name, dotted, hint)
    if len(parts) >= 2:
        owner_cls = ".".join(parts[:-1])
        if owner_cls in mod.classes:
            target = resolve_method(index, mod.name, owner_cls, parts[-1])
            return _internal(target) if target else _unresolved(hint, "not-found-in-hierarchy")
    return None


def _constructor(index: ProjectIndex, module: str, class_qualname: str, expr: str) -> Outcome:
    """ClassName() targets the defining class's __init__ (may live in a parsed base)."""
    target = resolve_method(index, module, class_qualname, "__init__")
    return _internal(target) if target else _unresolved(expr, "not-found-in-hierarchy")


def _resolve_absolute(index: ProjectIndex, dotted: str, expr: str, _seen: set[str] | None = None) -> Outcome:
    """Resolve an absolute dotted path (already expanded through an import table)."""
    if _seen is None:
        _seen = set()
    if dotted in _seen:
        return _unresolved(expr, "unknown-name")
    _seen.add(dotted)

    owner = index.module_for(dotted)
    if owner is None:
        return _external(dotted)
    if owner == dotted:
        return _unresolved(expr, "unknown-name")  # a module itself is not callable

    rem = dotted[len(owner) + 1 :]
    m = index.modules[owner]
    if rem in m.functions:
        return _internal(node_id(owner, rem))
    if rem in m.classes:
        return _constructor(index, owner, rem, expr)
    if "." in rem:
        cls, meth = rem.rsplit(".", 1)
        if cls in m.classes:
            target = resolve_method(index, owner, cls, meth)
            return _internal(target) if target else _unresolved(expr, "not-found-in-hierarchy")

    # chase re-exports one segment at a time (e.g. pkg/__init__.py: from .helpers import util_a)
    first, _, rest = rem.partition(".")
    if first in m.imports:
        chased = m.imports[first] + (f".{rest}" if rest else "")
        return _resolve_absolute(index, chased, expr, _seen)
    for star_mod in m.star_imports:
        sm = index.modules.get(star_mod)
        if sm is not None and (first in sm.functions or first in sm.classes):
            return _resolve_absolute(index, f"{star_mod}.{rem}", expr, _seen)

    return _unresolved(expr, "unknown-name")


def resolve_method(
    index: ProjectIndex,
    module: str,
    class_qualname: str,
    method: str,
    *,
    skip_self: bool = False,
    _seen: set[tuple[str, str]] | None = None,
) -> str | None:
    """MRO-lite: own methods, then bases depth-first left-to-right. Cycle-guarded.

    Approximates C3 linearization well enough for static mapping; diamond
    hierarchies follow DFS order (documented in the README).
    """
    if _seen is None:
        _seen = set()
    key = (module, class_qualname)
    if key in _seen:
        return None
    _seen.add(key)

    mod = index.modules.get(module)
    if mod is None:
        return None
    ci = mod.classes.get(class_qualname)
    if ci is None:
        return None
    if not skip_self and method in ci.methods:
        return node_id(module, ci.methods[method])
    for base_parts in ci.bases:
        ref = _resolve_class_ref(index, mod, base_parts)
        if ref is not None:
            base_module, base_cls = ref
            target = resolve_method(index, base_module, base_cls, method, _seen=_seen)
            if target:
                return target
    return None


def _resolve_class_ref(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...]) -> tuple[str, str] | None:
    """Resolve a base-class expression's dotted parts to a parsed (module, class_qualname)."""
    root = parts[0]
    if len(parts) == 1:
        if root in mod.classes:
            return (mod.name, root)
        if root in mod.imports:
            return _find_class_by_dotted(index, mod.imports[root])
        for star_mod in mod.star_imports:
            sm = index.modules.get(star_mod)
            if sm is not None and root in sm.classes:
                return (star_mod, root)
        return None
    dotted = ".".join((mod.imports[root], *parts[1:])) if root in mod.imports else ".".join(parts)
    return _find_class_by_dotted(index, dotted)


def _find_class_by_dotted(index: ProjectIndex, dotted: str, _seen: set[str] | None = None) -> tuple[str, str] | None:
    if _seen is None:
        _seen = set()
    if dotted in _seen:
        return None
    _seen.add(dotted)
    owner = index.module_for(dotted)
    if owner is None or owner == dotted:
        return None
    rem = dotted[len(owner) + 1 :]
    m = index.modules[owner]
    if rem in m.classes:
        return (owner, rem)
    first, _, rest = rem.partition(".")
    if first in m.imports:  # re-exported class
        chased = m.imports[first] + (f".{rest}" if rest else "")
        return _find_class_by_dotted(index, chased, _seen)
    return None
