from __future__ import annotations

from flowcli.models import ClassInfo, ModuleInfo, ParseFailure
from flowcli.parser import parse_source
from flowcli.resolver import EXTERNAL, INTERNAL, UNRESOLVED, ProjectIndex, resolve_all, resolve_method


def internal_targets(index: ProjectIndex, caller: str) -> set[str]:
    return {rc.target for rc in resolve_all(index) if rc.caller == caller and rc.status == INTERNAL}


def external_targets(index: ProjectIndex, caller: str) -> set[str]:
    return {rc.target for rc in resolve_all(index) if rc.caller == caller and rc.status == EXTERNAL}


def unresolved_of(index: ProjectIndex, caller: str) -> set[tuple[str, str]]:
    return {(rc.target, rc.reason) for rc in resolve_all(index) if rc.caller == caller and rc.status == UNRESOLVED}


def mini_index(*modules: ModuleInfo | ParseFailure) -> ProjectIndex:
    out: dict[str, ModuleInfo] = {}
    for m in modules:
        assert not isinstance(m, ParseFailure), m
        out[m.name] = m
    return ProjectIndex(out)


def test_same_module_call(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.helpers:util_a") == {"sampleproj.helpers:util_b"}


def test_recursion_self_edge(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.helpers:fact") == {"sampleproj.helpers:fact"}


def test_mutual_recursion(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.helpers:ping") == {"sampleproj.helpers:pong"}
    assert internal_targets(sample_index, "sampleproj.helpers:pong") == {"sampleproj.helpers:ping"}


def test_nested_function_scopes(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.helpers:outer") == {"sampleproj.helpers:outer.inner"}
    assert internal_targets(sample_index, "sampleproj.helpers:outer.inner") == {"sampleproj.helpers:util_b"}


def test_from_import_cross_module(sample_index: ProjectIndex) -> None:
    targets = internal_targets(sample_index, "sampleproj.app:main")
    assert "sampleproj.helpers:util_a" in targets
    assert "sampleproj.helpers:fact" in targets


def test_alias_module_dotted_call(sample_index: ProjectIndex) -> None:
    assert "sampleproj.helpers:util_b" in internal_targets(sample_index, "sampleproj.app:main")


def test_classname_call_resolves_to_inherited_init(sample_index: ProjectIndex) -> None:
    assert "sampleproj.models:Base.__init__" in internal_targets(sample_index, "sampleproj.app:main")


def test_classname_call_resolves_to_own_init(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.models:make_standalone") == {
        "sampleproj.models:Standalone.__init__"
    }


def test_super_call_targets_base(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.models:Engine.start") == {"sampleproj.models:Base.start"}


def test_self_dispatch_stays_in_own_hierarchy(sample_index: ProjectIndex) -> None:
    # Base.start's self.step() must NOT resolve downward into Engine.step
    assert unresolved_of(sample_index, "sampleproj.models:Base.start") == {("self.step", "not-found-in-hierarchy")}
    assert internal_targets(sample_index, "sampleproj.models:Base.start") == set()


def test_cls_call_in_classmethod(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.models:Engine.build") == {"sampleproj.models:Base.__init__"}


def test_externals_and_builtins(sample_index: ProjectIndex) -> None:
    assert external_targets(sample_index, "sampleproj.app:main") == {"os.path.join", "builtins.print"}


def test_constructor_assignment_type_inference(sample_index: ProjectIndex) -> None:
    # engine = Engine(); engine.start() -> resolved through the parsed hierarchy
    assert "sampleproj.models:Engine.start" in internal_targets(sample_index, "sampleproj.app:main")
    # engine.run() infers Engine but no run() exists anywhere in the parsed hierarchy
    assert ("engine.run", "not-found-in-hierarchy") in unresolved_of(sample_index, "sampleproj.models:make_engine")


def test_annotated_param_dispatch() -> None:
    src = "class Svc:\n    def run(self):\n        return 1\n\ndef use(svc: Svc):\n    return svc.run()\n"
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert internal_targets(index, "m:use") == {"m:Svc.run"}


def test_annotated_param_optional_union() -> None:
    src = (
        "class Svc:\n"
        "    def run(self):\n"
        "        return 1\n"
        "\n"
        "def a(svc: Svc | None):\n"
        "    return svc.run()\n"
        "\n"
        "def b(svc: 'Svc'):\n"
        "    return svc.run()\n"
    )
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert internal_targets(index, "m:a") == {"m:Svc.run"}
    assert internal_targets(index, "m:b") == {"m:Svc.run"}


def test_self_attribute_chain_dispatch() -> None:
    src = (
        "class DB:\n"
        "    def update(self):\n"
        "        return 1\n"
        "\n"
        "class Svc:\n"
        "    def __init__(self):\n"
        "        self.db = DB()\n"
        "\n"
        "    def go(self):\n"
        "        return self.db.update()\n"
    )
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert "m:DB.update" in internal_targets(index, "m:Svc.go")


def test_self_attribute_chain_via_annotation_and_base() -> None:
    src = (
        "class DB:\n"
        "    def update(self):\n"
        "        return 1\n"
        "\n"
        "class Base:\n"
        "    db: DB\n"
        "\n"
        "class Svc(Base):\n"
        "    def go(self):\n"
        "        return self.db.update()\n"
    )
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert "m:DB.update" in internal_targets(index, "m:Svc.go")


def test_self_attr_unparsed_type_stays_unresolved() -> None:
    src = (
        "import sqlite3\n"
        "\n"
        "class Svc:\n"
        "    def __init__(self):\n"
        "        self.conn = sqlite3.connect('x')\n"
        "\n"
        "    def go(self):\n"
        "        return self.conn.execute('q')\n"
    )
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert ("self.conn.execute", "instance-attr") in unresolved_of(index, "m:Svc.go")


def test_unparsed_annotation_stays_unresolved() -> None:
    # p: Path names a class we never parsed -> no recursion into stdlib
    src = "from pathlib import Path\n\ndef rm(p: Path):\n    p.unlink()\n"
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert unresolved_of(index, "m:rm") == {("p.unlink", "instance-attr")}


def test_subpackage_relative_import_and_alias(sample_index: ProjectIndex) -> None:
    caller = "sampleproj.sub.worker:work"
    assert internal_targets(sample_index, caller) == {
        "sampleproj.models:Base.__init__",
        "sampleproj.helpers:util_b",
    }
    assert external_targets(sample_index, caller) == {"os.path.join", "builtins.str"}


def test_star_import_resolution(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.stars:use_star") == {"sampleproj.helpers:util_b"}


def test_decorator_edge_from_module_node(sample_index: ProjectIndex) -> None:
    assert internal_targets(sample_index, "sampleproj.decor:<module>") == {"sampleproj.decor:deco"}


def test_same_name_distinct_modules(loose_index: ProjectIndex) -> None:
    assert internal_targets(loose_index, "a:run") == {"b:go", "a:util_a"}


def test_reexport_chase() -> None:
    pkg = parse_source("pkg", "pkg/__init__.py", "from .impl import f\n", is_package=True)
    impl = parse_source("pkg.impl", "pkg/impl.py", "def f():\n    pass\n")
    user = parse_source("user", "user.py", "import pkg\n\ndef go():\n    pkg.f()\n")
    index = mini_index(pkg, impl, user)
    assert internal_targets(index, "user:go") == {"pkg.impl:f"}


def test_unknown_name() -> None:
    m = parse_source("m", "m.py", "def go():\n    mystery()\n")
    index = mini_index(m)
    assert unresolved_of(index, "m:go") == {("mystery", "unknown-name")}


def test_deep_self_chain_is_instance_attr() -> None:
    m = parse_source("m", "m.py", "class C:\n    def m(self):\n        self.helper.run()\n")
    index = mini_index(m)
    assert unresolved_of(index, "m:C.m") == {("self.helper.run", "instance-attr")}


def test_bare_name_does_not_leak_class_scope() -> None:
    # step() inside a method is NOT a call to the class's step method in Python
    src = "class C:\n    def step(self):\n        pass\n\n    def go(self):\n        step()\n"
    m = parse_source("m", "m.py", src)
    index = mini_index(m)
    assert unresolved_of(index, "m:C.go") == {("step", "unknown-name")}


def test_hierarchy_cycle_guard() -> None:
    m = ModuleInfo(name="m", file="m.py", is_package=False)
    m.classes["A"] = ClassInfo(qualname="A", module="m", lineno=1, bases=[("B",)])
    m.classes["B"] = ClassInfo(qualname="B", module="m", lineno=2, bases=[("A",)])
    index = ProjectIndex({"m": m})
    assert resolve_method(index, "m", "A", "nope") is None


def test_cross_module_base_method(sample_index: ProjectIndex) -> None:
    # Engine (models) inherits from Base (same module) — resolve through resolve_method directly
    assert resolve_method(sample_index, "sampleproj.models", "Engine", "stop") == "sampleproj.models:Base.stop"
