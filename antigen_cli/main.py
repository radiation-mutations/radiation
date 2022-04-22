from dataclasses import fields
from typing import Any, Dict, Optional

import click

from antigen import Antigen
from antigen.config import Config
from antigen_cli.config import (
    CLIConfig,
    read_config,
    read_default_config,
    validate_path_suffix,
)


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

    for path in antigen.find_files(config.include):
        for index, mutation in enumerate(antigen.gen_mutations(path)):
            rel_path = mutation.context.file.path.relative_to(config.project_root)
            result = antigen.test_mutation(mutation, run_command=config.run_command)
            click.echo(f"{rel_path} #{index}: {result}")


if __name__ == "__main__":
    cli()
