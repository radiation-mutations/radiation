from __future__ import annotations

import subprocess
from dataclasses import dataclass

from whatthepatch import parse_patch
from whatthepatch.patch import Change

from ..mutation import Mutation


def _diff_matches(mutation: Mutation, change: Change) -> bool:
    lineno = mutation.context.node.lineno
    end_lineno = mutation.context.node.end_lineno or lineno
    return change.new is not None and lineno <= change.new <= end_lineno


@dataclass
class PatchFilter:
    patch: str

    def __call__(self, mutation: Mutation) -> bool:
        for diff in parse_patch(self.patch):
            if diff.header is None or diff.changes is None:
                continue
            if diff.header.new_path != str(mutation.context.file.path):
                continue
            return any(
                _diff_matches(mutation, change)
                for change in diff.changes
                if change.new is not None
            )
        return False

    @classmethod
    def from_git_diff(cls, target: str, base: str = "HEAD") -> PatchFilter:
        completed_process = subprocess.run(
            ["git", "diff", base, target], check=True, capture_output=True, text=True
        )
        return PatchFilter(patch=completed_process.stdout)
