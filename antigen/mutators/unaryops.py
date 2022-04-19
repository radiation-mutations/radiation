import ast
from ast import AST, UnaryOp, unaryop
from typing import Dict, Iterator, Type

from ..types import Mutation

MAPPING: Dict[Type[unaryop], Type[unaryop]] = {
    ast.UAdd: ast.USub,
    ast.USub: ast.UAdd,
}


def _switch_op(op: unaryop) -> unaryop:
    return MAPPING[type(op)]()


def switch_unary_ops(node: AST) -> Iterator[Mutation]:
    if isinstance(node, UnaryOp) and type(node.op) == ast.Invert:
        yield Mutation(node.operand)
    if isinstance(node, UnaryOp) and type(node.op) in MAPPING:
        yield Mutation(UnaryOp(_switch_op(node.op), node.operand))
