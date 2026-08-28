"""Bordered regions: a bare surface and a titled panel."""

from __future__ import annotations

from typing import Any

from textual.containers import Vertical
from textual.widget import Widget

from .base import BorderName


class Surface(Vertical):
    """A bordered region. ``border`` names an intent, not a glyph set."""

    DEFAULT_CSS = """
    Surface {
        width: 1fr;
        height: auto;
        padding: 0 $space-xs;
        border: round $border;
    }
    /* Each `$rule-*` carries style and colour together - see BORDERS in
       tokens.py for why Textual forces that shape. The style names used to be
       repeated here as literals while the token table sat unread. */
    Surface.-b-none { border: $rule-none; padding: 0; }
    Surface.-b-subtle { border: $rule-subtle; }
    Surface.-b-solid { border: $rule-solid; }
    Surface.-b-strong { border: $rule-strong-strong; }
    Surface.-b-emphasis { border: $rule-emphasis-strong; }
    Surface.-b-ascii { border: $rule-ascii; }
    Surface.-focused { border: $rule-strong-focus; }
    """

    def __init__(
        self,
        *children: Widget,
        border: BorderName = "subtle",
        focused: bool = False,
        title: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*children, **kwargs)
        self.add_class(f"-b-{border}")
        if focused:
            self.add_class("-focused")
        if title:
            self.border_title = title


class Panel(Vertical):
    """A titled surface - the workhorse container for grouped content."""

    DEFAULT_CSS = """
    Panel {
        width: 1fr;
        height: auto;
        border: round $border;
        border-title-color: $text-muted;
        border-title-style: bold;
        padding: 0 $space-xs;
    }
    Panel.-accent { border: round $accent; border-title-color: $accent; }
    """

    def __init__(self, *children: Widget, title: str = "", accent: bool = False, **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        if title:
            self.border_title = title
        if accent:
            self.add_class("-accent")
