import ast
from ast import AST
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from radiation.mutation import Mutation
from radiation.types import Context, FileContext, NodeContext
from radiation_cli.config import CLIConfig
from radiation_cli.utils import dump_mutation


def get_node_from_expr(expr: str) -> AST:
    return ast.parse(expr, mode="eval").body


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


def test_dump_mutation(tmp_path: Path, cli_runner: CliRunner) -> None:
    (tmp_path / "code.py").write_text(
        _dedent(
            """
            a = '5'


            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    with cli_runner.isolation(color=True) as (stdout, stderr):
        dump_mutation(
            Mutation(
                node=get_node_from_expr("n < 2"),
                tree=ast.parse(
                    _dedent(
                        """
                        a = '5'


                        def fib(n: int) -> int:
                            if n < 2:
                                return 1
                            return fib(n - 2) + fib(n - 1)
                        """
                    )
                ),
                context=Context(
                    node=NodeContext(
                        lineno=5, end_lineno=5, col_offset=7, end_col_offset=13
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            status="my status",
            config=CLIConfig(project_root=tmp_path),
            context_lines=3,
        )

    stdout.seek(0)
    assert stdout.read() == (
        b"\n"
        b"\x1b[1mMy status mutant in code.py:5\x1b[0m\n"
        b"\x1b[22m2 \x1b[0m\n"
        b"\x1b[22m3 \x1b[0m\n"
        b"\x1b[22m4 def fib(n: int) -> int:\x1b[0m\n"
        b"\x1b[1m5     if (n < 2):\x1b[0m\n"
        b"\x1b[22m6         return 1\x1b[0m\n"
        b"\x1b[22m7     return fib(n - 2) + fib(n - 1)\x1b[0m\n"
    )


def test_dump_mutation_default_context_lines(
    tmp_path: Path, cli_runner: CliRunner
) -> None:
    (tmp_path / "code.py").write_text(
        _dedent(
            """
            a = '5'


            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    with cli_runner.isolation(color=True) as (stdout, stderr):
        dump_mutation(
            Mutation(
                node=get_node_from_expr("n < 2"),
                tree=ast.parse(
                    _dedent(
                        """
                        a = '5'


                        def fib(n: int) -> int:
                            if n < 2:
                                return 1
                            return fib(n - 2) + fib(n - 1)
                        """
                    )
                ),
                context=Context(
                    node=NodeContext(
                        lineno=5, end_lineno=5, col_offset=7, end_col_offset=13
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            status="my status",
            config=CLIConfig(project_root=tmp_path),
        )

    stdout.seek(0)
    assert stdout.read() == (
        b"\n"
        b"\x1b[1mMy status mutant in code.py:5\x1b[0m\n"
        b"\x1b[22m3 \x1b[0m\n"
        b"\x1b[22m4 def fib(n: int) -> int:\x1b[0m\n"
        b"\x1b[1m5     if (n < 2):\x1b[0m\n"
        b"\x1b[22m6         return 1\x1b[0m\n"
        b"\x1b[22m7     return fib(n - 2) + fib(n - 1)\x1b[0m\n"
    )


def test_dump_mutation_start_of_file(tmp_path: Path, cli_runner: CliRunner) -> None:
    (tmp_path / "code.py").write_text(
        _dedent(
            """
            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    with cli_runner.isolation(color=True) as (stdout, stderr):
        dump_mutation(
            Mutation(
                node=get_node_from_expr("n < 2"),
                tree=ast.parse(
                    _dedent(
                        """
                        def fib(n: int) -> int:
                            if n < 2:
                                return 1
                            return fib(n - 2) + fib(n - 1)
                        """
                    )
                ),
                context=Context(
                    node=NodeContext(
                        lineno=2, end_lineno=2, col_offset=7, end_col_offset=13
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            status="my status",
            config=CLIConfig(project_root=tmp_path),
            context_lines=3,
        )

    stdout.seek(0)
    assert stdout.read() == (
        b"\n"
        b"\x1b[1mMy status mutant in code.py:2\x1b[0m\n"
        b"\x1b[22m1 def fib(n: int) -> int:\x1b[0m\n"
        b"\x1b[1m2     if (n < 2):\x1b[0m\n"
        b"\x1b[22m3         return 1\x1b[0m\n"
        b"\x1b[22m4     return fib(n - 2) + fib(n - 1)\x1b[0m\n"
    )


def test_dump_mutation_end_of_file(tmp_path: Path, cli_runner: CliRunner) -> None:
    (tmp_path / "code.py").write_text(
        _dedent(
            """
            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    with cli_runner.isolation(color=True) as (stdout, stderr):
        dump_mutation(
            Mutation(
                node=get_node_from_expr("n - 2"),
                tree=ast.parse(
                    _dedent(
                        """
                        def fib(n: int) -> int:
                            if n <= 1:
                                return 1
                            return fib(n - 2) + fib(n - 2)
                        """
                    )
                ),
                context=Context(
                    node=NodeContext(
                        lineno=4, end_lineno=4, col_offset=28, end_col_offset=33
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            status="my status",
            config=CLIConfig(project_root=tmp_path),
            context_lines=3,
        )

    stdout.seek(0)
    assert stdout.read() == (
        b"\n"
        b"\x1b[1mMy status mutant in code.py:4\x1b[0m\n"
        b"\x1b[22m1 def fib(n: int) -> int:\x1b[0m\n"
        b"\x1b[22m2     if n <= 1:\x1b[0m\n"
        b"\x1b[22m3         return 1\x1b[0m\n"
        b"\x1b[1m4     return fib(n - 2) + fib((n - 2))\x1b[0m\n"
    )
