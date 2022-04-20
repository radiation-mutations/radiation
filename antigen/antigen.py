from ast import Module, parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence, Union

from antigen.gen import gen_mutations
from antigen.types import Context, FileContext, Mutation, NodeContext

from .filters import MutantFilter, get_default_filters
from .mutators import Mutator, get_default_mutators


def _get_initial_context(filename: str, module: Module) -> Context:
    return Context(
        file=FileContext(filename=filename),
        node=NodeContext(
            lineno=module.body[0].lineno,
            end_lineno=module.body[-1].end_lineno,
            col_offset=module.body[0].col_offset,
            end_col_offset=module.body[-1].end_col_offset,
        ),
    )


@dataclass(frozen=True)
class Antigen:
    mutators: Sequence[Mutator] = field(default_factory=get_default_mutators)
    filters: Sequence[MutantFilter] = field(default_factory=get_default_filters)

    def gen_mutations_str(
        self, code: str, filename: Union[str, Path] = "<code>"
    ) -> Iterable[Mutation]:
        tree = parse(code)
        for mut in gen_mutations(
            tree,
            parent_context=_get_initial_context(str(filename), tree),
            mutators=self.mutators,
        ):
            if all(filter_fn(mut) for filter_fn in self.filters):
                yield mut

    def gen_mutations(self, path: Union[str, Path]) -> Iterable[Mutation]:
        yield from self.gen_mutations_str(Path(path).read_text(), path)
