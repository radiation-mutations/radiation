import ast
from ast import AST, Compare, cmpop
from copy import deepcopy
from typing import Dict, Iterable, Iterator, Type

from ..mutation import Mutation
from ..types import Context

MAPPING: Dict[Type[cmpop], Iterable[Type[cmpop]]] = {
    ast.In: (ast.NotIn,),
    ast.NotIn: (ast.In,),
    ast.Gt: (ast.GtE, ast.LtE),
    ast.GtE: (ast.Gt, ast.Lt),
    ast.Lt: (ast.LtE, ast.GtE),
    ast.LtE: (ast.Lt, ast.Gt),
    ast.Eq: (ast.NotEq,),
    ast.NotEq: (ast.Eq,),
    ast.Is: (ast.IsNot,),
    ast.IsNot: (ast.Is,),
}


def _get_replacement_ops(op: cmpop) -> Iterable[cmpop]:
    for op_type in MAPPING[type(op)]:
        yield op_type()


def switch_compare_ops(node: AST, context: Context) -> Iterator[Mutation]:
    if isinstance(node, Compare):
        for index, op in enumerate(node.ops):
            for new_op in _get_replacement_ops(op):
                new_node = deepcopy(node)
                new_node.ops[index] = new_op
                yield Mutation.from_node(new_node, context)
