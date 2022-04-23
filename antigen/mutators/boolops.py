import ast
from ast import AST, BoolOp, boolop
from typing import Dict, Iterator, Type

from ..mutation import Mutation
from ..types import Context

MAPPING: Dict[Type[boolop], Type[boolop]] = {
    ast.Or: ast.And,
    ast.And: ast.Or,
}


def _switch_op(op: boolop) -> boolop:
    return MAPPING[type(op)]()


def switch_bool_ops(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, BoolOp) and type(node.op) in MAPPING:
        yield Mutation.from_node(
            BoolOp(values=node.values, op=_switch_op(node.op)), context
        )
