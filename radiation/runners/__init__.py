from typing import Optional, Protocol

from ..config import Config
from ..mutation import Mutation
from ..types import TestsResult
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


def get_default_runner() -> Runner:
    return TempDirRunner(run_command="pytest")
