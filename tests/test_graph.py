from __future__ import annotations

from pathlib import Path

import pytest

from flowcli.graph import (
    Graph,
    build_graph,
    compute_depths,
    parse_entry_spec,
    parse_entry_specs,
    prune_unreachable,
    split_entry_spec,
)
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_source
from flowcli.resolver import ProjectIndex, resolve_all


def test_called_by_inverse(sample_graph: Graph) -> None:
    util_b = sample_graph.nodes["sampleproj.helpers:util_b"]
    assert "sampleproj.helpers:util_a" in util_b.called_by
    assert "sampleproj.app:main" in util_b.called_by
    assert "sampleproj.stars:use_star" in util_b.called_by
    assert "sampleproj.helpers:outer.inner" in util_b.called_by


def test_call_multiplicity_single_edge(sample_graph: Graph) -> None:
    main = sample_graph.nodes["sampleproj.app:main"]
    assert main.static_call_count["sampleproj.helpers:util_a"] == 2
    assert main.calls.count("sampleproj.helpers:util_a") == 1


def test_node_kinds(sample_graph: Graph) -> None:
    nodes = sample_graph.nodes
    assert nodes["sampleproj.app:<module>"].kind == "module"
    assert nodes["sampleproj.models:Engine.start"].kind == "method"
    assert nodes["sampleproj.helpers:util_a"].kind == "function"


def test_module_node_calls_main(sample_graph: Graph) -> None:
    assert "sampleproj.app:main" in sample_graph.nodes["sampleproj.app:<module>"].calls


def test_nodes_sorted_and_depth_none_by_default(sample_graph: Graph) -> None:
    ids = list(sample_graph.nodes)
    assert ids == sorted(ids)
    assert all(n.depth is None for n in sample_graph.nodes.values())


def test_bfs_depths(sample_graph: Graph) -> None:
    unreachable = compute_depths(sample_graph, "sampleproj.app:main")
    nodes = sample_graph.nodes
    assert nodes["sampleproj.app:main"].depth == 0
    assert nodes["sampleproj.helpers:util_a"].depth == 1
    assert nodes["sampleproj.helpers:util_b"].depth == 1  # direct edge via h.util_b()
    assert nodes["sampleproj.models:Base.__init__"].depth == 1
    assert nodes["sampleproj.helpers:ping"].depth is None
    assert nodes["sampleproj.app:<module>"].depth is None  # nothing calls module top level
    assert unreachable >= 2
    assert sample_graph.entry == "sampleproj.app:main"


def test_bfs_recursion_terminates(sample_graph: Graph) -> None:
    compute_depths(sample_graph, "sampleproj.helpers:ping")
    assert sample_graph.nodes["sampleproj.helpers:ping"].depth == 0
    assert sample_graph.nodes["sampleproj.helpers:pong"].depth == 1


def test_entry_spec_forms(sample_index: ProjectIndex, sampleproj_path: Path) -> None:
    assert parse_entry_spec("sampleproj.app:main", sample_index) == ("sampleproj.app:main", ["sampleproj.app:main"])
    file_spec = f"{sampleproj_path / 'app.py'}:main"
    assert parse_entry_spec(file_spec, sample_index)[1] == ["sampleproj.app:main"]
    label, ids = parse_entry_spec("sampleproj.app", sample_index)
    assert label == "sampleproj.app (module)"
    assert set(ids) == {"sampleproj.app:main", "sampleproj.app:<module>"}


def test_multiple_entries_merge(sample_index: ProjectIndex) -> None:
    label, ids = parse_entry_specs(["sampleproj.app:main", "sampleproj.helpers:ping"], sample_index)
    assert ids == ["sampleproj.app:main", "sampleproj.helpers:ping"]
    assert label == "2 entries: sampleproj.app:main, sampleproj.helpers:ping"


