from ast import Module, parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from .filters import MutantFilter, get_default_filters
from .gen import gen_mutations
from .mutation import Mutation
from .mutators import Mutator, get_default_mutators
from .runners import Runner, TempDirRunner
from .types import Context, FileContext, NodeContext, SuccessStatus


def _get_initial_context(path: Path, module: Module) -> Context:
    return Context(
        file=FileContext(path=path),
        node=NodeContext(
            lineno=module.body[0].lineno,
            end_lineno=module.body[-1].end_lineno,
            col_offset=module.body[0].col_offset,
            end_col_offset=module.body[-1].end_col_offset,
        ),
    )


@dataclass(frozen=True)
class Antigen:
    runner: Optional[Runner] = field(default=None)
    filters: Sequence[MutantFilter] = field(default_factory=get_default_filters)
    mutators: Sequence[Mutator] = field(default_factory=get_default_mutators)

    def gen_mutations_str(
        self, code: str, path: Union[str, Path] = "<code>"
    ) -> Iterable[Mutation]:
        tree = parse(code)
        for mut in gen_mutations(
            tree,
            parent_context=_get_initial_context(Path(path), tree),
            mutators=self.mutators,
        ):
            if all(filter_fn(mut) for filter_fn in self.filters):
                yield mut

    def gen_mutations(self, path: Union[str, Path]) -> Iterable[Mutation]:
        yield from self.gen_mutations_str(Path(path).read_text(), path)

    def test_mutation(
        self, mutation: Mutation, *, project_root: Union[str, Path], run_command: str
    ) -> SuccessStatus:
        runner = self.runner or TempDirRunner(
            project_root=Path(project_root), run_command=run_command
        )
        return runner(mutation)
