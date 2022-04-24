from typing import Tuple

import pytest

from antigen.mutation import Mutation
from antigen.mutators import switch_compare_ops
from antigen.types import Context

from ..utils import assert_results_equal, get_node_from_expr


@pytest.mark.parametrize(
    ["input_expr", "output_exprs"],
    (
        ("3 < 1", ("3 <= 1", "3 >= 1")),
        ("3 > 1", ("3 >= 1", "3 <= 1")),
        ("3 <= 1", ("3 < 1", "3 > 1")),
        ("3 >= 1", ("3 > 1", "3 < 1")),
        ("3 in [3]", ("3 not in [3]",)),
        ("3 not in [3]", ("3 in [3]",)),
        ("3 == 1", ("3 != 1",)),
        ("3 != 1", ("3 == 1",)),
        ("3 is None", ("3 is not None",)),
        ("3 is not None", ("3 is None",)),
    ),
)
def test_switch_compare_ops(
    dummy_context: Context, input_expr: str, output_exprs: Tuple[str]
) -> None:
    mutations = switch_compare_ops(get_node_from_expr(input_expr), dummy_context)
    assert_results_equal(
        list(mutations),
        [
            Mutation(
                get_node_from_expr(output_expr),
                get_node_from_expr(output_expr),
                dummy_context,
            )
            for output_expr in output_exprs
        ],
    )


@pytest.mark.parametrize(
    ["input_expr", "output_exprs"],
    (
        ("3 < 1 < 2", ("3 <= 1 < 2", "3 >= 1 < 2", "3 < 1 <= 2", "3 < 1 >= 2")),
        ("3 > 1 < 2", ("3 >= 1 < 2", "3 <= 1 < 2", "3 > 1 <= 2", "3 > 1 >= 2")),
        ("3 > 1 == 2", ("3 >= 1 == 2", "3 <= 1 == 2", "3 > 1 != 2")),
    ),
)
def test_switch_multiple_compare_ops(
    dummy_context: Context, input_expr: str, output_exprs: Tuple[str]
) -> None:
    mutations = switch_compare_ops(get_node_from_expr(input_expr), dummy_context)
    assert_results_equal(
        list(mutations),
        [
            Mutation(
                get_node_from_expr(output_expr),
                get_node_from_expr(output_expr),
                dummy_context,
            )
            for output_expr in output_exprs
        ],
    )
