"""A selectable row: marker, label, and a dimmed hint.

Composed from `HStack` + three `Text`s, which is why it lives here rather than
among the components: it has no drawing of its own, only an arrangement.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import ListItem

from ..primitives import HStack, Text, glyph


class ListRow(ListItem):
    """One selectable row: a marker, a name, and a dimmed summary.

    The selected state is the whole reason this class exists rather than a bare
    ``ListItem``. Three signals carry it, deliberately redundantly:

    * a chevron in a gutter reserved on every row, so nothing shifts sideways
      as the cursor moves;
    * a solid accent fill across the full row;
    * the label in bold, in the inverse tone, sitting on that fill.

    This mirrors how the existing Reflection CLI draws its own menus. The
    colour alone would not be enough: a terminal restricted to 16 colours
    renders `accent` and `text` closer together than a designer expects, and a
    reviewer reading over someone's shoulder loses a pure-colour cue entirely.
    The marker is what survives both.

    The child ``Text`` elements carry their own colours from the type scale, so
    a background on the row is not inherited by them - each tone that must
    change on selection is restated below. That is the bug this styling fixes:
    without it the highlighted row is pixel-identical to every other row, and
    the arrow keys appear to do nothing.
    """

    DEFAULT_CSS = """
    ListRow { padding: 0 $space-xs; background: transparent; }
    ListRow > HStack { width: 1fr; }
    /* Gutter is always present; only its glyph changes, so rows never shift. */
    ListRow .-marker { width: 2; color: $text-subtle; }
    ListRow .-name { width: 22; }

    /* The CLI fills the selected row solid and sets the label in white bold,
       leaving the chevron outside the fill. Matching that here: the name and
       summary sit ON the accent, so both take the inverse tone. */
    ListRow.-selected .-marker { color: $selection-fg; }
    ListRow.-selected .-name { color: $selection-fg; text-style: bold; }
    ListRow.-selected .-summary { color: $selection-fg; }
    """

    def __init__(self, item_id: str, name: str, summary: str) -> None:
        super().__init__()
        self.item_id = item_id
        # `_label`, not `_name`: Widget already defines `_name` as `str | None`,
        # and shadowing it with a `str` is both a type error and a latent bug.
        self._label = name
        self._summary = summary

    def compose(self) -> ComposeResult:
        yield HStack(
            Text(" ", classes="-marker"),
            Text(self._label, classes="-name"),
            Text(self._summary, variant="caption", classes="-summary"),
        )

    def watch_highlighted(self, value: bool) -> None:
        """Textual flips this as the cursor moves; translate it to our state.

        The parameter must stay named `value` to match `ListItem`; renaming it
        breaks callers that pass it by keyword.
        """
        self.set_class(value, "-selected")
        # `query(Text)` rather than `query_one`: the watcher can fire before
        # compose has run, and typing the query gives us `.update()`.
        for marker in self.query(Text).filter(".-marker"):
            marker.update(glyph("chevron") if value else " ")
