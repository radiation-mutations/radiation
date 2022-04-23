from ast import AST
from typing import Callable, Iterable, Sequence

from ..mutation import Mutation
from ..types import Context
from .binops import switch_bin_ops
from .boolops import switch_bool_ops
from .compare import switch_compare_ops
from .constants import modify_constants
from .invert import invert
from .unaryops import switch_unary_ops

Mutator = Callable[[AST, Context], Iterable[Mutation]]

builtin_mutators = [
    switch_bin_ops,
    switch_bool_ops,
    modify_constants,
    switch_unary_ops,
    switch_compare_ops,
    invert,
]


def get_default_mutators() -> Sequence[Mutator]:
    return builtin_mutators.copy()
