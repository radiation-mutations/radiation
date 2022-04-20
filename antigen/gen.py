from ast import AST, iter_fields
from copy import copy, deepcopy
from typing import Iterator, Sequence

from .context import get_context
from .mutators import Mutator
from .types import Context, Mutation


def gen_mutations(
    node: AST, *, parent_context: Context, mutators: Sequence[Mutator]
) -> Iterator[Mutation]:
    context = get_context(node, parent_context)
    for name, field in iter_fields(node):
        if isinstance(field, AST):
            for mutation in gen_mutations(
                field, parent_context=context, mutators=mutators
            ):
                new_node = copy(node)
                setattr(new_node, name, mutation.node)
                yield Mutation(new_node, mutation.context)
        elif isinstance(field, list):
            for index, item in enumerate(field):
                if isinstance(item, AST):
                    for mutation in gen_mutations(
                        item, parent_context=context, mutators=mutators
                    ):
                        new_node = deepcopy(node)
                        getattr(new_node, name)[index] = mutation.node
                        yield Mutation(new_node, mutation.context)
    for mutator in mutators:
        yield from mutator(node, context)
