"""Pick a flow to step through."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, ListView

from ..gallery import flows as flow_data
from ..ui import ListRow, Text, header


class FlowsScreen(Screen[None]):
    """Pick a flow to step through."""

    BINDINGS = [Binding("escape", "app.pop_screen", "back")]

    def compose(self) -> ComposeResult:
        yield from header("Reflection AI", "Prototype flows")
        yield Text("Scripted sequences - step them at your own pace.", variant="caption")
        yield Text(" ")
        yield ListView(
            *(ListRow(f.id, f.name, f.summary) for f in flow_data.FLOWS),
            id="flows-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        from .flow_screen import FlowScreen

        target = getattr(event.item, "item_id", None)
        if target in flow_data.BY_ID:
            self.app.push_screen(FlowScreen(target))
