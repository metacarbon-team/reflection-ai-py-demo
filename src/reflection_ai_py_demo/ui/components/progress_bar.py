"""A determinate bar drawn from block glyphs."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widgets import Static

from ..primitives import glyph


class ProgressBar(Static):
    """A determinate bar drawn from block glyphs.

    Kept custom rather than subclassing Textual's `ProgressBar`: the fill
    character has to come from the glyph tokens so the ASCII fallback works,
    and the stock widget draws with its own characters.
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "progressbar--fill",
        "progressbar--track",
        "progressbar--label",
    }
    """
    | Class | Description |
    | :- | :- |
    | `progressbar--fill` | The completed portion. |
    | `progressbar--track` | The remaining portion. |
    | `progressbar--label` | The trailing percentage. |
    """

    DEFAULT_CSS = """
    ProgressBar {
        width: 1fr;
        height: 1;

        & > .progressbar--fill { color: $accent; }
        & > .progressbar--track { color: $text-subtle; }
        & > .progressbar--label { color: $text-muted; }
    }
    """

    progress: reactive[float] = reactive(0.0)

    def __init__(
        self,
        *,
        progress: float = 0.0,
        width: int = 32,
        label: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__("", **kwargs)
        self._width = width
        self._label = label
        self.set_reactive(ProgressBar.progress, progress)

    def watch_progress(self) -> None:
        self.refresh()

    def render(self) -> RenderResult:
        ratio = min(max(self.progress, 0.0), 1.0)
        filled = round(ratio * self._width)

        bar = RichText(no_wrap=True)
        bar.append(
            glyph("bar_full") * filled,
            style=self.get_component_rich_style("progressbar--fill"),
        )
        bar.append(
            glyph("bar_empty") * (self._width - filled),
            style=self.get_component_rich_style("progressbar--track"),
        )
        if self._label:
            bar.append(
                f"  {int(ratio * 100):>3}%",
                style=self.get_component_rich_style("progressbar--label"),
            )
        return bar
