from typing import Callable, List, Sequence

from ..config import Config
from ..mutation import Mutation

MutantFilter = Callable[[Mutation, Config], bool]

builtin_filters: List[MutantFilter] = []


def get_default_filters() -> Sequence[MutantFilter]:
    return builtin_filters.copy()
