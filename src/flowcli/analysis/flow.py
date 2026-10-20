"""Control-flow extraction: each function body becomes a nested, JSON-able flow tree.

The tree drives the deterministic flowchart view. Node shapes:
  {"t": "stmt"|"ret", "label", "line", "end"}
  {"t": "if",     "label", "line", "head_end", "then": [...], "else": [...]}
  {"t": "loop",   "label", "line", "head_end", "body": [...]}
  {"t": "with",   "label", "line", "head_end", "body": [...]}
  {"t": "try",    "label", "line", "head_end", "body": [...],
                  "handlers": [{"label", "body": [...]}], "final": [...]}
  {"t": "switch", "label", "line", "head_end", "cases": [{"label", "body": [...]}]}

The resolver's per-line call targets are attached later (graph.build) as a
"calls" list on stmt/ret/head nodes.
"""

from __future__ import annotations

import ast

from flowcli.analysis.astutil import safe_unparse

MAX_FLOW_NODES = 200
_LABEL_LIMIT = 64


def flow_of(body: list[ast.stmt]) -> list[dict]:
    """Flow tree for one function body, capped at MAX_FLOW_NODES statements."""
    return _flow_of_body(body, [MAX_FLOW_NODES])


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
            "label": "if " + _short(safe_unparse(stmt.test, _LABEL_LIMIT)),
            "line": line,
            "head_end": stmt.test.end_lineno or line,
            "then": _flow_of_body(stmt.body, budget),
            "else": _flow_of_body(stmt.orelse, budget),
        }
    if isinstance(stmt, ast.For | ast.AsyncFor):
        label = "for " + _short(f"{safe_unparse(stmt.target)} in {safe_unparse(stmt.iter)}")
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
            "label": "while " + _short(safe_unparse(stmt.test, _LABEL_LIMIT)),
            "line": line,
            "head_end": stmt.test.end_lineno or line,
            "body": _flow_of_body(stmt.body, budget),
        }
    if isinstance(stmt, ast.With | ast.AsyncWith):
        items = ", ".join(safe_unparse(it, 40) for it in stmt.items)
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
            "label": "match " + _short(safe_unparse(stmt.subject, 40)),
            "line": line,
            "head_end": stmt.subject.end_lineno or line,
            "cases": [
                {"label": "case " + _short(safe_unparse(c.pattern, 40)), "body": _flow_of_body(c.body, budget)}
                for c in stmt.cases
            ],
        }
    if isinstance(stmt, ast.Return | ast.Raise):
        return {"t": "ret", "label": _short(safe_unparse(stmt, _LABEL_LIMIT)), "line": line, "end": _end(stmt)}
    if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
        return {"t": "stmt", "label": f"def {stmt.name}(…)", "line": line, "end": line}
    if isinstance(stmt, ast.ClassDef):
        return {"t": "stmt", "label": f"class {stmt.name}", "line": line, "end": line}
    return {"t": "stmt", "label": _short(safe_unparse(stmt, _LABEL_LIMIT)), "line": line, "end": _end(stmt)}


def _flow_of_try(stmt: ast.Try | ast.TryStar, budget: list[int]) -> dict:
    handlers = [
        {
            "label": "except" + (f" {_short(safe_unparse(h.type, 40))}" if h.type else ""),
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
