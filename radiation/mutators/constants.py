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
        values = {0, 1, node.value - 1, node.value + 1} - {node.value}
        for val in sorted(values, key=lambda n: (n.real, n.imag)):
            yield Mutation.from_node(Num(val, kind=None), context)
