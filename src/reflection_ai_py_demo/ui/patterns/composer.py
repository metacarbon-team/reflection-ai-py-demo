"""The prompt input: a chevron and a real text field in one channel."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Static

from ..primitives import glyph


class _ComposerInput(Input):
    """The prompt input.

    Subclasses stock `Input`, so editing, the cursor, selection, history and
    the `Changed` / `Submitted` messages all come from Textual - we supply only
    the appearance. See CONTRACT.md: Textual owns behaviour, we own looks.

    This replaced a `Static` mock that could not be typed into. The mock was
    defensible for a pure look-review, but it meant the component could never
    become the real thing, and it reimplemented a widget Textual already ships.
    """

    DEFAULT_CSS = """
    /* A filled channel with rules down each side - no top or bottom.

       We do NOT use Input's `compact` mode, tempting as it looks: it applies
       `border: none !important`, which no rule of ours can override, so the
       side rules would be unreachable. Instead we restate height and border
       ourselves and leave `compact` off.

       The fill is `$input-bg`, which resolves in opposite directions per
       scheme: LIGHTER than the page on dark (as in the reference), and darker
       on light, where nothing can be lighter than paper. */
    _ComposerInput {
        width: 1fr;
        height: 1;
        background: $input-bg;
        color: $text;
        /* `$border-strong`, not `$border`: on the dark scheme `$border` and
           `$input-bg` are the same value, so a plain border would vanish into
           its own fill. */
        border-left: solid $border-strong;
        border-right: solid $border-strong;
        padding: 0 0 0 0;
    }
    /* Input ships `:focus` rules of its own; ours must beat them. */
    _ComposerInput:focus {
        background: $input-bg;
        background-tint: $input-bg 0%;
    }
    _ComposerInput > .input--placeholder {
        color: $input-placeholder;
    }
    _ComposerInput > .input--cursor {
        background: $accent;
        color: $text-inverse;
    }
    """

    def __init__(
        self,
        value: str = "",
        *,
        placeholder: str = "Ask anything",
        focused: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            placeholder=placeholder,
            **kwargs,
        )
        # A showcase convenience, not part of the element's state: the gallery
        # renders several composers side by side and needs to show the focused
        # treatment without any of them actually holding terminal focus. Real
        # focus still works normally - this only asks for it on mount.
        self._autofocus = focused

    def on_mount(self) -> None:
        # Input's own stylesheet sets `border: tall`, and a widget's
        # DEFAULT_CSS is auto-scoped to its DESCENDANTS - so a `_ComposerInput`
        # rule in this file can never target the widget itself and clear it.
        # Setting the style directly is the reliable way to win, and it is far
        # clearer than escalating a selector-specificity fight in CSS.
        self.styles.border = ("none", "transparent")
        if self._autofocus:
            self.focus()


class Composer(Horizontal):
    """The prompt input: a chevron and a real text field in one channel.

    Behaviour comes entirely from the stock `Input` inside it - editing, the
    cursor, selection, history - so this class only owns the appearance and
    re-exposes the contract. See CONTRACT.md.

    The chevron is a sibling element rather than part of the value. Writing it
    into the text would mean offsetting every cursor position and selection
    range around it, and `Input` owns that maths.
    """

    DEFAULT_CSS = """
    /* The channel: a filled row with rules down each side, no top or bottom.
       `border-left`/`border-right` rather than `border: vkey` - vkey draws a
       thin half-cell glyph and reserves a blank row above and below. */
    Composer {
        width: 1fr;
        height: 1;
        background: $input-bg;
        /* `$border-strong`, not `$border`: on the dark scheme `$border` and
           `$input-bg` are the same value, so a plain border would vanish into
           its own fill. */
        border-left: solid $border-strong;
        border-right: solid $border-strong;
        padding: 0 $space-xs 0 $space-xs;
    }
    Composer.-focused {
        border-left: solid $focus-ring;
        border-right: solid $focus-ring;
    }
    Composer > .composer--marker {
        width: 2;
        height: 1;
        color: $accent;
        background: $input-bg;
    }
    """

    #: Re-exported so a parent can write `on_composer_changed` / `_submitted`
    #: without knowing there is an `Input` inside. The messages are posted by
    #: the inner element and bubble; `control` still points at the Input.
    Changed = Input.Changed
    Submitted = Input.Submitted

    def __init__(
        self,
        value: str = "",
        *,
        placeholder: str = "Ask anything",
        focused: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._input = _ComposerInput(value, placeholder=placeholder, focused=focused)
        if focused:
            self.add_class("-focused")

    def compose(self) -> ComposeResult:
        yield Static(glyph("chevron"), classes="composer--marker")
        yield self._input

    @property
    def value(self) -> str:
        """The current text. Settable, like `Input.value`."""
        return self._input.value

    @value.setter
    def value(self, new_value: str) -> None:
        self._input.value = new_value

    def focus(self, scroll_visible: bool = True) -> Composer:
        """Focus the field inside, not the container."""
        self._input.focus(scroll_visible)
        return self

    def on_descendant_focus(self) -> None:
        self.add_class("-focused")

    def on_descendant_blur(self) -> None:
        self.remove_class("-focused")
