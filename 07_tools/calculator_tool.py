"""Safe arithmetic on integers/floats via AST (no arbitrary code)."""

from __future__ import annotations

import ast
import operator

from pydantic import BaseModel, Field

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


class CalcParams(BaseModel):
    expression: str = Field(..., description="Arithmetic like (2+3)*4")


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand)
    raise ValueError("unsupported expression")


def calculator_eval(params: CalcParams) -> str:
    tree = ast.parse(params.expression, mode="eval")
    v = _eval(tree.body)
    return str(v)


if __name__ == "__main__":
    print(calculator_eval(CalcParams(expression="(2+3)*4")))
