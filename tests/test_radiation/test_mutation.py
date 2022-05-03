from pathlib import Path
from textwrap import dedent

from radiation.mutation import Mutation, apply_mutation_on_string
from radiation.types import Context, FileContext, NodeContext

from .utils import get_node_from_expr, get_node_from_stmt


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


def test_apply_mutation_on_string() -> None:
    assert (
        apply_mutation_on_string(
            _dedent(
                """
                b = 15
                a = 5 - 3 + 1
                c = a + 2
                """
            ),
            Mutation(
                tree=get_node_from_stmt("a = 5 * 3 + 1"),
                node=get_node_from_expr("5 * 3"),
                context=Context(
                    file=FileContext(path=Path("/bla.py")),
                    node=NodeContext(
                        lineno=2, end_lineno=2, col_offset=4, end_col_offset=9
                    ),
                ),
            ),
        )
        == _dedent(
            """
            b = 15
            a = (5 * 3) + 1
            c = a + 2
            """
        )
    )


def test_apply_multiline_mutation_on_string() -> None:
    assert (
        apply_mutation_on_string(
            _dedent(
                """
                b = 15
                a = (5
                    - 3) + 1
                c = a + 2
                """
            ),
            Mutation(
                tree=get_node_from_stmt("a = (5\n    * 3) + 1"),
                node=get_node_from_expr("(5\n    * 3)"),
                context=Context(
                    file=FileContext(path=Path("/bla.py")),
                    node=NodeContext(
                        lineno=2, end_lineno=3, col_offset=4, end_col_offset=8
                    ),
                ),
            ),
        )
        == _dedent(
            """
            b = 15
            a = (5 * 3) + 1
            c = a + 2
            """
        )
    )
