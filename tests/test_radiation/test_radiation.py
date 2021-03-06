import ast
from ast import AST, BinOp, Expr
from pathlib import Path
from typing import Iterable, cast

import pytest

from radiation import Radiation
from radiation.config import Config
from radiation.mutation import Mutation
from radiation.runners import TempDirRunner
from radiation.types import Context, FileContext, NodeContext

from .utils import assert_results_equal


@pytest.fixture()
def project_dir(tmp_path: Path) -> Iterable[Path]:
    (tmp_path / "a.py").touch()
    (tmp_path / "b.py").touch()

    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "b.py").touch()
    (tmp_path / "dir" / "b.java").touch()

    (tmp_path / "otherdir").mkdir()
    (tmp_path / "otherdir" / "b.py").touch()

    (tmp_path / "otherdir" / "nesteddir").mkdir(parents=True)
    (tmp_path / "otherdir" / "nesteddir" / "c.py").touch()
    (tmp_path / "otherdir" / "nesteddir" / "c.go").touch()

    yield tmp_path


def test_find_files(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files(".")
    ) == [
        project_dir / "a.py",
        project_dir / "b.py",
        project_dir / "dir" / "b.py",
        project_dir / "otherdir" / "b.py",
        project_dir / "otherdir" / "nesteddir" / "c.py",
    ]


def test_find_files_in_multiple_includes(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files(["dir", "b*"])
    ) == [
        project_dir / "dir" / "b.py",
        project_dir / "b.py",
    ]


def test_find_files_exclude_dir(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files(".", exclude="otherdir")
    ) == [
        project_dir / "a.py",
        project_dir / "b.py",
        project_dir / "dir" / "b.py",
    ]


def test_find_files_exclude_dirs(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files(".", excludes=["otherdir", "dir"])
    ) == [
        project_dir / "a.py",
        project_dir / "b.py",
    ]


def test_find_files_exclude_all(project_dir: Path) -> None:
    assert (
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                config=Config(project_root=project_dir),
            ).find_files(".", exclude=".")
        )
        == []
    )


def test_find_files_include_glob_to_dir(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files("*dir")
    ) == [
        project_dir / "dir" / "b.py",
        project_dir / "otherdir" / "b.py",
        project_dir / "otherdir" / "nesteddir" / "c.py",
    ]


def test_find_files_include_glob_to_files(project_dir: Path) -> None:
    assert list(
        Radiation(
            runner=TempDirRunner(run_command=""),
            config=Config(project_root=project_dir),
        ).find_files("*dir/*.py")
    ) == [project_dir / "dir" / "b.py", project_dir / "otherdir" / "b.py"]


def test_find_files_doesnt_allow_absolute_includes(project_dir: Path) -> None:
    with pytest.raises(AssertionError, match="must be relative"):
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                config=Config(project_root=project_dir),
            ).find_files("/dir/*.py")
        )


def test_find_files_doesnt_allow_absolute_excludes(project_dir: Path) -> None:
    with pytest.raises(AssertionError, match="must be relative"):
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                config=Config(project_root=project_dir),
            ).find_files(".", exclude="/dir/*.py")
        )


def test_gen_mutations_str(project_dir: Path) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert_results_equal(
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                mutators=[mutator],
                config=Config(project_root=project_dir),
            ).gen_mutations_str(
                "a + 6",
            )
        ),
        [
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).left,
                context=Context(
                    file=FileContext(path=project_dir / "<code>"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).right,
                context=Context(
                    file=FileContext(path=project_dir / "<code>"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(Expr, ast.parse("a + 6").body[0]).value,
                context=Context(
                    file=FileContext(path=project_dir / "<code>"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6").body[0],
                context=Context(
                    file=FileContext(path=project_dir / "<code>"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6"),
                context=Context(
                    file=FileContext(path=project_dir / "<code>"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
        ],
    )


def test_gen_mutations_str_abs_path(project_dir: Path) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert_results_equal(
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                mutators=[mutator],
                config=Config(project_root=project_dir),
            ).gen_mutations_str("a + 6", path=project_dir / "code.py")
        ),
        [
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).left,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).right,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(Expr, ast.parse("a + 6").body[0]).value,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6").body[0],
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6"),
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
        ],
    )


def test_gen_mutations_str_rel_path(project_dir: Path) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert_results_equal(
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                mutators=[mutator],
                config=Config(project_root=project_dir),
            ).gen_mutations_str("a + 6", path="code.py")
        ),
        [
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).left,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).right,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(Expr, ast.parse("a + 6").body[0]).value,
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6").body[0],
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6"),
                context=Context(
                    file=FileContext(path=project_dir / "code.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
        ],
    )


def test_gen_mutations_str_empty(project_dir: Path) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    assert (
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                mutators=[mutator],
                config=Config(project_root=project_dir),
            ).gen_mutations_str("")
        )
        == []
    )


def test_gen_mutations(project_dir: Path) -> None:
    def mutator(node: AST, context: Context) -> Iterable[Mutation]:
        yield Mutation.from_node(node, context)

    (project_dir / "otherdir" / "b.py").write_text("a + 6")

    assert_results_equal(
        list(
            Radiation(
                runner=TempDirRunner(run_command=""),
                mutators=[mutator],
                config=Config(project_root=project_dir),
            ).gen_mutations(project_dir / "otherdir" / "b.py")
        ),
        [
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).left,
                context=Context(
                    file=FileContext(path=project_dir / "otherdir" / "b.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=1
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(BinOp, cast(Expr, ast.parse("a + 6").body[0]).value).right,
                context=Context(
                    file=FileContext(path=project_dir / "otherdir" / "b.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=4, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=cast(Expr, ast.parse("a + 6").body[0]).value,
                context=Context(
                    file=FileContext(path=project_dir / "otherdir" / "b.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6").body[0],
                context=Context(
                    file=FileContext(path=project_dir / "otherdir" / "b.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
            Mutation(
                tree=ast.parse("a + 6"),
                node=ast.parse("a + 6"),
                context=Context(
                    file=FileContext(path=project_dir / "otherdir" / "b.py"),
                    node=NodeContext(
                        lineno=1, end_lineno=1, col_offset=0, end_col_offset=5
                    ),
                    extra=None,
                ),
            ),
        ],
    )
