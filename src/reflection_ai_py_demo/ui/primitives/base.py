"""Shared foundations for the component library.

Everything here is machinery the elements lean on rather than anything a screen
renders directly: the glyph resolver, the shared tone vocabulary, and the base
class for elements that build their own Rich text.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from ..tokens import FRAMES, FRAMES_ASCII, GLYPHS_ASCII, GLYPHS_UNICODE, GlyphName, SpinnerName

Tone = Literal[
    "text",
    "text_bright",
    "text_muted",
    "text_subtle",
    "accent",
    "accent_strong",
    "success",
    "warning",
    "danger",
    "info",
]

Intent = Literal["neutral", "accent", "success", "warning", "danger", "info"]

#: The shared prop vocabulary. Every component draws its prop types from here
#: rather than declaring `str`, so an editor offers the valid values and a
#: typo is caught before the app runs. A bare `str` prop turns a one-character
#: mistake into a `KeyError` at mount time with no hint of what was allowed -
#: the worst possible failure for a library someone is exploring by hand.
Status = Literal["success", "danger", "warning", "info", "pending"]
Variant = Literal["subtle", "solid"]
BorderName = Literal["none", "subtle", "solid", "strong", "emphasis", "ascii"]
Gap = Literal["none", "xs", "sm", "md", "lg"]
Speed = Literal["fast", "normal", "shimmer"]

#: Whether the terminal can be trusted with box drawing. Private, and reached
#: only through `set_unicode()` / `glyph()` below.
#:
#: This used to be a public module-level flag that the app assigned directly.
#: That worked while every component lived in one module and shared the single
#: global. Split across modules it would break silently: a component doing
#: `from .base import USE_UNICODE` binds its OWN copy at import time, and a
#: later write to the original never reaches it. The accessor pair keeps the
#: read late, so there is exactly one source of truth however the code is
#: arranged.
_use_unicode = True


def set_unicode(enabled: bool) -> None:
    """Choose the unicode or ASCII glyph set. Call before mounting the app."""
    global _use_unicode
    _use_unicode = enabled


def glyph(name: GlyphName) -> str:
    """Resolve a named glyph, honouring the unicode/ascii fallback."""
    return (GLYPHS_UNICODE if _use_unicode else GLYPHS_ASCII)[name]


def one_of(value: str, allowed: Iterable[str], prop: str) -> str:
    """Validate a prop value, naming the alternatives when it is wrong.

    The type annotations catch this at author time, but only if the editor or
    CI is running a typechecker. At runtime a bad value used to surface as a
    bare `KeyError: 'succes'` from deep inside a paint method - no mention of
    which prop, which component, or what was valid. For a library someone is
    exploring by hand, the error message IS the documentation.
    """
    options = tuple(allowed)
    if value not in options:
        raise ValueError(f"{prop}={value!r} is not valid. Expected one of: {', '.join(sorted(options))}")
    return value


def frames(name: SpinnerName) -> tuple[str, ...]:
    """Resolve a spinner frame set, honouring the unicode/ascii fallback."""
    return (FRAMES if _use_unicode else FRAMES_ASCII)[name]
