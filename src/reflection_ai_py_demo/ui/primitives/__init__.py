"""Primitives - the bottom of the system.

Nothing here composes another element: these draw directly, and every
other layer is built from them. If a class has a `compose()` that yields our own
components, it belongs in `patterns/`, not here.

`base` sits at this level too - the glyph resolver and the shared prop
vocabulary are machinery every layer leans on.
"""

from __future__ import annotations

from .base import (
    BorderName,
    Gap,
    Intent,
    Speed,
    Status,
    Tone,
    Variant,
    frames,
    glyph,
    one_of,
    set_unicode,
)
from .box import Panel, Surface
from .rule import Divider
from .stack import HStack, VStack
from .text import Text

__all__ = [
    "BorderName",
    "Divider",
    "Gap",
    "HStack",
    "Intent",
    "Panel",
    "Speed",
    "Status",
    "Surface",
    "Text",
    "Tone",
    "VStack",
    "Variant",
    "frames",
    "glyph",
    "one_of",
    "set_unicode",
]
