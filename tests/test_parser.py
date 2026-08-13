from __future__ import annotations

from pathlib import Path

from flowcli.models import MODULE_QUALNAME, CallKind, ModuleInfo, ParseFailure
from flowcli.parser import parse_module, parse_source


def parse(src: str, module: str = "m", *, is_package: bool = False) -> ModuleInfo:
    info = parse_source(module, f"{module}.py", src, is_package=is_package)
    assert not isinstance(info, ParseFailure), info
    return info


def test_nested_function_qualname() -> None:
    info = parse("def outer():\n    def inner():\n        pass\n    inner()\n")
    assert set(info.functions) == {"outer", "outer.inner"}


def test_method_qualname_and_class_link() -> None:
    info = parse("class C:\n    def m(self):\n        pass\n")
    assert info.functions["C.m"].class_qualname == "C"
    assert info.classes["C"].methods == {"m": "C.m"}


def test_call_kind_classification() -> None:
    src = (
        "class C:\n"
        "    def m(self):\n"
        "        f()\n"
        "        a.b.f()\n"
        "        self.x()\n"
        "        cls.y()\n"
        "        super().z()\n"
        "        self.helper.run()\n"
        "        (get())()\n"
    )
    info = parse(src)
    kinds = [c.kind for c in info.functions["C.m"].raw_calls]
    assert kinds == [
        CallKind.NAME,
        CallKind.DOTTED,
        CallKind.SELF_ATTR,
        CallKind.CLS_ATTR,
        CallKind.SUPER_ATTR,
        CallKind.OPAQUE,  # self.helper.run() — deep self chain
        CallKind.OPAQUE,  # (get())() — call on a call result
        CallKind.NAME,  # the nested get() itself
    ]
    dotted = info.functions["C.m"].raw_calls[1]
    assert dotted.parts == ("a", "b", "f")


def test_relative_import_level1_in_package_init() -> None:
    info = parse("from .helpers import util_a\n", module="pkg", is_package=True)
    assert info.imports["util_a"] == "pkg.helpers.util_a"


def test_relative_import_level2_in_nested_module() -> None:
    info = parse("from ..models import Engine\n", module="pkg.sub.worker")
    assert info.imports["Engine"] == "pkg.models.Engine"


def test_relative_import_from_dot() -> None:
    info = parse("from . import sibling\n", module="pkg.sub", is_package=True)
    assert info.imports["sibling"] == "pkg.sub.sibling"


def test_import_aliases() -> None:
    info = parse("import a.b as ab\nimport c.d\n")
    assert info.imports == {"ab": "a.b", "c": "c"}


def test_star_import() -> None:
    info = parse("from x import *\n")
    assert info.star_imports == ["x"]


def test_function_local_import_is_module_wide() -> None:
    info = parse("def f():\n    from x import y\n    y()\n")
    assert info.imports == {"y": "x.y"}


def test_main_guard_detected() -> None:
    assert parse("def f():\n    pass\n\nif __name__ == '__main__':\n    f()\n").has_main_guard
    assert parse("if '__main__' == __name__:\n    pass\n").has_main_guard  # either order
    assert not parse("if __name__ == 'other':\n    pass\n").has_main_guard
    assert not parse("def f():\n    if __name__ == '__main__':\n        pass\n").has_main_guard


def test_module_level_call_creates_module_sink() -> None:
    info = parse("def main():\n    pass\n\nif __name__ == '__main__':\n    main()\n")
    assert MODULE_QUALNAME in info.functions
    assert [c.parts for c in info.functions[MODULE_QUALNAME].raw_calls] == [("main",)]


def test_no_module_sink_without_toplevel_calls() -> None:
    info = parse("def f():\n    pass\n")
    assert MODULE_QUALNAME not in info.functions


def test_decorator_recorded_as_module_call_and_metadata() -> None:
    info = parse("def deco(fn):\n    return fn\n\n@deco\ndef f():\n    pass\n")
    assert info.functions["f"].decorators == ["deco"]
    assert [c.parts for c in info.functions[MODULE_QUALNAME].raw_calls] == [("deco",)]


def test_function_default_call_attributed_to_enclosing_scope() -> None:
    info = parse("def g():\n    return 1\n\ndef f(x=g()):\n    pass\n")
    assert [c.parts for c in info.functions[MODULE_QUALNAME].raw_calls] == [("g",)]
    assert info.functions["f"].raw_calls == []


