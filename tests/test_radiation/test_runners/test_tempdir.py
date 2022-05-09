import ast
from pathlib import Path
from textwrap import dedent

from radiation.config import Config
from radiation.mutation import Mutation
from radiation.runners import TempDirRunner
from radiation.types import Context, FileContext, NodeContext, SuccessStatus

from ..utils import get_node_from_expr


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


def test_tempdir_runner_surviving_mutant(tmp_path: Path) -> None:
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

    (tmp_path / "test_code.py").write_text(
        _dedent(
            """
            from code import fib

            def test_fib() -> int:
                results = [1, 1, 2, 3, 5, 8, 13, 21]
                for n, result in enumerate(results):
                    assert fib(n) == result

            test_fib()
            """
        )
    )

    assert (
        TempDirRunner("python test_code.py")(
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
            Config(project_root=tmp_path),
        )
        == SuccessStatus.SURVIVED
    )


def test_tempdir_runner_killed_mutant(tmp_path: Path) -> None:
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

    (tmp_path / "test_code.py").write_text(
        _dedent(
            """
            from code import fib

            def test_fib() -> int:
                results = [1, 1, 2, 3, 5, 8, 13, 21]
                for n, result in enumerate(results):
                    assert fib(n) == result

            test_fib()
            """
        )
    )

    assert (
        TempDirRunner("python test_code.py")(
            Mutation(
                node=get_node_from_expr("2"),
                tree=ast.parse(
                    _dedent(
                        """
                        def fib(n: int) -> int:
                            if n <= 2:
                                return 1
                            return fib(n - 2) + fib(n - 1)
                        """
                    )
                ),
                context=Context(
                    node=NodeContext(
                        lineno=2, end_lineno=2, col_offset=12, end_col_offset=13
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            Config(project_root=tmp_path),
        )
        == SuccessStatus.KILLED
    )


def test_tempdir_runner_timed_out_mutant(tmp_path: Path) -> None:
    (tmp_path / "code.py").write_text("1")

    assert (
        TempDirRunner("sleep 0.1", timeout=0.05)(
            Mutation(
                node=get_node_from_expr("2"),
                tree=get_node_from_expr("2"),
                context=Context(
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            Config(project_root=tmp_path),
        )
        == SuccessStatus.TIMED_OUT
    )


def test_tempdir_runner_not_timed_out_mutant(tmp_path: Path) -> None:
    (tmp_path / "code.py").write_text("1")

    assert (
        TempDirRunner("sleep 0.05", timeout=0.1)(
            Mutation(
                node=get_node_from_expr("2"),
                tree=get_node_from_expr("2"),
                context=Context(
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    file=FileContext(path=tmp_path / "code.py"),
                ),
            ),
            Config(project_root=tmp_path),
        )
        == SuccessStatus.SURVIVED
    )
