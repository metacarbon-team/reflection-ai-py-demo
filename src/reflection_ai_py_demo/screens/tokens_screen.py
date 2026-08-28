"""The palette and scales, rendered as swatches."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer

from ..ui import HStack, Text, VStack, glyph, header


class TokensScreen(Screen[None]):
    """The palette and scales, rendered as swatches.

    Worth a screen of its own: a token sheet is the fastest way to settle an
    argument about whether two greys are actually different.
    """

    BINDINGS = [Binding("escape", "app.pop_screen", "back")]

    DEFAULT_CSS = """
    TokensScreen .-swatch { width: 6; }
    /* Wide enough for the longest role name, so nothing wraps onto a second
       row and breaks the alignment of the column. */
    TokensScreen .-role { width: 16; }
    """

    def compose(self) -> ComposeResult:
        yield from header("Reflection AI", "Design tokens")
        yield Text("Semantic roles, resolved by the active theme.", variant="caption")
        yield Text(" ")
        yield VerticalScroll(id="token-sheet")
        yield Footer()

    def on_mount(self) -> None:
        self._paint()
        # The sheet prints hex values, so it has to be rebuilt when the active
        # theme changes - a resume hook is not enough, since the screen never
        # leaves the stack during a toggle.
        self.watch(self.app, "theme", lambda _: self._paint(), init=False)

    def _paint(self) -> None:
        from ..themes import SCHEMES
        from ..ui.theme import ROLES

        scheme = SCHEMES.get(self.app.theme, SCHEMES["reflection-dark"])
        sheet = self.query_one("#token-sheet", VerticalScroll)
        sheet.remove_children()

        rows: list[HStack] = []
        for role in ROLES:
            swatch = Text(glyph("bar_full") * 4, classes="-swatch")
            swatch.styles.color = scheme.hex(role)
            rows.append(
                HStack(
                    swatch,
                    Text(role.replace("_", "-"), classes="-role"),
                    Text(scheme.hex(role), variant="caption"),
                )
            )
        sheet.mount(VStack(*rows))

    def on_screen_resume(self) -> None:
        self._paint()
