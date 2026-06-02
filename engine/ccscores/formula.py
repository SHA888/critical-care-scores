"""Safe arithmetic expression evaluator for score formulas.

Parses an expression with Python's `ast` module and walks a strict whitelist of
node types — NO `eval`, no attribute access, no arbitrary calls. Names resolve
to input values; booleans coerce to 1/0. The grammar deliberately mirrors what
the TypeScript engine implements so both stay in lock-step.

Allowed functions: ln, exp, log10, sqrt, min, max, round, floor, ceil, abs,
clamp(x, lo, hi).
"""

from __future__ import annotations

import ast
import math
from typing import Mapping

from .errors import EngineError


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def round_half_up(x: float) -> float:
    """Round half away-from-zero via floor(x+0.5), matching JS Math.round.

    Used by both engines so cross-implementation golden vectors agree exactly
    (Python's built-in round() is banker's rounding and would diverge)."""
    return float(math.floor(x + 0.5))


# name -> (callable, arity or None for variadic min/max)
_FUNCS = {
    "ln": (math.log, 1),
    "exp": (math.exp, 1),
    "log10": (math.log10, 1),
    "sqrt": (math.sqrt, 1),
    "floor": (lambda x: float(math.floor(x)), 1),
    "ceil": (lambda x: float(math.ceil(x)), 1),
    "abs": (abs, 1),
    "round": (round_half_up, 1),
    "min": (min, None),
    "max": (max, None),
    "clamp": (_clamp, 3),
}

_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
    ast.Mod: lambda a, b: a % b,
}


def _coerce(value: object, name: str) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raise EngineError(f"formula variable '{name}' is not numeric: {value!r}")


def evaluate(expr: str, variables: Mapping[str, object]) -> float:
    """Evaluate `expr` over `variables`. Raises EngineError on anything unsafe."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:  # pragma: no cover - guarded by schema in practice
        raise EngineError(f"invalid formula syntax: {expr!r} ({exc})") from exc

    def walk(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return 1.0 if node.value else 0.0
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise EngineError(f"unsupported literal in formula: {node.value!r}")
        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise EngineError(f"formula references unknown variable '{node.id}'")
            return _coerce(variables[node.id], node.id)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -walk(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +walk(node.operand)
            raise EngineError("unsupported unary operator in formula")
        if isinstance(node, ast.BinOp):
            op = _BINOPS.get(type(node.op))
            if op is None:
                raise EngineError(f"unsupported operator in formula: {type(node.op).__name__}")
            return op(walk(node.left), walk(node.right))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords or node.func.id not in _FUNCS:
                fn = getattr(node.func, "id", "?")
                raise EngineError(f"call to disallowed function '{fn}' in formula")
            func, arity = _FUNCS[node.func.id]
            args = [walk(a) for a in node.args]
            if arity is not None and len(args) != arity:
                raise EngineError(f"function '{node.func.id}' expects {arity} args, got {len(args)}")
            return float(func(*args))
        raise EngineError(f"disallowed expression element: {type(node).__name__}")

    return walk(tree)
