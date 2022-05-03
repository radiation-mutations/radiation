import ast
from ast import AST, BinOp, operator
from typing import Dict, Iterator, Type

from ..mutation import Mutation
from ..types import Context

MAPPING: Dict[Type[operator], Type[operator]] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.Div,
    ast.Div: ast.Mult,
    ast.FloorDiv: ast.Div,
}


def _switch_op(op: operator) -> operator:
    return MAPPING[type(op)]()


def switch_bin_ops(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, BinOp) and type(node.op) in MAPPING:
        yield Mutation.from_node(
            BinOp(left=node.left, op=_switch_op(node.op), right=node.right), context
        )
