"""The map pipeline end to end: discover → parse → resolve → graph → scope → simulate → write.

`map_project` is everything `flowcli map` does short of argument parsing and
terminal output, so it can be driven from code as well as from the CLI.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flowcli import __version__
from flowcli.analysis.classes import ClassGraph, build_class_graph, scope_class_graph
from flowcli.analysis.discovery import discover
from flowcli.analysis.entrypoints import detect
from flowcli.analysis.index import ProjectIndex
from flowcli.analysis.model import ModuleInfo, ParseFailure, split_node_id
from flowcli.analysis.parser import parse_module
from flowcli.analysis.resolver import INTERNAL, resolve_all
from flowcli.graph.build import apply_runtime, apply_simulation, build_graph
from flowcli.graph.entry import parse_entry_specs
from flowcli.graph.model import Graph
from flowcli.graph.scope import compute_depths, prune_unreachable
from flowcli.output.html import render_html
from flowcli.output.report import write_json, write_markdown

FORMATS = frozenset({"json", "md", "html"})


class MapError(Exception):
    """The map cannot be built. `exit_code` is 1 for bad input, 2 when there is nothing to map."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass
class MapOptions:
    root: Path
    entries: list[str] = field(default_factory=list)  # entry specs, see graph.entry
    exclude: list[str] = field(default_factory=list)
    depth: int | None = None
    keep_unreachable: bool = False
    include_external: bool = False
    simulate: bool = True
    classes: bool = True
    runtime_file: Path | None = None


@dataclass
class MapResult:
    graph: Graph
    meta: dict[str, Any]
    class_graph: ClassGraph | None
    replay: list[list[str]]  # [[caller, callee], ...] — observed when runtime data was merged, else simulated
    suggestions: list[dict[str, Any]]  # ranked entry-point candidates


def map_project(opts: MapOptions) -> MapResult:
    files = discover(opts.root, opts.exclude)
    if not files:
        raise MapError(f"no Python files found under {opts.root}", exit_code=2)
    modules, failures = _parse_all(files)
    if not modules:
        raise MapError("no parseable Python files", exit_code=2)

    index = ProjectIndex(modules)
    resolved = resolve_all(index)
    graph = build_graph(index, resolved, include_external=opts.include_external)
    suggestions = detect(index, {rc.target for rc in resolved if rc.status == INTERNAL}, opts.root)

    entry_label: str | None = None
    entry_ids: list[str] = []
    unreachable = 0
    scoped = False
    if opts.entries:
        try:
            entry_label, entry_ids = parse_entry_specs(opts.entries, index)
        except ValueError as exc:
            raise MapError(str(exc)) from exc
        unreachable = compute_depths(graph, entry_ids, opts.depth)
        if not opts.keep_unreachable:
            prune_unreachable(graph)
            scoped = True

    simulated = apply_simulation(graph, index, resolved, entry_ids or None) if opts.simulate else []

    class_graph = None
    if opts.classes:
        class_graph = build_class_graph(index)
        if scoped:
            class_graph = scope_class_graph(class_graph, {split_node_id(nid)[0] for nid in graph.nodes})

    runtime = _read_runtime(opts.runtime_file) if opts.runtime_file else None

    meta: dict[str, Any] = {
        "tool": "flowcli",
        "version": __version__,
        "schema_version": 1,
        "root": str(opts.root.resolve()),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "module_count": len(index.modules),
        "node_count": len(graph.nodes),
        "edge_count": sum(len(n.calls) for n in graph.nodes.values()),
        "entry": entry_label,
        "unreachable_count": unreachable,
        "include_external": opts.include_external,
        "skipped_files": [{"file": f.file, "error": f.error} for f in failures],
        "unresolved_count": len(graph.unresolved),
        "scoped": scoped,
        "depth_limit": opts.depth,
        "entry_nodes": entry_ids,
        "simulated": opts.simulate,
        "has_runtime": runtime is not None,
        "entry_points": [s for s in suggestions if not scoped or s["id"] in graph.nodes],
    }
    if runtime is not None:
        meta["runtime_file"] = str(opts.runtime_file)
        meta["runtime_total"] = len(runtime.get("functions", {}))
        meta["runtime_matched"] = apply_runtime(graph, runtime)
    meta["class_count"] = len(class_graph.nodes) if class_graph else 0

    replay = runtime.get("events", []) if runtime else simulated
    return MapResult(graph, meta, class_graph, replay, suggestions)


def write_outputs(result: MapResult, formats: set[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if "json" in formats:
        write_json(result.graph, result.meta, out_dir / "report.json", result.class_graph)
    if "md" in formats:
        write_markdown(result.graph, result.meta, out_dir / "report.md", result.class_graph)
    if "html" in formats:
        replay = {"events": result.replay}
        render_html(result.graph, result.meta, out_dir / "graph.html", runtime=replay, class_graph=result.class_graph)


def _parse_all(files: list[tuple[str, Path]]) -> tuple[dict[str, ModuleInfo], list[ParseFailure]]:
    modules: dict[str, ModuleInfo] = {}
    failures: list[ParseFailure] = []
    for mod_name, path in files:
        result = parse_module(mod_name, path)
        if isinstance(result, ParseFailure):
            failures.append(result)
            print(f"flowcli: warning: skipping {result.file}: {result.error}", file=sys.stderr)
        else:
            modules.setdefault(mod_name, result)  # duplicate module names: first (deterministic) wins
    return modules, failures


def _read_runtime(path: Path) -> dict[str, Any]:
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MapError(f"cannot read runtime file: {exc}") from exc
    return data
