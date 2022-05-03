from ast import AST, boolop, cmpop, expr_context, iter_fields, operator, unaryop
from copy import copy, deepcopy
from typing import Iterator, Sequence

from .context import get_context
from .mutation import Mutation
from .mutators import Mutator
from .types import Context

SKIP_CLASSES = (operator, boolop, cmpop, unaryop, expr_context)


def gen_mutations(
    node: AST, *, parent_context: Context, mutators: Sequence[Mutator]
) -> Iterator[Mutation]:
    context = get_context(node, parent_context)
    for name, field in iter_fields(node):
        if isinstance(field, SKIP_CLASSES):
            continue
        if isinstance(field, AST):
            for mutation in gen_mutations(
                field, parent_context=context, mutators=mutators
            ):
                new_node = copy(node)
                setattr(new_node, name, mutation.tree)
                yield mutation.with_tree(new_node)
        elif isinstance(field, list):
            for index, item in enumerate(field):
                if isinstance(item, SKIP_CLASSES):
                    continue
                if isinstance(item, AST):
                    for mutation in gen_mutations(
                        item, parent_context=context, mutators=mutators
                    ):
                        new_node = deepcopy(node)
                        getattr(new_node, name)[index] = mutation.tree
                        yield mutation.with_tree(new_node)
    for mutator in mutators:
        yield from mutator(node, context)
