"""An indeterminate spinner."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.widgets import Static

from ..primitives import Speed, frames
from ..tokens import DURATION, SpinnerName


class Spinner(Static):
    """An indeterminate spinner. Frame set and tick rate come from tokens."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {"spinner--frame", "spinner--label"}
    """
    | Class | Description |
    | :- | :- |
    | `spinner--frame` | The animating glyph. |
    | `spinner--label` | The text beside it. |
    """

    DEFAULT_CSS = """
    Spinner {
        width: auto;
        height: 1;

        & > .spinner--frame { color: $accent; }
        & > .spinner--label { color: $text; }
    }
    """

    def __init__(
        self,
        label: str = "",
        *,
        variant: SpinnerName = "dots",
        speed: Speed = "fast",
        **kwargs: Any,
    ) -> None:
        super().__init__("", **kwargs)
        self._frames = frames(variant)
        self._interval = DURATION[speed]
        self._label = label
        self._index = 0

    def on_mount(self) -> None:
        self.set_interval(self._interval, self._advance)

    def _advance(self) -> None:
        self._index = (self._index + 1) % len(self._frames)
        self.refresh()

    def render(self) -> RenderResult:
        text = RichText(no_wrap=True)
        text.append(
            self._frames[self._index],
            style=self.get_component_rich_style("spinner--frame"),
        )
        if self._label:
            text.append(
                f" {self._label}",
                style=self.get_component_rich_style("spinner--label"),
            )
        return text
