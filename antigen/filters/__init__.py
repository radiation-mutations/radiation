from typing import Callable, List, Sequence

from ..mutation import Mutation

MutantFilter = Callable[[Mutation], bool]

builtin_filters: List[MutantFilter] = []


def get_default_filters() -> Sequence[MutantFilter]:
    return builtin_filters.copy()
