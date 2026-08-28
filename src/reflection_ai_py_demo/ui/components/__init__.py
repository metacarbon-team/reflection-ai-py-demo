"""Components - self-contained units of meaning.

Each one draws itself and stands alone: a `Badge` needs no other component to
be useful. Anything that composes our own components belongs in `patterns/`.
"""

from __future__ import annotations

from .badge import Badge
from .key_hints import KeyHintBar
from .progress_bar import ProgressBar
from .shimmer import Shimmer
from .spinner import Spinner
from .status_line import StatusLine

__all__ = [
    "Badge",
    "KeyHintBar",
    "ProgressBar",
    "Shimmer",
    "Spinner",
    "StatusLine",
]
