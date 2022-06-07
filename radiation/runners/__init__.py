import datetime as dt
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from ..config import Config
from ..mutation import Mutation
from ..types import ResultStatus, TestsResult
from .tempdir import TempDirRunner


class Runner(Protocol):
    def run_baseline_tests(
        self, *, config: Config, timeout: Optional[float] = None
    ) -> TestsResult:
        ...

    def test_mutation(
        self, mutation: Mutation, *, config: Config, timeout: Optional[float] = None
    ) -> TestsResult:
        ...
