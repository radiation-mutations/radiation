from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from whatthepatch import parse_patch
from whatthepatch.patch import Change

from ..config import Config
from ..mutation import Mutation


def is_mutation_in_diff(mutation: Mutation, file_changes: List[Change]) -> bool:
    lineno = mutation.context.node.lineno
    end_lineno = mutation.context.node.end_lineno or lineno

    return any(
        lineno <= change.new <= end_lineno
        for change in file_changes
        if change.new is not None and change.old is None
    )


@dataclass
class PatchFilter:
    patch: str

    def __call__(self, mutation: Mutation, config: Config) -> bool:
        mutation_path = str(mutation.context.file.path.relative_to(config.project_root))

        for diff in parse_patch(self.patch):
            if diff.header is None or diff.changes is None:
                continue
            if diff.header.new_path != mutation_path:
                continue
            return is_mutation_in_diff(mutation, diff.changes)

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
