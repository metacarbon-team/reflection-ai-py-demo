"""Design tokens - the single source of truth for every visual decision.

Rules of the system:

1. Components NEVER hardcode a colour, a spacing value, or a glyph. They read
   from the theme (see :mod:`.theme`), which is assembled from these tokens.
2. Tokens are *semantic* (``text_muted``) rather than literal (``gray``), so a
   theme can be re-skinned without touching a single component.
3. The terminal is the constraint: space is measured in whole cells, and a
   glyph must advance exactly one cell. Colour is truecolor - Textual degrades
   it for lower-capability terminals via `App.ansi_color`, so this file does
   not carry a second mapping of its own.

This is a design-showcase scaffold: the tokens exist to be looked at, argued
about, and changed. Everything downstream is wiring.
"""

from __future__ import annotations

from typing import Final, Literal, NamedTuple

# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------


class ColorToken(NamedTuple):
    """A single colour value.

    Truecolor only, deliberately. Every token used to carry a 16-colour ANSI
    name beside the hex, on the theory that we owed low-colour terminals a
    fallback - but nothing ever read it, because Textual already handles this:
    `App.ansi_color` plus its `ANSIToTruecolor` filter degrade colours for the
    terminal at hand. A second, hand-maintained mapping was a parallel
    implementation that could only drift from the real one.
    """

    hex: str


def _color(hex_value: str) -> ColorToken:
    return ColorToken(hex_value)


class Palette(NamedTuple):
    """Raw palette.

    Nothing outside the theme should reference these names - they exist only to
    be mapped onto semantic roles.
    """

    # Neutrals - the spine of a terminal UI.
    ink: ColorToken
    slate_900: ColorToken
    slate_700: ColorToken
    slate_500: ColorToken
    slate_400: ColorToken
    slate_300: ColorToken
    slate_200: ColorToken
    slate_100: ColorToken
    paper: ColorToken

    # Brand - Reflection AI's accent ramp.
    brand: ColorToken
    brand_fill: ColorToken
    brand_bright: ColorToken
    brand_dim: ColorToken

    # Feedback.
    success: ColorToken
    warning: ColorToken
    danger: ColorToken
    info: ColorToken


#: Sampled from screenshots of the existing Reflection CLI (Figma "Workflow",
#: node 52:1393). The hexes below are measured pixel values, not approximations
#: - the surfaces and the accent green are exact.
#:
#: The one deliberate departure is the text ramp. The CLI's body grey measures
#: #7d7d7d, which is 3.40:1 against the #292c33 background - under the 4.5:1
#: needed to read comfortably, and it showed in the screenshots as washed out.
#: `slate_100` is lifted to #c2c6cd (8.1:1) so body copy is legible, with the
#: original grey kept below as the MUTED step where low contrast is the intent.
#: Matching a palette should not mean inheriting its legibility problems.
PALETTE: Final = Palette(
    # Terminal chrome. `ink` is the surrounding page, `slate_900` the terminal
    # body - the CLI is slightly lighter than its own frame, not darker.
    ink=_color("#1e1e1e"),
    slate_900=_color("#292c33"),
    slate_700=_color("#3a3d45"),
    slate_500=_color("#666769"),
    slate_400=_color("#7d7d7d"),
    slate_300=_color("#949599"),
    # Between `slate_100` and `paper`. Exists so the light scheme can have a
    # RAISED surface: `slate_300` is dark enough to be a border, and using it
    # as a background made "raised" mean the opposite of what it means on dark
    # (it sat *below* `bg_subtle` in luminance) while dropping body text to
    # 3.63:1. See the `bg_raised` note in `theme.py`.
    slate_200=_color("#dadde2"),
    slate_100=_color("#c2c6cd"),
    paper=_color("#ffffff"),
    # The selection green, straight off the highlighted row.
    #
    # `brand` is the measured #688663 and is what text sits ON in the CLI's
    # selected row. At that exact value white text reads 4.05:1 - just under
    # the 4.5:1 threshold - so `brand_fill` below is the same hue taken down
    # ~4% lightness, which buys legible white text while still reading as a
    # solid block against the terminal body. `brand` itself is unchanged, so
    # anywhere the green is used as a FOREGROUND still matches the source.
    brand=_color("#688663"),
    brand_fill=_color("#5f7a5a"),
    brand_bright=_color("#84a081"),
    brand_dim=_color("#4f6a4c"),
    # Feedback. `warning` is the amber the CLI uses for tool names, which is
    # the only strong warm colour on screen; `success` leans brighter than the
    # brand green so a passing state stays distinct from a selected one.
    success=_color("#84a081"),
    warning=_color("#e9c77f"),
    danger=_color("#d17b72"),
    info=_color("#6886d1"),
)


