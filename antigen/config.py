from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    project_root: Path
