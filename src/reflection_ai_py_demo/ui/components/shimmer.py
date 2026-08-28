"""Text with a highlight travelling along it."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.widgets import Static

from ..primitives import Speed
from ..tokens import DURATION, SHIMMER


class Shimmer(Static):
    """Text with a highlight travelling along it, character by character.

    The ramp is a neutral lightness sweep - see the note on
    :data:`~.tokens.SHIMMER` for why it must never pick up the accent hue.

    The four ramp steps are component classes, so the sweep is restyleable from
    CSS and re-resolves on a theme change without this element watching for one.
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "shimmer--crest",
        "shimmer--near",
        "shimmer--far",
        "shimmer--rest",
    }
    """
    | Class | Description |
    | :- | :- |
    | `shimmer--crest` | The brightest character, under the highlight. |
    | `shimmer--near` | First falloff step. |
    | `shimmer--far` | Second falloff step. |
    | `shimmer--rest` | The trough - where most of the string sits. |
    """

    DEFAULT_CSS = """
    Shimmer {
        width: auto;
        height: 1;

        /* The trough is the label's RESTING tone, not its dimmest. The crest
           covers a few cells, so most of the string sits on `--rest`; letting
           it fall to a near-background tone makes the label unreadable
           between passes. A shimmer brightens; it must not dim. */
        & > .shimmer--crest { color: $text-bright; }
        & > .shimmer--near  { color: $text; }
        & > .shimmer--far   { color: $text-muted; }
        & > .shimmer--rest  { color: $text-muted; }
    }
    """

    #: Crest to trough. Index matches the falloff distance in `render`.
    _RAMP: ClassVar[tuple[str, ...]] = (
        "shimmer--crest",
        "shimmer--near",
        "shimmer--far",
        "shimmer--rest",
    )

    def __init__(self, content: str, *, speed: Speed = "shimmer", **kwargs: Any) -> None:
        super().__init__("", **kwargs)
        self._content = content
        self._interval = DURATION[speed]
        self._crest = 0

    def on_mount(self) -> None:
        self.set_interval(self._interval, self._advance)

    def _advance(self) -> None:
        span = len(self._content) + SHIMMER.tail_pause
        self._crest = (self._crest + SHIMMER.step) % span
        self.refresh()

    def render(self) -> RenderResult:
        text = RichText(no_wrap=True)
        for index, char in enumerate(self._content):
            # Beyond the falloff the character sits at the trough of the ramp.
            step = min(abs(index - self._crest), SHIMMER.width)
            part = self._RAMP[min(step, len(self._RAMP) - 1)]
            text.append(char, style=self.get_component_rich_style(part))
        return text
