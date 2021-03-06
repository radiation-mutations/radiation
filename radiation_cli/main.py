from collections import defaultdict
from dataclasses import replace
from typing import Any, Dict, List, Optional

import click
from click import ClickException

from radiation import Radiation
from radiation.config import Config
from radiation.filters.line_limit import LineLimitFilter
from radiation.filters.patch import PatchFilter
from radiation.mutation import Mutation
from radiation.runners import TempDirRunner
from radiation.types import ResultStatus
from radiation_cli.config import (
    CLIConfig,
    read_config,
    read_default_config,
    validate_path_suffix,
)
from radiation_cli.utils import dump_mutation, get_mutation_loc


def _override_config(config: CLIConfig, overrides: Dict[str, Any]) -> CLIConfig:
    overrides = {key: val for key, val in overrides.items() if val is not None}
    return replace(config, **overrides)


pass_config = click.make_pass_decorator(CLIConfig)


@click.group()
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="configuration file to use",
    required=False,
    show_default=".radiation.cfg",
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
    "--tests-timeout",
    type=float,
    help="maximum time for each test suite to run in seconds",
    required=False,
)
@click.option(
    "--run-command",
    type=str,
    help="command to run to test a mutation",
    required=False,
    show_default="pytest",
)
@click.option(
    "--diff-command",
    type=str,
    help="filter out mutations on unchanged lines according to the diff"
    " returned from running this command, shell expansions available",
    required=False,
)
@click.option(
    "--line-limit",
    type=int,
    help="limit the number of mutations on any given line",
    required=False,
    show_default="none",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: Optional[str],
    project_root: Optional[str],
    **config_overrides: Any,
) -> None:
    config_base = (
        read_config(config_file)
        if config_file
        else read_default_config(root_path=project_root)
    )
    config = _override_config(config_base, config_overrides)
    ctx.obj = config


@cli.command(help="run the mutation testing pipeline")
@pass_config
def run(config: CLIConfig) -> None:
    patch = (
        PatchFilter.from_shell_command(
            config.diff_command, project_dir=config.project_root
        )
        if config.diff_command
        else None
    )
    limiter = LineLimitFilter(config.line_limit) if config.line_limit else None

    radiation = Radiation(
        runner=TempDirRunner(run_command=config.run_command),
        filters=list(filter(None, [patch, limiter])),
        config=Config(project_root=config.project_root),
    )

    mutations = [
        mutation
        for path in radiation.find_files(config.include, exclude=config.tests_dir)
        for mutation in radiation.gen_mutations(path)
    ]

    click.echo(f"Generated {len(mutations)} mutations")

    click.echo("Running baseline tests ..")
    result = radiation.run_baseline_tests()

    if result.status == "killed":
        click.secho(result.output, fg="red", err=True)
        raise ClickException(
            "Cannot test mutations when the baseline "
            "tests are failing (test command output printed above)"
        )

    baseline_timeout = result.duration.total_seconds() * 1.5
    timeout = (
        min(baseline_timeout, config.tests_timeout)
        if config.tests_timeout
        else baseline_timeout
    )

    results: Dict[ResultStatus, List[Mutation]] = defaultdict(list)

    with click.progressbar(
        mutations,
        label="Running tests",
        show_percent=False,
        item_show_func=lambda mutation: get_mutation_loc(mutation, config=config),
    ) as progress_bar:

        for mutation in progress_bar:
            result = radiation.test_mutation(mutation, timeout=timeout)
            results[result.status].append(mutation)

    for mutation in results["survived"]:
        dump_mutation(mutation, status="surviving", config=config)

    for mutation in results["timed out"]:
        dump_mutation(mutation, status="timed out", config=config)


if __name__ == "__main__":
    cli()
