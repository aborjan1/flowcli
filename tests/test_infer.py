from __future__ import annotations

from flowcli.graph import Graph
from flowcli.infer import infer_signatures
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_source
from flowcli.resolver import ProjectIndex


def build(*sources: tuple[str, str]) -> ProjectIndex:
    modules: dict[str, ModuleInfo] = {}
    for name, src in sources:
        info = parse_source(name, f"{name}.py", src)
        assert not isinstance(info, ParseFailure), info
        modules[name] = info
    return ProjectIndex(modules)


def sig_of(index: ProjectIndex, nid: str) -> dict:
    signatures, _ = infer_signatures(index)
    return signatures[nid]


def test_params_extracted_with_defaults_and_varargs() -> None:
    src = "def f(a: int, b=0, *args, c: str = 'x', **kw):\n    pass\n"
    index = build(("m", src))
    params = sig_of(index, "m:f")["params"]
    assert [p["name"] for p in params] == ["a", "b", "*args", "c", "**kw"]
    assert params[0]["ann"] == "int"
    assert params[1]["default"] == "0"
    assert params[3]["ann"] == "str"
    assert params[3]["default"] == "'x'"


def test_returns_annotation_is_ground_truth() -> None:
    index = build(("m", "def f() -> list[int]:\n    return []\n"))
    sig = sig_of(index, "m:f")
    assert sig["returns"] == ["list[int]"]
    assert sig["inferred"] is False


def test_const_return_types_bool_before_int() -> None:
    src = "def f(x):\n    if x:\n        return True\n    return 1\n"
    index = build(("m", src))
    assert sig_of(index, "m:f")["returns"] == ["bool", "int"]


def test_fstring_and_literals() -> None:
    src = "def f(x):\n    if x:\n        return f'v{x}'\n    return [x]\n"
    index = build(("m", src))
    assert sig_of(index, "m:f")["returns"] == ["list", "str"]


def test_no_return_means_none() -> None:
    index = build(("m", "def f():\n    pass\n"))
    sig = sig_of(index, "m:f")
    assert sig["returns"] == ["None"]
    assert sig["inferred"] is True


def test_unknown_only_returns_stay_empty() -> None:
    index = build(("m", "def f():\n    return foo() + 1\n"))
    assert sig_of(index, "m:f")["returns"] == []


def test_generator_flag() -> None:
    index = build(("m", "def g():\n    yield 1\n"))
    assert sig_of(index, "m:g")["returns"] == ["Generator"]


def test_constructor_return_is_class(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.models:make_standalone")["returns"] == ["Standalone"]


def test_typed_local_name_return(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.models:make_engine")["returns"] == ["Engine"]


def test_cls_return_is_own_class(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.models:Engine.build")["returns"] == ["Engine"]


def test_chained_call_fixpoint(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.helpers:util_a")["returns"] == ["int"]
    assert sig_of(sample_index, "sampleproj.helpers:outer")["returns"] == ["int"]  # via nested inner -> util_b


def test_recursion_and_mutual_recursion_terminate(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.helpers:fact")["returns"] == ["int"]
    assert sig_of(sample_index, "sampleproj.helpers:ping")["returns"] == ["int"]
    assert sig_of(sample_index, "sampleproj.helpers:pong")["returns"] == ["int"]


def test_implicit_none_for_init(sample_index: ProjectIndex) -> None:
    assert sig_of(sample_index, "sampleproj.models:Base.__init__")["returns"] == ["None"]


def test_node_signature_and_flow_ret_types(sample_graph: Graph) -> None:
    fact = sample_graph.nodes["sampleproj.helpers:fact"]
    assert fact.signature is not None
    assert fact.signature["returns"] == ["int"]
    assert fact.signature["params"][0]["name"] == "n"
    then_ret = fact.flow[0]["then"][0]
    assert then_ret["t"] == "ret"
    assert then_ret["rt"] == "int"
    util_a = sample_graph.nodes["sampleproj.helpers:util_a"]
    assert util_a.flow[0]["rt"] == "int"  # dep-based line type resolved after the fixpoint
    assert sample_graph.nodes["sampleproj.app:<module>"].signature is None
