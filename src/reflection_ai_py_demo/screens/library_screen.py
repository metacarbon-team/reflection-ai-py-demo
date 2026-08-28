"""Browse every component in the system."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, ListView

from ..gallery.registry import BY_ID, REGISTRY
from ..ui import ListRow, Text, header


class LibraryScreen(Screen[None]):
    """Browse every component in the system."""

    BINDINGS = [Binding("escape", "app.pop_screen", "back")]

    def compose(self) -> ComposeResult:
        yield from header("Reflection AI", "Component library")
        yield Text(
            f"{len(REGISTRY)} components - up/down to browse, enter to preview",
            variant="caption",
        )
        yield Text(" ")
        yield ListView(
            *(ListRow(e.id, e.name, e.summary) for e in REGISTRY),
            id="library-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        from .component_screen import ComponentScreen

        target = getattr(event.item, "item_id", None)
        if target in BY_ID:
            self.app.push_screen(ComponentScreen(target))
