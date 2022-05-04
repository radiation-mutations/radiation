from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import Iterable

import pytest

from radiation_cli.config import CLIConfig, read_default_config


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


@pytest.fixture()
def project_dir() -> Iterable[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


def test_read_default_config(project_dir: Path) -> None:
    (project_dir / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )

    assert read_default_config(project_dir) == CLIConfig(
        include=["."],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )
