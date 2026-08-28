"""Typed, toned text - the type scale made concrete."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from ..tokens import TYPOGRAPHY, TextRole
from .base import Tone


class Text(Static):
    """Typed, toned text.

    ``variant`` selects a role from the type scale (weight + casing, the only
    levers a terminal offers); ``tone`` selects a semantic colour role.
    """

    DEFAULT_CSS = """
    Text {
        width: auto;
        height: auto;
    }
    Text.-title { color: $text-bright; text-style: bold; }
    Text.-heading { color: $text-bright; text-style: bold; }
    Text.-label { color: $text-muted; }
    Text.-body { color: $text; }
    Text.-caption { color: $text-muted; }
    Text.-code { color: $text; background: $bg-subtle; }

    Text.-tone-text { color: $text; }
    Text.-tone-text-bright { color: $text-bright; }
    Text.-tone-text-muted { color: $text-muted; }
    Text.-tone-text-subtle { color: $text-subtle; }
    Text.-tone-accent { color: $accent; }
    Text.-tone-accent-strong { color: $accent-strong; }
    Text.-tone-success { color: $success; }
    Text.-tone-warning { color: $warning; }
    Text.-tone-danger { color: $danger; }
    Text.-tone-info { color: $info; }
    """

    def __init__(
        self,
        content: str = "",
        *,
        variant: TextRole = "body",
        tone: Tone | None = None,
        **kwargs: Any,
    ) -> None:
        style = TYPOGRAPHY[variant]
        rendered = content.upper() if style.transform == "upper" else content
        super().__init__(rendered, **kwargs)
        self.add_class(f"-{variant}")
        if tone is not None:
            # A tone always wins over the variant's default colour.
            self.add_class(f"-tone-{tone.replace('_', '-')}")
