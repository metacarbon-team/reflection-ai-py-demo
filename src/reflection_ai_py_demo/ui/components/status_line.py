"""One line of state: a glyph, a message, and an optional detail."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widgets import Static

from ..primitives import Status, glyph, one_of
from ..tokens import GlyphName


class StatusLine(Static):
    """One line of state: a glyph, a message, and an optional detail.

    Written the way a stock Textual widget is written - see `Switch` for the
    canonical shape. The styleable parts are declared in `COMPONENT_CLASSES`
    and coloured from CSS, so this class carries no colour of its own and no
    theme-change plumbing: Textual re-resolves the styles on every repaint.
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "statusline--mark",
        "statusline--message",
        "statusline--detail",
    }
    """
    | Class | Description |
    | :- | :- |
    | `statusline--mark` | The leading status glyph. |
    | `statusline--message` | The message body. |
    | `statusline--detail` | The trailing dimmed detail. |
    """

    DEFAULT_CSS = """
    StatusLine {
        width: 1fr;
        height: 1;
        color: $text;

        & > .statusline--message { color: $text; }
        & > .statusline--detail { color: $text-muted; }
        & > .statusline--mark { color: $info; }

        &.-success > .statusline--mark { color: $success; }
        &.-danger  > .statusline--mark { color: $danger; }
        &.-warning > .statusline--mark { color: $warning; }
        &.-info    > .statusline--mark { color: $info; }
        &.-pending > .statusline--mark { color: $text-muted; }
    }
    """

    message: reactive[str] = reactive("")
    status: reactive[Status] = reactive[Status]("info")
    detail: reactive[str | None] = reactive(None)

    #: Only the glyph now - the colour moved to CSS, where it belongs.
    _MARKS: ClassVar[dict[str, GlyphName]] = {
        "success": "check",
        "danger": "cross",
        "warning": "warning",
        "info": "info",
        "pending": "dot",
    }

    def __init__(
        self,
        message: str = "",
        *,
        status: Status = "info",
        detail: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("", **kwargs)
        one_of(status, self._MARKS, "status")
        self.set_reactive(StatusLine.message, message)
        self.set_reactive(StatusLine.status, status)
        self.set_reactive(StatusLine.detail, detail)

    def on_mount(self) -> None:
        self._sync_status_class()

    def watch_message(self) -> None:
        self.refresh()

    def watch_status(self) -> None:
        self._sync_status_class()
        self.refresh()

    def watch_detail(self) -> None:
        self.refresh()

    def _sync_status_class(self) -> None:
        """Mirror the status onto a CSS class so the stylesheet can target it."""
        for name in self._MARKS:
            self.set_class(name == self.status, f"-{name}")

    def render(self) -> RenderResult:
        """Compose from component styles, which Textual resolves per repaint.

        This is why the element needs no theme watcher: `get_component_rich_style`
        reads the CURRENT theme every time, where a hand-built `rich.Text` that
        baked in hex values would go stale on a light/dark toggle.
        """
        text = RichText(no_wrap=True, overflow="ellipsis")
        text.append(
            glyph(self._MARKS[self.status]),
            style=self.get_component_rich_style("statusline--mark"),
        )
        text.append(
            f" {self.message}",
            style=self.get_component_rich_style("statusline--message"),
        )
        if self.detail:
            text.append(
                f"  {self.detail}",
                style=self.get_component_rich_style("statusline--detail"),
            )
        return text
