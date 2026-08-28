"""The showcase application shell.

Registers the themes, sets the global chrome, and pushes the home screen. All
the interesting decisions live in :mod:`.ui.tokens` and :mod:`.ui.theme` - this
file is deliberately thin.
"""

from __future__ import annotations

import os
from pathlib import Path

from textual.app import App
from textual.binding import Binding

from . import ui
from .screens import HomeScreen
from .themes import BUILTIN_THEMES, DEFAULT_THEME


class ShowcaseApp(App[None]):
    """Reflection AI's TUI design showcase."""

    CSS_PATH = Path(__file__).parent / "app.tcss"
    TITLE = "Reflection AI"
    SUB_TITLE = "design showcase"

    BINDINGS = [
        Binding("ctrl+t", "cycle_theme", "theme", priority=True),
        Binding("ctrl+c", "quit", "quit", priority=True, show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        # Themes must be registered before the stylesheet is parsed: the CSS
        # below refers to `$bg` and friends, which only exist once a theme
        # publishing those variables is the active one.
        for theme in BUILTIN_THEMES.values():
            self.register_theme(theme)
        self.theme = DEFAULT_THEME

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def action_cycle_theme(self) -> None:
        """Flip between the two schemes, so a design is judged in both.

        Nothing else has to happen: every component reads its colours through
        component classes, which Textual re-resolves on the next repaint.
        """
        names = list(BUILTIN_THEMES)
        current = names.index(self.theme) if self.theme in names else 0
        self.theme = names[(current + 1) % len(names)]


def main() -> None:
    """Console-script entry point."""
    # A console the terminal cannot be trusted with gets the ASCII glyph set.
    ui.set_unicode(os.environ.get("REFLECTION_ASCII") != "1")
    ShowcaseApp().run()


if __name__ == "__main__":
    main()
