from __future__ import annotations

from flowcli.graph import Graph, apply_simulation, build_graph
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_source
from flowcli.resolver import ProjectIndex, resolve_all


def build(src: str, name: str = "m") -> tuple[Graph, ProjectIndex, list]:
    info = parse_source(name, f"{name}.py", src)
    assert not isinstance(info, ParseFailure), info
    modules: dict[str, ModuleInfo] = {name: info}
    index = ProjectIndex(modules)
    resolved = resolve_all(index)
    return build_graph(index, resolved), index, resolved


def test_literal_values_flow_to_parameters() -> None:
    src = "def target(n, label):\n    return n\n\ndef main():\n    target(5, 'hi')\n"
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:main"])
    sim = graph.nodes["m:target"].simulated
    assert sim["args"]["n"]["values"] == ["5"]
    assert sim["args"]["n"]["types"] == ["int"]
    assert sim["args"]["label"]["values"] == ["'hi'"]
    assert sim["args"]["label"]["types"] == ["str"]
    assert sim["sites"] == 1
    assert sim["args"]["n"]["from"] == ["m:main"]


def test_keyword_binding_and_multiple_sites() -> None:
    src = (
        "def target(a, b=0):\n"
        "    return a\n"
        "\n"
        "def one():\n"
        "    target(1)\n"
        "\n"
        "def two():\n"
        "    target(2, b='x')\n"
    )
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:one", "m:two"])
    sim = graph.nodes["m:target"].simulated
    assert sim["args"]["a"]["values"] == ["1", "2"]
    assert sim["args"]["b"]["values"] == ["'x'"]
    assert sim["sites"] == 2


def test_entry_params_seeded_from_annotations() -> None:
    src = "def entry(count: int, name: str = 'x'):\n    return count\n"
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:entry"])
    sim = graph.nodes["m:entry"].simulated
    assert sim["args"]["count"]["types"] == ["int"]
    assert sim["args"]["name"]["values"] == ["'x'"]


def test_types_propagate_across_hops() -> None:
    src = (
        "def leaf(v):\n"
        "    return v\n"
        "\n"
        "def middle(x):\n"
        "    return leaf(x)\n"
        "\n"
        "def main():\n"
        "    middle(7)\n"
    )
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:main"])
    assert graph.nodes["m:middle"].simulated["args"]["x"]["values"] == ["7"]
    assert graph.nodes["m:leaf"].simulated["args"]["v"]["values"] == ["7"]  # forwarded two hops


def test_method_call_skips_self() -> None:
    src = (
        "class Svc:\n"
        "    def handle(self, payload):\n"
        "        return payload\n"
        "\n"
        "def main():\n"
        "    svc = Svc()\n"
        "    svc.handle(b'data')\n"
    )
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:main"])
    sim = graph.nodes["m:Svc.handle"].simulated
    assert "self" not in sim["args"]
    assert sim["args"]["payload"]["values"] == ["b'data'"]


def test_constructor_arg_type_from_return() -> None:
    src = (
        "class Conn:\n"
        "    pass\n"
        "\n"
        "def use(c):\n"
        "    return c\n"
        "\n"
        "def main():\n"
        "    use(Conn())\n"
    )
    graph, index, resolved = build(src)
    apply_simulation(graph, index, resolved, ["m:main"])
    assert graph.nodes["m:use"].simulated["args"]["c"]["types"] == ["Conn"]


def test_simulated_events_are_call_order() -> None:
    src = (
        "def a():\n"
        "    return 1\n"
        "\n"
        "def b():\n"
        "    return a()\n"
        "\n"
        "def main():\n"
        "    a()\n"
        "    b()\n"
    )
    graph, index, resolved = build(src)
    events = apply_simulation(graph, index, resolved, ["m:main"])
    assert events == [["m:main", "m:a"], ["m:main", "m:b"], ["m:b", "m:a"]]


def test_recursion_does_not_unroll(sample_index: ProjectIndex) -> None:
    resolved = resolve_all(sample_index)
    graph = build_graph(sample_index, resolved)
    events = apply_simulation(graph, sample_index, resolved, ["sampleproj.helpers:ping"])
    assert events.count(["sampleproj.helpers:ping", "sampleproj.helpers:pong"]) == 1
    assert len(events) < 10


def test_simulation_runs_without_entry(sample_index: ProjectIndex) -> None:
    resolved = resolve_all(sample_index)
    graph = build_graph(sample_index, resolved)
    events = apply_simulation(graph, sample_index, resolved, None)
    assert events
    assert graph.nodes["sampleproj.helpers:fact"].simulated["args"]["n"]["values"] == ["5"]
