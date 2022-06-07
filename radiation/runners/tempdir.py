import datetime as dt
import subprocess
from dataclasses import dataclass
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional, Union

from ..config import Config
from ..mutation import Mutation, apply_mutation_on_disk
from ..types import TestsResult


@dataclass
class TempDirRunner:
    run_command: str

    def _run_tests_in_dir(
        self, cwd: Union[str, Path], *, timeout: Optional[float] = None
    ) -> TestsResult:
        start_time = dt.datetime.now()
        try:
            completed_process = subprocess.run(
                self.run_command,
                shell=True,
                capture_output=True,
                cwd=cwd,
                timeout=timeout,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return TestsResult(
                duration=dt.datetime.now() - start_time,
                status="timed out",
            )
        return TestsResult(
            duration=dt.datetime.now() - start_time,
            status=("survived" if completed_process.returncode == 0 else "killed"),
            output=completed_process.stdout,
        )

    def run_baseline_tests(
        self, *, config: Config, timeout: Optional[float] = None
    ) -> TestsResult:
        with TemporaryDirectory() as tempdir:
            copytree(config.project_root, tempdir, dirs_exist_ok=True)
            return self._run_tests_in_dir(tempdir, timeout=timeout)

    def test_mutation(
        self, mutation: Mutation, *, config: Config, timeout: Optional[float] = None
    ) -> TestsResult:
        mut_rel_path = mutation.context.file.path.relative_to(config.project_root)
        with TemporaryDirectory() as tempdir:
            copytree(config.project_root, tempdir, dirs_exist_ok=True)
            apply_mutation_on_disk(
                Path(tempdir) / mut_rel_path,
                mutation,
            )
            return self._run_tests_in_dir(tempdir, timeout=timeout)
