from typing import Callable

from ..config import Config
from ..mutation import Mutation
from ..types import SuccessStatus
from .tempdir import TempDirRunner

Runner = Callable[[Mutation, Config], SuccessStatus]
