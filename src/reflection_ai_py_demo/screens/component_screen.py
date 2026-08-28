"""A single component, previewed on its own."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer

from ..gallery.registry import BY_ID
from ..ui import Badge, HStack, Text, VStack, header


class ComponentScreen(Screen[None]):
    """A single component, previewed on its own."""

    BINDINGS = [Binding("escape", "app.pop_screen", "back")]

    def __init__(self, entry_id: str) -> None:
        super().__init__()
        self.entry = BY_ID[entry_id]

    def compose(self) -> ComposeResult:
        entry = self.entry
        yield from header("Reflection AI", "Component library", entry.name)
        yield HStack(
            Text(entry.name, variant="heading"),
            Badge(entry.group),
        )
        yield Text(entry.summary, variant="caption")
        yield Text(" ")
        yield VerticalScroll(VStack(*entry.render()), id="preview")
        yield Footer()
