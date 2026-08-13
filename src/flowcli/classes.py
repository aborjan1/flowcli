"""The data model behind the code: classes, their properties, and how they compose.

The call graph answers "what runs what". This answers "what holds what" — a
`Measurement` with a `value: float` and a `unit: Unit`, where `Unit` is itself a
class inheriting `StrEnum`. Two edge kinds: `inherits` (a base class) and `has`
(a property whose declared type is another parsed class).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from flowcli.models import ClassInfo, ModuleInfo
from flowcli.resolver import ProjectIndex, _resolve_class_ref

ENUM_BASES = frozenset({"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "ReprEnum"})
DATACLASS_DECORATORS = frozenset({"dataclass", "attrs", "define", "frozen"})
STRUCT_BASES = frozenset({"Struct", "BaseModel", "NamedTuple", "TypedDict"})
ABSTRACT_BASES = frozenset({"ABC", "Protocol", "ABCMeta"})
CONTAINERS = frozenset({"list", "set", "tuple", "dict", "frozenset", "Sequence", "Iterable", "Optional"})


@dataclass
class ClassNode:
    id: str  # "module:Qualname"
    module: str
    name: str
    file: str
    lineno: int
    stereotype: str = ""  # enum | dataclass | struct | abstract | ""
    bases: list[str] = field(default_factory=list)  # display strings, resolved or not
    base_refs: list[str | None] = field(default_factory=list)  # aligned with bases: class id, or None
    fields: list[dict[str, Any]] = field(default_factory=list)  # {name, type, ref, value}
    methods: list[dict[str, Any]] = field(default_factory=list)  # {name, id}


@dataclass
class ClassEdge:
    source: str
    target: str
    kind: str  # inherits | has
    label: str = ""  # the property name, for `has`


@dataclass
class ClassGraph:
    nodes: dict[str, ClassNode] = field(default_factory=dict)
    edges: list[ClassEdge] = field(default_factory=list)


def class_id(module: str, qualname: str) -> str:
    return f"{module}:{qualname}"


def build_class_graph(index: ProjectIndex) -> ClassGraph:
    graph = ClassGraph()
    for mod_name in sorted(index.modules):
        mod = index.modules[mod_name]
        for qualname in sorted(mod.classes):
            ci = mod.classes[qualname]
            graph.nodes[class_id(mod_name, qualname)] = _make_node(index, mod, ci)

    for nid in sorted(graph.nodes):
        node = graph.nodes[nid]
        mod = index.modules[node.module]
        ci = mod.classes[node.name]
        _add_inheritance(index, mod, ci, nid, graph)
        _add_composition(node, nid, graph)
    graph.edges.sort(key=lambda e: (e.source, e.kind, e.label, e.target))
    return graph


def _make_node(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo) -> ClassNode:
    node = ClassNode(
        id=class_id(mod.name, ci.qualname),
        module=mod.name,
        name=ci.qualname,
        file=mod.file,
        lineno=ci.lineno,
        stereotype=_stereotype(ci),
        bases=list(ci.base_reprs),
    )
    for parts in ci.bases:  # resolvable bases, in declaration order
        found = _resolve_class_ref(index, mod, parts)
        node.base_refs.append(class_id(found[0], found[1]) if found is not None else None)
    while len(node.base_refs) < len(node.bases):
        node.base_refs.append(None)  # dynamic bases (namedtuple(...)) have a display but no parts
    for f in ci.fields:
        ref = None
        parts = tuple(f.get("parts") or ())
        if parts:
            found = _resolve_class_ref(index, mod, parts)
            if found is not None:
                ref = class_id(found[0], found[1])
        node.fields.append(
            {
                "name": f["name"],
                "type": f.get("ann") or (".".join(parts) if parts else None),
                "ref": ref,
                "value": f.get("value"),
            }
        )
    for name in sorted(ci.methods):
        qual = ci.methods[name]
        if not name.startswith("_") or name == "__init__":
            node.methods.append({"name": name, "id": f"{mod.name}:{qual}"})
    return node


def _stereotype(ci: ClassInfo) -> str:
    base_names = {parts[-1] for parts in ci.bases}
    base_names.update(repr_.rsplit(".", 1)[-1].split("[")[0] for repr_ in ci.base_reprs)
    decorators = {d.rsplit(".", 1)[-1] for d in ci.decorators}
    if base_names & ENUM_BASES:
        return "enum"
    if decorators & DATACLASS_DECORATORS:
        return "dataclass"
    if base_names & STRUCT_BASES:
        return "struct"
    if base_names & ABSTRACT_BASES:
        return "abstract"
    return ""


def _add_inheritance(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo, nid: str, graph: ClassGraph) -> None:
    for parts in ci.bases:
        found = _resolve_class_ref(index, mod, parts)
        if found is not None:
            target = class_id(found[0], found[1])
            if target in graph.nodes and target != nid:
                graph.edges.append(ClassEdge(source=nid, target=target, kind="inherits"))


def _add_composition(node: ClassNode, nid: str, graph: ClassGraph) -> None:
    seen: set[tuple[str, str]] = set()
    for f in node.fields:
        ref = f.get("ref")
        if not ref or ref == nid or ref not in graph.nodes:
            continue
        key = (ref, f["name"])
        if key in seen:
            continue
        seen.add(key)
        graph.edges.append(ClassEdge(source=nid, target=ref, kind="has", label=f["name"]))


def scope_class_graph(graph: ClassGraph, keep_modules: set[str]) -> ClassGraph:
    """Keep classes in the scoped modules, plus anything they point at (one closure pass)."""
    if not keep_modules:
        return graph
    keep = {nid for nid, node in graph.nodes.items() if node.module in keep_modules}
    for edge in graph.edges:
        if edge.source in keep:
            keep.add(edge.target)  # a referenced enum/base stays visible even if its module was pruned
    nodes = {nid: node for nid, node in graph.nodes.items() if nid in keep}
    edges = [e for e in graph.edges if e.source in nodes and e.target in nodes]
    return ClassGraph(nodes=nodes, edges=edges)
