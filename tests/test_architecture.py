"""Package boundaries, enforced: each layer imports only the layers below it, and only their public names."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import flowcli

PACKAGE_DIR = Path(flowcli.__file__).parent

# layer -> layers it may import from (the root package itself, for __version__, is always allowed)
ALLOWED: dict[str, set[str]] = {
    "analysis": {"analysis"},
    "graph": {"analysis", "graph"},
    "output": {"analysis", "graph", "output"},
    "runtime": {"analysis", "runtime"},
    "pipeline": {"analysis", "graph", "output"},
    "cli": {"graph", "output", "pipeline", "runtime"},
    "__main__": {"cli"},
}


def _layer(module: str) -> str:
    """'flowcli.graph.build' -> 'graph'; 'flowcli' -> ''."""
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else ""


def _source_modules() -> list[tuple[str, Path]]:
    out = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        rel = path.relative_to(PACKAGE_DIR.parent).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts.pop()
        out.append((".".join(parts), path))
    return out


def _flowcli_imports(tree: ast.Module) -> list[tuple[ast.ImportFrom | ast.Import, str, list[str]]]:
    out: list[tuple[ast.ImportFrom | ast.Import, str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "flowcli":
            out.append((node, node.module, [a.name for a in node.names]))
        elif isinstance(node, ast.Import):
            out += [(node, a.name, []) for a in node.names if a.name.split(".")[0] == "flowcli"]
    return out


MODULES = _source_modules()


@pytest.mark.parametrize(("module", "path"), MODULES, ids=[m for m, _ in MODULES])
def test_layer_dependencies(module: str, path: Path) -> None:
    layer = _layer(module)
    if not layer:
        return  # the root package
    allowed = ALLOWED[layer]
    for node, target, _ in _flowcli_imports(ast.parse(path.read_text(encoding="utf-8"))):
        target_layer = _layer(target)
        assert not target_layer or target_layer in allowed, (
            f"{module}:{node.lineno} imports {target} — the {layer!r} layer may only use {sorted(allowed)}"
        )


@pytest.mark.parametrize(("module", "path"), MODULES, ids=[m for m, _ in MODULES])
def test_no_private_imports_across_modules(module: str, path: Path) -> None:
    for node, target, names in _flowcli_imports(ast.parse(path.read_text(encoding="utf-8"))):
        private = [n for n in names if n.startswith("_") and n != "__version__"]
        assert not private, f"{module}:{node.lineno} imports private {private} from {target}"


@pytest.mark.parametrize(("module", "path"), MODULES, ids=[m for m, _ in MODULES])
def test_flowcli_imports_are_module_level(module: str, path: Path) -> None:
    """A function-local import is how a dependency cycle hides; keep them all at the top."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    top_level = {id(stmt) for stmt in tree.body}
    for node, target, _ in _flowcli_imports(tree):
        assert id(node) in top_level, f"{module}:{node.lineno} imports {target} inside a function"


def test_every_layer_is_known() -> None:
    layers = {_layer(m) for m, _ in MODULES} - {""}
    assert layers == set(ALLOWED), f"update ALLOWED for: {sorted(layers ^ set(ALLOWED))}"