class OnLight(NamedTuple):
    """Feedback colours darkened for use on a light background.

    The CLI is dark-only, so these have no counterpart to match against. The
    dark palette's feedback hues all fall under 4.5:1 on white - amber is the
    worst at 1.62:1, effectively invisible - so reusing them would make the
    light scheme unreadable. Each entry below is the same hue pushed down in
    lightness until it clears 4.5:1, which keeps the two schemes recognisably
    related without pretending the dark values work on paper.
    """

    success: ColorToken
    warning: ColorToken
    danger: ColorToken
    info: ColorToken
    accent: ColorToken


ON_LIGHT: Final = OnLight(
    success=_color("#3f6b3c"),
    warning=_color("#7a5a12"),
    danger=_color("#a33228"),
    info=_color("#2f4fa8"),
    accent=_color("#3f5a3c"),
)


# --------------------------------------------------------------------------
# Space
# --------------------------------------------------------------------------

#: Spacing scale, in terminal cells. Deliberately tiny: a terminal has no
#: sub-pixel room, so every step must be a whole cell and earn its place.
#:
#: Published to CSS as `$space-xs` .. `$space-lg` by `theme.css_variables`, so a
#: stylesheet writes `padding: 0 $space-xs` rather than a bare number. This
#: table used to exist without a consumer while every stylesheet hardcoded its
#: own numbers - two sources of truth that agreed only by luck.
SPACE: Final[dict[str, int]] = {
    "none": 0,
    # Hairline gap - the default gutter between inline items.
    "xs": 1,
    # Standard block padding.
    "sm": 2,
    # Generous padding for hero surfaces.
    "md": 3,
    "lg": 4,
}

SpaceToken = Literal["none", "xs", "sm", "md", "lg"]


# --------------------------------------------------------------------------
# Borders
# --------------------------------------------------------------------------

#: Border styles, named by intent rather than by glyph, so an element asks for
#: ``subtle`` and the theme decides which box-drawing set that means.
#:
#: Published to CSS as `$border-subtle` .. `$border-ascii`, each carrying the
#: style AND the colour, because Textual's parser will not accept a variable in
#: the style slot alone - `border: $border-subtle` works, `border: $style $c`
#: does not. Values here are Textual border names.
BORDERS: Final[dict[str, str]] = {
    "none": "none",
    "subtle": "round",
    "solid": "solid",
    "strong": "heavy",
    "emphasis": "double",
    "ascii": "ascii",
}

BorderToken = Literal["none", "subtle", "solid", "strong", "emphasis", "ascii"]


# --------------------------------------------------------------------------
# Glyphs
# --------------------------------------------------------------------------

#: Glyph inventory, restricted to characters monospace fonts actually ship.
#:
#: Every glyph here advances exactly one cell. The heavier dingbats (U+2714,
#: U+2716, U+2139) are deliberately absent: no mono font we tested contains
#: them, so both Figma and the terminal substitute a proportional fallback that
#: occupies ~1.7 cells and shears every following column. The entries below are
#: the single-cell equivalents.
GLYPHS_UNICODE: Final[dict[str, str]] = {
    "bullet": "•",
    "arrow_right": "→",
    "chevron": "❯",
    "check": "✓",
    "cross": "×",
    "warning": "▲",
    "info": "i",
    "dot": "●",
    "ellipsis": "…",
    "line_h": "─",
    "caret": "▌",
    "bar_full": "█",
    "bar_empty": "░",
}

#: ASCII fallback, for consoles that cannot be trusted with box drawing.
GLYPHS_ASCII: Final[dict[str, str]] = {
    "bullet": "*",
    "arrow_right": "->",
    "chevron": ">",
    "check": "v",
    "cross": "x",
    "warning": "!",
    "info": "i",
    "dot": "o",
    "ellipsis": "...",
    "line_h": "-",
    "caret": "|",
    "bar_full": "#",
    "bar_empty": ".",
}

GlyphName = Literal[
    "bullet",
    "arrow_right",
    "chevron",
    "check",
    "cross",
    "warning",
    "info",
    "dot",
    "ellipsis",
    "line_h",
    "caret",
    "bar_full",
    "bar_empty",
]


# --------------------------------------------------------------------------
# Motion
# --------------------------------------------------------------------------

#: Tick intervals in seconds. Textual drives animation with ``set_interval``,
#: which takes seconds rather than milliseconds.
#: Note these are not one continuous scale. A spinner's interval is seconds per
#: FRAME, while the shimmer's is seconds per CELL - the crest advances one cell
#: per tick, so a long label multiplies the cost of a slow value. Comparing the
#: two numbers directly is meaningless; each is tuned against what it drives.
DURATION: Final[dict[str, float]] = {
    # Snappy - spinners and carets.
    "fast": 0.08,
    # Deliberate - progress and pulses.
    "normal": 0.12,
    # Ambient - background shimmer, per cell travelled.
    #
    # At 0.32 a 22-character label took ~9s per pass, which read as stalled
    # rather than ambient. 0.06 crosses the same label in about 1.7s: alive,
    # but still a sweep rather than a strobe.
    "shimmer": 0.06,
}

