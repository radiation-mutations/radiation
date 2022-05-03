import ast
import os
from ast import Module
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


def _find_files(
    search: str, extension: str = ".py", excludes: Optional[List[Path]] = None
) -> Iterable[Path]:
    for path in iglob(search, recursive=True):
        if Path(path).is_dir():
            yield from _find_files(f"{path}/*", extension=extension, excludes=excludes)
            continue
        if not path.endswith(extension):
            continue
        if excludes and any(exclude in Path(path).parents for exclude in excludes):
            continue
        yield Path(path)


def _assert_relative(paths: List[str]) -> None:
    assert not any(path.startswith("/") for path in paths), "paths must be relative"


@dataclass(frozen=True)
class Radiation:
    config: Config
    runner: Optional[Runner] = field(default=None)
    filters: Sequence[MutantFilter] = field(default_factory=get_default_filters)
    mutators: Sequence[Mutator] = field(default_factory=get_default_mutators)

    def find_files(
        self,
        globs: Union[str, List[str]],
        *,
        exclude: Optional[str] = None,
        excludes: Optional[List[str]] = None,
    ) -> Iterable[Path]:
        globs = [globs] if isinstance(globs, str) else globs
        excludes = [exclude] if exclude else excludes or []
        _assert_relative(globs)
        _assert_relative(excludes)

        for glob in globs:
            yield from _find_files(
                # include is a glob and thus won't be handled well by pathlib
                os.path.join(self.config.project_root, glob),
                excludes=[self.config.project_root / exclude for exclude in excludes],
            )

    def gen_mutations_str(
        self, code: str, path: Union[str, Path] = "<code>"
    ) -> Iterable[Mutation]:
        path = Path(path)
        path = path if path.is_absolute() else self.config.project_root / path

        tree = ast.parse(code)

        if len(tree.body) == 0:
            return

        for mut in gen_mutations(
            tree,
            parent_context=_get_initial_context(path, tree),
            mutators=self.mutators,
        ):
            if all(filter_fn(mut, self.config) for filter_fn in self.filters):
                yield mut

    def gen_mutations(self, path: Union[str, Path]) -> Iterable[Mutation]:
        yield from self.gen_mutations_str(Path(path).read_text(), path)

    def test_mutation(self, mutation: Mutation, *, run_command: str) -> SuccessStatus:
        runner = self.runner or TempDirRunner(run_command=run_command)
        return runner(mutation, self.config)
