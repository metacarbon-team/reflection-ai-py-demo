"""A horizontal rule, optionally labelled."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from .base import glyph


class Divider(Static):
    """A horizontal rule, optionally labelled."""

    DEFAULT_CSS = """
    Divider { width: 1fr; height: 1; color: $border; }
    Divider.-strong { color: $border-strong; }
    """

    def __init__(self, label: str | None = None, *, strong: bool = False, **kwargs: Any) -> None:
        super().__init__("", **kwargs)
        self._label = label
        if strong:
            self.add_class("-strong")

    def on_resize(self) -> None:
        self._paint()

    def on_mount(self) -> None:
        self._paint()

    def _paint(self) -> None:
        width = max(self.size.width, 1)
        rule = glyph("line_h")
        if self._label:
            head = rule * 2
            text = f"{head} {self._label} "
            self.update(text + rule * max(width - len(text), 0))
        else:
            self.update(rule * width)
