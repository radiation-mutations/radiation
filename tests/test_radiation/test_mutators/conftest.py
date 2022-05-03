from pathlib import Path

import pytest

from radiation.types import Context, FileContext, NodeContext


@pytest.fixture
def dummy_context() -> Context:
    return Context(
        file=FileContext(path=Path("a.py")),
        node=NodeContext(
            lineno=1,
            end_lineno=None,
            col_offset=0,
            end_col_offset=None,
        ),
    )
