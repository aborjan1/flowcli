"""Runtime capture: observed argument/return types and sampled values per function.

Built on sys.setprofile (call/return events only — cheap, and it does not fight
tools that own sys.settrace, like coverage). Node ids are derived from code
filenames with the same logic `flowcli map` uses, so records merge exactly.

Caveats (by design of the mechanism):
- main thread only (sys.setprofile is per-thread);
- a frame unwinding with an exception fires 'return' with None — indistinguishable
  from `return None`;
- C-implemented callables and functools.lru_cache hits produce no Python frame;
- classes defined inside the traced __main__ script report `__main__.X` type names.
"""

from __future__ import annotations

import inspect
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import CodeType, FrameType
from typing import Any

from flowcli.discovery import SKIP_DIRS, derive_module_name, find_package_prefix
from flowcli.models import MODULE_QUALNAME, node_id

SAMPLE_LIMIT = 5  # repr samples kept per function
TYPE_LIMIT = 8  # distinct observed types kept per param / return
EVENT_LIMIT = 2000  # replay call-event cap
REPR_LIMIT = 80

_SKIP_NAMES = ("<lambda>", "<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>")


@dataclass
class RuntimeCapture:
    functions: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: list[list[str]] = field(default_factory=list)
    calls_total: int = 0
    events_truncated: bool = False


def _type_name(value: Any) -> str:
    t = type(value)
    if t.__module__ == "builtins":
        return t.__qualname__
    return f"{t.__module__}.{t.__qualname__}"


def _safe_repr(value: Any) -> str:
    try:
        return repr(value)[:REPR_LIMIT]
    except Exception:
        return "<unreprable>"


def _param_names(code: CodeType) -> list[tuple[str, str]]:
    """[(display name with */** prefix, bare local name)] in declaration order."""
    base = code.co_argcount + code.co_kwonlyargcount
    names = [(v, v) for v in code.co_varnames[:base]]
    idx = base
    if code.co_flags & inspect.CO_VARARGS:
        names.append(("*" + code.co_varnames[idx], code.co_varnames[idx]))
        idx += 1
    if code.co_flags & inspect.CO_VARKEYWORDS:
        names.append(("**" + code.co_varnames[idx], code.co_varnames[idx]))
    return names


@contextmanager
def capture(root: Path, *, samples: bool = True) -> Iterator[RuntimeCapture]:
    """Trace Python calls in files under `root` for the duration of the block."""
    root = root.resolve()
    if root.is_file():
        root = root.parent
    anchor, _ = find_package_prefix(root)
    root_prefix = str(root) + os.sep

    cap = RuntimeCapture()
    file_memo: dict[str, str | None] = {}
    code_memo: dict[CodeType, str | None] = {}
    pending: dict[int, dict[str, Any]] = {}

    def module_of(filename: str) -> str | None:
        if filename in file_memo:
            return file_memo[filename]
        result: str | None = None
        ap = os.path.abspath(filename)
        if ap.startswith(root_prefix) and ap.endswith(".py"):
            rel_dirs = os.path.relpath(ap, str(root)).split(os.sep)[:-1]
            if not any(d in SKIP_DIRS or d.startswith(".") for d in rel_dirs):
                result = derive_module_name(Path(ap), anchor)
        file_memo[filename] = result
        return result

    def node_for(code: CodeType) -> str | None:
        if code in code_memo:
            return code_memo[code]
        result: str | None = None
        qual = code.co_qualname
        if not any(s in qual for s in _SKIP_NAMES):
            module = module_of(code.co_filename)
            if module is not None:
                if code.co_name == "<module>":
                    result = node_id(module, MODULE_QUALNAME)
                elif code.co_flags & inspect.CO_OPTIMIZED:  # class bodies lack CO_OPTIMIZED
                    result = node_id(module, qual.replace(".<locals>.", "."))
        code_memo[code] = result
        return result

    def on_call(frame: FrameType) -> None:
        nid = node_for(frame.f_code)
        if nid is None:
            return
        cap.calls_total += 1
        rec = cap.functions.get(nid)
        if rec is None:
            rec = {"ncalls": 0, "args": {}, "returns": [], "samples": []}
            cap.functions[nid] = rec
        rec["ncalls"] += 1
        locs = frame.f_locals
        sample: dict[str, str] | None = {} if samples and len(rec["samples"]) < SAMPLE_LIMIT else None
        for display, bare in _param_names(frame.f_code):
            if bare not in locs:
                continue
            value = locs[bare]
            types = rec["args"].setdefault(display, [])
            tname = _type_name(value)
            if tname not in types and len(types) < TYPE_LIMIT:
                types.append(tname)
            if sample is not None:
                sample[display] = _safe_repr(value)
        if sample is not None:
            pending[id(frame)] = {"args": sample}
        back = frame.f_back
        if back is not None:
            caller = node_for(back.f_code)
            if caller is not None:
                if len(cap.events) < EVENT_LIMIT:
                    cap.events.append([caller, nid])
                else:
                    cap.events_truncated = True

    def on_return(frame: FrameType, arg: Any) -> None:
        nid = code_memo.get(frame.f_code)
        if not nid:
            return
        rec = cap.functions.get(nid)
        if rec is None:
            return
        tname = _type_name(arg)
        if tname not in rec["returns"] and len(rec["returns"]) < TYPE_LIMIT:
            rec["returns"].append(tname)
        sample = pending.pop(id(frame), None)
        if sample is not None and len(rec["samples"]) < SAMPLE_LIMIT:
            sample["ret"] = _safe_repr(arg)
            rec["samples"].append(sample)

    def profiler(frame: FrameType, event: str, arg: Any) -> None:
        if event == "call":
            on_call(frame)
        elif event == "return":
            on_return(frame, arg)

    prev = sys.getprofile()
    sys.setprofile(profiler)
    try:
        yield cap
    finally:
        sys.setprofile(prev)
        cap.functions = {k: cap.functions[k] for k in sorted(cap.functions)}
        for rec in cap.functions.values():
            rec["args"] = {k: sorted(v) for k, v in rec["args"].items()}
            rec["returns"] = sorted(rec["returns"])