#: Frame sets a spinner advances through.
#:
#: Two sets, for the same reason the glyphs have two: braille and block frames
#: are invisible on a console that cannot render them, and a spinner that shows
#: nothing is worse than one that shows `-\|/`. Resolved through
#: `frames()` in `components.base`, never indexed directly.
FRAMES: Final[dict[str, tuple[str, ...]]] = {
    "dots": (
        "⠋",
        "⠙",
        "⠹",
        "⠸",
        "⠼",
        "⠴",
        "⠦",
        "⠧",
        "⠇",
        "⠏",
    ),
    "line": ("-", "\\", "|", "/"),
    "pulse": ("·", "•", "●", "•"),
    "bar": (
        "▁",
        "▃",
        "▄",
        "▅",
        "▆",
        "▇",
        "▆",
        "▅",
        "▄",
        "▃",
    ),
}

#: ASCII counterparts. Each keeps the *character* of its unicode twin - `dots`
#: still reads as a rotation, `bar` still as a rising and falling level - so the
#: fallback is a downgrade in fidelity, not in meaning.
FRAMES_ASCII: Final[dict[str, tuple[str, ...]]] = {
    "dots": ("-", "\\", "|", "/"),
    "line": ("-", "\\", "|", "/"),
    "pulse": (".", "o", "O", "o"),
    "bar": ("_", ".", "-", "=", "*", "#", "*", "=", "-", "."),
}

SpinnerName = Literal["dots", "line", "pulse", "bar"]


class Shimmer(NamedTuple):
    """A highlight that travels along a string, character by character.

    A terminal cannot do a gradient, so the effect is built from a small ramp of
    tones applied per character. The ramp is deliberately NEUTRAL-ONLY: a
    shimmer is a lightness sweep, not a change of hue. Introducing the accent
    would make it read as a state change rather than a highlight, and would
    collide with the accent's actual meaning elsewhere in the system.

    The TROUGH is the label's resting colour, not its dimmest possible one.
    That distinction matters more than it sounds: the crest covers only a few
    characters, so at any instant the great majority of the string sits at the
    last ramp step. Letting that step fall to a near-background tone leaves the
    label mostly unreadable, flickering into legibility only as the crest
    passes. A shimmer BRIGHTENS text above its resting state; it must never dim
    it below what the same text would be if it were not animated at all.
    """

    #: Tone ramp from crest to trough. Index 0 is the brightest character.
    ramp: tuple[str, ...]
    #: Characters covered by the falloff on each side of the crest.
    width: int
    #: Cells the crest advances per tick.
    step: int
    #: Ticks to hold before the crest re-enters from the left.
    tail_pause: int


SHIMMER: Final = Shimmer(
    # Crest -> trough, using only roles the system already has.
    #
    # The trough is `text_muted`: the shimmer's resting tone. It reads as
    # secondary copy - which is what an ambient "working" label IS - while the
    # crest lifts a few characters to full brightness as it passes.
    #
    # `text_subtle` is deliberately absent. It measures 1.29:1 on the dark
    # scheme, and because the crest only covers a few cells it was previously
    # applied to ~19 of 22 characters, leaving the label all but invisible.
    ramp=("text_bright", "text", "text_muted", "text_muted"),
    width=3,
    step=1,
    tail_pause=6,
)


# --------------------------------------------------------------------------
# Typography
# --------------------------------------------------------------------------


class TypeStyle(NamedTuple):
    """A terminal has exactly one font size.

    "Typography" here therefore means weight, casing, and dimming - the only
    levers the medium actually offers. Only `transform` lives here: casing has
    to be applied to the string before it is rendered, so Python must know it.
    Weight and colour are CSS (`text-style: bold`, `color: $text-bright`) and
    stay there - this table carried a `bold` flag for a while that nothing read,
    a second opinion about boldness that the stylesheet always overruled.
    """

    transform: Literal["none", "upper"]


TYPOGRAPHY: Final[dict[str, TypeStyle]] = {
    "title": TypeStyle(transform="none"),
    "heading": TypeStyle(transform="none"),
    "label": TypeStyle(transform="upper"),
    "body": TypeStyle(transform="none"),
    "caption": TypeStyle(transform="none"),
    "code": TypeStyle(transform="none"),
}

TextRole = Literal["title", "heading", "label", "body", "caption", "code"]
