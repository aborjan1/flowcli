"""File discovery and module-name derivation."""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Sequence
from pathlib import Path

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".tox",
    "node_modules",
    "build",
    "dist",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}


PROJECT_MARKERS = ("pyproject.toml", "setup.py", "setup.cfg")
_MAX_NAMESPACE_WALK = 4


def find_package_prefix(root: Path) -> tuple[Path, str]:
    """Walk upward from `root` while an `__init__.py` marks it as a package.

    Returns (anchor_dir, dotted_prefix): module names are derived relative to
    anchor_dir, so scanning `src/pkg/sub` still yields names like `pkg.sub.x`,
    which keeps relative imports resolvable.

    Packages without `__init__.py` (namespace packages, plain source trees) are
    handled too: the walk continues up to a project marker or a `src/` dir, so
    `src/pkg/sub` still names modules `pkg.sub.x` with no `__init__.py` in sight.
    """
    cur = root.resolve()
    parts: list[str] = []
    while (cur / "__init__.py").is_file() and cur.parent != cur:
        parts.insert(0, cur.name)
        cur = cur.parent
    return (cur, ".".join(parts)) if parts else _namespace_prefix(cur)


def _is_project_root(path: Path) -> bool:
    return path.name == "src" or any((path / marker).is_file() for marker in PROJECT_MARKERS)


def _holds_modules(path: Path) -> bool:
    """True when the directory has .py files of its own — a plausible import-path component."""
    try:
        return any(entry.name.endswith(".py") and entry.is_file() for entry in path.iterdir())
    except OSError:
        return False


def _namespace_prefix(start: Path) -> tuple[Path, str]:
    """Same idea as the __init__.py walk, for trees that simply don't use __init__.py.

    The __init__.py walk gets a positive signal at every step: each directory
    proves it is a package. This walk has none, so it needs its own test for
    whether a directory is really part of an import path.

    A directory that holds modules of its own clearly is. One that holds only
    other directories is only an import path when it sits directly at the
    project root — that is where an empty namespace-package root lives
    (`nspkg/inner/mod.py`). Deeper down, a module-less directory is
    organisation, not packaging (`tests/fixtures/`), so the walk stops below it
    and the start directory becomes its own root. That is what a folder of loose
    scripts importing each other by bare name (`from b import go`) needs.
    """
    probe = start
    namespace: list[str] = []
    for _ in range(_MAX_NAMESPACE_WALK):
        parent = probe.parent
        if parent == probe or _is_project_root(probe):
            break
        namespace.insert(0, probe.name)
        if _is_project_root(parent):
            return parent, ".".join(namespace)
        if not _holds_modules(parent) and not _is_project_root(parent.parent):
            break
        probe = parent
    return start, ""


def derive_module_name(file: Path, anchor: Path) -> str:
    rel = file.resolve().relative_to(anchor)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][: -len(".py")]
    return ".".join(parts)


def _excluded(rel_posix: str, name: str, excludes: Sequence[str]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) or fnmatch.fnmatch(name, pat) for pat in excludes)


def discover(root: Path, excludes: Sequence[str] = ()) -> list[tuple[str, Path]]:
    """Find all .py files under `root` (or `root` itself if it is a file).

    Returns a deterministic list of (dotted_module_name, path). Directory
    symlinks are not followed (os.walk default), so link loops cannot recurse.
    """
    root = root.resolve()
    if root.is_file():
        if root.suffix != ".py":
            return []
        anchor, _ = find_package_prefix(root.parent)
        return [(derive_module_name(root, anchor), root)]

    anchor, _ = find_package_prefix(root)
    out: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dpath = Path(dirpath)
        kept = []
        for d in sorted(dirnames):
            if d in SKIP_DIRS or d.startswith("."):
                continue
            rel = (dpath / d).relative_to(root).as_posix()
            if _excluded(rel, d, excludes):
                continue
            kept.append(d)
        dirnames[:] = kept
        for f in sorted(filenames):
            if not f.endswith(".py"):
                continue
            fpath = dpath / f
            rel = fpath.relative_to(root).as_posix()
            if _excluded(rel, f, excludes):
                continue
            out.append((derive_module_name(fpath, anchor), fpath))
    return out
