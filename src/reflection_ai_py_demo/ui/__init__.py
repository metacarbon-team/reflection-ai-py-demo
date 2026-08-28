"""The design system.

Three layers, ordered by composition. The rule that separates them is
mechanical rather than editorial:

* :mod:`.primitives` — draw directly, compose nothing of ours
* :mod:`.components` — self-contained units of meaning, still no composition
* :mod:`.patterns`   — arrange our own elements

Underneath sit :mod:`.tokens` (values) and :mod:`.theme` (semantic roles), which
every layer reads and none of them may bypass.

Everything is re-exported here, so a caller writes
``from ..ui import Badge, Composer`` without tracking which layer an element
currently lives in — moving one between layers stays a private refactor.
"""

from __future__ import annotations

from . import theme, tokens
from .components import Badge, KeyHintBar, ProgressBar, Shimmer, Spinner, StatusLine
from .patterns import Composer, ListRow, Thinking, header
from .primitives import (
    BorderName,
    Divider,
    Gap,
    HStack,
    Intent,
    Panel,
    Speed,
    Status,
    Surface,
    Text,
    Tone,
    Variant,
    VStack,
    frames,
    glyph,
    one_of,
    set_unicode,
)

__all__ = [
    "Badge",
    "BorderName",
    "Composer",
    "Divider",
    "Gap",
    "HStack",
    "Intent",
    "KeyHintBar",
    "ListRow",
    "Panel",
    "ProgressBar",
    "Shimmer",
    "Speed",
    "Spinner",
    "Status",
    "StatusLine",
    "Surface",
    "Text",
    "Thinking",
    "Tone",
    "VStack",
    "Variant",
    "frames",
    "glyph",
    "header",
    "one_of",
    "set_unicode",
    "theme",
    "tokens",
]
