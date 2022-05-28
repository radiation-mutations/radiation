import datetime as dt
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ResultStatus(Enum):
    SURVIVED = "survived"
    KILLED = "killed"
    TIMED_OUT = "timed out"


@dataclass
class TestsResult:
    duration: dt.timedelta
    status: ResultStatus
    output: Optional[str] = None


@dataclass(frozen=True)
class NodeContext:
    lineno: int
    end_lineno: Optional[int]
    col_offset: int
    end_col_offset: Optional[int]


@dataclass(frozen=True)
class FileContext:
    path: Path


@dataclass(frozen=True)
class Context:
    file: FileContext
    node: NodeContext
    extra: Optional[Any] = None
