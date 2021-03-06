import os
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import click
import toml


@dataclass(frozen=True)
class CLIConfig:
    project_root: Path
    include: List[str] = field(default_factory=lambda: ["."])
    run_command: str = "pytest"
    tests_dir: str = "tests"
    tests_timeout: Optional[float] = None
    diff_command: Optional[str] = None
    line_limit: Optional[int] = None


DEFAULT_SECTIONS = ("radiation", "settings")

DEFAULT_FILES = [
    (".radiation.cfg", DEFAULT_SECTIONS),
    (".radiation.toml", DEFAULT_SECTIONS),
    ("pyproject.toml", ("tool.radiation",)),
]


def _get_nested(data: Dict[str, Any], key: str) -> Optional[Any]:
    if "." not in key:
        return data.get(key)

    head, rest = key.split(".", maxsplit=1)
    return _get_nested(data.get(head, {}), rest)


def _toml_parse_list(value: str) -> List[str]:
    return [value] if isinstance(value, str) else value


def _parse_limit(value: Optional[str]) -> Optional[int]:
    return int(value) if value and value != "none" else None


def _read_toml(
    path: Union[str, Path], possible_sections: Sequence[str] = DEFAULT_SECTIONS
) -> Optional[CLIConfig]:
    value = toml.loads(Path(path).read_text())
    for section in possible_sections:
        if config := _get_nested(value, section):
            return CLIConfig(
                include=_toml_parse_list(config["include"]),
                run_command=config["run_command"],
                tests_dir=config["tests_dir"],
                project_root=Path(path).parent,
                tests_timeout=config.get("tests_timeout"),
                diff_command=config.get("diff_command"),
                line_limit=_parse_limit(config.get("line_limit")),
            )
    return None


def _cfg_parse_list(value: str) -> List[str]:
    return [line.strip() for line in value.split("\n") if line.strip()]


def _read_cfg(
    path: Union[str, Path], possible_sections: Sequence[str] = DEFAULT_SECTIONS
) -> Optional[CLIConfig]:
    parser = ConfigParser()
    parser.read(path)
    for section in possible_sections:
        if parser.has_section(section):
            return CLIConfig(
                include=_cfg_parse_list(parser.get(section, "include")),
                run_command=parser.get(section, "run_command"),
                tests_dir=parser.get(section, "tests_dir"),
                project_root=Path(path).parent,
                tests_timeout=parser.getfloat(section, "tests_timeout", fallback=None),
                diff_command=parser.get(section, "diff_command", fallback=None),
                line_limit=_parse_limit(
                    parser.get(section, "line_limit", fallback=None)
                ),
            )
    return None


PARSERS = {
    ".toml": _read_toml,
    ".cfg": _read_cfg,
}


def validate_path_suffix(path: Optional[Union[str, Path]]) -> None:
    if path and Path(path).suffix not in PARSERS:
        raise click.BadParameter(
            f"Unrecognized config file format (supported: {', '.join(PARSERS.keys())})"
        )


def read_config(path: Union[str, Path]) -> CLIConfig:
    validate_path_suffix(path)

    if config := PARSERS[Path(path).suffix](path, DEFAULT_SECTIONS):
        return config

    raise Exception(
        "Cannot find expected sections in config file "
        f"(expected: {' or '.join(f'[{section}]' for section in DEFAULT_SECTIONS)})"
    )


def read_default_config(root_path: Optional[Union[str, Path]] = None) -> CLIConfig:
    root_path = Path(root_path or os.getcwd())

    for filename, sections in DEFAULT_FILES:
        path = root_path / filename
        if not path.exists():
            continue
        if config := PARSERS[path.suffix](path, sections):
            return config

    return CLIConfig(project_root=root_path)
