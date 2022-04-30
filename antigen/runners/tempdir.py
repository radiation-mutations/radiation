import subprocess
from dataclasses import dataclass
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional

from ..config import Config
from ..mutation import Mutation, apply_mutation_on_disk
from ..types import SuccessStatus


@dataclass
class TempDirRunner:
    run_command: str
    timeout: Optional[float] = None

    def __call__(self, mutation: Mutation, config: Config) -> SuccessStatus:
        mut_rel_path = mutation.context.file.path.relative_to(config.project_root)
        with TemporaryDirectory() as tempdir:
            copytree(config.project_root, tempdir, dirs_exist_ok=True)
            apply_mutation_on_disk(
                Path(tempdir) / mut_rel_path,
                mutation,
            )
            try:
                completed_process = subprocess.run(
                    self.run_command,
                    shell=True,
                    capture_output=True,
                    cwd=tempdir,
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired:
                return SuccessStatus.TIMED_OUT
            if completed_process.returncode != 0:
                return SuccessStatus.KILLED
            return SuccessStatus.SURVIVED
