from typing import Callable, List, cast

from pkg_resources import iter_entry_points

from ..types import Mutation
from .patch import filter_changed_lines

MutantFilter = Callable[[Mutation], bool]

builtin_filters = [filter_changed_lines]


def get_filters() -> List[MutantFilter]:
    additional_filters = [
        cast(MutantFilter, entry_point.load())
        for entry_point in iter_entry_points("antigen.mutators")
    ]
    return [*builtin_filters, *additional_filters]
