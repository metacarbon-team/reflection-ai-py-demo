"""Patterns - components composed from other components.

The distinction is mechanical, not a matter of taste: if a class has a
`compose()` that yields our own elements, it is a pattern. That is what makes
the hierarchy checkable rather than a naming convention, and a test enforces it.
"""

from __future__ import annotations

from .composer import Composer
from .header import header
from .list_row import ListRow
from .thinking import Thinking

__all__ = ["Composer", "ListRow", "Thinking", "header"]
