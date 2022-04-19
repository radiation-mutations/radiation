from ast import AST, Bytes, Num, Str
from typing import Iterator

from ..types import Mutation


def modify_constants(node: AST) -> Iterator[Mutation]:
    if isinstance(node, Str):
        yield Mutation(Str(f"XXX{node.s}XXX", kind=None))
    if isinstance(node, Bytes):
        yield Mutation(Bytes(b"XXX%bXXX" % node.s, kind=None))
    if isinstance(node, Num):
        yield Mutation(Num(node.value + 1, kind=None))
        yield Mutation(Num(node.value - 1, kind=None))
        yield Mutation(Num(1, kind=None))
        yield Mutation(Num(0, kind=None))
