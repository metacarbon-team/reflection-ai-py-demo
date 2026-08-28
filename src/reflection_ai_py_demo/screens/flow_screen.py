"""One flow, one frame at a time."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer

from ..gallery import flows as flow_data
from ..ui import Text, header


class FlowScreen(Screen[None]):
    """One flow, one frame at a time."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "back"),
        Binding("right,space,n", "next_frame", "next"),
        Binding("left,p", "prev_frame", "prev"),
        Binding("r", "restart", "restart"),
    ]

    def __init__(self, flow_id: str) -> None:
        super().__init__()
        self.flow = flow_data.BY_ID[flow_id]
        self.index = 0

    def compose(self) -> ComposeResult:
        yield from header("Reflection AI", "Prototype flows", self.flow.name)
        yield Text("", id="flow-caption", variant="caption")
        yield Text(" ")
        yield VerticalScroll(id="flow-stage")
        yield Footer()

    def on_mount(self) -> None:
        self._paint()

    def _paint(self) -> None:
        frame = self.flow.frames[self.index]
        counter = f"[{self.index + 1}/{len(self.flow.frames)}]"

        caption = self.query_one("#flow-caption", Text)
        caption.update(f"{counter}  {frame.caption}")

        stage = self.query_one("#flow-stage", VerticalScroll)
        stage.remove_children()
        stage.mount_all(list(frame.build()))

    def action_next_frame(self) -> None:
        if self.index < len(self.flow.frames) - 1:
            self.index += 1
            self._paint()

    def action_prev_frame(self) -> None:
        if self.index > 0:
            self.index -= 1
            self._paint()

    def action_restart(self) -> None:
        self.index = 0
        self._paint()
