"""Semantic colour roles, and the bridge onto Textual's theme system.

The role list below is the contract between design and code: a component may
only ask for a role, never for a palette entry. Adding a role is a design-system
decision; adding a hex value inside a component is a bug.

Textual resolves colour through CSS, so the bridge works in two directions:

* :func:`textual_theme` hands Textual its own ``Theme`` object, whose
  ``variables`` expose every role as a ``$token`` usable from CSS.
* :class:`Scheme` stays available in Python for the handful of places that
  need a hex outside CSS - the token sheet prints them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from textual.theme import Theme as TextualTheme

from .tokens import BORDERS, ON_LIGHT, PALETTE, SPACE, ColorToken

#: Every semantic colour role in the system.
ColorRole = Literal[
    # Surfaces
    "bg",
    "bg_subtle",
    "bg_raised",
    # Text - a neutral lightness ramp, brightest first.
    "text_bright",
    "text",
    "text_muted",
    "text_subtle",
    "text_inverse",
    # Accent
    "accent",
    "accent_muted",
    "accent_strong",
    # Feedback
    "success",
    "warning",
    "danger",
    "info",
    # Lines
    "border",
    "border_strong",
    "focus_ring",
    # Selection - the row under the cursor. A pair, because the fill and the
    # text on it have to be chosen together to stay legible.
    "selection_bg",
    "selection_fg",
    # Input - the composer's filled channel, and the placeholder resting on it.
    "input_bg",
    "input_placeholder",
]

#: Typed as the role literal, not `str`, so `scheme.hex(role)` typechecks
#: when iterating. A bare `tuple[str, ...]` silently defeats the very
#: contract `ColorRole` exists to enforce.
ROLES: Final[tuple[ColorRole, ...]] = (
    "bg",
    "bg_subtle",
    "bg_raised",
    "text_bright",
    "text",
    "text_muted",
    "text_subtle",
    "text_inverse",
    "accent",
    "accent_muted",
    "accent_strong",
    "success",
    "warning",
    "danger",
    "info",
    "border",
    "border_strong",
    "focus_ring",
    "selection_bg",
    "selection_fg",
    "input_bg",
    "input_placeholder",
)


@dataclass(frozen=True, slots=True)
class Scheme:
    """A full mapping of every semantic role onto a concrete colour."""

    bg: ColorToken
    bg_subtle: ColorToken
    bg_raised: ColorToken
    text_bright: ColorToken
    text: ColorToken
    text_muted: ColorToken
    text_subtle: ColorToken
    text_inverse: ColorToken
    accent: ColorToken
    accent_muted: ColorToken
    accent_strong: ColorToken
    success: ColorToken
    warning: ColorToken
    danger: ColorToken
    info: ColorToken
    border: ColorToken
    border_strong: ColorToken
    focus_ring: ColorToken
    selection_bg: ColorToken
    selection_fg: ColorToken
    input_bg: ColorToken
    input_placeholder: ColorToken

    def hex(self, role: ColorRole) -> str:
        """Resolve a role to a hex string."""
        return getattr(self, role).hex


#: The dark scheme is the one the CLI actually ships, so it is a match rather
#: than an interpretation. `bg` is the terminal body (#292c33), NOT the darker
#: page behind it - getting these the wrong way round is the easy mistake, and
#: it makes every panel look like it is floating on the wrong surface.
DARK: Final = Scheme(
    bg=PALETTE.slate_900,
    bg_subtle=PALETTE.ink,
    bg_raised=PALETTE.slate_700,
    text_bright=PALETTE.paper,
    text=PALETTE.slate_100,
    text_muted=PALETTE.slate_500,
    text_subtle=PALETTE.slate_700,
    text_inverse=PALETTE.ink,
    accent=PALETTE.brand,
    accent_muted=PALETTE.brand_dim,
    accent_strong=PALETTE.brand_bright,
    success=PALETTE.success,
    warning=PALETTE.warning,
    danger=PALETTE.danger,
    info=PALETTE.info,
    border=PALETTE.slate_700,
    border_strong=PALETTE.slate_500,
    focus_ring=PALETTE.brand,
    selection_bg=PALETTE.brand_fill,
    selection_fg=PALETTE.paper,
    input_bg=PALETTE.slate_700,
    input_placeholder=PALETTE.slate_400,
)

#: The light scheme inverts the neutral ramp: on light, the crest is the
#: DARKEST ink.
#:
#: The ramp is asymmetric with the dark scheme, and that is a property of paper
#: rather than a preference: there is far less usable range between white and a
#: still-readable grey than between near-black and white, so the light steps sit
#: closer together. Legibility beats resolution - a further step here would mean
#: text the reader cannot see.
#:
#: The feedback and accent roles come from `ON_LIGHT` rather than the main
#: palette: the CLI's own hues are tuned for a dark terminal and every one of
#: them falls below 4.5:1 on white. See `OnLight` for the reasoning.
LIGHT: Final = Scheme(
    bg=PALETTE.paper,
    bg_subtle=PALETTE.slate_100,
    # `bg_raised` must sit FURTHER from `bg` than `bg_subtle` does, in whichever
    # direction that scheme raises. On dark that means lighter; on light, darker
    # than paper but still lighter than `bg_subtle`. Using `slate_300` here once
    # inverted that and dropped body text to 3.63:1.
    bg_raised=PALETTE.slate_200,
    text_bright=PALETTE.ink,
    text=PALETTE.slate_700,
    text_muted=PALETTE.slate_500,
    text_subtle=PALETTE.slate_400,
    text_inverse=PALETTE.paper,
    accent=ON_LIGHT.accent,
    accent_muted=PALETTE.brand_dim,
    accent_strong=ON_LIGHT.success,
    success=ON_LIGHT.success,
    warning=ON_LIGHT.warning,
    danger=ON_LIGHT.danger,
    info=ON_LIGHT.info,
    border=PALETTE.slate_300,
    border_strong=PALETTE.slate_500,
    focus_ring=ON_LIGHT.accent,
    selection_bg=ON_LIGHT.accent,
    selection_fg=PALETTE.paper,
    input_bg=PALETTE.slate_100,
    input_placeholder=PALETTE.slate_500,
)


def css_variables(scheme: Scheme) -> dict[str, str]:
    """Expose every semantic role to CSS as a ``$role`` variable.

    This is what lets a stylesheet say ``color: $text-muted`` and stay honest -
    the value can only ever come from a token.
    """
    variables: dict[str, str] = {role.replace("_", "-"): scheme.hex(role) for role in ROLES}
    # Textual resolves a handful of built-in variables for its own widgets.
    # Point them at our roles so stock widgets inherit the system too.
    # Spacing, as whole terminal cells. A stylesheet writes `padding: 0 $space-xs`
    # so the scale has one home.
    variables |= {f"space-{name}": str(cells) for name, cells in SPACE.items()}

    # Borders carry style AND colour in one value: Textual's parser rejects a
    # variable in the style slot (`border: $style $colour` is a syntax error),
    # but accepts a variable holding the whole value.
    # Namespaced `rule-*`, NOT `border-*`: the colour roles already own
    # `$border` and `$border-strong`, and a `$border-strong` holding
    # "heavy #666769" silently breaks every `color: $border-strong` rule.
    variables |= {
        f"rule-{name}": (style if style == "none" else f"{style} {scheme.hex('border')}")
        for name, style in BORDERS.items()
    }
    variables |= {
        f"rule-{name}-strong": (style if style == "none" else f"{style} {scheme.hex('border_strong')}")
        for name, style in BORDERS.items()
    }
    variables |= {
        f"rule-{name}-focus": (style if style == "none" else f"{style} {scheme.hex('focus_ring')}")
        for name, style in BORDERS.items()
    }

    variables |= {
        "block-cursor-background": scheme.hex("accent"),
        "block-cursor-foreground": scheme.hex("text_inverse"),
        "block-cursor-text-style": "none",
        "footer-key-foreground": scheme.hex("accent_strong"),
        "footer-description-foreground": scheme.hex("text_muted"),
        "input-selection-background": scheme.hex("accent_muted"),
    }
    return variables


def textual_theme(name: str, scheme: Scheme, *, dark: bool) -> TextualTheme:
    """Build the Textual theme object the app registers at startup."""
    return TextualTheme(
        name=name,
        primary=scheme.hex("accent"),
        secondary=scheme.hex("accent_strong"),
        accent=scheme.hex("accent"),
        foreground=scheme.hex("text"),
        background=scheme.hex("bg"),
        surface=scheme.hex("bg_subtle"),
        panel=scheme.hex("bg_raised"),
        success=scheme.hex("success"),
        warning=scheme.hex("warning"),
        error=scheme.hex("danger"),
        dark=dark,
        variables=css_variables(scheme),
    )


# NOTE: the app-facing registry of themes lives in `reflection_ai_py_demo.themes`.
# This module builds schemes and converts them; choosing which ones an app
# registers is an application decision, not a design-system one.
