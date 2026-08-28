---
name: add-element
description: Add a new element (primitive, component, or pattern) to the Reflection AI Textual design system in src/reflection_ai_py_demo/ui/, following the element contract. Use this whenever someone wants to add, create, build, or scaffold anything that renders in this library — a badge, a spinner, a transcript, a diff view, a tool-call row, an input, a panel, a list item, a progress indicator — and also when they want to move an existing element between layers, or ask "where should this live?". Reach for it even when the request is phrased as ordinary work ("we need a component for showing tool output", "add a diff renderer") rather than as a design-system task, because getting the layer and the contract right up front is much cheaper than retrofitting them.
---

# Adding an element to the design system

This library has a contract, and the contract exists because each rule in it was
paid for by a bug. Following it is not ceremony — it is how you avoid rediscovering
the same five problems.

Read [`src/reflection_ai_py_demo/ui/CONTRACT.md`](../../../src/reflection_ai_py_demo/ui/CONTRACT.md)
before writing code. This skill is the procedure; the contract is the reasoning.

## Before anything else: does it already exist?

Textual ships 42 widgets. The single most common mistake in this library was
reimplementing one of them — the composer was a fake `Static` for a while, and
had to be rebuilt on `Input` to get editing, cursor, selection and history that
were available the whole time.

```bash
.venv/Scripts/python -c "import textual.widgets as w; print(sorted(w.__all__))"
```

If something close exists, subclass or wrap it. You supply appearance; Textual
supplies behaviour. When you deliberately keep a custom implementation, say why
in the docstring — "we already wrote it" is not a reason, but "the stock one
draws with its own characters and we need tokenised glyphs" is.

## Step 1: Pick the layer

The rule is mechanical, which is what keeps the hierarchy honest:

| Layer | Test | Lives in |
| --- | --- | --- |
| **primitive** | draws directly, composes nothing of ours | `ui/primitives/` |
| **component** | self-contained unit of meaning, still draws itself | `ui/components/` |
| **pattern** | arranges our elements — a `compose()`, or a helper that yields them | `ui/patterns/` |

Ask: *does it yield our own elements?* If yes it is a pattern, regardless of how
simple it looks. `header` is eight lines and still a pattern.

Two tests enforce this in both directions, so guessing wrong fails loudly rather
than quietly eroding the structure.

## Step 2: Write the element

One file per element, named after it in snake_case. Follow the shape of a stock
Textual widget — read `ui/components/status_line.py` for the canonical example
in this codebase.

```python
"""One-line summary of what this is for."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text as RichText
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widgets import Static

from ..primitives import Status, glyph, one_of


class Example(Static):
    """What it is, and any decision a reader would otherwise wonder about."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {"example--mark", "example--label"}
    """
    | Class | Description |
    | :- | :- |
    | `example--mark` | The leading glyph. |
    | `example--label` | The text body. |
    """

    DEFAULT_CSS = """
    Example {
        width: 1fr;
        height: 1;

        & > .example--mark { color: $accent; }
        & > .example--label { color: $text; }
    }
    """

    label: reactive[str] = reactive("")

    def __init__(self, label: str = "", *, status: Status = "info", **kwargs: Any) -> None:
        super().__init__("", **kwargs)
        # Pass whatever holds the valid values - a tuple, or the mapping you
        # already keep (`one_of(status, self._MARKS, "status")` reads its keys).
        one_of(status, ("info", "success"), "status")
        self.set_reactive(Example.label, label)

    def watch_label(self) -> None:
        # Plain `refresh()` because this element is `height: 1` and cannot
        # resize. If yours is `height: auto`, a text change alters its size -
        # use `refresh(layout=True)` there or the row will not re-measure.
        self.refresh()

    def render(self) -> RenderResult:
        text = RichText(no_wrap=True)
        text.append(glyph("chevron"), style=self.get_component_rich_style("example--mark"))
        text.append(self.label, style=self.get_component_rich_style("example--label"))
        return text
```

The five things that matter, and why:

- **`COMPONENT_CLASSES` + `get_component_rich_style()`** — if you build a
  `rich.Text` by hand and read colours any other way, they bake in at paint time
  and a theme toggle leaves stale values on screen. This library once carried a
  whole base class (`_Painted`) to work around that; component classes deleted it.
- **`reactive` + `watch_*`** — a private `self._foo` cannot be updated, so callers
  are forced to destroy and rebuild the element. Use `set_reactive()` in
  `__init__` so watchers do not fire against a half-built widget.
- **Tokens for every value** — no hex, no literal glyph, no magic spacing. This
  includes drawing characters: a hardcoded `"█"` silently breaks the ASCII
  fallback, and the terminal that cannot render it is exactly the one that asked
  for ASCII.
- **`Literal` props, not `str`** — a bare `str` turns a one-character typo into a
  `KeyError` from deep inside a paint method. Use the vocabulary in
  `ui/primitives/base.py`, and add `one_of()` when a REPL user could plausibly
  get it wrong. Two of those overlap, so pick deliberately:
  **`Status`** (`success/danger/warning/info/pending`) is *what happened* — it
  carries a glyph and suits anything reporting an outcome. **`Intent`**
  (`neutral/accent/success/warning/danger/info`) is *how loud to be* — pure
  emphasis, no glyph, and it has `neutral`/`accent` for things that are not
  outcomes at all. If your element shows a mark next to a message, you want
  `Status`; if it only tints, you want `Intent`. They are not co-extensive, so
  expect an imperfect fit at the edges — a note/warning/error block takes
  `Status` for the glyph but inherits `success` and `pending` it has little use
  for. Handle them rather than leaving a hole; a narrower vocabulary is worth
  adding only if two elements would share it.
