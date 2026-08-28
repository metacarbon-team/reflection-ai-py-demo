# Document parity

Three documents describe this design system from three angles:

| Document | Answers | Audience |
| --- | --- | --- |
| [`README.md`](README.md) | *What is this and how is it arranged?* | someone opening the repo |
| [`ui/CONTRACT.md`](src/reflection_ai_py_demo/ui/CONTRACT.md) | *Why are the rules what they are?* | someone changing an element |
| [`.claude/skills/add-element/`](.claude/skills/add-element/SKILL.md) | *What do I do, in order?* | Claude, adding an element |

They overlap on purpose — the same rule stated as orientation, as reasoning, and
as procedure. That redundancy is what makes each one readable alone, and it is
also why they drift. This file records what has to move together.

## The parity table

When you change the left column, check every cell in the row.

| If you change… | README | CONTRACT | SKILL |
| --- | --- | --- | --- |
| **The layer rule** (what makes something a primitive / component / pattern) | "The three layers" table | §0 *Pick the right layer* | Step 1 table |
| **Vocabulary** (widget / element / component) | "A note on vocabulary" | *Vocabulary* section | wording throughout |
| **Directory structure** | the tree in "The design system" | §0 layer paths | Step 2 file placement, Step 3 exports |
| **A contract rule** (§1–§7) | "How a component is written" → five declarations | the rule itself | Step 2 bullet list |
| **The element checklist** | "Adding to the showcase" numbered list | *Checklist for a new element* | Steps 1–5 |
| **Verify commands** | "Verify" section | — | Step 5 |
| **Adding an element** | — | add a row to the §1 status table | — (the skill covers the rest) |
| **Moving an element between layers** | — | update its row in §1 | — (plus both `__init__` exports) |
| **What is production-suitable** | "What is production-suitable" | — | — |
| **Token or theme structure** | "Tokens → theme → CSS" | §6 *Appearance comes from tokens* | Step 2, tokens bullet |

## Invariants

These are asserted by the test suite (`tests/test_showcase.py`), so they cannot
drift silently — but if you deliberately change one, all three documents describe
it and all three need updating.

- Nothing below `patterns/` defines `compose()`; everything in `patterns/` arranges
  our elements — `test_primitives_and_components_do_not_compose`,
  `test_patterns_actually_compose`
- No layer imports from a layer above it — `test_layers_only_depend_downwards`
- Anything with a text-building `render()` declares `COMPONENT_CLASSES` —
  `test_widgets_that_draw_text_declare_component_classes`
- No element reads `app.current_theme.variables` — `test_no_component_reads_the_theme_by_hand`
- No hardcoded box-drawing glyphs outside `tokens.py` — `test_no_hardcoded_glyphs_outside_tokens`
- ASCII mode leaks nothing — `test_ascii_mode_leaks_nothing`
- Constrained props are `Literal`, not `str` — `test_component_props_use_named_types_not_bare_str`

## Facts that live in exactly one place

Not everything should be repeated. These have a single home; link to it rather
than restating it, or the copies will disagree.

| Fact | Home |
| --- | --- |
| Colour values sampled from the CLI screenshots | README → "Where the colours come from" |
| Why the glyph set is single-cell only | README → "Notes worth knowing" |
| Why the shimmer ramp is neutral-only | `ui/tokens.py`, `SHIMMER` docstring |
| Why the light scheme needs its own feedback hues | `ui/tokens.py`, `OnLight` docstring |
| Why `bg` is the terminal body, not the page | `ui/theme.py`, `DARK` comment |
| Why `Composer` wraps rather than subclasses `Input` | CONTRACT §1, note under the table |

## When you add a document

Add a row to the table at the top and a column to the parity table. Three is
already at the edge of what stays in sync by hand; a fourth needs a reason.
