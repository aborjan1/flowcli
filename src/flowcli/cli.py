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
import sys
from pathlib import Path

from flowcli import __version__
from flowcli.graph.entry import split_entry_spec
from flowcli.output.report import print_summary
from flowcli.pipeline import FORMATS, MapError, MapOptions, map_project, write_outputs
from flowcli.runtime.runner import Program, execute, runtime_payload

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
    head, qual = split_entry_spec(entry)
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
        return _fail(f"path not found: {args.path}")
    formats = {f.strip() for f in args.formats.split(",") if f.strip()}
    if not formats or formats - FORMATS:
        return _fail(f"unknown format(s): {', '.join(sorted(formats - FORMATS)) or '(none)'}")

    entry_specs = _entry_specs(args.entry, root)
    options = MapOptions(
        root=root,
        entries=entry_specs,
        exclude=args.exclude,
        depth=args.depth,
        keep_unreachable=args.keep_unreachable,
        include_external=args.include_external,
        simulate=not args.no_simulate,
        classes=not args.no_classes,
        runtime_file=Path(args.runtime) if args.runtime else None,
    )
    try:
        result = map_project(options)
    except MapError as exc:
        # "nothing to map" is a plain notice, not a usage error
        return _fail(str(exc), exc.exit_code, prefix="" if exc.exit_code == 2 else "error: ")

    write_outputs(result, formats, Path(args.out_dir))
    if not args.quiet:
        print_summary(result.graph, result.meta)
        if not entry_specs and result.suggestions:
            print("suggested entry points (pass one as the second argument):")
            for s in result.suggestions[:5]:
                print(f"  {s['id']:<48} {s['why']}")
        print(f"wrote {', '.join(sorted(formats))} to {args.out_dir}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        program = Program.parse(args.prog)
    except ValueError as exc:
        return _fail(str(exc))
    root = Path(args.root).resolve() if args.root else program.home
    if not root.exists():
        return _fail(f"root not found: {root}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    samples = not args.no_samples
    cap, exit_code = execute(program, root, samples=samples)
    runtime_path = out_dir / "runtime.json"
    payload = runtime_payload(cap, program, root, exit_code, samples)
    runtime_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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


def _fail(message: str, code: int = 1, *, prefix: str = "error: ") -> int:
    print(f"flowcli: {prefix}{message}", file=sys.stderr)
    return code
