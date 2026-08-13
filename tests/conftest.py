from __future__ import annotations

from pathlib import Path

import pytest

from flowcli.discovery import discover
from flowcli.graph import Graph, build_graph
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_module
from flowcli.resolver import ProjectIndex, resolve_all

FIXTURES = Path(__file__).parent / "fixtures"


def build_index(root: Path) -> ProjectIndex:
    modules: dict[str, ModuleInfo] = {}
    for name, path in discover(root):
        info = parse_module(name, path)
        assert not isinstance(info, ParseFailure), info
        modules.setdefault(name, info)
    return ProjectIndex(modules)


@pytest.fixture(scope="session")
def sampleproj_path() -> Path:
    return FIXTURES / "sampleproj"


@pytest.fixture(scope="session")
def looseproj_path() -> Path:
    return FIXTURES / "looseproj"


@pytest.fixture(scope="session")
def sample_index(sampleproj_path: Path) -> ProjectIndex:
    return build_index(sampleproj_path)


@pytest.fixture(scope="session")
def loose_index(looseproj_path: Path) -> ProjectIndex:
    return build_index(looseproj_path)


@pytest.fixture()
def sample_graph(sample_index: ProjectIndex) -> Graph:
    # function-scoped: compute_depths mutates node.depth
    return build_graph(sample_index, resolve_all(sample_index))
