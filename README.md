# Reflection AI — Python TUI design showcase

A design environment for the Agentic CLI, built on [Textual](https://github.com/textualize/textual).

This is a **design artefact, not a product**. There is no CLI functionality and
no agent behind it: the app exists so that TUI components and flows can be seen,
compared, and argued over in a real terminal. 

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Run

```bash
uv run reflection-ai-py-demo
```

## Verify

```bash
uv run pytest && uv run ruff check . && uv run ruff format --check .
```

## What is in it

Three modes, chosen from the home screen:

| Mode | What it is for |
| --- | --- |
| **Component library** | Every component, previewed one at a time. |
| **Prototype flows** | Scripted sequences you step through frame by frame. |
| **Design tokens** | The palette and semantic roles as swatches, resolved live. |

### Keys

| Key | Action |
| --- | --- |
| `↑` `↓` | Move |
| `enter` | Select |
| `esc` | Back |
| `→` / `space` / `n` | Next frame (in a flow) |
| `←` / `p` | Previous frame |
| `r` | Restart the flow |
| `ctrl+t` | Toggle light / dark |
| `q` / `ctrl+c` | Quit |

## The design system

The whole point of the scaffold is the layering below. Three rules hold it up:

1. **Components never invent a value.** No component contains a hex code, a
   count of spaces, or a literal glyph. It asks the system for a *role*.
2. **Tokens are semantic, not literal.** `text_muted`, not `gray`. That is what
   makes the system re-skinnable without touching a component.
3. **The terminal is the constraint.** Space is whole cells, and a glyph must
   advance exactly one cell. Colour is truecolor — Textual degrades it for
   lower-capability terminals, so we do not maintain a second palette.

```
src/reflection_ai_py_demo/
├── app.py            # App only: lifecycle, global bindings, theme registration
├── app.tcss          # app-level stylesheet
├── themes.py         # which themes this app registers
├── ui/               # THE DESIGN SYSTEM - three layers by composition
│   ├── tokens.py     #   values: palette, space, glyphs, motion, type
│   ├── theme.py      #   semantic roles -> CSS variables
│   ├── primitives/   #   draw directly, compose nothing of ours
│   │   ├── base.py   #     glyph resolver, prop vocabulary
│   │   ├── text.py   #     Text
│   │   ├── stack.py  #     VStack, HStack
│   │   ├── box.py    #     Surface, Panel
│   │   └── rule.py   #     Divider
│   ├── components/   #   self-contained units of meaning
│   │   ├── badge.py, status_line.py, progress_bar.py
│   │   └── spinner.py, shimmer.py, key_hints.py
│   └── patterns/     #   composed FROM the layers below
│       ├── composer.py   #   Input + chevron
│       ├── thinking.py   #   Spinner + Shimmer
│       ├── list_row.py   #   HStack + Text x3
│       └── header.py     #   breadcrumb helper
├── screens/          # one file per screen
└── gallery/          # showcase data - the one part that is NOT production
    ├── registry.py
    └── flows.py
```

### A note on vocabulary

Three words describe the same objects, and mixing them is the fastest way to
confuse a hand-off:

- **Textual widget** — the framework type. Every element here subclasses
  Textual's `Widget`, so technically they are all widgets. Use this word only
  when talking about the framework.
- **element** — anything in `ui/`, whatever its layer. The general word.
- **primitive / component / pattern** — a specific layer, below.

`Badge` is a *component*, implemented as a Textual *widget*. Note that
`component` names one specific tier rather than "anything in the library" —
reach for **element** when you mean the general case.

### The three layers

The rule that separates them is **mechanical, not editorial**:

| Layer | Rule | Example |
| --- | --- | --- |
| `primitives/` | draws directly, composes nothing of ours | `Text`, `Surface` |
| `components/` | self-contained unit of meaning, still draws itself | `Badge`, `Spinner` |
| `patterns/` | arranges our own elements — a `compose()`, or a helper that yields them | `Composer`, `ListRow`, `header` |

Two tests enforce it: nothing below `patterns/` may define `compose()`, and no
layer may import from one above it. That is what keeps the split a fact rather
than a naming convention.

Import through the facade, not the layer:

```python
from ..ui import Badge, Composer, Text  # yes
from ..ui.patterns import Composer  # works, but couples you to a layer
```

Everything is re-exported from `ui/__init__.py`, so moving an element between
layers stays a private refactor.

### What is production-suitable

Everything except `gallery/`. `ui/` and the `screens/` patterns are
all written to be lifted into a real CLI — they are not a final deliverable, but
they are not throwaway either. `gallery/` holds the showcase registry and the
scripted flows, and is the only part that exists purely for the demo.

Four rules hold the layout together:

1. **`app.py` stays thin.** Lifecycle, bindings, theme registration. Nothing else.
2. **One screen per file.** A screen is a unit of navigation, so it gets a module.
3. **`ui/` never imports from the app.** The design system is a library: it knows
   about tokens and roles, not about screens, flows, or the registry. That is what
   makes it liftable into a real CLI unchanged.
4. **`gallery/` is the only non-production part.** It holds the showcase registry
   and the scripted flows. Everything else is written to be lifted into a real CLI.

App-level CSS lives in `app.tcss` rather than an `App.CSS` string — easier to
read as CSS, and not subject to the `DEFAULT_CSS` auto-scoping that catches
people out inside a Textual widget class. Per-element styling stays with the
element so the library remains self-contained.

### Tokens → theme → CSS

`tokens.py` holds the raw values. `theme.py` maps them onto semantic roles and
publishes every role to Textual as a CSS variable, so a stylesheet can only ever
say `color: $text-muted` — it has no way to reach a raw hex. Both directions of
the bridge exist because a handful of effects (the shimmer) compute colour per
character and cannot go through CSS.

Two schemes ship: `reflection-dark` and `reflection-light`. Toggle with `ctrl+t`
and judge the design in both.

### Where the colours come from

`reflection-dark` is sampled from screenshots of the **existing Reflection
CLI** (Figma "Workflow", node `52:1393`). The values are measured pixels, not
approximations:

| Role | Hex | In the CLI |
| --- | --- | --- |
| `bg` | `#292c33` | terminal body |
| `bg_subtle` | `#1e1e1e` | the page behind it |
| `accent` | `#688663` | selected-row green |
| `warning` | `#e9c77f` | amber tool names |
| `info` | `#6886d1` | blue panel headings |

Two deliberate departures, both about legibility:

- **Body text is lifted.** The CLI's body grey is `#7d7d7d`, which is 3.40:1
  against its own background - under the readable threshold, and visibly washed
  out in the screenshots. `text` is `#c2c6cd` (8.16:1) instead, with the
  original grey kept as the *muted* step where low contrast is the point.
- **The light scheme does not reuse the dark hues.** Every one of them fails on
  white - the amber is 1.62:1, effectively invisible - so `ON_LIGHT` in
  `tokens.py` carries darkened equivalents of the same hues.

`accent` (3.45:1) and `info` (3.94:1) are kept at their exact measured values
even though both sit under 4.5:1. They are the product's real colours and this
showcase exists to represent it faithfully; raising them is a design decision to
take deliberately, not a thing to smuggle in through a port. Both are used for
accents and headings rather than body copy, which is what makes that tolerable.

### Notes worth knowing

Three decisions in here look arbitrary and are not:

- **The glyph set is restricted to single-cell characters.** The heavier
  dingbats (`✔` U+2714, `✖` U+2716, `ℹ` U+2139) are deliberately absent: common
  monospace fonts do not ship them, so Figma and the terminal both substitute a
  proportional fallback that occupies ~1.7 cells and shears every column after
  it. `✓` and `×` are the single-cell equivalents. A test enforces this.
- **The shimmer ramp is neutral-only.** A shimmer is a lightness sweep, not a
  change of hue. Pulling the accent into the ramp would make it read as a state
  change and collide with what the accent actually means elsewhere.
- **The selected row carries three signals at once** — a chevron in a reserved
  gutter, the accent colour on the name, and a raised background. Colour alone
  is not enough: a downgraded terminal renders `accent` and `text` closer
  together than a designer expects, and the marker is what survives that. The
  gutter is present on every row, selected or not, so nothing shifts sideways
  as the cursor moves.

The light scheme's neutral ramp is also asymmetric with the dark one — there is
less usable range between white and a readable grey than between near-black and
white. See the comment on `LIGHT` in `theme.py`.

One Textual footgun worth knowing if you restyle rows: `DEFAULT_CSS` on a
Textual widget is auto-scoped to that widget's *descendants*, so a rule naming
the widget itself (`ListRow.-selected`) silently becomes
`ListRow ListRow.-selected` and never matches. The row's own background
therefore lives in `app.tcss`; only the per-child tones stay in `ListRow`.

## How a component is written

There is **one API**, and it is Textual's own — not a dialect invented here.
Every element is shaped like a stock Textual widget, so anyone who has read
the source of `Switch` or `Input` already knows how to extend this library.

There is no third-party "design system for TUI" package to adopt. The PyPI
ecosystem offers individual widgets (`textual-plotext`, `textual-autocomplete`,
`textual-fastdatatable`), but nothing that supplies a system for building them —
Textual is both the behaviour layer and the base. So the discipline below is the
whole product: use Textual's extension points, and add nothing of our own that
Textual already has.

### The five declarations

```python
class StatusLine(Static):
    COMPONENT_CLASSES = {"statusline--mark", "statusline--message"}  # styleable parts
    DEFAULT_CSS = "..."  # appearance
    message: reactive[str] = reactive("")  # state

    class Changed(Message): ...  # events (if any)

    def render(self) -> RenderResult:
        text = RichText()
        text.append(glyph("check"), style=self.get_component_rich_style("statusline--mark"))
        return text
```

`COMPONENT_CLASSES` is the important one, and the easiest to skip. It declares
which parts of an element a stylesheet may target, and `get_component_rich_style()`
resolves them **at paint time, against the current theme**.

That property is what keeps a whole class of machinery out of the library. The
alternative — hand-rolling CSS classes and reading colours from
`self.app.current_theme.variables` — fails in two ways:

- Colours get baked into a `rich.Text` when it is built, so a light/dark toggle
  leaves stale values on screen, and every animated element needs its own theme
  watcher to repaint.
- Hand-written selectors collide with Textual's CSS auto-scoping (see the
  footgun note above), turning styling into a specificity fight.

