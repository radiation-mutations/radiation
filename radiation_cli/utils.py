from pathlib import Path
from typing import Optional, Union

import click

from radiation.mutation import Mutation, apply_mutation_on_string
from radiation_cli.config import CLIConfig


def is_relative_to(path: Union[str, Path], parent: Union[str, Path]) -> bool:
    assert Path(path).is_absolute()
    assert Path(parent).is_absolute()
    return Path(parent) in Path(path).parents


def get_mutation_loc(mutation: Optional[Mutation], *, config: CLIConfig) -> str:
    if not mutation:
        return ""
    rel_path = str(mutation.context.file.path.relative_to(config.project_root))
    return f"{rel_path}:{mutation.context.node.lineno}"


def dump_mutation(
    mutation: Mutation, *, status: str, config: CLIConfig, context_lines: int = 2
) -> None:
    path = mutation.context.file.path
    lineno = mutation.context.node.lineno

    lines = apply_mutation_on_string(path.read_text(), mutation).splitlines()

    start = max(0, lineno - context_lines - 1)
    end = min(len(lines), lineno + context_lines)

    click.echo("")
    click.secho(
        f"{status.capitalize()} mutant in {get_mutation_loc(mutation, config=config)}",
        bold=True,
    )
    for index, line in enumerate(lines[start:end]):
        curr_lineno = index + start + 1
        click.secho(f"{curr_lineno} {line}", bold=curr_lineno == lineno)
