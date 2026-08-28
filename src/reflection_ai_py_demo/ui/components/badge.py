"""A status chip. Six intents, two variants."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from ..primitives import Intent, Variant


class Badge(Static):
    """A status chip. Six intents, two variants."""

    DEFAULT_CSS = """
    Badge { width: auto; height: 1; padding: 0 $space-xs; }

    Badge.-subtle.-neutral { color: $text-muted; background: $bg-subtle; }
    Badge.-subtle.-accent  { color: $accent; background: $bg-subtle; }
    Badge.-subtle.-success { color: $success; background: $bg-subtle; }
    Badge.-subtle.-warning { color: $warning; background: $bg-subtle; }
    Badge.-subtle.-danger  { color: $danger; background: $bg-subtle; }
    Badge.-subtle.-info    { color: $info; background: $bg-subtle; }

    Badge.-solid { color: $text-inverse; text-style: bold; }
    Badge.-solid.-neutral { background: $text-muted; }
    Badge.-solid.-accent  { background: $accent; }
    Badge.-solid.-success { background: $success; }
    Badge.-solid.-warning { background: $warning; }
    Badge.-solid.-danger  { background: $danger; }
    Badge.-solid.-info    { background: $info; }
    """

    def __init__(
        self,
        label: str,
        *,
        intent: Intent = "neutral",
        variant: Variant = "subtle",
        **kwargs: Any,
    ) -> None:
        super().__init__(label, **kwargs)
        self.add_class(f"-{variant}", f"-{intent}")
