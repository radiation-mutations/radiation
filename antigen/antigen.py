import os
from ast import Module, parse
from dataclasses import dataclass, field
from glob import iglob
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

from .config import Config
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


def _find_files(search: str, extension: str = ".py") -> Iterable[Path]:
    for path in iglob(search, recursive=True):
        if Path(path).is_dir():
            yield from _find_files(f"{path}/**/*", extension=extension)
            continue
        if not path.endswith(extension):
            continue
        yield Path(path)


@dataclass(frozen=True)
class Antigen:
    config: Config
    runner: Optional[Runner] = field(default=None)
    filters: Sequence[MutantFilter] = field(default_factory=get_default_filters)
    mutators: Sequence[Mutator] = field(default_factory=get_default_mutators)

    def find_files(self, globs: Union[str, List[str]]) -> Iterable[Path]:
        globs = [globs] if isinstance(globs, str) else globs
        assert not any(
            include.startswith("/") for include in globs
        ), "globs must be relative"
        for include in globs:
            yield from _find_files(f"{self.config.project_root}{os.path.sep}{include}")

    def gen_mutations_str(
        self, code: str, path: Union[str, Path] = "<code>"
    ) -> Iterable[Mutation]:
        path = Path(path)
        path = path if path.is_absolute() else self.config.project_root / path

        tree = parse(code)
        for mut in gen_mutations(
            tree,
            parent_context=_get_initial_context(path, tree),
            mutators=self.mutators,
        ):
            if all(filter_fn(mut) for filter_fn in self.filters):
                yield mut

    def gen_mutations(self, path: Union[str, Path]) -> Iterable[Mutation]:
        yield from self.gen_mutations_str(Path(path).read_text(), path)

    def test_mutation(self, mutation: Mutation, *, run_command: str) -> SuccessStatus:
        runner = self.runner or TempDirRunner(run_command=run_command)
        return runner(mutation, self.config)
