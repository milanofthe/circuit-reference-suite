"""Circuits by their properties: a filter is an expression over the columns of index.csv.

    m >= 1 and 100 <= devices <= 10000 and 'tran' in analyses and not linear
    family in ('opamp', 'ldo') or glob(name, 'synthetic_rc*')

Comparisons (chained too), ``and``, ``or``, ``not``, ``in`` and ``not in``, numbers,
strings, tuples and lists of them, and ``glob(column, pattern)``. The columns analyses,
libraries and models are tuples of words. A comparison with an empty value (a node count
the netlist does not give) is false. The expression is checked against this grammar
and evaluated on it, never by ``eval``.
"""
from __future__ import annotations

import ast
import csv
import fnmatch
import operator
from collections.abc import Callable
from functools import lru_cache

from .entry import ROOT

INDEX = ROOT / "index.csv"
WORDS = ("analyses", "libraries", "models")
COMPARE = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
           ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
           ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}


class FilterError(ValueError):
    pass


def _value(column: str, text: str):
    if column in WORDS:
        return tuple(text.split())
    if text in ("true", "false"):
        return text == "true"
    if text == "":
        return None
    try:
        return int(text)
    except ValueError:
        return text


@lru_cache(maxsize=1)
def index() -> tuple[dict, ...]:
    with INDEX.open(encoding="utf-8", newline="") as f:
        return tuple({k: _value(k, v) for k, v in row.items()} for row in csv.DictReader(f))


def compile_filter(expr: str) -> Callable[[dict], bool]:
    """The filter as a function of an index row; raises FilterError on anything outside
    the grammar or a column the index does not have."""
    columns = set(index()[0])
    try:
        tree = ast.parse(expr, mode="eval").body
    except SyntaxError as e:
        raise FilterError(f"not an expression: {expr!r} ({e.msg})") from None

    def build(node) -> Callable[[dict], object]:
        if isinstance(node, ast.BoolOp):
            parts = [build(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return lambda r: all(p(r) for p in parts)
            return lambda r: any(p(r) for p in parts)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            inner = build(node.operand)
            return lambda r: not inner(r)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = build(node.operand)
            return lambda r: -inner(r)
        if isinstance(node, ast.Compare) and all(type(o) in COMPARE for o in node.ops):
            terms = [build(node.left)] + [build(c) for c in node.comparators]
            ops = [COMPARE[type(o)] for o in node.ops]

            def compare(r):
                values = [t(r) for t in terms]
                return all(a is not None and b is not None and op(a, b)
                           for op, a, b in zip(ops, values, values[1:]))
            return compare
        if isinstance(node, ast.Name):
            if node.id not in columns:
                raise FilterError(f"no column {node.id!r}; columns: {', '.join(sorted(columns))}")
            return lambda r, k=node.id: r[k]
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str, bool)):
            return lambda r, v=node.value: v
        if isinstance(node, (ast.Tuple, ast.List)):
            items = [build(e) for e in node.elts]
            return lambda r: tuple(i(r) for i in items)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "glob" and len(node.args) == 2 and not node.keywords):
            value, pattern = (build(a) for a in node.args)
            return lambda r: (v := value(r)) is not None and fnmatch.fnmatchcase(str(v), pattern(r))
        raise FilterError(f"not allowed in a filter: {ast.unparse(node)!r}")

    test = build(tree)
    return lambda row: bool(test(row))


def select(expr: str | None) -> list[str]:
    """The names of the circuits a filter matches, all when there is none."""
    test = compile_filter(expr) if expr else (lambda row: True)
    return [row["name"] for row in index() if test(row)]
