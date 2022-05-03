from _ast import BinOp
from ast import AST, Compare
from pathlib import Path
from typing import Iterable, cast

import pytest

from radiation.gen import gen_mutations
from radiation.mutation import Mutation
from radiation.types import Context, FileContext, NodeContext

from .utils import assert_results_equal, get_node_from_expr


@pytest.fixture
def dummy_context() -> Context:
    return Context(
        file=FileContext(path=Path("a.py")),
        node=NodeContext(
            lineno=1,
            end_lineno=None,
            col_offset=0,
            end_col_offset=None,
        ),
    )


def test_gen_mutations(dummy_context: Context) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert_results_equal(
        list(
            gen_mutations(
                get_node_from_expr("a + 6 * 3"),
                parent_context=dummy_context,
                mutators=[mutator],
            )
        ),
        [
            Mutation(
                tree=get_node_from_expr("a + 6 * 3"),
                node=cast(BinOp, get_node_from_expr("a + 6 * 3")).left,
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("a + 6 * 3"),
                node=cast(
                    BinOp, cast(BinOp, get_node_from_expr("a + 6 * 3")).right
                ).left,
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("a + 6 * 3"),
                node=cast(
                    BinOp, cast(BinOp, get_node_from_expr("a + 6 * 3")).right
                ).right,
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=8, end_col_offset=9
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("a + 6 * 3"),
                node=cast(BinOp, get_node_from_expr("a - 6 * 3")).right,
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=9
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("a + 6 * 3"),
                node=get_node_from_expr("a + 6 * 3"),
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=9
                    ),
                    extra=None,
                ),
            ),
        ],
    )


def test_gen_mutations_cmp_ops(dummy_context: Context) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert_results_equal(
        list(
            gen_mutations(
                get_node_from_expr("1 < 2 < 3"),
                parent_context=dummy_context,
                mutators=[mutator],
            )
        ),
        [
            Mutation(
                tree=get_node_from_expr("1 < 2 < 3"),
                node=cast(Compare, get_node_from_expr("1 < 2 < 3")).left,
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("1 < 2 < 3"),
                node=cast(Compare, get_node_from_expr("1 < 2 < 3")).comparators[0],
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("1 < 2 < 3"),
                node=cast(Compare, get_node_from_expr("1 < 2 < 3")).comparators[1],
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=8, end_col_offset=9
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=get_node_from_expr("1 < 2 < 3"),
                node=get_node_from_expr("1 < 2 < 3"),
                context=Context(
                    file=FileContext(path=Path("a.py")),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=9
                    ),
                    extra=None,
                ),
            ),
        ],
    )
