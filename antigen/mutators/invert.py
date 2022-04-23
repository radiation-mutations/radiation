from ast import AST, If, IfExp, Not, UnaryOp, While
from typing import Iterator

from ..context import get_context
from ..mutation import Mutation
from ..types import Context


def _invert(node: AST) -> AST:
    return UnaryOp(op=Not(), operand=node)


def invert(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, (IfExp, If, While)):
        yield Mutation(
            type(node)(body=node.body, test=_invert(node.test), orelse=node.orelse),
            _invert(node.test),
            get_context(node.test, context),
        )
