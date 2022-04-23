import pytest

from antigen.mutation import Mutation
from antigen.mutators import switch_bool_ops
from antigen.types import Context

from .utils import assert_results_equal, get_node_from_expr


@pytest.mark.parametrize(
    ["input_expr", "output_expr"],
    (
        ("5 or 3", "5 and 3"),
        ("5 and 3", "5 or 3"),
    ),
)
def test_switch_bool_op(
    dummy_context: Context, input_expr: str, output_expr: str
) -> None:
    mutations = switch_bool_ops(get_node_from_expr(input_expr), dummy_context)
    assert_results_equal(
        list(mutations),
        [
            Mutation(
                get_node_from_expr(output_expr),
                get_node_from_expr(output_expr),
                dummy_context,
            )
        ],
    )


@pytest.mark.parametrize(
    ["expr"],
    (
        ("5 * 3",),
        ("5 / 3",),
        ("5 + 3",),
        ("5 - 3",),
        ("5 | 3",),
        ("5 > 3",),
    ),
)
def test_dont_switch_op(dummy_context: Context, expr: str) -> None:
    mutations = switch_bool_ops(get_node_from_expr(expr), dummy_context)
    assert list(mutations) == []
