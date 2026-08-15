from __future__ import annotations

from pathlib import Path

from flowcli.discovery import discover, find_package_prefix


def names(entries: list[tuple[str, Path]]) -> list[str]:
    return [n for n, _ in entries]


def test_package_scan_names(sampleproj_path: Path) -> None:
    got = dict(discover(sampleproj_path))
    assert set(got) == {
        "sampleproj",
        "sampleproj.app",
        "sampleproj.decor",
        "sampleproj.helpers",
        "sampleproj.models",
        "sampleproj.stars",
        "sampleproj.sub",
        "sampleproj.sub.worker",
    }
    assert got["sampleproj"].name == "__init__.py"
    assert got["sampleproj.sub"].name == "__init__.py"


def test_package_prefix_walkup(sampleproj_path: Path) -> None:
    sub = sampleproj_path / "sub"
    anchor, prefix = find_package_prefix(sub)
    assert prefix == "sampleproj.sub"
    assert anchor == sampleproj_path.parent.resolve()
    assert names(discover(sub)) == ["sampleproj.sub", "sampleproj.sub.worker"]


def test_loose_scripts(looseproj_path: Path) -> None:
    assert names(discover(looseproj_path)) == ["a", "b"]


def test_loose_scripts_below_a_container_dir(tmp_path: Path) -> None:
    """A module-less directory below the project root is organisation, not an import path."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("", encoding="utf-8")
    scripts = tmp_path / "tests" / "fixtures" / "demo"
    scripts.mkdir(parents=True)
    (scripts / "a.py").write_text("import b\n", encoding="utf-8")
    (scripts / "b.py").write_text("def go():\n    pass\n", encoding="utf-8")
    anchor, prefix = find_package_prefix(scripts)
    assert prefix == ""  # not tests.fixtures.demo — the scripts import each other by bare name
    assert anchor == scripts.resolve()
    assert names(discover(scripts)) == ["a", "b"]


def test_single_file_input(sampleproj_path: Path) -> None:
    assert names(discover(sampleproj_path / "app.py")) == ["sampleproj.app"]


def test_skips_pycache_and_hidden(tmp_path: Path) -> None:
    (tmp_path / "z.py").write_text("x = 1\n", encoding="utf-8")
    pyc = tmp_path / "__pycache__"
    pyc.mkdir()
    (pyc / "junk.py").write_text("x = 1\n", encoding="utf-8")
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "y.py").write_text("x = 1\n", encoding="utf-8")
    assert names(discover(tmp_path)) == ["z"]


def test_exclude_glob(sampleproj_path: Path) -> None:
    got = names(discover(sampleproj_path, excludes=["sub/*"]))
    assert "sampleproj.sub.worker" not in got
    assert "sampleproj.app" in got
