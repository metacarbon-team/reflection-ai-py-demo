"""The agent's working affordance: a spinner beside shimmering text."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal

from ..components import Shimmer, Spinner
from ..primitives import glyph


class Thinking(Horizontal):
    """The agent's "working" affordance: a spinner beside shimmering text."""

    DEFAULT_CSS = """
    Thinking { width: auto; height: 1; }
    Thinking > Spinner { margin-right: $space-xs; }
    """

    def __init__(self, label: str = "Thinking", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._label = label

    def compose(self) -> ComposeResult:
        yield Spinner()
        yield Shimmer(f"{self._label}{glyph('ellipsis')}")
