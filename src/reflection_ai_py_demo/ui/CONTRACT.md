# Element contract

Every element in this library follows the same contract. It is not invented
here — it is Textual's own widget API, written down so we apply it consistently
instead of rediscovering it per element.

One rule sits above the rest:

> **Textual owns behaviour. We own appearance.**

Behaviour means editing, focus, selection, scrolling, key handling — everything
a terminal UI has to get right and that is tedious and easy to get wrong. That
work is already done and maintained upstream. Our job is what the product looks
like, which is the part nobody else can do for us.

An element that reimplements what a stock Textual widget already does is a bug,
not a design decision: it is unpaid maintenance, and it drifts from the
framework's behaviour the moment either side changes.

---

## Vocabulary

Three words get used for the same objects, so they are pinned here:

| Term | Means | Use it when |
| --- | --- | --- |
| **Textual widget** | the framework type — anything subclassing `Widget` | talking about the framework |
| **element** | anything in `ui/`, regardless of layer | talking about the library generally |
| **primitive / component / pattern** | a specific layer of `ui/` | the layer matters |

So: *`Badge` is a **component**, implemented as a Textual **widget**.* Note
that `component` is not a synonym for "anything in the library" — since the
layer split it names one specific tier, and `ui/components/` is where those
live. Reach for **element** when you mean the general case.

---

## 0. Pick the right layer

Three layers, separated by a mechanical rule:

* **`primitives/`** — draws directly, composes nothing of ours (`Text`, `Surface`)
* **`components/`** — a self-contained unit of meaning, still draws itself (`Badge`)
* **`patterns/`** — arranges our own elements: a `compose()`, or a helper that
  yields them (`Composer`, `header`)

If you write `def compose()` and yield our elements, it is a pattern. Tests
enforce both directions, and no layer may import from one above it.

## 1. Subclass the stock widget

Start from the Textual widget that already does the job. Reach for `Static` only
when nothing in `textual.widgets` fits.

```python
from textual.widgets import Input


class Composer(Input):  # inherits editing, cursor, selection, focus
    DEFAULT_CSS = "..."  # we supply only the appearance
```

Current mapping:

| Ours | Stock base | Status |
| --- | --- | --- |
| `Composer` | wraps `Input` | ✅ editing, cursor, selection, history, `Changed`/`Submitted` |
| `StatusLine` | `Static` | ✅ component classes + reactive props |
| `ProgressBar` | `Static` | ✅ component classes; custom bar so glyphs stay tokenised |
| `Spinner` | `Static` | ✅ component classes; custom so frame sets stay tokenised |
| `Shimmer` | `Static` | ✅ ramp exposed as four component classes |
| `KeyHintBar` | `Static` | ⚠️ works, but overlaps stock `Footer` |
| `Text`, `Badge` | `Static` | ✅ pure CSS, no `render()` — no component classes needed |
| `ListRow` | `ListItem` | ✅ pattern: composes `HStack` + `Text` |
| `Divider` | `Static` | ❌ should subclass `Rule` |
| `Panel` | `Vertical` | ❌ overlaps `Collapsible` |

`Composer` *wraps* rather than subclasses `Input`: the chevron has to sit inside
the channel, and writing it into the value would mean offsetting every cursor
position and selection range around it. The wrapper re-exports `value`, `focus`,
`Changed` and `Submitted`, so callers still see one component.

When we *do* keep a custom implementation, the reason belongs in the docstring.
"We already wrote it" is not a reason.

## 2. Styleable parts are `COMPONENT_CLASSES`

If an element implements `render()` and builds its own text, every part that can
be coloured gets a component class. Read the style with
`get_component_rich_style()` — never from `app.current_theme.variables`.

```python
class StatusLine(Static):
    COMPONENT_CLASSES = {"statusline--mark", "statusline--message"}

    DEFAULT_CSS = """
    StatusLine {
        & > .statusline--mark { color: $info; }
        &.-success > .statusline--mark { color: $success; }
    }
    """

    def render(self) -> RenderResult:
        text = RichText()
        text.append(glyph("check"), style=self.get_component_rich_style("statusline--mark"))
        return text
```

