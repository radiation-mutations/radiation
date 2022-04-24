from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from typing import Dict, Tuple

from ..config import Config
from ..mutation import Mutation


@dataclass
class LineLimitFilter:
    limit: int = 2
    _lines: Dict[Tuple[Path, int], count] = field(init=False, default_factory=dict)

    def __call__(self, mutation: Mutation, config: Config) -> bool:
        key = (mutation.context.file.path, mutation.context.node.lineno)
        return next(self._lines.setdefault(key, count())) < self.limit
