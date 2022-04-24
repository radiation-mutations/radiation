from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from whatthepatch import parse_patch

from ..config import Config
from ..mutation import Mutation


@dataclass
class PatchFilter:
    patch: str

    def __call__(self, mutation: Mutation, config: Config) -> bool:
        rel_path = mutation.context.file.path.relative_to(config.project_root)
        lineno = mutation.context.node.lineno
        end_lineno = mutation.context.node.end_lineno or lineno

        for diff in parse_patch(self.patch):
            if diff.header is None or diff.changes is None:
                continue
            if diff.header.new_path != str(rel_path):
                continue
            return any(
                lineno <= change.new <= end_lineno
                for change in diff.changes
                if change.new is not None and change.old is None
            )
        return False

    @classmethod
    def from_git_diff(
        cls,
        target: str,
        base: Optional[str] = None,
        project_dir: Optional[Union[str, Path]] = None,
    ) -> PatchFilter:
        completed_process = subprocess.run(
            ["git", "diff", base, target] if base else ["git", "diff", target],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_dir,
        )
        return PatchFilter(patch=completed_process.stdout)