Why this matters more than it looks: `get_component_rich_style()` resolves
against the CURRENT theme on every repaint. Reading the theme by hand bakes the
colour in when the text is built, so a light/dark toggle leaves stale values on
screen — which is why a `_Painted` base class used to exist here solely to watch
the theme. Component classes deleted it. Hand-rolled selectors also fight
Textual's CSS auto-scoping, which cost several rounds of debugging.

Naming follows the stock Textual convention: `elementname--part`, lowercase,
double dash.

## 3. State is reactive, not constructor-baked

Anything that can change after mount is a `reactive`. A private `self._foo`
assigned in `__init__` is the anti-pattern this contract exists to kill: it
cannot be updated, so callers destroy and rebuild the element instead.

```python
class StatusLine(Static):
    message: reactive[str] = reactive("")
    status: reactive[Status] = reactive[Status]("info")

    def __init__(self, message: str = "", *, status: Status = "info") -> None:
        super().__init__()
        # set_reactive assigns WITHOUT firing watchers before mount.
        self.set_reactive(StatusLine.message, message)
        self.set_reactive(StatusLine.status, status)
```

Rules:

- Declare with the class-level annotation, exactly as stock widgets do.
- Use `set_reactive()` in `__init__`; plain assignment fires watchers against a
  half-built element.
- Pass `layout=True` when a change resizes the element, `recompose=True` when it
  changes children. Default (`repaint=True`) is right for colour and text.

## 4. Repaint through `watch_*`, never inline

One `_render()` that every watcher calls. Do not repaint from a setter.

```python
def watch_message(self) -> None:
    self._render()


def watch_status(self) -> None:
    self._render()
```

An element using component classes needs no theme handling at all: `refresh()` is
enough, because the styles re-resolve on the next paint. This is why `_Painted`
no longer exists.

## 5. Interaction is a `Message`, never a callback

Components never call into their parent. They post a message and let it bubble.
Follow the stock shape exactly — a nested `@dataclass` carrying the element plus
what changed, with a `control` alias.

```python
class Composer(Input):
    @dataclass
    class Submitted(Message):
        composer: Composer
        value: str

        @property
        def control(self) -> Composer:
            return self.composer
```

Parents handle `on_composer_submitted`. This is what makes a component reusable
without knowing its context — the thing constructor callbacks prevent.

## 6. Appearance comes from tokens, always

No hex, no literal glyph, no magic spacing in a component. Colour arrives as a
CSS variable (`$text-muted`), glyphs through `glyph()`, timings from `tokens`.

This applies to *drawing* characters too. A hardcoded `"█"` breaks the ASCII
fallback silently — the terminal that cannot render it is exactly the terminal
that asked for ASCII.

## 7. Variants are classes, not branches

A variant sets a CSS class and lets the stylesheet decide. No `if intent ==
"danger"` inside a render method.

```python
Badge.-solid.-danger { background: $danger; }
```

---

## Checklist for a new element

Adding one? Run the **`add-element` skill** — it turns this contract into an
ordered procedure, including the exports and gallery entry that are easy to
forget. This document stays the reasoning behind each step.

1. Does a stock Textual widget already do this? Subclass or wrap it.
2. Does every styleable part have a `COMPONENT_CLASSES` entry?
3. Is every mutable field a `reactive` with a `watch_*`?
4. Does interaction post a `Message` rather than call a callback?
5. Are all colours, glyphs, and timings from tokens?
6. Are constrained props typed with a `Literal`, not `str`?
7. Does it appear in `registry.py` so the gallery renders it?

---

## Keeping this in sync

This contract, the [README](../../../README.md) and the `add-element` skill
describe the same system from three angles, and they drift silently.
[`MEMORY.md`](../../../MEMORY.md) records which sections mirror each other —
check it whenever you change a rule here.
