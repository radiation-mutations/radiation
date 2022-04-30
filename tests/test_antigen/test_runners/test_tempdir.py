import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import Iterable

import pytest

from antigen.config import Config
from antigen.mutation import Mutation
from antigen.runners import TempDirRunner
from antigen.types import Context, FileContext, NodeContext, SuccessStatus

from ..utils import get_node_from_expr


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


@pytest.fixture
def tempdir() -> Iterable[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@pytest.fixture
def project_path(tempdir: Path) -> Path:
    return tempdir


def test_tempdir_runner_surviving_mutant(project_path: Path) -> None:
    (project_path / "code.py").write_text(
        _dedent(
            """
            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    (project_path / "test_code.py").write_text(
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
                    file=FileContext(path=project_path / "code.py"),
                ),
            ),
            Config(project_root=project_path),
        )
        == SuccessStatus.SURVIVED
    )


def test_tempdir_runner_killed_mutant(project_path: Path) -> None:
    (project_path / "code.py").write_text(
        _dedent(
            """
            def fib(n: int) -> int:
                if n <= 1:
                    return 1
                return fib(n - 2) + fib(n - 1)
            """
        )
    )

    (project_path / "test_code.py").write_text(
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
                    file=FileContext(path=project_path / "code.py"),
                ),
            ),
            Config(project_root=project_path),
        )
        == SuccessStatus.KILLED
    )


def test_tempdir_runner_timed_out_mutant(project_path: Path) -> None:
    (project_path / "code.py").write_text("1")

    assert (
        TempDirRunner("sleep 1", timeout=0.1)(
            Mutation(
                node=get_node_from_expr("2"),
                tree=get_node_from_expr("2"),
                context=Context(
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    file=FileContext(path=project_path / "code.py"),
                ),
            ),
            Config(project_root=project_path),
        )
        == SuccessStatus.TIMED_OUT
    )