def test_class_body_call_goes_to_module_sink() -> None:
    info = parse("def make():\n    return 1\n\nclass C:\n    x = make()\n")
    assert [c.parts for c in info.functions[MODULE_QUALNAME].raw_calls] == [("make",)]


def test_qualname_collision_gets_lineno_suffix() -> None:
    info = parse("def f():\n    pass\n\ndef f():\n    pass\n")
    assert set(info.functions) == {"f", "f#4"}


def test_overload_stubs_skipped() -> None:
    src = (
        "from typing import overload\n"
        "\n"
        "class C:\n"
        "    @overload\n"
        "    def m(self, x: int) -> int: ...\n"
        "    @overload\n"
        "    def m(self, x: str) -> str: ...\n"
        "    def m(self, x):\n"
        "        return x\n"
    )
    info = parse(src)
    assert set(info.functions) == {"C.m"}
    assert info.classes["C"].methods == {"m": "C.m"}
    assert info.functions["C.m"].lineno == 8  # the real implementation, not a stub


def test_duplicate_method_last_definition_wins() -> None:
    src = "class C:\n    def m(self):\n        pass\n\n    def m(self):\n        pass\n"
    info = parse(src)
    assert set(info.functions) == {"C.m", "C.m#5"}
    assert info.classes["C"].methods == {"m": "C.m#5"}  # runtime binding is the last def


def test_local_types_collected() -> None:
    src = (
        "def f(gen: Generator, n: int, opt: Engine | None):\n"
        "    x = Engine()\n"
        "    y: Base = make()\n"
        "    z = plain\n"
    )
    info = parse(src)
    assert info.functions["f"].local_types == {
        "gen": ("Generator",),
        "n": ("int",),
        "opt": ("Engine",),
        "x": ("Engine",),
        "y": ("Base",),
    }


def test_self_attr_types_collected() -> None:
    src = (
        "class C:\n"
        "    level: Marker\n"
        "\n"
        "    def __init__(self):\n"
        "        self.db = DBLayer()\n"
        "        self.name: Title = make()\n"
    )
    info = parse(src)
    assert info.classes["C"].attr_types == {
        "level": ("Marker",),
        "db": ("DBLayer",),
        "name": ("Title",),
    }


def test_flow_extraction_if_loop_return() -> None:
    src = (
        "def f(x):\n"
        "    if x > 0:\n"
        "        return 1\n"
        "    for i in range(x):\n"
        "        g(i)\n"
        "    return 2\n"
    )
    info = parse(src)
    flow = info.functions["f"].flow
    assert [it["t"] for it in flow] == ["if", "loop", "ret"]
    assert flow[0]["label"] == "if x > 0"
    assert flow[0]["then"][0]["t"] == "ret"
    assert flow[0]["else"] == []
    assert flow[1]["label"] == "for i in range(x)"
    assert flow[1]["body"][0]["label"] == "g(i)"
    assert flow[2]["label"] == "return 2"


def test_flow_try_with_and_nested_def() -> None:
    src = (
        "def f():\n"
        "    try:\n"
        "        risky()\n"
        "    except ValueError:\n"
        "        handle()\n"
        "    finally:\n"
        "        cleanup()\n"
        "    with open('x') as fh:\n"
        "        fh.read()\n"
        "    def inner():\n"
        "        pass\n"
    )
    info = parse(src)
    flow = info.functions["f"].flow
    assert flow[0]["t"] == "try"
    assert flow[0]["body"][0]["label"] == "risky()"
    assert flow[0]["handlers"][0]["label"] == "except ValueError"
    assert flow[0]["final"][0]["label"] == "cleanup()"
    assert flow[1]["t"] == "with"
    assert flow[1]["label"].startswith("with")
    assert flow[2] == {"t": "stmt", "label": "def inner(…)", "line": 10, "end": 10}


def test_flow_deterministic() -> None:
    src = "def f(x):\n    if x:\n        return 1\n    return 2\n"
    first = parse(src).functions["f"].flow
    second = parse(src).functions["f"].flow
    assert first == second


def test_syntax_error_returns_failure(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def (\n", encoding="utf-8")
    result = parse_module("bad", bad)
    assert isinstance(result, ParseFailure)
    assert "SyntaxError" in result.error