- **Variants are CSS classes** — never `if intent == "danger"` inside `render()`.

For interaction, post a `Message` rather than taking a callback: a nested
`@dataclass` carrying the element and what changed, with a `control` alias. That
is what lets an element be reused without knowing its parent.

## Step 3: Export it

Two files, or the element is invisible to callers:

1. The layer's `__init__.py` — add the import and the `__all__` entry.
2. `ui/__init__.py` — the facade. Callers write `from ..ui import Example`, so
   moving an element between layers later stays a private refactor.

Keep both `__all__` lists alphabetical; ruff enforces import order.

## Step 4: Add it to the gallery

An element nobody can see has not really been added. Add one `Entry` to
`REGISTRY` in `gallery/registry.py` with a preview factory:

```python
# at the top of registry.py, add it to the existing facade import
from ..ui import (
    ...,
    Example,
)


def _example_preview() -> Iterator[Widget]:
    yield Text("what varies here", variant="caption")
    yield Example("first state")
    yield Example("second state", status="success")


REGISTRY: Final[tuple[Entry, ...]] = (
    ...,
    Entry("example", "Example", "one-line summary", "Feedback", _example_preview),
)
```

The fourth argument is the gallery group, and `Group` in `registry.py` is a
closed `Literal["Primitives", "Feedback", "Motion", "Interactive"]`. Pick the one
that fits; if nothing does, widen the literal rather than forcing a bad fit — the
groups are how the library reads at a glance, not a fixed taxonomy.

A factory, not a list — elements are single-use, and mounting the same instance
on a second visit fails. Show the states a reviewer needs to compare, and keep
the preview short enough to fit one viewport.

## Step 5: Verify

```bash
.venv/Scripts/python -m pytest -q && .venv/Scripts/python -m ruff check . && uvx ty check src/
```

(`uv run` re-syncs the environment and is blocked in this checkout — call the
venv's interpreter directly. On macOS/Linux the path is `.venv/bin/python`.)

The suite already guards the contract: layer boundaries, no `compose()` below
`patterns/`, component classes on anything that renders text, no hardcoded
glyphs, ASCII-mode leaks, and readable contrast. If one fails, it is usually
telling you the layer is wrong rather than that the test is wrong.

Then check it in **both themes** — a passing suite does not mean it reads well,
and every colour resolves differently on light. If you have a terminal:

```bash
uv run reflection-ai-py-demo      # ctrl+t toggles the theme
```

(`uv run` is fine for launching the app interactively; it is only the verify
commands above that need the venv interpreter, because they run inside a
sandbox where the environment sync is blocked.)

Headless, drive the app and read the resolved styles. This runs as-is against
`StatusLine` — check it works, then swap in your own id, class and part names:

```python
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles are cp1252

from reflection_ai_py_demo.app import ShowcaseApp
from reflection_ai_py_demo import screens

ENTRY_ID = "status-line"  # the Entry id you added to REGISTRY
SELECTOR = "StatusLine"  # your class name
PARTS = ("statusline--mark", "statusline--message")


async def main():
    app = ShowcaseApp()
    async with app.run_test(size=(88, 26)) as pilot:
        app.push_screen(screens.ComponentScreen(ENTRY_ID))
        await pilot.pause()
        await pilot.pause()
        for _ in range(2):
            print(app.theme)  # read it, do not assume
            for el in app.screen.query(SELECTOR):  # every variant, not just [0]
                for part in PARTS:
                    print("   ", part, el.get_component_rich_style(part), "on", el.background_colors[1])
            await pilot.press("ctrl+t")
            await pilot.pause()
            await pilot.pause()


asyncio.run(main())
```

Read the background from `background_colors[1]`, not `styles.background` — the
latter reports `#000000` when unset, which quietly yields fake contrast numbers.
Print `app.theme` rather than labelling the iterations, so you are reading the
theme instead of assuming the app started on dark.

**One thing the suite does not check for you.** It verifies body `text` against
each surface, and the feedback roles against `$bg` — but not a feedback colour
against a surface *your element introduces*. `ON_LIGHT` is tuned against `$bg`,
so giving a callout or a banner its own tinted fill re-opens the exact problem
`ON_LIGHT` exists to solve, and the tests will stay green. If your element sets
its own `background` under a feedback hue, work out the ratio by hand. The
cheaper move is usually what `StatusLine` does: leave the surface alone and let
a border and a mark carry the intent.

## Step 6: Add a row to the contract's element table

Adding an element is a one-line documentation change: append it to the status
table in §1 of [`CONTRACT.md`](../../../src/reflection_ai_py_demo/ui/CONTRACT.md),
with its stock base and a note on what it inherits or why it stays custom. That
table is the inventory of what the library contains and where each thing came
from, so an element missing from it is invisible to the next reader.

Nothing else needs touching for a routine addition. If you changed a *rule*
rather than adding an element — a new layer, a different vocabulary, a new
contract clause — then check [`MEMORY.md`](../../../MEMORY.md), which maps which
sections of the README, the contract and this skill mirror each other.

## Common mistakes

**Styling a sub-part from the app stylesheet.** `DEFAULT_CSS` is auto-scoped to a
widget's *descendants*, so a rule naming the widget itself becomes
`Example Example` and never matches. Use `COMPONENT_CLASSES` for parts; only the
element's own background may need to live in `app.tcss`.

**Losing to a stock rule.** Textual's own CSS can beat yours at equal
specificity. When a stock widget's shorthand (`border: tall`) fights a longhand
of yours, reset the shorthand first, or set the style in Python — clearer than
escalating a selector fight.

**Contrast that fails in one theme.** Every colour resolves differently in dark
and light. Check both; the light scheme cannot reuse the dark feedback hues,
which is why `ON_LIGHT` exists.
