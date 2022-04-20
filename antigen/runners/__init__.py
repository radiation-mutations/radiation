from typing import Callable

from ..mutation import Mutation
from ..types import SuccessStatus
from .tempdir import TempDirRunner

Runner = Callable[[Mutation], SuccessStatus]