A test enforces this: any element with a `render()` that builds text must declare
`COMPONENT_CLASSES`, and no file under `ui/` may read `current_theme.variables`.

### What we still add on top

Deliberately small — three things Textual genuinely does not provide:

| Ours | Why it exists |
| --- | --- |
| `tokens.py` / `theme.py` | Semantic roles published as CSS variables. Textual has themes but no opinion about *what* roles a system should have. |
| `Status`, `Variant`, `Gap`, … | Literal types for constrained props, so an editor autocompletes and `ty` rejects typos. |
| `one_of()` | Runtime check that names the valid values, for anyone exploring in a REPL. |

Everything else is stock Textual.

## Adding to the showcase

**An element** — Claude has a skill for this:
[`add-element`](.claude/skills/add-element/SKILL.md). It walks the whole
procedure — pick the layer, write the element, export it from both the layer and
the facade, add the gallery entry, verify. Ask for it by name, or just describe
what you want to add.

By hand: write it in the matching `ui/` layer reading only tokens and roles,
export it from that layer's `__init__.py` **and** from `ui/__init__.py`, then add
one `Entry` to `REGISTRY` in `gallery/registry.py`. Keep the preview short enough
to fit one viewport.

Checklist (the reasoning behind each line lives in
[`ui/CONTRACT.md`](src/reflection_ai_py_demo/ui/CONTRACT.md)):

