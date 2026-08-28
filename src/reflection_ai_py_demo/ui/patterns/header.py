"""The breadcrumb every screen wears.

A pattern by the same rule as the rest of this layer: it composes our own
elements rather than drawing anything itself.
"""

from __future__ import annotations

from textual.app import ComposeResult

from ..primitives import Divider, HStack, Text


def header(title: str, *trail: str) -> ComposeResult:
    """The breadcrumb every screen wears, so the reviewer knows where they are."""
    crumbs: list[Text] = [Text(title, variant="title", tone="accent_strong")]
    for crumb in trail:
        crumbs.append(Text("/", tone="text_subtle"))
        crumbs.append(Text(crumb, variant="caption"))
    yield HStack(*crumbs)
    yield Divider()
