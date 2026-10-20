"""Small AST helpers shared by the parser and the control-flow extractor."""

from __future__ import annotations

import ast


def safe_unparse(node: ast.AST, limit: int = 80) -> str:
    try:
        return ast.unparse(node)[:limit]
    except Exception:
        return "<expr>"


def dotted_parts(node: ast.expr) -> tuple[str, ...]:
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
