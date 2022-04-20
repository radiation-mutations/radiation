import ast
from ast import AST, UnaryOp, unaryop
from typing import Dict, Iterator, Type

from ..mutation import Mutation
from ..types import Context

MAPPING: Dict[Type[unaryop], Type[unaryop]] = {
    ast.UAdd: ast.USub,
    ast.USub: ast.UAdd,
}


def _switch_op(op: unaryop) -> unaryop:
    return MAPPING[type(op)]()


def switch_unary_ops(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, UnaryOp) and type(node.op) == ast.Invert:
        yield Mutation.from_node(node.operand, context)
    if isinstance(node, UnaryOp) and type(node.op) in MAPPING:
        yield Mutation.from_node(UnaryOp(_switch_op(node.op), node.operand), context)
