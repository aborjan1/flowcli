"""Detect where a package is meant to be entered.

Some code is the surface a user calls (a package's exported API, a CLI, a
`main()`); the rest is interior plumbing reached only from other functions.
This ranks the candidates so `flowcli` can suggest a starting point instead of
making you guess one.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from flowcli.models import MODULE_QUALNAME, ModuleInfo, node_id
from flowcli.resolver import ProjectIndex

MAIN_NAMES = ("main", "run", "cli", "execute", "serve", "start", "app")
MAX_SUGGESTIONS = 12


def detect(index: ProjectIndex, called: set[str], root: Path | None = None) -> list[dict[str, Any]]:
    """Rank entry-point candidates. `called` is the set of node ids with internal callers."""
    found: dict[str, dict[str, Any]] = {}

    def add(nid: str, kind: str, score: int, why: str) -> None:
        prior = found.get(nid)
        if prior is None or score > prior["score"]:
            found[nid] = {"id": nid, "kind": kind, "score": score, "why": why}

    for script in _console_scripts(root):
        nid = _script_to_node(script, index)
        if nid:
            add(nid, "script", 100, f"console script: {script}")

    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        if mod_name.endswith("__main__") and MODULE_QUALNAME in mod.functions:
            add(node_id(mod_name, MODULE_QUALNAME), "script", 95, "python -m entry point")
        for qual, fn in mod.functions.items():
            nid = node_id(mod_name, qual)
            if qual == MODULE_QUALNAME:
                # import-time side effects (a module-level logger, a registry call) are not
                # entry points — only a real script guard or a body-only module is.
                if mod.has_main_guard:
                    add(nid, "script", 92, "runs as a script (__main__ guard)")
                elif fn.raw_calls and not _defines_api(mod):
                    add(nid, "script", 55, "script: top-level code, no functions or classes")
                continue
            bare = qual.rsplit(".", 1)[-1]
            if bare.startswith("_") or "." in qual and qual.split(".")[0] not in mod.classes:
                continue
            if bare in MAIN_NAMES and nid not in called:
                add(nid, "main", 90, f"named {bare}() and never called internally")
            elif nid in _exported(index) and nid not in called:
                add(nid, "public", 75, "exported from the package __init__")
            elif nid not in called and not _is_private_path(mod_name, qual):
                add(nid, "root", 40 + min(len(fn.params), 5), "nothing in the package calls it")

    ranked = sorted(found.values(), key=lambda c: (-c["score"], c["id"]))
    return ranked[:MAX_SUGGESTIONS]


def _defines_api(mod: ModuleInfo) -> bool:
    """True when the module exists to define things, not to do things when imported."""
    return bool(mod.classes) or any(q != MODULE_QUALNAME for q in mod.functions)


def _is_private_path(mod_name: str, qual: str) -> bool:
    if any(part.startswith("_") and part != "__init__" for part in mod_name.split(".")):
        return True
    return any(part.startswith("_") for part in qual.split("."))


def _exported(index: ProjectIndex) -> set[str]:
    """Node ids re-exported from a package __init__ (its import table is the public surface)."""
    out: set[str] = set()
    for mod_name, mod in index.modules.items():
        if not mod.is_package:
            continue
        for target in mod.imports.values():
            owner = index.module_for(target)
            if owner and owner != target:
                rest = target[len(owner) + 1 :]
                candidate = index.modules[owner]
                if rest in candidate.functions or rest in candidate.classes:
                    out.add(node_id(owner, rest))
    return out


def _console_scripts(root: Path | None) -> list[str]:
    """`project.scripts` entries from the nearest pyproject.toml, as 'module:qualname'."""
    if root is None:
        return []
    for base in [root, *root.resolve().parents][:5]:
        pyproject = base / "pyproject.toml"
        if not pyproject.is_file():
            continue
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return []
        scripts = data.get("project", {}).get("scripts", {})
        return [str(v) for v in scripts.values()]
    return []


def _script_to_node(spec: str, index: ProjectIndex) -> str | None:
    """'pkg.cli:main' or 'pkg:__main__.main' -> a node id, when it exists in the parsed index."""
    module, _, qual = spec.partition(":")
    if not qual:
        return None
    qual = qual.removeprefix("__main__.") if module in index.modules else qual
    for candidate_mod, candidate_qual in ((module, qual), (f"{module}.__main__", qual)):
        mod: ModuleInfo | None = index.modules.get(candidate_mod)
        if mod is not None and candidate_qual in mod.functions:
            return node_id(candidate_mod, candidate_qual)
    return None
