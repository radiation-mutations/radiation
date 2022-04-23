from dataclasses import fields
from typing import Any, Dict, List, Optional

import click

from antigen import Antigen
from antigen.config import Config
from antigen.mutation import Mutation
from antigen.types import SuccessStatus
from antigen_cli.config import (
    CLIConfig,
    read_config,
    read_default_config,
    validate_path_suffix,
)
from antigen_cli.utils import dump_mutation, get_mutation_loc


def _override_config(config: CLIConfig, values: Dict[str, Any]) -> CLIConfig:
    return CLIConfig(
        **{
            field.name: values.get(field.name) or getattr(config, field.name)
            for field in fields(config)
        }
    )


pass_config = click.make_pass_decorator(CLIConfig)


@click.group()
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="configuration file to use",
    required=False,
    show_default=".antigen.cfg",
    callback=lambda ctx, param, value: validate_path_suffix(value),
)
@click.option(
    "-p",
    "--project-root",
    type=click.Path(exists=True),
    help="path to project to run on",
    required=False,
    show_default="cwd",
)
@click.option(
    "-i",
    "--include",
    type=str,
    help="paths from which to take files for mutation, can be globs",
    required=False,
)
@click.option(
    "--tests-dir",
    type=str,
    help="path to the tests, will not be mutated",
    required=False,
    show_default="tests",
)
@click.option(
    "--run-command",
    type=str,
    help="command to run to test a mutation",
    required=False,
    show_default="pytest",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: Optional[str],
    project_root: Optional[str],
    **config_overrides: Any,
) -> None:
    config = (
        read_config(config_file)
        if config_file
        else read_default_config(root_path=project_root)
    )
    config = _override_config(config, config_overrides)
    ctx.obj = config


@cli.command(help="run the mutation testing pipeline")
@pass_config
def run(config: CLIConfig) -> None:
    antigen = Antigen(
        config=Config(project_root=config.project_root),
    )
    mutations = [
        mutation
        for path in antigen.find_files(config.include, exclude=config.tests_dir)
        for mutation in antigen.gen_mutations(path)
    ]

    click.echo(f"Generated {len(mutations)} mutations")

    survived: List[Mutation] = []
    timed_out: List[Mutation] = []

    with click.progressbar(
        mutations,
        label="Running tests",
        show_percent=False,
        item_show_func=lambda mutation: get_mutation_loc(mutation, config=config),
    ) as progress_bar:

        for mutation in progress_bar:
            result = antigen.test_mutation(mutation, run_command=config.run_command)
            if result == SuccessStatus.SURVIVED:
                survived += [mutation]
            if result == SuccessStatus.TIMED_OUT:
                timed_out += [mutation]

    for mutation in survived:
        dump_mutation(mutation, status="surviving", config=config)

    for mutation in timed_out:
        dump_mutation(mutation, status="timed out", config=config)


if __name__ == "__main__":
    cli()
