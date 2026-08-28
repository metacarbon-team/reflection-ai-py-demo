"""The footer affordance: which keys do what, here."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.widgets import Static


class KeyHintBar(Static):
    """The footer affordance: which keys do what, here."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {"keyhint--key", "keyhint--label"}
    """
    | Class | Description |
    | :- | :- |
    | `keyhint--key` | The key name. |
    | `keyhint--label` | What the key does. |
    """

    DEFAULT_CSS = """
    KeyHintBar {
        width: 1fr;
        height: 1;

        & > .keyhint--key { color: $accent-strong; }
        & > .keyhint--label { color: $text-muted; }
    }
    """

    def __init__(self, hints: list[tuple[str, str]], **kwargs: Any) -> None:
        super().__init__("", **kwargs)
        self._hints = hints

    def render(self) -> RenderResult:
        key_style = self.get_component_rich_style("keyhint--key")
        label_style = self.get_component_rich_style("keyhint--label")

        text = RichText(no_wrap=True, overflow="ellipsis")
        for index, (key, label) in enumerate(self._hints):
            if index:
                text.append("   ")
            text.append(key, style=key_style)
            text.append(f" {label}", style=label_style)
        return text
