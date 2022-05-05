from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import Iterable

import click
import pytest

from radiation_cli.config import CLIConfig, read_default_config, read_config


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


@pytest.fixture()
def project_dir() -> Iterable[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


def test_read_default_config_cfg(project_dir: Path) -> None:
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


def test_read_default_config_cfg_multiple_includes(project_dir: Path) -> None:
    (project_dir / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include =
                *.py
                mydir/
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )

    assert read_default_config(project_dir) == CLIConfig(
        include=["*.py", "mydir/"],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_default_config_toml(project_dir: Path) -> None:
    (project_dir / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )

    assert read_default_config(project_dir) == CLIConfig(
        include=["."],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_default_config_toml_multiple_includes(project_dir: Path) -> None:
    (project_dir / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = ["*.py", "mydir/"]
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )

    assert read_default_config(project_dir) == CLIConfig(
        include=["*.py", "mydir/"],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_default_config_pyproject_toml(project_dir: Path) -> None:
    (project_dir / "pyproject.toml").write_text(
        _dedent(
            """
            [otherkey]
            include = ".."

            [tool.othertool]
            include = ".."

            [tool.radiation]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )

    assert read_default_config(project_dir) == CLIConfig(
        include=["."],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_config(project_dir: Path) -> None:
    (project_dir / "custom_name.cfg").write_text(
        _dedent(
            """
            [radiation]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )

    assert read_config(project_dir / "custom_name.cfg") == CLIConfig(
        include=["."],
        project_root=project_dir,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_config_unknown_file_type(project_dir: Path) -> None:
    (project_dir / "custom_name.bla").write_text(
        _dedent(
            """
            [radiation]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )
    with pytest.raises(click.BadParameter):
        read_config(project_dir / "custom_name.bla")


def test_read_config_no_recognized_sections(project_dir: Path) -> None:
    (project_dir / "custom_name.toml").write_text(
        _dedent(
            """
            [mysection]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )
    with pytest.raises(Exception, match="Cannot find expected sections in config file"):
        read_config(project_dir / "custom_name.toml")