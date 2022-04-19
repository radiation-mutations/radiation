from ast import AST, If, IfExp, Not, UnaryOp, While
from typing import Iterator

from ..types import Mutation


def _invert(node: AST) -> AST:
    return UnaryOp(op=Not(), operand=node)


def invert(node: AST) -> Iterator[Mutation]:
    if isinstance(node, (IfExp, If, While)):
        yield Mutation(
            IfExp(body=node.body, test=_invert(node.test), orelse=node.orelse)
        )