def test_multiple_entries_mix_kinds(sample_index: ProjectIndex, sampleproj_path: Path) -> None:
    specs = [str(sampleproj_path / "sub"), "sampleproj.app:main", "sampleproj.helpers"]
    _label, ids = parse_entry_specs(specs, sample_index)
    assert "sampleproj.sub.worker:work" in ids  # folder
    assert "sampleproj.app:main" in ids  # single function
    assert "sampleproj.helpers:fact" in ids  # whole module
    assert ids == sorted(ids)


def test_multiple_entries_dedupe(sample_index: ProjectIndex) -> None:
    # the module entry already contains the function entry — it must appear once
    _label, ids = parse_entry_specs(["sampleproj.helpers", "sampleproj.helpers:fact"], sample_index)
    assert ids.count("sampleproj.helpers:fact") == 1


def test_many_entries_label_truncates(sample_index: ProjectIndex) -> None:
    specs = [
        "sampleproj.app:main",
        "sampleproj.helpers:ping",
        "sampleproj.helpers:pong",
        "sampleproj.helpers:fact",
    ]
    label, _ids = parse_entry_specs(specs, sample_index)
    assert label.startswith("4 entries: ")
    assert label.endswith("+1 more")


def test_single_entry_keeps_plain_label(sample_index: ProjectIndex) -> None:
    label, ids = parse_entry_specs(["sampleproj.app:main"], sample_index)
    assert label == "sampleproj.app:main"
    assert ids == ["sampleproj.app:main"]


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("mod.py", ("mod.py", None)),
        ("mod.py:main", ("mod.py", "main")),
        ("pkg.mod", ("pkg.mod", None)),
        ("pkg.mod:Cls.meth", ("pkg.mod", "Cls.meth")),
        ("a:run", ("a", "run")),  # single-letter module, not a drive
        ("relative/dir", ("relative/dir", None)),
        (r"C:\src\app.py", (r"C:\src\app.py", None)),
        (r"C:\src\app.py:main", (r"C:\src\app.py", "main")),
        ("C:/src/app.py:main", ("C:/src/app.py", "main")),
        (r"C:\src\sub", (r"C:\src\sub", None)),
    ],
)
def test_split_entry_spec(spec: str, expected: tuple[str, str | None]) -> None:
    assert split_entry_spec(spec) == expected


def test_directory_entry_covers_whole_subtree(sample_index: ProjectIndex, sampleproj_path: Path) -> None:
    label, ids = parse_entry_spec(str(sampleproj_path / "sub"), sample_index)
    assert label == "sub/ (2 modules)"  # sub/__init__.py + sub/worker.py
    assert ids == ["sampleproj.sub.worker:work"]


def test_directory_entry_accepts_trailing_slash(sample_index: ProjectIndex, sampleproj_path: Path) -> None:
    label, ids = parse_entry_spec(f"{sampleproj_path / 'sub'}/", sample_index)
    assert ids == ["sampleproj.sub.worker:work"]
    assert label.startswith("sub/")


def test_package_name_entry_covers_subtree(sample_index: ProjectIndex) -> None:
    label, ids = parse_entry_spec("sampleproj.sub", sample_index)
    assert label == "sampleproj.sub (2 modules)"
    assert ids == ["sampleproj.sub.worker:work"]


def test_root_package_entry_covers_everything(sample_index: ProjectIndex) -> None:
    _label, ids = parse_entry_spec("sampleproj", sample_index)
    assert "sampleproj.app:main" in ids
    assert "sampleproj.sub.worker:work" in ids  # nested subpackage included
    assert "sampleproj.helpers:util_b" in ids


def test_directory_without_modules_errors(sample_index: ProjectIndex, tmp_path: Path) -> None:
    empty = tmp_path / "nothing"
    empty.mkdir()
    with pytest.raises(ValueError, match="no parsed modules"):
        parse_entry_spec(str(empty), sample_index)


def test_module_entry_scopes_to_file_ecosystem(sample_graph: Graph, sample_index: ProjectIndex) -> None:
    label, ids = parse_entry_spec("sampleproj.helpers", sample_index)
    compute_depths(sample_graph, ids)
    assert all(sample_graph.nodes[nid].depth == 0 for nid in ids)
    prune_unreachable(sample_graph)
    assert set(sample_graph.nodes) == {
        "sampleproj.helpers:fact",
        "sampleproj.helpers:outer",
        "sampleproj.helpers:outer.inner",
        "sampleproj.helpers:ping",
        "sampleproj.helpers:pong",
        "sampleproj.helpers:util_a",
        "sampleproj.helpers:util_b",
    }


