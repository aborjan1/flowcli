"""Execute a script or module under the tracer, the way `python script.py` / `python -m mod` would."""

from __future__ import annotations

import runpy
import sys
import traceback
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flowcli import __version__
from flowcli.runtime.tracer import RuntimeCapture, capture


@dataclass(frozen=True)
class Program:
    mode: str  # script | module
    target: str  # script path or dotted module name
    args: tuple[str, ...] = ()

    @classmethod
    def parse(cls, prog: list[str]) -> Program:
        """`script.py [args...]` or `-- -m module [args...]`. Raises ValueError on a malformed spec."""
        prog = [p for p in prog if p != "--"] if prog and prog[0] == "--" else list(prog)
        if not prog:
            raise ValueError("no program given (script.py [args] or -- -m module [args])")
        if prog[0] == "-m":
            if len(prog) < 2:
                raise ValueError("-m requires a module name")
            return cls("module", prog[1], tuple(prog[2:]))
        if not Path(prog[0]).is_file():
            raise ValueError(f"script not found: {prog[0]}")
        return cls("script", prog[0], tuple(prog[1:]))

    @property
    def argv(self) -> list[str]:
        return [self.target, *self.args]

    @property
    def home(self) -> Path:
        """Where the program's own imports resolve from: the script's directory, or the cwd for -m."""
        return Path(self.target).resolve().parent if self.mode == "script" else Path.cwd()


def execute(program: Program, root: Path, *, samples: bool) -> tuple[RuntimeCapture, int]:
    """Run `program` with calls under `root` traced. Returns (capture, the program's exit code)."""
    exit_code = 0
    old_argv = sys.argv[:]
    added_path = str(program.home)
    sys.path.insert(0, added_path)
    try:
        with capture(root, samples=samples) as cap:
            try:
                sys.argv = program.argv
                if program.mode == "script":
                    runpy.run_path(program.target, run_name="__main__")
                else:
                    runpy.run_module(program.target, run_name="__main__", alter_sys=True)
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


def runtime_payload(cap: RuntimeCapture, program: Program, root: Path, exit_code: int, samples: bool) -> dict[str, Any]:
    """The runtime.json document `flowcli map --runtime` merges back in."""
    return {
        "meta": {
            "tool": "flowcli",
            "version": __version__,
            "schema_version": 1,
            "root": str(root),
            "argv": program.argv,
            "mode": program.mode,
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "samples": samples,
            "calls_total": cap.calls_total,
            "events_truncated": cap.events_truncated,
            "exit": exit_code,
        },
        "functions": cap.functions,
        "events": cap.events,
    }


def _exit_code_of(exc: SystemExit) -> int:
    code = exc.code
    if code is None:
        return 0
    return code if isinstance(code, int) else 1
