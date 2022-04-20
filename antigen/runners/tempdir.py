import subprocess
from dataclasses import dataclass
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from ..mutation import Mutation, apply_mutation_on_disk
from ..types import SuccessStatus


@dataclass
class TempDirRunner:
    project_root: Path
    run_command: str

    def __call__(self, mutation: Mutation) -> SuccessStatus:
        with TemporaryDirectory() as tempdir:
            copytree(self.project_root, Path(tempdir), dirs_exist_ok=True)
            apply_mutation_on_disk(
                Path(tempdir)
                / mutation.context.file.path.relative_to(self.project_root),
                mutation,
            )
            # TODO: Timeout
            completed_process = subprocess.run(
                self.run_command, shell=True, cwd=Path(tempdir)
            )
            if completed_process.returncode == 1:
                return SuccessStatus.KILLED
            return SuccessStatus.SURVIVED