def test_entry_spec_suggestions(sample_index: ProjectIndex) -> None:
    with pytest.raises(ValueError, match="main"):
        parse_entry_spec("sampleproj.app:mian", sample_index)
    with pytest.raises(ValueError, match="not found"):
        parse_entry_spec("nosuch.module:f", sample_index)


def test_include_external_creates_nodes(sample_index: ProjectIndex) -> None:
    graph = build_graph(sample_index, resolve_all(sample_index), include_external=True)
    assert "os.path.join" in graph.nodes
    assert graph.nodes["os.path.join"].kind == "external"
    assert "sampleproj.app:main" in graph.nodes["os.path.join"].called_by
    assert not any(u.reason == "external" for u in graph.unresolved)


def test_external_unresolved_by_default(sample_graph: Graph) -> None:
    assert any(u.callee_expr == "os.path.join" and u.reason == "external" for u in sample_graph.unresolved)
    assert "os.path.join" not in sample_graph.nodes


def test_dead_code_candidates_have_no_callers(sample_graph: Graph) -> None:
    # ping/pong call each other but nothing else calls them
    ping = sample_graph.nodes["sampleproj.helpers:ping"]
    assert ping.called_by == ["sampleproj.helpers:pong"]


def test_depth_limit(sample_graph: Graph) -> None:
    compute_depths(sample_graph, "sampleproj.app:<module>", max_depth=1)
    nodes = sample_graph.nodes
    assert nodes["sampleproj.app:<module>"].depth == 0
    assert nodes["sampleproj.app:main"].depth == 1
    assert nodes["sampleproj.helpers:util_a"].depth is None  # 2 hops away — beyond the limit
    removed = prune_unreachable(sample_graph)
    assert removed > 0
    assert set(sample_graph.nodes) == {"sampleproj.app:<module>", "sampleproj.app:main"}
    assert sample_graph.nodes["sampleproj.app:main"].calls == []  # edges past the depth fence scrubbed


def test_prune_unreachable_scopes_graph(sample_graph: Graph) -> None:
    unreachable = compute_depths(sample_graph, "sampleproj.app:main")
    removed = prune_unreachable(sample_graph)
    assert removed == unreachable
    assert "sampleproj.app:main" in sample_graph.nodes
    assert "sampleproj.helpers:ping" not in sample_graph.nodes
    assert all(n.depth is not None for n in sample_graph.nodes.values())
    util_b = sample_graph.nodes["sampleproj.helpers:util_b"]
    assert "sampleproj.app:main" in util_b.called_by
    assert "sampleproj.stars:use_star" not in util_b.called_by  # pruned caller scrubbed from back-refs
    assert all(u.caller in sample_graph.nodes for u in sample_graph.unresolved)
    assert prune_unreachable(sample_graph) == 0  # idempotent


def test_flow_call_annotation(sample_graph: Graph) -> None:
    flow = sample_graph.nodes["sampleproj.helpers:util_a"].flow
    assert flow[0]["t"] == "ret"
    assert flow[0]["calls"] == ["sampleproj.helpers:util_b"]


def test_flow_branch_head_annotation() -> None:
    src = "def a():\n    return 1\n\ndef f(x):\n    if a():\n        return 2\n    return 3\n"
    info = parse_source("m", "m.py", src)
    assert not isinstance(info, ParseFailure)
    modules: dict[str, ModuleInfo] = {"m": info}
    index = ProjectIndex(modules)
    graph = build_graph(index, resolve_all(index))
    flow = graph.nodes["m:f"].flow
    assert flow[0]["t"] == "if"
    assert flow[0]["calls"] == ["m:a"]
    assert flow[0]["then"][0]["calls"] == []
