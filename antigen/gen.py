from ast import AST, iter_fields
from copy import copy, deepcopy
from typing import Iterator

from .mutators import get_mutators
from .types import Mutation


def gen_mutations(node: AST) -> Iterator[Mutation]:
    for name, field in iter_fields(node):
        if isinstance(field, AST):
            for mutation in gen_mutations(field):
                new_node = copy(node)
                setattr(new_node, name, mutation.node)
                yield Mutation(new_node)
        elif isinstance(field, list):
            for index, item in enumerate(field):
                if isinstance(item, AST):
                    for mutation in gen_mutations(item):
                        new_node = deepcopy(node)
                        getattr(new_node, name)[index] = mutation.node
                        yield Mutation(new_node)
    for mutator in get_mutators():
        yield from mutator(node)
