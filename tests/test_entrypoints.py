from __future__ import annotations

from pathlib import Path

from flowcli.discovery import discover, find_package_prefix
from flowcli.entrypoints import detect
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_module
from flowcli.resolver import ProjectIndex, resolve_all


def index_of(root: Path) -> ProjectIndex:
    modules: dict[str, ModuleInfo] = {}
    for name, path in discover(root):
        info = parse_module(name, path)
        assert not isinstance(info, ParseFailure), info
        modules.setdefault(name, info)
    return ProjectIndex(modules)


def suggestions(root: Path) -> list[dict]:
    index = index_of(root)
    called = {rc.target for rc in resolve_all(index) if rc.status == "internal"}
    return detect(index, called, root)


def test_main_function_ranks_high(sampleproj_path: Path) -> None:
    found = suggestions(sampleproj_path)
    ids = [s["id"] for s in found]
    assert "sampleproj.app:main" in ids
    top = found[ids.index("sampleproj.app:main")]
    assert top["kind"] in ("main", "script")


def test_internal_helpers_are_not_suggested(sampleproj_path: Path) -> None:
    ids = {s["id"] for s in suggestions(sampleproj_path)}
    assert "sampleproj.helpers:util_b" not in ids  # called by util_a — interior plumbing
    assert "sampleproj.models:Base.start" not in ids


def test_public_exports_detected(sampleproj_path: Path) -> None:
    # sampleproj/__init__.py does `from .helpers import util_a`
    found = {s["id"]: s for s in suggestions(sampleproj_path)}
    assert "sampleproj.helpers:util_a" in found
    assert found["sampleproj.helpers:util_a"]["kind"] == "public"


def test_uncalled_roots_included(sampleproj_path: Path) -> None:
    ids = {s["id"] for s in suggestions(sampleproj_path)}
    assert "sampleproj.sub.worker:work" in ids  # nothing calls it


def test_import_time_calls_are_not_entry_points(tmp_path: Path) -> None:
    pkg = tmp_path / "noisy"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    # a module-level logger call must NOT make this module look like a script
    (pkg / "client.py").write_text(
        "import logging\n\nlogger = logging.getLogger(__name__)\n\ndef connect():\n    pass\n", encoding="utf-8"
    )
    ids = {s["id"] for s in suggestions(pkg)}
    assert "noisy.client:<module>" not in ids
    assert "noisy.client:connect" in ids


def test_main_guard_module_is_a_script_entry(tmp_path: Path) -> None:
    pkg = tmp_path / "guarded"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "tool.py").write_text("def run():\n    pass\n\nif __name__ == '__main__':\n    run()\n", encoding="utf-8")
    found = {s["id"]: s for s in suggestions(pkg)}
    assert found["guarded.tool:<module>"]["kind"] == "script"
    assert "__main__ guard" in found["guarded.tool:<module>"]["why"]


def test_body_only_script_is_an_entry(tmp_path: Path) -> None:
    pkg = tmp_path / "plain"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "go.py").write_text("import os\n\nprint(os.getcwd())\n", encoding="utf-8")
    ids = {s["id"] for s in suggestions(pkg)}
    assert "plain.go:<module>" in ids  # nothing but top-level code — that IS the entry


def test_namespace_package_keeps_dotted_prefix(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    pkg = tmp_path / "nspkg" / "inner"
    pkg.mkdir(parents=True)
    (pkg / "mod.py").write_text("def go():\n    pass\n", encoding="utf-8")
    anchor, prefix = find_package_prefix(pkg)
    assert prefix == "nspkg.inner"  # no __init__.py anywhere, still correctly rooted
    assert anchor == tmp_path.resolve()
    assert [name for name, _ in discover(pkg)] == ["nspkg.inner.mod"]


def test_console_script_detected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n[project.scripts]\ndemo = 'demo.cli:main'\n", encoding="utf-8"
    )
    pkg = tmp_path / "demo"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "cli.py").write_text("def main():\n    helper()\n\ndef helper():\n    pass\n", encoding="utf-8")
    found = suggestions(pkg)
    assert found[0]["id"] == "demo.cli:main"
    assert found[0]["kind"] == "script"
