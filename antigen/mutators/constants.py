from ast import AST, Bytes, Num, Str
from typing import Iterator

from ..mutation import Mutation
from ..types import Context


def modify_constants(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, Str):
        yield Mutation.from_node(Str(f"XXX{node.s}XXX", kind=None), context)
    if isinstance(node, Bytes):
        yield Mutation.from_node(Bytes(b"XXX%bXXX" % node.s, kind=None), context)
    if isinstance(node, Num):
        yield Mutation.from_node(Num(node.value + 1, kind=None), context)
        yield Mutation.from_node(Num(node.value - 1, kind=None), context)
        yield Mutation.from_node(Num(1, kind=None), context)
        yield Mutation.from_node(Num(0, kind=None), context)
