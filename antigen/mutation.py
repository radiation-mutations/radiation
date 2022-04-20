from __future__ import annotations

from ast import AST
from dataclasses import dataclass
from pathlib import Path
from typing import List

from astunparse import unparse

from antigen.types import Context


@dataclass
class Mutation:
    tree: AST
    node: AST
    context: Context

    @staticmethod
    def from_node(node: AST, context: Context) -> Mutation:
        return Mutation(node, node, context)

    def with_tree(self, tree: AST) -> Mutation:
        return Mutation(tree, self.node, self.context)


def apply_mutation_on_lines(lines: List[str], mutation: Mutation) -> str:
    lineno = mutation.context.node.lineno
    col_offset = mutation.context.node.col_offset
    end_lineno = mutation.context.node.end_lineno or lineno
    end_col_offset = mutation.context.node.end_col_offset

    start_of_line = lines[lineno - 1][:col_offset]
    end_of_line = lines[end_lineno - 1][end_col_offset:]

    return "\n".join(
        lines[: lineno - 1]
        + [start_of_line + unparse(mutation.node).strip("\n") + end_of_line]
        + lines[end_lineno:]
    )


def apply_mutation_on_disk(path: Path, mutation: Mutation) -> None:
    mutated = apply_mutation_on_lines(path.read_text().splitlines(), mutation)
    path.write_text(mutated)
