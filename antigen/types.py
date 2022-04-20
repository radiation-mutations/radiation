from ast import AST
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class NodeContext:
    lineno: int
    end_lineno: Optional[int]
    col_offset: int
    end_col_offset: Optional[int]


@dataclass
class FileContext:
    filename: str


@dataclass
class Context:
    file: FileContext
    node: NodeContext
    extra: Optional[Any] = None


@dataclass
class Mutation:
    node: AST
    context: Context
