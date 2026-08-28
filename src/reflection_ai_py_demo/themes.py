"""Themes the app registers at startup.

A top-level module, so the answer to "which themes does this app ship?" is one
file rather than a detail buried in the UI package.

The themes themselves are assembled in `ui/theme.py` from `ui/tokens.py`. That
split is deliberate: `ui/` is the design system and knows nothing about this
application, while this module is the application choosing what to register.
"""

from __future__ import annotations

from typing import Final

from textual.theme import Theme as TextualTheme

from .ui.theme import DARK, LIGHT, Scheme, textual_theme

#: Name -> Textual theme, in the order `ctrl+t` cycles them.
BUILTIN_THEMES: Final[dict[str, TextualTheme]] = {
    "reflection-dark": textual_theme("reflection-dark", DARK, dark=True),
    "reflection-light": textual_theme("reflection-light", LIGHT, dark=False),
}

#: The same schemes in Python form, for the handful of places that compute a
#: colour outside CSS (the token sheet prints hex values).
SCHEMES: Final[dict[str, Scheme]] = {
    "reflection-dark": DARK,
    "reflection-light": LIGHT,
}

DEFAULT_THEME: Final = "reflection-dark"
