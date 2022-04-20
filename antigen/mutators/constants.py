from ast import AST, Bytes, Num, Str
from typing import Iterator

from ..types import Context, Mutation


def modify_constants(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, Str):
        yield Mutation(Str(f"XXX{node.s}XXX", kind=None), context)
    if isinstance(node, Bytes):
        yield Mutation(Bytes(b"XXX%bXXX" % node.s, kind=None), context)
    if isinstance(node, Num):
        yield Mutation(Num(node.value + 1, kind=None), context)
        yield Mutation(Num(node.value - 1, kind=None), context)
        yield Mutation(Num(1, kind=None), context)
        yield Mutation(Num(0, kind=None), context)
