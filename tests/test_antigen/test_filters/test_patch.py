import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import Iterable

import pytest

from antigen.config import Config
from antigen.filters.patch import PatchFilter
from antigen.mutation import Mutation
from antigen.types import Context, FileContext, NodeContext

from ..utils import get_node_from_expr, get_node_from_stmt


@pytest.fixture
def tempdir() -> Iterable[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@pytest.fixture
def project_path(tempdir: Path) -> Path:
    return tempdir


@pytest.fixture
def filename() -> str:
    return "myfile.py"


@pytest.fixture
def mutation_in_line_1(project_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=project_path / filename),
            node=NodeContext(lineno=1, end_lineno=1, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def mutation_in_line_2(project_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=project_path / filename),
            node=NodeContext(lineno=2, end_lineno=2, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def mutation_in_lines_1_to_2(project_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = (5 * \n3)"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=project_path / filename),
            node=NodeContext(lineno=1, end_lineno=2, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def patch_line_1_edited(filename: str) -> str:
    return dedent(
        f"""
        diff --git blabla
        index 1d36346..6a53a30 100644
        --- a/oldfilename.py
        +++ b/{filename}
        @@ -1,1 +1,1 @@
        -a = 5
        +a = 5 * 3
        """.lstrip(
            "\n"
        )
    )


@pytest.fixture
def patch_line_2_edited(filename: str) -> str:
    return dedent(
        f"""
        diff --git blabla
        index 1d36346..6a53a30 100644
        --- a/oldfilename.py
        +++ b/{filename}
        @@ -2,1 +2,1 @@
        -a = 5
        +a = 5 * 3
        """.lstrip(
            "\n"
        )
    )


@pytest.fixture
def patch_no_hunks(filename: str) -> str:
    return dedent(
        f"""
        diff --git blabla
        index 1d36346..6a53a30 100644
        --- a/oldfilename.py
        +++ b/{filename}
        """.lstrip(
            "\n"
        )
    )


@pytest.fixture
def patch_other_file(filename: str) -> str:
    return dedent(
        """
        diff --git blabla
        index 1d36346..6a53a30 100644
        --- a/oldfilename.py
        +++ b/otherfilename.py
        @@ -1,1 +1,1 @@
        -a = 5
        +a = 5 * 3
        """.lstrip(
            "\n"
        )
    )


@pytest.fixture
def config(project_path: Path) -> Config:
    return Config(project_root=project_path)


def test_patch_filter_mutation_in_patch(
    mutation_in_line_1: Mutation, patch_line_1_edited: str, config: Config
) -> None:
    assert PatchFilter(patch_line_1_edited)(mutation_in_line_1, config)


def test_patch_filter_mutation_not_in_patch(
    mutation_in_line_2: Mutation, patch_line_1_edited: str, config: Config
) -> None:
    assert not PatchFilter(patch_line_1_edited)(mutation_in_line_2, config)


def test_patch_multiline_mutation(
    mutation_in_lines_1_to_2: Mutation, patch_line_2_edited: str, config: Config
) -> None:
    assert PatchFilter(patch_line_2_edited)(mutation_in_lines_1_to_2, config)


def test_filter_no_body(
    mutation_in_line_1: Mutation, patch_no_hunks: str, config: Config
) -> None:
    assert not PatchFilter(patch_no_hunks)(mutation_in_line_1, config)


def test_filter_other_filename(
    mutation_in_line_1: Mutation, patch_other_file: str, config: Config
) -> None:
    assert not PatchFilter(patch_other_file)(mutation_in_line_1, config)


def test_patch_filter_from_git_diff(
    mutation_in_line_1: Mutation, mutation_in_line_2: Mutation, tempdir: Path
) -> None:
    file_path = Path(tempdir) / "myfile.py"
    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb
            """.lstrip()
        )
    )
    subprocess.run(["git", "init"], check=True, cwd=tempdir)
    subprocess.run(["git", "add", "-A"], check=True, cwd=tempdir)
    subprocess.run(["git", "commit", '-m"First commit"'], check=True, cwd=tempdir)

    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb * 2
            """.lstrip()
        )
    )

    pf = PatchFilter.from_git_diff("HEAD", project_dir=tempdir)

    assert pf(mutation_in_line_2, Config(project_root=Path(tempdir)))
    assert not pf(mutation_in_line_1, Config(project_root=Path(tempdir)))


def test_patch_filter_from_git_diff_with_base(
    mutation_in_line_1: Mutation, mutation_in_line_2: Mutation, tempdir: Path
) -> None:
    file_path = Path(tempdir) / "myfile.py"
    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb
            """.lstrip()
        )
    )
    subprocess.run(["git", "init"], check=True, cwd=tempdir)
    subprocess.run(["git", "add", "-A"], check=True, cwd=tempdir)
    subprocess.run(["git", "commit", '-m"First commit"'], check=True, cwd=tempdir)

    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb * 2
            """.lstrip()
        )
    )

    subprocess.run(["git", "add", "-A"], check=True, cwd=tempdir)
    subprocess.run(["git", "commit", '-m"Second commit"'], check=True, cwd=tempdir)

    pf = PatchFilter.from_git_diff("HEAD~", base="HEAD", project_dir=tempdir)

    assert not pf(mutation_in_line_1, Config(project_root=Path(tempdir)))
    assert pf(mutation_in_line_2, Config(project_root=Path(tempdir)))
