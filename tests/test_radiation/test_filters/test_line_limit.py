from pathlib import Path

import pytest

from radiation.config import Config
from radiation.filters.line_limit import LineLimitFilter
from radiation.mutation import Mutation
from radiation.types import Context, FileContext, NodeContext

from ..utils import get_node_from_expr, get_node_from_stmt


@pytest.fixture
def project_path() -> Path:
    return Path("/home/myuser/myrepo")


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
def other_mutation_in_line_1(project_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=project_path / filename),
            node=NodeContext(lineno=1, end_lineno=1, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def third_mutation_in_line_1(project_path: Path, filename: str) -> Mutation:
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
def mutation_in_line_1_other_file(project_path: Path, filename: str) -> Mutation:
    return Mutation(
        tree=get_node_from_stmt("a = 5 * 3"),
        node=get_node_from_expr("5 * 3"),
        context=Context(
            file=FileContext(path=project_path / "other.py"),
            node=NodeContext(lineno=1, end_lineno=1, col_offset=4, end_col_offset=9),
        ),
    )


@pytest.fixture
def config(project_path: Path) -> Config:
    return Config(project_root=project_path)


def test_line_limit_filter_two_mutations_in_line(
    mutation_in_line_1: Mutation, other_mutation_in_line_1: Mutation, config: Config
) -> None:
    limiter = LineLimitFilter(1)
    assert limiter(mutation_in_line_1, config)
    assert not limiter(other_mutation_in_line_1, config)


def test_line_limit_filter_two_mutations_in_line_different_limit(
    mutation_in_line_1: Mutation,
    other_mutation_in_line_1: Mutation,
    third_mutation_in_line_1: Mutation,
    config: Config,
) -> None:
    limiter = LineLimitFilter(2)
    assert limiter(mutation_in_line_1, config)
    assert limiter(other_mutation_in_line_1, config)
    assert not limiter(third_mutation_in_line_1, config)


def test_line_limit_filter_two_mutations_in_line_default_limit(
    mutation_in_line_1: Mutation,
    other_mutation_in_line_1: Mutation,
    third_mutation_in_line_1: Mutation,
    config: Config,
) -> None:
    limiter = LineLimitFilter()
    assert limiter(mutation_in_line_1, config)
    assert limiter(other_mutation_in_line_1, config)
    assert not limiter(third_mutation_in_line_1, config)


def test_line_limit_multiline_mutation(
    mutation_in_line_1: Mutation, mutation_in_lines_1_to_2: Mutation, config: Config
) -> None:
    limiter = LineLimitFilter(1)
    assert limiter(mutation_in_line_1, config)
    assert not limiter(mutation_in_lines_1_to_2, config)


def test_line_limit_mutation_on_different_lines(
    mutation_in_line_1: Mutation, mutation_in_line_2: Mutation, config: Config
) -> None:
    limiter = LineLimitFilter(1)
    assert limiter(mutation_in_line_1, config)
    assert limiter(mutation_in_line_2, config)


def test_line_limit_mutation_on_different_files(
    mutation_in_line_1: Mutation,
    mutation_in_line_1_other_file: Mutation,
    config: Config,
) -> None:
    limiter = LineLimitFilter(1)
    assert limiter(mutation_in_line_1, config)
    assert limiter(mutation_in_line_1_other_file, config)
