"""Entry specs — `file.py`, `file.py:func`, `pkg.mod:Class.m`, a folder — resolved to seed node ids."""

from __future__ import annotations

import difflib
from collections.abc import Sequence
from pathlib import Path

from flowcli.analysis.index import ProjectIndex
from flowcli.analysis.model import ModuleInfo, node_id


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


def split_entry_spec(spec: str) -> tuple[str, str | None]:
    """Split an entry spec into (module-or-path, qualname or None).

    A leading Windows drive letter belongs to the path, not to a qualname:
    `C:\\src\\app.py` is one path, `C:\\src\\app.py:main` is that path plus
    `main`. A single-letter *module* is not a drive though — `a:run` must stay
    module `a`, function `run` — so the drive test requires the separator that a
    drive-rooted path always carries.
    """
    drive = 2 if len(spec) > 2 and spec[0].isalpha() and spec[1] == ":" and spec[2] in "\\/" else 0
    head, sep, qual = spec[drive:].rpartition(":")
    if not sep:
        return spec, None
    return spec[:drive] + head, qual


def parse_entry_spec(spec: str, index: ProjectIndex) -> tuple[str, list[str]]:
    """Resolve an entry spec to (display label, seed node ids).

    'path/to/mod.py:qualname' / 'dotted.module:qualname' -> that one function.
    'path/to/mod.py' / 'dotted.module' (no qualname) -> every function the module defines.
    'path/to/dir' / 'dotted.package' -> every function in every module beneath it,
    subpackages included — the whole folder's ecosystem.
    """
    mod_part, qual = split_entry_spec(spec)

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
