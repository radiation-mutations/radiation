from typing import Tuple

import pytest

from antigen.mutation import Mutation
from antigen.mutators import modify_constants
from antigen.types import Context

from ..utils import assert_results_equal, get_node_from_expr


@pytest.mark.parametrize(
    ["input_expr", "output_exprs"],
    (
        ("'a'", ("'XXXaXXX'",)),
        ("b'a'", ("b'XXXaXXX'",)),
        ("5", ("0", "1", "4", "6")),
        ("1", ("0", "2")),
        ("0", ("-1", "1")),
        ("2", ("0", "1", "3")),
    ),
)
def test_modify_constants(
    dummy_context: Context, input_expr: str, output_exprs: Tuple[str]
) -> None:
    mutations = modify_constants(get_node_from_expr(input_expr), dummy_context)
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
