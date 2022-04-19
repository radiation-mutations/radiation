from ast import AST
from typing import Callable, Iterable, List, cast

from pkg_resources import iter_entry_points

from ..types import Mutation
from .binops import switch_bin_ops
from .compare import switch_compare_ops
from .constants import modify_constants
from .invert import invert
from .unaryops import switch_unary_ops

Mutator = Callable[[AST], Iterable[Mutation]]

builtin_mutators = [
    switch_bin_ops,
    modify_constants,
    switch_unary_ops,
    switch_compare_ops,
    invert,
]


def get_mutators() -> List[Mutator]:
    additional_mutators = [
        cast(Mutator, entry_point.load())
        for entry_point in iter_entry_points("antigen.mutators")
    ]
    return [*builtin_mutators, *additional_mutators]
