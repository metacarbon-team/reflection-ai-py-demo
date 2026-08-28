"""Stacks: the only layout primitives a terminal needs."""

from __future__ import annotations

from typing import Any

from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from .base import Gap


class VStack(Vertical):
    """Vertical stack with a token-sized gutter."""

    DEFAULT_CSS = """
    VStack { width: 1fr; height: auto; }
    VStack.-gap-xs > * { margin-bottom: $space-xs; }
    VStack.-gap-sm > * { margin-bottom: $space-sm; }
    VStack.-gap-md > * { margin-bottom: $space-md; }
    VStack.-gap-lg > * { margin-bottom: $space-lg; }
    """

    def __init__(self, *children: Widget, gap: Gap = "none", **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.add_class(f"-gap-{gap}")


class HStack(Horizontal):
    """Horizontal stack with a token-sized gutter."""

    DEFAULT_CSS = """
    HStack { width: auto; height: auto; }
    HStack.-gap-xs > * { margin-right: $space-xs; }
    HStack.-gap-sm > * { margin-right: $space-sm; }
    HStack.-gap-md > * { margin-right: $space-md; }
    HStack.-gap-lg > * { margin-right: $space-lg; }
    """

    def __init__(self, *children: Widget, gap: Gap = "xs", **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.add_class(f"-gap-{gap}")
