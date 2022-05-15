from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from radiation_cli.main import cli


def _dedent(text: str) -> str:
    return dedent(text.lstrip("\n")).rstrip("\n")


@pytest.fixture
def project_path(tmp_path: Path) -> Path:
    (tmp_path / "code.py").write_text(
        _dedent(
            """
            from typing import List

            def grep(lines: List[str], line: str, context: int = 0) -> List[str]:
                index = lines.index(line)
                start = max(0, index - context)
                end = min(len(lines), index + context + 1)
                return lines[start:end]
            """
        )
    )

    (tmp_path / "test_code.py").write_text(
        _dedent(
            """
            from code import grep

            def test_grep() -> int:
                assert grep([
                    "aaa",
                    "bbb",
                    "ccc",
                    "ddd",
                    "eee",
                ], "bbb", context=2) == ["aaa", "bbb", "ccc", "ddd"]

            test_grep()
            """
        )
    )

    (tmp_path / ".radiation.cfg").write_text(
        _dedent(
            """
            [settings]
            include = code.py
            tests_dir = test_code.py
            run_command = python test_code.py
            """
        )
    )

    return tmp_path


def test_cli_run(project_path: Path) -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(cli, ["-p", str(project_path), "run"])
    assert result.stdout.rstrip("\n") == _dedent(
        """
        Generated 9 mutations
        Running tests

        Surviving mutant in code.py:3
        1 from typing import List
        2 
        3 def grep(lines: List[str], line: str, context: int = -1) -> List[str]:
        4     index = lines.index(line)
        5     start = max(0, index - context)

        Surviving mutant in code.py:3
        1 from typing import List
        2 
        3 def grep(lines: List[str], line: str, context: int = 1) -> List[str]:
        4     index = lines.index(line)
        5     start = max(0, index - context)
        """  # noqa: W291
    )
    assert result.stderr == ""
    assert result.exit_code == 0


def test_cli_run_line_limit(project_path: Path) -> None:
    cli_runner = CliRunner(mix_stderr=False)
    result = cli_runner.invoke(
        cli, ["--line-limit", "1", "-p", str(project_path), "run"]
    )
    assert result.stdout.rstrip("\n") == _dedent(
        """
        Generated 3 mutations
        Running tests

        Surviving mutant in code.py:3
        1 from typing import List
        2 
        3 def grep(lines: List[str], line: str, context: int = -1) -> List[str]:
        4     index = lines.index(line)
        5     start = max(0, index - context)
        """  # noqa: W291
    )
    assert result.stderr == ""
    assert result.exit_code == 0


def test_cli_run_with_diff(project_path: Path) -> None:
    cli_runner = CliRunner(mix_stderr=False)

    (project_path / "patch").write_text(
        _dedent(
            """
            diff --git blabla
            index 1d36346..6a53a30 100644
            --- a/oldfilename.py
            +++ b/code.py
            @@ -5,1 +5,1 @@
            -start = max(1, index - context)
            +start = max(0, index - context)
            """
        )
    )

    result = cli_runner.invoke(
        cli, ["--diff-command", "cat patch", "-p", str(project_path), "run"]
    )

    assert result.stdout.rstrip("\n") == _dedent(
        """
        Generated 3 mutations
        Running tests
        """
    )
    assert result.stderr == ""
    assert result.exit_code == 0
