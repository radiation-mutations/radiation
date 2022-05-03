import pytest

from radiation.mutation import Mutation
from radiation.mutators import switch_bin_ops
from radiation.types import Context

from ..utils import assert_results_equal, get_node_from_expr


@pytest.mark.parametrize(
    ["input_expr", "output_expr"],
    (
        ("5 + 3", "5 - 3"),
        ("5 - 3", "5 + 3"),
        ("5 * 3", "5 / 3"),
        ("5 // 3", "5 / 3"),
    ),
)
def test_switch_bin_op(
    dummy_context: Context, input_expr: str, output_expr: str
) -> None:
    mutations = switch_bin_ops(get_node_from_expr(input_expr), dummy_context)
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
        ("5 or 3",),
        ("5 and 3",),
        ("5 | 3",),
        ("5 > 3",),
    ),
)
def test_dont_switch_op(dummy_context: Context, expr: str) -> None:
    mutations = switch_bin_ops(get_node_from_expr(expr), dummy_context)
    assert list(mutations) == []
