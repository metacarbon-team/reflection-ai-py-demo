"""Top level: pick a showcase mode."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, ListView

from ..gallery import flows as flow_data
from ..gallery.registry import REGISTRY
from ..ui import ListRow, Text, header


class HomeScreen(Screen[None]):
    """Top level: pick a showcase mode."""

    BINDINGS = [Binding("q", "app.quit", "quit")]

    def compose(self) -> ComposeResult:
        yield from header("Reflection AI")
        yield Text("A terminal design system built with Textual.", variant="caption")
        yield Text(" ")
        yield ListView(
            ListRow("library", "Component library", f"{len(REGISTRY)} components"),
            ListRow("flows", "Prototype flows", f"{len(flow_data.FLOWS)} flows"),
            ListRow("tokens", "Design tokens", "the values everything reads from"),
            id="home-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        from .flows_screen import FlowsScreen
        from .library_screen import LibraryScreen
        from .tokens_screen import TokensScreen

        target = getattr(event.item, "item_id", None)
        if target == "library":
            self.app.push_screen(LibraryScreen())
        elif target == "flows":
            self.app.push_screen(FlowsScreen())
        elif target == "tokens":
            self.app.push_screen(TokensScreen())
