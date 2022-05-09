import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

from radiation.config import Config
from radiation.filters.patch import PatchFilter
from radiation.mutation import Mutation
from radiation.types import Context, FileContext, NodeContext

from ..utils import get_node_from_expr, get_node_from_stmt


@pytest.fixture
def filename() -> str:
    return "myfile.py"


@pytest.fixture
def mutation_in_line_1(tmp_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=tmp_path / filename),
            node=NodeContext(lineno=1, end_lineno=1, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def mutation_in_line_2(tmp_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=tmp_path / filename),
            node=NodeContext(lineno=2, end_lineno=2, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def mutation_in_lines_1_to_2(tmp_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = (5 * \n3)"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=tmp_path / filename),
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
def config(tmp_path: Path) -> Config:
    return Config(project_root=tmp_path)


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
    mutation_in_line_1: Mutation, mutation_in_line_2: Mutation, tmp_path: Path
) -> None:
    file_path = Path(tmp_path) / "myfile.py"
    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb
            """.lstrip()
        )
    )
    subprocess.run(["git", "init"], check=True, cwd=tmp_path)
    subprocess.run(["git", "add", "-A"], check=True, cwd=tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            'user.email="your@email.com"',
            "-c",
            'user.name="Your Name"',
            "commit",
            '-m"First commit"',
        ],
        check=True,
        cwd=tmp_path,
    )

    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb * 2
            """.lstrip()
        )
    )

    pf = PatchFilter.from_git_diff("HEAD", project_dir=tmp_path)

    assert pf(mutation_in_line_2, Config(project_root=Path(tmp_path)))
    assert not pf(mutation_in_line_1, Config(project_root=Path(tmp_path)))


def test_patch_filter_from_git_diff_with_base(
    mutation_in_line_1: Mutation, mutation_in_line_2: Mutation, tmp_path: Path
) -> None:
    file_path = Path(tmp_path) / "myfile.py"
    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb
            """.lstrip()
        )
    )
    subprocess.run(["git", "init"], check=True, cwd=tmp_path)
    subprocess.run(["git", "add", "-A"], check=True, cwd=tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            'user.email="your@email.com"',
            "-c",
            'user.name="Your Name"',
            "commit",
            '-m"First commit"',
        ],
        check=True,
        cwd=tmp_path,
    )

    file_path.write_text(
        dedent(
            """
            aaaaa
            bbbbb * 2
            """.lstrip()
        )
    )

    subprocess.run(["git", "add", "-A"], check=True, cwd=tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            'user.email="your@email.com"',
            "-c",
            'user.name="Your Name"',
            "commit",
            '-m"Second commit"',
        ],
        check=True,
        cwd=tmp_path,
    )

    pf = PatchFilter.from_git_diff("HEAD~", base="HEAD", project_dir=tmp_path)

    assert not pf(mutation_in_line_1, Config(project_root=Path(tmp_path)))
    assert pf(mutation_in_line_2, Config(project_root=Path(tmp_path)))
