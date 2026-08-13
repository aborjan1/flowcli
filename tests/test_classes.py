from __future__ import annotations

from flowcli.classes import build_class_graph, scope_class_graph
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_source
from flowcli.resolver import ProjectIndex

MEASUREMENT = (
    "from enum import StrEnum\n"
    "from dataclasses import dataclass\n"
    "\n"
    "class Unit(StrEnum):\n"
    "    MM = 'mm'\n"
    "    CM = 'cm'\n"
    "\n"
    "@dataclass\n"
    "class Measurement:\n"
    "    value: float\n"
    "    unit: Unit\n"
    "\n"
    "    def convert(self, target: Unit) -> float:\n"
    "        return self.value\n"
    "\n"
    "    def _private(self):\n"
    "        pass\n"
)


def build(*sources: tuple[str, str]) -> ProjectIndex:
    modules: dict[str, ModuleInfo] = {}
    for name, src in sources:
        info = parse_source(name, f"{name}.py", src)
        assert not isinstance(info, ParseFailure), info
        modules[name] = info
    return ProjectIndex(modules)


def test_properties_and_types() -> None:
    graph = build_class_graph(build(("m", MEASUREMENT)))
    meas = graph.nodes["m:Measurement"]
    assert [(f["name"], f["type"]) for f in meas.fields] == [("value", "float"), ("unit", "Unit")]
    assert meas.stereotype == "dataclass"


def test_composition_edge_labelled_by_property() -> None:
    graph = build_class_graph(build(("m", MEASUREMENT)))
    has = [e for e in graph.edges if e.kind == "has"]
    assert len(has) == 1
    assert (has[0].source, has[0].target, has[0].label) == ("m:Measurement", "m:Unit", "unit")


def test_enum_stereotype_and_members() -> None:
    graph = build_class_graph(build(("m", MEASUREMENT)))
    unit = graph.nodes["m:Unit"]
    assert unit.stereotype == "enum"
    assert [(f["name"], f["value"]) for f in unit.fields] == [("MM", "'mm'"), ("CM", "'cm'")]
    assert unit.bases == ["StrEnum"]


def test_inheritance_edge_between_parsed_classes() -> None:
    src = "class Base:\n    pass\n\nclass Child(Base):\n    pass\n"
    graph = build_class_graph(build(("m", src)))
    inherits = [e for e in graph.edges if e.kind == "inherits"]
    assert (inherits[0].source, inherits[0].target) == ("m:Child", "m:Base")


def test_unparsed_base_shows_but_makes_no_edge() -> None:
    graph = build_class_graph(build(("m", MEASUREMENT)))
    assert graph.nodes["m:Unit"].bases == ["StrEnum"]  # displayed
    assert graph.nodes["m:Unit"].base_refs == [None]  # not resolvable -> not expandable
    assert not [e for e in graph.edges if e.target.endswith(":StrEnum")]  # but not a node


def test_base_refs_resolve_to_parsed_classes() -> None:
    src = "class Base:\n    x: int\n\nclass Child(Base):\n    y: int\n"
    graph = build_class_graph(build(("m", src)))
    child = graph.nodes["m:Child"]
    assert child.bases == ["Base"]
    assert child.base_refs == ["m:Base"]  # the panel can expand this one inline


def test_cross_module_composition() -> None:
    units = "from enum import StrEnum\n\nclass Unit(StrEnum):\n    MM = 'mm'\n"
    core = "from units import Unit\n\nclass Reading:\n    def __init__(self):\n        self.unit = Unit()\n"
    graph = build_class_graph(build(("units", units), ("core", core)))
    has = [e for e in graph.edges if e.kind == "has"]
    assert (has[0].source, has[0].target, has[0].label) == ("core:Reading", "units:Unit", "unit")


def test_methods_listed_public_plus_init() -> None:
    graph = build_class_graph(build(("m", MEASUREMENT)))
    names = [m["name"] for m in graph.nodes["m:Measurement"].methods]
    assert names == ["convert"]
    assert graph.nodes["m:Measurement"].methods[0]["id"] == "m:Measurement.convert"


def test_init_attributes_become_properties() -> None:
    src = "class Store:\n    def __init__(self):\n        self.count = 0\n        self.name: str = 'x'\n"
    graph = build_class_graph(build(("m", src)))
    assert [f["name"] for f in graph.nodes["m:Store"].fields] == ["count", "name"]
    assert graph.nodes["m:Store"].fields[1]["type"] == "str"


def test_scope_keeps_referenced_classes() -> None:
    units = "from enum import StrEnum\n\nclass Unit(StrEnum):\n    MM = 'mm'\n"
    core = "from units import Unit\n\nclass Reading:\n    unit: Unit\n"
    graph = build_class_graph(build(("units", units), ("core", core)))
    scoped = scope_class_graph(graph, {"core"})
    assert "core:Reading" in scoped.nodes
    assert "units:Unit" in scoped.nodes  # pulled in because Reading points at it
    assert len(scoped.edges) == 1


def test_deterministic_ordering() -> None:
    index = build(("m", MEASUREMENT))
    first, second = build_class_graph(index), build_class_graph(index)
    assert list(first.nodes) == list(second.nodes) == sorted(first.nodes)
    assert [(e.source, e.target, e.kind) for e in first.edges] == [(e.source, e.target, e.kind) for e in second.edges]
