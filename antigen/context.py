from ast import AST

from .types import Context, NodeContext


def get_context(node: AST, parent_context: Context) -> Context:
    return Context(
        file=parent_context.file,
        node=NodeContext(
            lineno=getattr(node, "lineno", parent_context.node.lineno),
            end_lineno=getattr(node, "end_lineno", parent_context.node.end_lineno),
            col_offset=getattr(node, "col_offset", parent_context.node.col_offset),
            end_col_offset=getattr(
                node, "end_col_offset", parent_context.node.end_col_offset
            ),
        ),
    )
