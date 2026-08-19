"""Pass 1: parse one file's AST into a ModuleInfo (symbol tables + raw call records)."""

from __future__ import annotations

import ast
import tokenize
from pathlib import Path
from typing import Any

from flowcli.models import (
    MODULE_QUALNAME,
    ArgAtom,
    CallKind,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseFailure,
    RawCall,
)


def parse_module(module_name: str, file: Path) -> ModuleInfo | ParseFailure:
    try:
        with tokenize.open(file) as fh:  # honors PEP 263 encoding declarations
            source = fh.read()
    except (OSError, SyntaxError, ValueError) as exc:
        return ParseFailure(file=str(file), error=f"{type(exc).__name__}: {exc}")
    return parse_source(module_name, str(file), source, is_package=file.name == "__init__.py")


def parse_source(module_name: str, file: str, source: str, *, is_package: bool = False) -> ModuleInfo | ParseFailure:
    try:
        tree = ast.parse(source, filename=file)
    except (SyntaxError, ValueError) as exc:
        return ParseFailure(file=file, error=f"{type(exc).__name__}: {exc}")
    info = ModuleInfo(name=module_name, file=file, is_package=is_package)
    _Collector(info).visit(tree)
    return info


def _safe_unparse(node: ast.AST, limit: int = 80) -> str:
    try:
        return ast.unparse(node)[:limit]
    except Exception:
        return "<expr>"


