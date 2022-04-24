from ast import If, IfExp, While
from pathlib import Path
from textwrap import dedent
from typing import Union, cast

import pytest

from antigen.mutation import Mutation
from antigen.mutators import invert
from antigen.types import Context, FileContext, NodeContext

from ..utils import assert_results_equal, get_node_from_expr, get_node_from_stmt

IfOrWhile = Union[If, While]


@pytest.mark.parametrize(
    ["input_expr", "output_expr", "output_context"],
    (
        (
            "5 if condition else 3",
            "5 if (not condition) else 3",
            Context(
                file=FileContext(path=Path("a.py")),
                node=NodeContext(
                    lineno=1, end_lineno=1, col_offset=5, end_col_offset=14
                ),
            ),
        ),
        (
            "5 if 5 < 3 else 3",
            "5 if (not 5 < 3) else 3",
            Context(
                file=FileContext(path=Path("a.py")),
                node=NodeContext(
                    lineno=1, end_lineno=1, col_offset=5, end_col_offset=10
                ),
            ),
        ),
    ),
)
def test_invert_expr(
    dummy_context: Context, input_expr: str, output_expr: str, output_context: Context
) -> None:
    mutations = invert(get_node_from_expr(input_expr), dummy_context)
    assert_results_equal(
        list(mutations),
        [
            Mutation(
                get_node_from_expr(output_expr),
                cast(Union[IfExp], get_node_from_expr(output_expr)).test,
                output_context,
            )
        ],
    )


@pytest.mark.parametrize(
    ["input_expr", "output_expr", "output_context"],
    (
        (
            dedent(
                """
                if condition:
                    do_stuff()
                """.strip()
            ),
            dedent(
                """
                if not condition:
                    do_stuff()
                """.strip()
            ),
            Context(
                file=FileContext(path=Path("a.py")),
                node=NodeContext(
                    lineno=1, end_lineno=1, col_offset=3, end_col_offset=12
                ),
            ),
        ),
        (
            dedent(
                """
                while condition:
                    do_stuff()
                """.strip()
            ),
            dedent(
                """
                while not condition:
                    do_stuff()
                """.strip()
            ),
            Context(
                file=FileContext(path=Path("a.py")),
                node=NodeContext(
                    lineno=1, end_lineno=1, col_offset=6, end_col_offset=15
                ),
            ),
        ),
    ),
)
def test_invert_stmt(
    dummy_context: Context, input_expr: str, output_expr: str, output_context: Context
) -> None:
    mutations = invert(get_node_from_stmt(input_expr), dummy_context)
    assert_results_equal(
        list(mutations),
        [
            Mutation(
                get_node_from_stmt(output_expr),
                cast(Union[If, While], get_node_from_stmt(output_expr)).test,
                output_context,
            )
        ],
    )