1. Does a stock Textual widget already do this? Subclass or wrap it.
2. Does every styleable part have a `COMPONENT_CLASSES` entry?
3. Is every mutable field a `reactive` with a `watch_*`?
4. Does interaction post a `Message` rather than call a callback?
5. Are all colours, glyphs, and timings from tokens?
6. Are constrained props typed with a `Literal`, not `str`?

**A flow** — add a `Flow` of `Frame`s to `gallery/flows.py`. Frames are plain
data and build elements on demand; nothing executes.

## ASCII fallback

Consoles that cannot be trusted with box drawing get the ASCII glyph set.
Glyph choice is reached through `set_unicode()` / `glyph()` in
`ui/primitives/base.py` rather than a module-level flag — a flag would be copied
by value at import time and never reach the other element modules:

```bash
REFLECTION_ASCII=1 uv run reflection-ai-py-demo
```

## Keeping the docs in sync

This README, [`ui/CONTRACT.md`](src/reflection_ai_py_demo/ui/CONTRACT.md) and the
[`add-element`](.claude/skills/add-element/SKILL.md) skill describe the same
system as orientation, reasoning, and procedure. That overlap is deliberate, and
it is also how they drift. [`MEMORY.md`](MEMORY.md) maps which sections mirror
each other, and which facts deliberately live in exactly one place.
