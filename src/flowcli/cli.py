"""flowcli command-line interface.

Two arguments: what to map, and where to start.

    flowcli src/mypkg                      # map the whole package
    flowcli src/mypkg core.py              # start from that file's functions
    flowcli src/mypkg core.py:process      # start from one function
    flowcli src/mypkg mypkg.core:process   # dotted entry works too

Static map, signature inference, simulated data flow and all three output
formats happen by default; flags only narrow things down (--depth, --exclude…).
`flowcli run ...` adds real runtime data when the code can actually be executed.
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

from flowcli import __version__
from flowcli.classes import ClassGraph, build_class_graph, scope_class_graph
from flowcli.discovery import discover
from flowcli.entrypoints import detect
from flowcli.graph import (
    Graph,
    apply_runtime,
    apply_simulation,
    build_graph,
    compute_depths,
    parse_entry_specs,
    prune_unreachable,
)
from flowcli.models import ModuleInfo, ParseFailure
from flowcli.parser import parse_module
from flowcli.render_html import render_html
from flowcli.report import print_summary, write_json, write_markdown
from flowcli.resolver import ProjectIndex, resolve_all
from flowcli.tracer import capture

VALID_FORMATS = {"json", "md", "html"}
SUBCOMMANDS = {"map", "run"}


def main(argv: list[str] | None = None) -> int:
    args_in = list(sys.argv[1:] if argv is None else argv)
    if args_in and args_in[0] not in SUBCOMMANDS and not args_in[0].startswith("-"):
        args_in.insert(0, "map")  # bare target: `flowcli src/pkg` == `flowcli map src/pkg`

    parser = argparse.ArgumentParser(
        prog="flowcli",
        description="Map, understand and simulate the call graph of a Python codebase.",
        epilog="Usage is `flowcli PATH [ENTRY]` — PATH is the package to map, ENTRY is where to "
        "start reading (a file, or file:function). The `map` subcommand is implied.",
    )
    parser.add_argument("--version", action="version", version=f"flowcli {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_map_parser(sub)
    _add_run_parser(sub)

    args = parser.parse_args(args_in)
    if args.command == "map":
        return _cmd_map(args)
    return _cmd_run(args)


def _add_map_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("map", help="parse a codebase and map its call graph (the default action)")
    p.add_argument("path", help="the package or directory to map")
    p.add_argument(
        "entry",
        nargs="*",
        default=[],
        help="where to start — repeatable, and comma-separated lists are accepted: a folder "
        "(everything under it), a .py file (its whole ecosystem), or file.py:function / "
        "module:qualname for a single function",
    )
    p.add_argument("-o", "--out-dir", default="MODEL", help="output directory (default: ./MODEL)")
    p.add_argument("--depth", type=int, default=None, metavar="N", help="include at most N call-hops from the entry")
    p.add_argument("--keep-unreachable", action="store_true", help="keep functions outside the entry's call graph")
    p.add_argument("--include-external", action="store_true", help="materialize stdlib/third-party targets")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="skip matching paths")
    p.add_argument("--no-simulate", action="store_true", help="skip the inferred data-flow simulation")
    p.add_argument("--no-classes", action="store_true", help="skip the class / data-model view")
    p.add_argument("--runtime", default=None, metavar="FILE", help="merge a flowcli-run runtime.json")
    p.add_argument("--formats", default="json,md,html", help="comma-separated subset of json,md,html")
    p.add_argument("-q", "--quiet", action="store_true", help="suppress the terminal summary")


def _add_run_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("run", help="execute a program under the tracer, then map it with real runtime data")
    p.add_argument("--root", default=None, help="code root to trace (defaults to the script's package)")
    p.add_argument("-o", "--out-dir", default="MODEL", help="output directory (default: ./MODEL)")
    p.add_argument("--no-samples", action="store_true", help="record observed types only, no value samples")
    p.add_argument("--no-map", action="store_true", help="only write runtime.json, skip building the map")
    p.add_argument("-q", "--quiet", action="store_true", help="suppress the summary")
    p.add_argument(
        "prog",
        nargs=argparse.REMAINDER,
        help="script.py [args...] or -- -m module [args...] (flowcli options go before it)",
    )


def _resolve_entry(entry: str, root: Path) -> str:
    """Entry may be given relative to the mapped path — accept both forms."""
    head, sep, qual = entry.rpartition(":")
    if not sep or (len(head) == 1 and entry[1:2] == ":"):  # no qualname (or a windows drive letter)
        head, qual = entry, ""
    candidate = Path(head)
    if not candidate.exists():
        nested = root / head
        if nested.exists():
            head = str(nested)
    return f"{head}:{qual}" if qual else head


def _entry_specs(raw: list[str], root: Path) -> list[str]:
    """Entries arrive as separate arguments and/or comma-separated lists."""
    return [_resolve_entry(part.strip(), root) for item in raw for part in item.split(",") if part.strip()]


def _cmd_map(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        print(f"flowcli: error: path not found: {args.path}", file=sys.stderr)
        return 1
    entry_specs = _entry_specs(args.entry, root)

    formats = {f.strip() for f in args.formats.split(",") if f.strip()}
    if not formats or formats - VALID_FORMATS:
        print(f"flowcli: error: unknown format(s): {', '.join(sorted(formats - VALID_FORMATS)) or '(none)'}",
              file=sys.stderr)
        return 1

    files = discover(root, args.exclude)
    if not files:
        print(f"flowcli: no Python files found under {root}", file=sys.stderr)
        return 2
    modules, failures = _parse_all(files)
    if not modules:
        print("flowcli: no parseable Python files", file=sys.stderr)
        return 2

    index = ProjectIndex(modules)
    resolved = resolve_all(index)
    graph = build_graph(index, resolved, include_external=args.include_external)
    called = {rc.target for rc in resolved if rc.status == "internal"}
    suggestions = detect(index, called, root)

    entry_label: str | None = None
    entry_ids: list[str] = []
    unreachable = 0
    scoped = False
    if entry_specs:
        try:
            entry_label, entry_ids = parse_entry_specs(entry_specs, index)
        except ValueError as exc:
            print(f"flowcli: error: {exc}", file=sys.stderr)
            return 1
        unreachable = compute_depths(graph, entry_ids, args.depth)
        if not args.keep_unreachable:
            prune_unreachable(graph)
            scoped = True

    sim_events: list[list[str]] = []
    if not args.no_simulate:
        sim_events = apply_simulation(graph, index, resolved, entry_ids or None)

    class_graph = None
    if not args.no_classes:
        class_graph = build_class_graph(index)
        if scoped:
            class_graph = scope_class_graph(class_graph, {nid.split(":", 1)[0] for nid in graph.nodes})

    runtime_data = None
    if args.runtime:
        try:
            runtime_data = json.loads(Path(args.runtime).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"flowcli: error: cannot read runtime file: {exc}", file=sys.stderr)
            return 1

    meta = _build_meta(graph, index, root, entry_label, unreachable, args.include_external, failures)
    meta.update({"scoped": scoped, "depth_limit": args.depth, "entry_nodes": entry_ids,
                 "simulated": not args.no_simulate, "has_runtime": runtime_data is not None,
                 "entry_points": [s for s in suggestions if not scoped or s["id"] in graph.nodes]})
    if runtime_data is not None:
        meta["runtime_file"] = str(args.runtime)
        meta["runtime_total"] = len(runtime_data.get("functions", {}))
        meta["runtime_matched"] = apply_runtime(graph, runtime_data)

    meta["class_count"] = len(class_graph.nodes) if class_graph else 0
    _write_outputs(graph, meta, formats, Path(args.out_dir), runtime_data, sim_events, class_graph)
    if not args.quiet:
        print_summary(graph, meta)
        if not entry_specs and suggestions:
            print("suggested entry points (pass one as the second argument):")
            for s in suggestions[:5]:
                print(f"  {s['id']:<48} {s['why']}")
        print(f"wrote {', '.join(sorted(formats))} to {args.out_dir}")
    return 0


def _write_outputs(
    graph: Graph,
    meta: dict,
    formats: set[str],
    out_dir: Path,
    runtime_data: dict | None,
    sim_events: list[list[str]],
    class_graph: ClassGraph | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if "json" in formats:
        write_json(graph, meta, out_dir / "report.json", class_graph)
    if "md" in formats:
        write_markdown(graph, meta, out_dir / "report.md", class_graph)
    if "html" in formats:
        events = runtime_data if runtime_data else {"events": sim_events}
        render_html(graph, meta, out_dir / "graph.html", runtime=events, class_graph=class_graph)


def _cmd_run(args: argparse.Namespace) -> int:
    prog = [p for p in args.prog if p != "--"] if args.prog and args.prog[0] == "--" else list(args.prog)
    if not prog:
        print("flowcli: error: no program given (script.py [args] or -- -m module [args])", file=sys.stderr)
        return 1

    if prog[0] == "-m":
        if len(prog) < 2:
            print("flowcli: error: -m requires a module name", file=sys.stderr)
            return 1
        mode, target, prog_args = "module", prog[1], prog[2:]
        default_root = Path.cwd()
    else:
        mode, target, prog_args = "script", prog[0], prog[1:]
        if not Path(target).is_file():
            print(f"flowcli: error: script not found: {target}", file=sys.stderr)
            return 1
        default_root = Path(target).resolve().parent

    root = Path(args.root).resolve() if args.root else default_root
    if not root.exists():
        print(f"flowcli: error: root not found: {root}", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cap, exit_code = _execute(mode, target, prog_args, root, default_root, samples=not args.no_samples)
    runtime_path = out_dir / "runtime.json"
    runtime_path.write_text(
        json.dumps(_runtime_payload(cap, root, mode, target, prog_args, exit_code, not args.no_samples), indent=2)
        + "\n",
        encoding="utf-8",
    )
    if not args.quiet:
        print(f"flowcli: observed {len(cap.functions)} function(s), {cap.calls_total} call(s)")
        print(f"wrote runtime.json to {out_dir}")

    if not args.no_map:
        map_argv = ["map", str(root), "-o", str(out_dir), "--runtime", str(runtime_path)]
        if args.quiet:
            map_argv.append("-q")
        rc = main(map_argv)
        if rc:
            return rc
    return exit_code


def _execute(mode: str, target: str, prog_args: list[str], root: Path, script_dir: Path, *, samples: bool):
    exit_code = 0
    old_argv = sys.argv[:]
    added_path = str(script_dir if mode == "script" else Path.cwd())
    sys.path.insert(0, added_path)
    try:
        with capture(root, samples=samples) as cap:
            try:
                sys.argv = [target, *prog_args]
                if mode == "script":
                    runpy.run_path(target, run_name="__main__")
                else:
                    runpy.run_module(target, run_name="__main__", alter_sys=True)
            except SystemExit as exc:
                exit_code = _exit_code_of(exc)
            except BaseException:
                traceback.print_exc()
                exit_code = 1
    finally:
        sys.argv = old_argv
        if added_path in sys.path:
            sys.path.remove(added_path)
    return cap, exit_code


def _exit_code_of(exc: SystemExit) -> int:
    code = exc.code
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def _runtime_payload(cap, root: Path, mode: str, target: str, prog_args: list[str], exit_code: int, samples: bool):
    return {
        "meta": {
            "tool": "flowcli",
            "version": __version__,
            "schema_version": 1,
            "root": str(root),
            "argv": [target, *prog_args],
            "mode": mode,
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "samples": samples,
            "calls_total": cap.calls_total,
            "events_truncated": cap.events_truncated,
            "exit": exit_code,
        },
        "functions": cap.functions,
        "events": cap.events,
    }


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


def _build_meta(
    graph: Graph,
    index: ProjectIndex,
    root: Path,
    entry_id: str | None,
    unreachable: int,
    include_external: bool,
    failures: list[ParseFailure],
) -> dict:
    return {
        "tool": "flowcli",
        "version": __version__,
        "schema_version": 1,
        "root": str(root.resolve()),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "module_count": len(index.modules),
        "node_count": len(graph.nodes),
        "edge_count": sum(len(n.calls) for n in graph.nodes.values()),
        "entry": entry_id,
        "unreachable_count": unreachable,
        "include_external": include_external,
        "skipped_files": [{"file": f.file, "error": f.error} for f in failures],
        "unresolved_count": len(graph.unresolved),
    }
