import re
from pathlib import Path
from textwrap import dedent

import click
import pytest

from radiation_cli.config import CLIConfig, read_config, read_default_config


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


def test_read_default_config_cfg(tmp_path: Path) -> None:
    (tmp_path / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            tests_timeout = 2.5
            diff_command = git diff develop
            line_limit = 4
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=2.5,
        diff_command="git diff develop",
        line_limit=4,
    )


def test_read_default_config_limit_none(tmp_path: Path) -> None:
    (tmp_path / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            tests_timeout = 2.5
            line_limit = none
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=2.5,
        line_limit=None,
    )


def test_read_default_config_cfg_no_timeout(tmp_path: Path) -> None:
    (tmp_path / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=None,
    )


def test_read_default_config_cfg_multiple_includes(tmp_path: Path) -> None:
    (tmp_path / ".radiation.cfg").write_text(
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

    assert read_default_config(tmp_path) == CLIConfig(
        include=["*.py", "mydir/"],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_default_config_toml(tmp_path: Path) -> None:
    (tmp_path / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            tests_timeout = 2.5
            diff_command = "git diff develop"
            line_limit = 4
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=2.5,
        diff_command="git diff develop",
        line_limit=4,
    )


def test_read_default_config_toml_limit_none(tmp_path: Path) -> None:
    (tmp_path / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            tests_timeout = 2.5
            line_limit = "none"
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=2.5,
        line_limit=None,
    )


def test_read_default_config_toml_no_timeout(tmp_path: Path) -> None:
    (tmp_path / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
        tests_timeout=None,
    )


def test_read_default_config_toml_multiple_includes(tmp_path: Path) -> None:
    (tmp_path / ".radiation.toml").write_text(
        _dedent(
            """
            [settings]
            include = ["*.py", "mydir/"]
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )

    assert read_default_config(tmp_path) == CLIConfig(
        include=["*.py", "mydir/"],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_default_config_no_file_present(tmp_path: Path) -> None:
    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="pytest",
        tests_dir="tests",
    )


def test_read_default_config_pyproject_toml(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
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

    assert read_default_config(tmp_path) == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_config(tmp_path: Path) -> None:
    (tmp_path / "custom_name.cfg").write_text(
        _dedent(
            """
            [radiation]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )

    assert read_config(tmp_path / "custom_name.cfg") == CLIConfig(
        include=["."],
        project_root=tmp_path,
        run_command="poetry install && poetry run pytest",
        tests_dir="tests",
    )


def test_read_config_unknown_file_type(tmp_path: Path) -> None:
    (tmp_path / "custom_name.bla").write_text(
        _dedent(
            """
            [radiation]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )
    with pytest.raises(
        click.BadParameter,
        match=re.escape("Unrecognized config file format (supported: .toml, .cfg)"),
    ):
        read_config(tmp_path / "custom_name.bla")


def test_read_config_no_recognized_sections_toml(tmp_path: Path) -> None:
    (tmp_path / "custom_name.toml").write_text(
        _dedent(
            """
            [mysection]
            include = "."
            tests_dir = "tests"
            run_command = "poetry install && poetry run pytest"
            """
        )
    )
    with pytest.raises(
        Exception,
        match=re.escape(
            "Cannot find expected sections in config file "
            "(expected: [radiation] or [settings])"
        ),
    ):
        read_config(tmp_path / "custom_name.toml")


def test_read_config_no_recognized_sections_cfg(tmp_path: Path) -> None:
    (tmp_path / "custom_name.cfg").write_text(
        _dedent(
            """
            [mysection]
            include = .
            tests_dir = tests
            run_command = poetry install && poetry run pytest
            """
        )
    )
    with pytest.raises(
        Exception,
        match=re.escape(
            "Cannot find expected sections in config file "
            "(expected: [radiation] or [settings])"
        ),
    ):
        read_config(tmp_path / "custom_name.cfg")
