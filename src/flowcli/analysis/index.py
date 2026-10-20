"""The project-wide symbol index: which modules exist, and where a class or method lives.

Every pass after parsing asks the same questions — "what parsed class does this
dotted expression name?", "which def does `Cls.method` reach through the bases?" —
so they are answered here, once, rather than inside call resolution.
"""

from __future__ import annotations

from flowcli.analysis.model import ModuleInfo, node_id

ClassRef = tuple[str, str]  # (module, class qualname)


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

    def find_class(self, mod: ModuleInfo, parts: tuple[str, ...]) -> ClassRef | None:
        """Resolve a class expression's dotted parts, seen from `mod`'s namespace, to a parsed class."""
        root = parts[0]
        if len(parts) == 1:
            if root in mod.classes:
                return (mod.name, root)
            if root in mod.imports:
                return self._find_class_by_dotted(mod.imports[root])
            for star_mod in mod.star_imports:
                sm = self.modules.get(star_mod)
                if sm is not None and root in sm.classes:
                    return (star_mod, root)
            return None
        dotted = ".".join((mod.imports[root], *parts[1:])) if root in mod.imports else ".".join(parts)
        return self._find_class_by_dotted(dotted)

    def type_display(self, mod: ModuleInfo, parts: tuple[str, ...]) -> str:
        """Display name for a type expression: the parsed class's qualname, else the expression as written."""
        ref = self.find_class(mod, parts)
        return ref[1] if ref is not None else ".".join(parts)

    def resolve_method(
        self,
        module: str,
        class_qualname: str,
        method: str,
        *,
        skip_self: bool = False,
        _seen: set[ClassRef] | None = None,
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

        mod = self.modules.get(module)
        ci = mod.classes.get(class_qualname) if mod is not None else None
        if mod is None or ci is None:
            return None
        if not skip_self and method in ci.methods:
            return node_id(module, ci.methods[method])
        for base_parts in ci.bases:
            ref = self.find_class(mod, base_parts)
            if ref is not None:
                target = self.resolve_method(ref[0], ref[1], method, _seen=_seen)
                if target:
                    return target
        return None

    def attr_type(
        self, module: str, class_qualname: str, attr: str, _seen: set[ClassRef] | None = None
    ) -> tuple[str, tuple[str, ...]] | None:
        """Locate self.<attr>'s recorded type parts in the class or its parsed bases: (declaring_module, parts)."""
        if _seen is None:
            _seen = set()
        key = (module, class_qualname)
        if key in _seen:
            return None
        _seen.add(key)
        mod = self.modules.get(module)
        ci = mod.classes.get(class_qualname) if mod is not None else None
        if mod is None or ci is None:
            return None
        if attr in ci.attr_types:
            return (module, ci.attr_types[attr])
        for base_parts in ci.bases:
            ref = self.find_class(mod, base_parts)
            if ref is not None:
                found = self.attr_type(ref[0], ref[1], attr, _seen)
                if found is not None:
                    return found
        return None

    def _find_class_by_dotted(self, dotted: str, _seen: set[str] | None = None) -> ClassRef | None:
        if _seen is None:
            _seen = set()
        if dotted in _seen:
            return None
        _seen.add(dotted)
        owner = self.module_for(dotted)
        if owner is None or owner == dotted:
            return None
        rem = dotted[len(owner) + 1 :]
        m = self.modules[owner]
        if rem in m.classes:
            return (owner, rem)
        first, _, rest = rem.partition(".")
        if first in m.imports:  # re-exported class
            chased = m.imports[first] + (f".{rest}" if rest else "")
            return self._find_class_by_dotted(chased, _seen)
        return None
