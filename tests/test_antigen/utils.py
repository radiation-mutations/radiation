from ast import AST, parse
from typing import List

from astunparse import unparse

from antigen.mutation import Mutation


def _normalize(node: AST) -> AST:
    # Some expressions have multiple possible representations,
    # for example: -1 can be a constant or a 1 with a unary minus operator.
    # This normalises all cases to one representation.
    return parse(unparse(node))


def assert_mutations_equal(a: Mutation, b: Mutation) -> None:
    assert unparse(_normalize(a.node)) == unparse(_normalize(b.node))
    assert unparse(_normalize(a.tree)) == unparse(_normalize(b.tree))
    assert a.context == b.context


def assert_results_equal(a: List[Mutation], b: List[Mutation]) -> None:
    assert len(a) == len(b)
    for a_item, b_item in zip(a, b):
        assert_mutations_equal(a_item, b_item)


def get_node_from_expr(expr: str) -> AST:
    return parse(expr, mode="eval").body


def get_node_from_stmt(expr: str) -> AST:
    return parse(expr, mode="single").body[0]
