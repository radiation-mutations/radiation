from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import pytest

from antigen import Antigen
from antigen.config import Config


@pytest.fixture()
def tempdir() -> Iterable[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@pytest.fixture()
def project_dir(tempdir: Path) -> Iterable[Path]:
    (tempdir / "a.py").touch()
    (tempdir / "b.py").touch()

    (tempdir / "dir").mkdir()
    (tempdir / "dir" / "b.py").touch()

    (tempdir / "otherdir").mkdir()
    (tempdir / "otherdir" / "b.py").touch()

    (tempdir / "otherdir" / "nesteddir").mkdir(parents=True)
    (tempdir / "otherdir" / "nesteddir" / "c.py").touch()

    yield tempdir


def test_find_files(project_dir: Path) -> None:
    assert list(Antigen(config=Config(project_root=project_dir)).find_files(".")) == [
        project_dir / "dir" / "b.py",
        project_dir / "a.py",
        project_dir / "b.py",
        project_dir / "otherdir" / "nesteddir" / "c.py",
        project_dir / "otherdir" / "b.py",
    ]


def test_find_files_in_multiple_includes(project_dir: Path) -> None:
    assert list(
        Antigen(config=Config(project_root=project_dir)).find_files(["dir", "b*"])
    ) == [
        project_dir / "dir" / "b.py",
        project_dir / "b.py",
    ]


def test_find_files_exclude_dir(project_dir: Path) -> None:
    assert list(
        Antigen(config=Config(project_root=project_dir)).find_files(
            ".", exclude="otherdir"
        )
    ) == [
        project_dir / "dir" / "b.py",
        project_dir / "a.py",
        project_dir / "b.py",
    ]


def test_find_files_exclude_dirs(project_dir: Path) -> None:
    assert list(
        Antigen(config=Config(project_root=project_dir)).find_files(
            ".", excludes=["otherdir", "dir"]
        )
    ) == [
        project_dir / "a.py",
        project_dir / "b.py",
    ]


def test_find_files_exclude_all(project_dir: Path) -> None:
    assert (
        list(
            Antigen(config=Config(project_root=project_dir)).find_files(
                ".", exclude="."
            )
        )
        == []
    )


def test_find_files_include_glob_to_dir(project_dir: Path) -> None:
    assert list(
        Antigen(config=Config(project_root=project_dir)).find_files("*dir")
    ) == [
        project_dir / "dir" / "b.py",
        project_dir / "otherdir" / "nesteddir" / "c.py",
        project_dir / "otherdir" / "b.py",
    ]


def test_find_files_include_glob_to_files(project_dir: Path) -> None:
    assert list(
        Antigen(config=Config(project_root=project_dir)).find_files("*dir/*.py")
    ) == [project_dir / "dir" / "b.py", project_dir / "otherdir" / "b.py"]


def test_find_files_doesnt_allow_absolute_includes(project_dir: Path) -> None:
    with pytest.raises(AssertionError, match="must be relative"):
        list(Antigen(config=Config(project_root=project_dir)).find_files("/dir/*.py"))


def test_find_files_doesnt_allow_absolute_excludes(project_dir: Path) -> None:
    with pytest.raises(AssertionError, match="must be relative"):
        list(
            Antigen(config=Config(project_root=project_dir)).find_files(
                ".", exclude="/dir/*.py"
            )
        )