class _Collector(ast.NodeVisitor):
    """Single walk per file: registers functions/classes/imports and records raw calls.

    Scope is tracked as a stack of (kind, registered_qualname); the current
    call sink is the enclosing FunctionInfo, or the lazily-created `<module>`
    pseudo-function for import-time code (top-level calls, decorators,
    class-body statements).
    """

    def __init__(self, info: ModuleInfo) -> None:
        self.info = info
        self._stack: list[tuple[str, str]] = []  # (kind: "class"|"function", qualname)
        self._sink: FunctionInfo | None = None  # None = module level

    # -- helpers ---------------------------------------------------------

    def _qual(self, name: str) -> str:
        return f"{self._stack[-1][1]}.{name}" if self._stack else name

    def _nearest_class(self) -> str | None:
        for kind, qualname in reversed(self._stack):
            if kind == "class":
                return qualname
        return None

    def _ensure_module_fn(self) -> FunctionInfo:
        fn = self.info.functions.get(MODULE_QUALNAME)
        if fn is None:
            fn = FunctionInfo(
                qualname=MODULE_QUALNAME,
                module=self.info.name,
                file=self.info.file,
                lineno=1,
            )
            self.info.functions[MODULE_QUALNAME] = fn
        return fn

    def _record_call(self, rc: RawCall) -> None:
        (self._sink or self._ensure_module_fn()).raw_calls.append(rc)

    def _classify_callable_expr(self, expr: ast.expr, lineno: int) -> RawCall | None:
        if isinstance(expr, ast.Name):
            if expr.id == "super":  # bare super() carries no edge; super().m() is handled below
                return None
            return RawCall(CallKind.NAME, (expr.id,), lineno, expr.id)
        if isinstance(expr, ast.Attribute):
            return self._classify_attribute(expr, lineno)
        return RawCall(CallKind.OPAQUE, (), lineno, _safe_unparse(expr))

    def _classify_attribute(self, expr: ast.Attribute, lineno: int) -> RawCall:
        attrs: list[str] = []
        cur: ast.expr = expr
        while isinstance(cur, ast.Attribute):
            attrs.append(cur.attr)
            cur = cur.value
        attrs.reverse()
        in_class = self._nearest_class() is not None
        if isinstance(cur, ast.Name):
            parts = (cur.id, *attrs)
            hint = ".".join(parts)
            if cur.id in ("self", "cls") and in_class:
                if len(parts) == 2:
                    kind = CallKind.SELF_ATTR if cur.id == "self" else CallKind.CLS_ATTR
                    return RawCall(kind, parts, lineno, hint)
                return RawCall(CallKind.OPAQUE, parts, lineno, hint)  # self.helper.run() — instance attr
            return RawCall(CallKind.DOTTED, parts, lineno, hint)
        is_super = isinstance(cur, ast.Call) and isinstance(cur.func, ast.Name) and cur.func.id == "super"
        if is_super and len(attrs) == 1 and in_class:
            return RawCall(CallKind.SUPER_ATTR, ("super", attrs[0]), lineno, f"super().{attrs[0]}")
        return RawCall(CallKind.OPAQUE, tuple(attrs), lineno, _safe_unparse(expr))

    def _visit_decorators(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
        """Record decorator applications as calls in the *enclosing* sink (they execute there)."""
        names: list[str] = []
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            names.append(_safe_unparse(target))
            if isinstance(dec, ast.Call):
                self.visit(dec)  # records the call and walks its args
            else:
                rc = self._classify_callable_expr(dec, node.lineno)
                if rc is not None:
                    self._record_call(rc)
        return names

    # -- definitions -----------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_function(node)

    def _handle_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if _is_overload_stub(node):
            return  # @overload defs are type declarations; the real def follows and keeps the name
        qualname = self._qual(node.name)
        if qualname in self.info.functions:
            qualname = f"{qualname}#{node.lineno}"
        fn = FunctionInfo(
            qualname=qualname,
            module=self.info.name,
            file=self.info.file,
            lineno=node.lineno,
            class_qualname=self._nearest_class(),
        )
        self.info.functions[qualname] = fn

        if self._stack and self._stack[-1][0] == "class":
            owner = self.info.classes.get(self._stack[-1][1])
            if owner is not None:
                owner.methods[node.name] = qualname  # redefinition: the last def is what exists at runtime

        fn.decorators = self._visit_decorators(node)
        fn.flow = _flow_of_body(node.body, [_MAX_FLOW_NODES])
        fn.params = _param_list(node.args)
        if node.returns is not None:
            fn.returns_ann = _safe_unparse(node.returns, 60)
            fn.returns_ann_parts = _annotation_parts(node.returns)
        for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
            if arg.annotation is not None:
                parts = _annotation_parts(arg.annotation)
                if parts:
                    fn.local_types[arg.arg] = parts
        for default in [*node.args.defaults, *(d for d in node.args.kw_defaults if d is not None)]:
            self.visit(default)  # defaults execute at def time, in the enclosing sink

        prev_sink = self._sink
        self._sink = fn
        self._stack.append(("function", qualname))
        for stmt in node.body:
            self.visit(stmt)
        self._stack.pop()
        self._sink = prev_sink

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qualname = self._qual(node.name)
        if qualname in self.info.classes:
            qualname = f"{qualname}#{node.lineno}"
        ci = ClassInfo(qualname=qualname, module=self.info.name, lineno=node.lineno)
        self.info.classes[qualname] = ci

        for base in node.bases:
            target = base.value if isinstance(base, ast.Subscript) else base  # unwrap Generic[T]-style bases
            parts = _dotted_parts(target)
            ci.base_reprs.append(_safe_unparse(base, 40))
            if parts:
                ci.bases.append(parts)
            else:
                self.visit(base)  # dynamic base like namedtuple(...) — collect calls, no hierarchy edge
        for kw in node.keywords:
            self.visit(kw.value)

        ci.decorators = self._visit_decorators(node)

        prev_sink = self._sink
        self._sink = None  # class bodies execute at import time
        self._stack.append(("class", qualname))
        for stmt in node.body:
            self.visit(stmt)
        self._stack.pop()
        self._sink = prev_sink

    # -- imports ---------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.asname:
                self.info.imports[alias.asname] = alias.name
            else:
                top = alias.name.split(".")[0]
                self.info.imports[top] = top

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = self._resolve_from_base(node)
        if base is None:
            return
        for alias in node.names:
            if alias.name == "*":
                if base:
                    self.info.star_imports.append(base)
            else:
                local = alias.asname or alias.name
                self.info.imports[local] = f"{base}.{alias.name}" if base else alias.name

    def _resolve_from_base(self, node: ast.ImportFrom) -> str | None:
        if node.level == 0:
            return node.module or None
        anchor = self.info.name.split(".")
        if not self.info.is_package:
            anchor = anchor[:-1]
        drop = node.level - 1
        if drop > len(anchor):
            return None  # relative import beyond the scanned root
        if drop:
            anchor = anchor[:-drop]
        parts = anchor + (node.module.split(".") if node.module else [])
        return ".".join(parts) if parts else None

    # -- local & instance-attribute type tracking (for method resolution) --

    def _record_self_attr(
        self, attr: str, parts: tuple[str, ...], *, ann: str | None = None, lineno: int = 0, source: str = "init"
    ) -> None:
        cq = self._nearest_class()
        if cq is None:
            return
        ci = self.info.classes.get(cq)
        if ci is None:
            return
        if parts:
            ci.attr_types.setdefault(attr, parts)  # first sight wins (__init__ usually comes first)
        self._record_field(ci, attr, ann=ann, parts=parts, lineno=lineno, source=source)

    def _record_field(
        self,
        ci: ClassInfo,
        name: str,
        *,
        ann: str | None = None,
        parts: tuple[str, ...] = (),
        value: str | None = None,
        lineno: int = 0,
        source: str = "class",
    ) -> None:
        for existing in ci.fields:
            if existing["name"] == name:
                if ann and not existing["ann"]:  # a later annotation improves an earlier bare assignment
                    existing.update(ann=ann, parts=list(parts))
                return
        ci.fields.append(
            {"name": name, "ann": ann, "parts": list(parts), "value": value, "source": source, "lineno": lineno}
        )

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) == 1:
            target = node.targets[0]
            parts = _dotted_parts(node.value.func) if isinstance(node.value, ast.Call) else ()
            in_class_body = self._sink is None and self._stack and self._stack[-1][0] == "class"
            if parts and isinstance(target, ast.Name) and self._sink is not None:
                self._sink.local_types[target.id] = parts  # x = Engine() -> x behaves as Engine
            elif in_class_body and isinstance(target, ast.Name):
                ci = self.info.classes.get(self._stack[-1][1])
                if ci is not None:  # class-level constant, or an enum member
                    self._record_field(
                        ci, target.id, parts=parts, value=_safe_unparse(node.value, 30), lineno=node.lineno
                    )
                if parts:
                    self._record_self_attr(target.id, parts, lineno=node.lineno, source="class")
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                # every `self.x = ...` is a property; only a constructor call also gives it a type
                self._record_self_attr(target.attr, parts, lineno=node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        parts = _annotation_parts(node.annotation)
        ann = _safe_unparse(node.annotation, 40)
        if isinstance(node.target, ast.Name):
            if self._sink is not None:
                if parts:
                    self._sink.local_types[node.target.id] = parts
            elif self._stack and self._stack[-1][0] == "class":
                # class-body annotation: the dataclass / attrs / msgspec field style
                self._record_self_attr(node.target.id, parts, ann=ann, lineno=node.lineno, source="class")
        elif (
            isinstance(node.target, ast.Attribute)
            and isinstance(node.target.value, ast.Name)
            and node.target.value.id == "self"
        ):
            self._record_self_attr(node.target.attr, parts, ann=ann, lineno=node.lineno)  # annotated instance attr
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if self._sink is None and _is_main_guard(node.test):
            self.info.has_main_guard = True
        self.generic_visit(node)

    # -- returns & generators (for return-type inference) ------------------

    def visit_Return(self, node: ast.Return) -> None:
        if self._sink is not None:
            tag, value = _classify_return_expr(node.value)
            self._sink.return_exprs.append((tag, value, node.lineno))
        self.generic_visit(node)

    def _mark_generator(self, node: ast.Yield | ast.YieldFrom) -> None:
        if self._sink is not None:
            self._sink.is_generator = True
        self.generic_visit(node)

    visit_Yield = _mark_generator
    visit_YieldFrom = _mark_generator

    # -- calls -----------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        rc = self._classify_callable_expr(node.func, node.lineno)
        if rc is not None:
            rc.args = _classify_args(node)
            self._record_call(rc)
        self.generic_visit(node)  # nested calls in args (and in the func expr itself) still count


# -- control-flow extraction ------------------------------------------------
#
# Each function gets a nested, JSON-able flow tree used for the deterministic
# flowchart view. Node shapes:
#   {"t": "stmt"|"ret", "label", "line", "end"}
#   {"t": "if",     "label", "line", "head_end", "then": [...], "else": [...]}
#   {"t": "loop",   "label", "line", "head_end", "body": [...]}
#   {"t": "with",   "label", "line", "head_end", "body": [...]}
#   {"t": "try",    "label", "line", "head_end", "body": [...],
#                   "handlers": [{"label", "body": [...]}], "final": [...]}
#   {"t": "switch", "label", "line", "head_end", "cases": [{"label", "body": [...]}]}
# The resolver's per-line call targets are attached later (graph.build_graph)
# as a "calls" list on stmt/ret/head nodes.

_MAX_FLOW_NODES = 200
_LABEL_LIMIT = 64


def _short(text: str) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= _LABEL_LIMIT else flat[: _LABEL_LIMIT - 1] + "…"


def _flow_of_body(body: list[ast.stmt], budget: list[int]) -> list[dict]:
    out: list[dict] = []
    for stmt in body:
        if budget[0] <= 0:
            out.append({"t": "stmt", "label": "…", "line": stmt.lineno, "end": stmt.lineno})
            break
        budget[0] -= 1
        out.append(_flow_of_stmt(stmt, budget))
    return out


def _flow_of_stmt(stmt: ast.stmt, budget: list[int]) -> dict:  # noqa: C901
    line = stmt.lineno
    if isinstance(stmt, ast.If):
        return {
            "t": "if",
            "label": "if " + _short(_safe_unparse(stmt.test, _LABEL_LIMIT)),
            "line": line,
            "head_end": stmt.test.end_lineno or line,
            "then": _flow_of_body(stmt.body, budget),
            "else": _flow_of_body(stmt.orelse, budget),
        }
    if isinstance(stmt, ast.For | ast.AsyncFor):
        label = "for " + _short(f"{_safe_unparse(stmt.target)} in {_safe_unparse(stmt.iter)}")
        return {
            "t": "loop",
            "label": label,
            "line": line,
            "head_end": stmt.iter.end_lineno or line,
            "body": _flow_of_body(stmt.body, budget),
        }
    if isinstance(stmt, ast.While):
        return {
            "t": "loop",
            "label": "while " + _short(_safe_unparse(stmt.test, _LABEL_LIMIT)),
            "line": line,
            "head_end": stmt.test.end_lineno or line,
            "body": _flow_of_body(stmt.body, budget),
        }
    if isinstance(stmt, ast.With | ast.AsyncWith):
        items = ", ".join(_safe_unparse(it, 40) for it in stmt.items)
        return {
            "t": "with",
            "label": _short(f"with {items}"),
            "line": line,
            "head_end": stmt.items[-1].context_expr.end_lineno or line,
            "body": _flow_of_body(stmt.body, budget),
        }
    if isinstance(stmt, ast.Try | ast.TryStar):
        return _flow_of_try(stmt, budget)
    if isinstance(stmt, ast.Match):
        return {
            "t": "switch",
            "label": "match " + _short(_safe_unparse(stmt.subject, 40)),
            "line": line,
            "head_end": stmt.subject.end_lineno or line,
            "cases": [
                {"label": "case " + _short(_safe_unparse(c.pattern, 40)), "body": _flow_of_body(c.body, budget)}
                for c in stmt.cases
            ],
        }
    if isinstance(stmt, ast.Return | ast.Raise):
        return {"t": "ret", "label": _short(_safe_unparse(stmt, _LABEL_LIMIT)), "line": line, "end": _end(stmt)}
    if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
        return {"t": "stmt", "label": f"def {stmt.name}(…)", "line": line, "end": line}
    if isinstance(stmt, ast.ClassDef):
        return {"t": "stmt", "label": f"class {stmt.name}", "line": line, "end": line}
    return {"t": "stmt", "label": _short(_safe_unparse(stmt, _LABEL_LIMIT)), "line": line, "end": _end(stmt)}


def _flow_of_try(stmt: ast.Try | ast.TryStar, budget: list[int]) -> dict:
    handlers = [
        {
            "label": "except" + (f" {_short(_safe_unparse(h.type, 40))}" if h.type else ""),
            "body": _flow_of_body(h.body, budget),
        }
        for h in stmt.handlers
    ]
    return {
        "t": "try",
        "label": "try",
        "line": stmt.lineno,
        "head_end": stmt.lineno,
        "body": _flow_of_body(stmt.body + stmt.orelse, budget),
        "handlers": handlers,
        "final": _flow_of_body(stmt.finalbody, budget),
    }


def _end(stmt: ast.stmt) -> int:
    return stmt.end_lineno or stmt.lineno


def _is_main_guard(test: ast.expr) -> bool:
    """`__name__ == "__main__"` in either order."""
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    sides = [test.left, test.comparators[0]]
    names = {s.id for s in sides if isinstance(s, ast.Name)}
    consts = {s.value for s in sides if isinstance(s, ast.Constant)}
    return "__name__" in names and "__main__" in consts


def _param_list(args: ast.arguments) -> list[dict[str, str | None]]:
    """Canonical parameter display list: posonly, args, *vararg, kwonly, **kwarg."""

    def entry(arg: ast.arg, default: ast.expr | None, prefix: str = "") -> dict[str, str | None]:
        return {
            "name": prefix + arg.arg,
            "ann": _safe_unparse(arg.annotation, 40) if arg.annotation is not None else None,
            "default": _safe_unparse(default, 30) if default is not None else None,
        }

    out: list[dict[str, str | None]] = []
    positional = [*args.posonlyargs, *args.args]
    defaults: list[ast.expr | None] = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(positional, defaults):
        out.append(entry(arg, default))
    if args.vararg is not None:
        out.append(entry(args.vararg, None, "*"))
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        out.append(entry(arg, default))
    if args.kwarg is not None:
        out.append(entry(args.kwarg, None, "**"))
    return out


_CONST_TYPES: list[tuple[type, str]] = [(bool, "bool"), (int, "int"), (float, "float"), (str, "str"), (bytes, "bytes")]

_ARG_LITERALS: list[tuple[type, str]] = [
    (ast.List, "list"),
    (ast.ListComp, "list"),
    (ast.Dict, "dict"),
    (ast.DictComp, "dict"),
    (ast.Set, "set"),
    (ast.SetComp, "set"),
    (ast.Tuple, "tuple"),
]


def _classify_args(node: ast.Call) -> tuple[ArgAtom, ...]:
    """Capture each call-site argument for the simulation pass."""
    out: list[ArgAtom] = []
    for arg in node.args:
        out.append((None, *_classify_arg_expr(arg)))
    for kw in node.keywords:
        out.append((kw.arg, *_classify_arg_expr(kw.value)))  # kw.arg is None for **kwargs
    return tuple(out)


def _literal_arg(value: ast.expr) -> tuple[str, Any] | None:
    if isinstance(value, ast.Constant):
        tname = "None" if value.value is None else ""
        for pytype, name in _CONST_TYPES:
            if isinstance(value.value, pytype):
                tname = name
                break
        return ("lit", (_safe_unparse(value, 30), tname or "object"))
    if isinstance(value, ast.JoinedStr):
        return ("lit", (_safe_unparse(value, 30), "str"))
    for node_type, tname in _ARG_LITERALS:
        if isinstance(value, node_type):
            return ("lit", (_safe_unparse(value, 30), tname))
    return None


def _classify_arg_expr(value: ast.expr) -> tuple[str, Any]:
    if isinstance(value, ast.Starred):
        return ("star", "")
    literal = _literal_arg(value)
    if literal is not None:
        return literal
    if isinstance(value, ast.Name):
        return ("name", value.id)
    if isinstance(value, ast.Call):
        parts = _dotted_parts(value.func)
        return ("call", parts) if parts else ("unknown", "")
    if isinstance(value, ast.Attribute):
        parts = _dotted_parts(value)
        if parts and parts[0] == "self" and len(parts) == 2:
            return ("selfattr", parts[1])
    return ("unknown", "")


def _classify_return_expr(value: ast.expr | None) -> tuple[str, Any]:
    """Coarse classification of a return expression for the inference pass."""
    if value is None:
        return ("const", "None")
    if isinstance(value, ast.Constant):
        if value.value is None:
            return ("const", "None")
        for pytype, tname in _CONST_TYPES:  # bool before int — isinstance(True, int) is True
            if isinstance(value.value, pytype):
                return ("const", tname)
        return ("unknown", "")
    if isinstance(value, ast.JoinedStr):
        return ("const", "str")
    if isinstance(value, ast.List | ast.ListComp):
        return ("const", "list")
    if isinstance(value, ast.Dict | ast.DictComp):
        return ("const", "dict")
    if isinstance(value, ast.Set | ast.SetComp):
        return ("const", "set")
    if isinstance(value, ast.Tuple):
        return ("const", "tuple")
    if isinstance(value, ast.Call):
        parts = _dotted_parts(value.func)
        return ("call", parts) if parts else ("unknown", "")
    if isinstance(value, ast.Name):
        return ("name", value.id)
    return ("unknown", "")


def _is_overload_stub(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True for @overload / @typing.overload-decorated defs — type declarations, not runtime code."""
    for dec in node.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        parts = _dotted_parts(target)
        if parts and parts[-1] == "overload":
            return True
    return False


def _annotation_parts(node: ast.expr) -> tuple[str, ...]:
    """Dotted parts of the class a type annotation names; () when it names none we could use.

    Unwraps `X | None`, `Optional[X]`, and string annotations. Generic containers
    (`list[X]`, `dict[...]`) resolve to their base, which is never a parsed class — fine.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return _annotation_parts(ast.parse(node.value, mode="eval").body)
        except (SyntaxError, ValueError):
            return ()
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left = _annotation_parts(node.left)
        return left or _annotation_parts(node.right)
    if isinstance(node, ast.Subscript):
        base = _dotted_parts(node.value)
        if base and base[-1] == "Optional":
            return _annotation_parts(node.slice)
        return base
    return _dotted_parts(node)


def _dotted_parts(node: ast.expr) -> tuple[str, ...]:
    """Flatten a Name/Attribute chain to its dotted parts; () if not a plain chain."""
    attrs: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        attrs.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        attrs.append(cur.id)
        return tuple(reversed(attrs))
    return ()
