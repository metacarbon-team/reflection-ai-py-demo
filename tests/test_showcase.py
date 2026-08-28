"""Tests for the showcase.

These are design-system guardrails rather than product tests. They assert the
things a showcase must never get wrong: every preview mounts, every flow frame
builds, the token contract holds, and a theme flip actually repaints.
"""

from __future__ import annotations

import pytest

from reflection_ai_py_demo import screens
from reflection_ai_py_demo.app import ShowcaseApp
from reflection_ai_py_demo.gallery import flows as flow_data
from reflection_ai_py_demo.gallery.registry import BY_ID, REGISTRY
from reflection_ai_py_demo.themes import BUILTIN_THEMES, SCHEMES
from reflection_ai_py_demo.ui import tokens
from reflection_ai_py_demo.ui.theme import DARK, LIGHT, ROLES

# --------------------------------------------------------------------------
# Token contract
# --------------------------------------------------------------------------


def test_every_role_resolves_in_both_schemes() -> None:
    """A role missing from a scheme is a hole an element would fall through."""
    for scheme in (DARK, LIGHT):
        for role in ROLES:
            assert scheme.hex(role).startswith("#")


def test_themes_publish_every_role_to_css() -> None:
    """Components reach colour through CSS, so every role must be a variable."""
    for theme in BUILTIN_THEMES.values():
        for role in ROLES:
            assert role.replace("_", "-") in theme.variables


def test_glyph_sets_are_parallel() -> None:
    """The ASCII fallback must cover every glyph, or a console loses content."""
    assert set(tokens.GLYPHS_UNICODE) == set(tokens.GLYPHS_ASCII)


def test_unicode_glyphs_are_single_cell() -> None:
    """A wide glyph shears every column after it - the whole reason for this set."""
    from rich.cells import cell_len

    for name, char in tokens.GLYPHS_UNICODE.items():
        assert cell_len(char) == 1, f"{name} is not one cell wide"


def test_shimmer_trough_stays_readable() -> None:
    """Most of a shimmering label sits at the TROUGH, not the crest.

    The crest covers a few cells, so the last ramp step is what the reader
    actually sees across most of the string. `text_subtle` used to sit there
    and measures 1.29:1 on dark - the label was effectively invisible between
    passes. The trough must be the resting tone of ordinary secondary copy.
    """
    trough = tokens.SHIMMER.ramp[-1]
    assert trough == "text_muted", f"trough is {trough!r}"
    assert "text_subtle" not in tokens.SHIMMER.ramp

    # And the crest must genuinely brighten, or there is no shimmer at all.
    assert tokens.SHIMMER.ramp[0] == "text_bright"
    for scheme in (DARK, LIGHT):
        crest = _contrast(scheme.hex("text_bright"), scheme.hex("bg"))
        rest = _contrast(scheme.hex(trough), scheme.hex("bg"))
        assert crest > rest


def test_shimmer_crosses_a_label_briskly() -> None:
    """The shimmer interval is seconds per CELL, so a slow value compounds.

    At 0.32s/cell a 22-character label took ~9s per pass and read as stalled.
    This pins the pass time rather than the raw interval, since that is the
    thing a reviewer actually perceives.
    """
    label_length = 22
    span = label_length + tokens.SHIMMER.tail_pause
    pass_seconds = span * tokens.DURATION["shimmer"] / tokens.SHIMMER.step
    assert 0.8 <= pass_seconds <= 3.0, f"a full pass takes {pass_seconds:.2f}s"


def test_shimmer_ramp_is_neutral_only() -> None:
    """The shimmer is a lightness sweep; an accent in the ramp would read as state."""
    assert all(role.startswith("text") for role in tokens.SHIMMER.ramp)


def test_light_scheme_inverts_the_neutral_ramp() -> None:
    """On light, the crest of the text ramp must be the darkest ink, not the brightest."""
    assert LIGHT.hex("text_bright") == tokens.PALETTE.ink.hex
    assert DARK.hex("text_bright") == tokens.PALETTE.paper.hex


# --------------------------------------------------------------------------
# Registry and flow data
# --------------------------------------------------------------------------


def test_registry_ids_are_unique() -> None:
    assert len(BY_ID) == len(REGISTRY)


def test_flow_ids_are_unique() -> None:
    assert len(flow_data.BY_ID) == len(flow_data.FLOWS)


def test_every_flow_has_frames() -> None:
    for flow in flow_data.FLOWS:
        assert flow.frames, f"{flow.id} has no frames"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_home_screen_mounts() -> None:
    app = ShowcaseApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, screens.HomeScreen)


@pytest.mark.asyncio
@pytest.mark.parametrize("entry_id", [e.id for e in REGISTRY])
async def test_every_component_preview_mounts(entry_id: str) -> None:
    """The showcase's core promise: no preview may fail to render."""
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        app.push_screen(screens.ComponentScreen(entry_id))
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, screens.ComponentScreen)
        assert app.screen.query("#preview")


@pytest.mark.asyncio
@pytest.mark.parametrize("flow_id", [f.id for f in flow_data.FLOWS])
async def test_every_flow_frame_renders(flow_id: str) -> None:
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        app.push_screen(screens.FlowScreen(flow_id))
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, screens.FlowScreen)

        for expected in range(len(screen.flow.frames)):
            await pilot.pause()
            assert screen.index == expected
            await pilot.press("right")

        # Stepping past the end must clamp, not wrap or crash.
        assert screen.index == len(screen.flow.frames) - 1


@pytest.mark.asyncio
async def test_flow_navigation_clamps_at_the_start() -> None:
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        app.push_screen(screens.FlowScreen("task"))
        await pilot.pause()
        await pilot.press("left")
        await pilot.pause()
        assert app.screen.index == 0  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_theme_toggle_repaints_the_token_sheet() -> None:
    """A stale colour after a theme flip is the bug this guards."""
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        app.push_screen(screens.TokensScreen())
        await pilot.pause()
        await pilot.pause()

        assert app.theme == "reflection-dark"
        await pilot.press("ctrl+t")
        await pilot.pause()
        assert app.theme == "reflection-light"

        # The sheet prints hex values, so the light scheme's background must now
        # be on screen. Note we cannot assert the dark values are simply absent:
        # the two schemes share a palette, so `#0d1117` is still there - as the
        # light scheme's `text_bright`. Compare the full ordered list instead.
        sheet = app.screen.query_one("#token-sheet")
        shown = [str(widget.render()) for widget in sheet.query("Static")]

        light = SCHEMES["reflection-light"]
        dark = SCHEMES["reflection-dark"]
        assert [h for h in shown if h.startswith("#")] == [light.hex(r) for r in ROLES]
        assert [h for h in shown if h.startswith("#")] != [dark.hex(r) for r in ROLES]


@pytest.mark.asyncio
async def test_navigation_pushes_and_pops() -> None:
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        await pilot.pause()
        depth = len(app.screen_stack)

        await pilot.press("enter")  # Component library
        await pilot.pause()
        assert isinstance(app.screen, screens.LibraryScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert len(app.screen_stack) == depth
        assert isinstance(app.screen, screens.HomeScreen)


# --------------------------------------------------------------------------
# Selected state
# --------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("screen_factory", "list_id"),
    [
        (screens.HomeScreen, "home-list"),
        (screens.LibraryScreen, "library-list"),
        (screens.FlowsScreen, "flows-list"),
    ],
)
async def test_arrow_keys_move_a_visible_selection(screen_factory, list_id: str) -> None:
    """Arrow keys must move the cursor AND make the move visible.

    The regression this guards: the cursor moved correctly, but the selected
    row was styled identically to the others, so the keys appeared dead.
    """
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        await pilot.pause()
        if not isinstance(app.screen, screen_factory):
            app.push_screen(screen_factory())
            await pilot.pause()
        await pilot.pause()

        rows = list(app.screen.query_one(f"#{list_id}").children)
        assert len(rows) >= 2

        def selected() -> list[int]:
            return [i for i, row in enumerate(rows) if "-selected" in row.classes]

        # Exactly one row is ever selected, and it starts at the top.
        assert selected() == [0]

        await pilot.press("down")
        await pilot.pause()
        assert selected() == [1]

        await pilot.press("up")
        await pilot.pause()
        assert selected() == [0]


@pytest.mark.asyncio
async def test_selected_row_differs_visibly_from_its_neighbours() -> None:
    """Three signals carry selection; a change in any one is not enough alone."""
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        await pilot.pause()
        await pilot.pause()
        rows = list(app.screen.query_one("#home-list").children)
        chosen, other = rows[0], rows[1]

        def parts(row):
            marker = str(next(iter(row.query(".-marker"))).render())
            name = next(iter(row.query(".-name")))
            return marker, name.styles.color, row.styles.background

        chosen_marker, chosen_color, chosen_bg = parts(chosen)
        other_marker, other_color, other_bg = parts(other)

        assert chosen_marker.strip(), "selected row has no marker glyph"
        assert other_marker.strip() == "", "unselected row should reserve an empty gutter"
        assert chosen_color != other_color
        assert chosen_bg != other_bg


@pytest.mark.asyncio
async def test_selection_survives_returning_to_a_list() -> None:
    """Coming back from a preview must restore both cursor and its styling."""
    app = ShowcaseApp()
    async with app.run_test(size=(96, 32)) as pilot:
        await pilot.pause()
        await pilot.press("enter")  # Component library
        await pilot.pause()

        for _ in range(3):
            await pilot.press("down")
            await pilot.pause()

        listing = app.screen.query_one("#library-list")
        expected = listing.index
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, screens.ComponentScreen)

        await pilot.press("escape")
        await pilot.pause()
        await pilot.pause()

        listing = app.screen.query_one("#library-list")
        assert listing.index == expected
        rows = list(listing.children)
        assert [i for i, r in enumerate(rows) if "-selected" in r.classes] == [expected]


# --------------------------------------------------------------------------
# Palette fidelity to the existing CLI
# --------------------------------------------------------------------------


def _contrast(fg: str, bg: str) -> float:
    def lum(h: str) -> float:
        rgb = [int(h[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        f = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]

    hi, lo = sorted((lum(fg), lum(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_dark_scheme_matches_the_cli_screenshots() -> None:
    """These hexes are measured pixel values from the real CLI, not guesses.

    If one of them changes, the theme has drifted from the product it is meant
    to represent - which for a design showcase is the whole ballgame.
    """
    assert DARK.hex("bg") == "#292c33"  # terminal body
    assert DARK.hex("bg_subtle") == "#1e1e1e"  # page behind it
    assert DARK.hex("accent") == "#688663"  # selection green
    assert DARK.hex("warning") == "#e9c77f"  # amber tool names
    assert DARK.hex("info") == "#6886d1"  # blue headings


def test_body_text_is_legible_in_both_schemes() -> None:
    """The one place we deliberately depart from the CLI.

    Its body grey (#7d7d7d) is 3.40:1 on #292c33 - under the readable
    threshold. We keep the hue but lift the value; matching a palette should
    not mean inheriting its legibility problems.
    """
    for scheme in (DARK, LIGHT):
        assert _contrast(scheme.hex("text"), scheme.hex("bg")) >= 4.5


def test_selected_row_text_is_legible_on_its_fill() -> None:
    """The fill and the text on it are chosen as a pair, so check them as one."""
    for scheme in (DARK, LIGHT):
        ratio = _contrast(scheme.hex("selection_fg"), scheme.hex("selection_bg"))
        assert ratio >= 4.5, f"selection text is {ratio:.2f}:1"


def test_light_scheme_does_not_reuse_the_dark_feedback_hues() -> None:
    """Every dark feedback colour fails on white; the light scheme must differ."""
    for role in ("success", "warning", "danger", "info", "accent"):
        assert LIGHT.hex(role) != DARK.hex(role), f"{role} was not adapted for light"
        assert _contrast(LIGHT.hex(role), LIGHT.hex("bg")) >= 4.5


@pytest.mark.asyncio
async def test_composer_is_a_single_filled_row() -> None:
    """The composer is a filled channel with side rules and no vertical padding.

    Two things this pins, both of which broke once already:

    * height stays 1 - Textual's 2-value `padding` shorthand does not mean
      "vertical horizontal" here, and `padding: 0 1` silently added a blank row
      above and below;
    * the side rule is distinguishable from the fill - on the dark scheme
      `$border` and `$input-bg` resolve to the SAME value, so the obvious
      choice of `$border` made the rules disappear into the background.
    """
    app = ShowcaseApp()
    async with app.run_test(size=(88, 26)) as pilot:
        app.push_screen(screens.ComponentScreen("composer"))
        await pilot.pause()
        await pilot.pause()

        composers = list(app.screen.query("Composer"))
        assert composers

        for composer in composers:
            assert composer.outer_size.height == 1, "composer grew a vertical edge"
            fill = composer.styles.background
            rule = composer.styles.border_left[1]
            assert rule != fill, "side rule is invisible against its own fill"
            # Sides only - no top or bottom edge.
            assert not composer.styles.border_top[0]
            assert not composer.styles.border_bottom[0]


def test_input_surface_is_readable_in_both_schemes() -> None:
    """Body text and the placeholder both sit on the fill, not on the page."""
    for scheme in (DARK, LIGHT):
        fill = scheme.hex("input_bg")
        assert _contrast(scheme.hex("text"), fill) >= 4.5
        # The placeholder is meant to be quiet, but it must still be present.
        assert _contrast(scheme.hex("input_placeholder"), fill) >= 1.9


# --------------------------------------------------------------------------
# The element contract (see ui/CONTRACT.md)
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_composer_is_a_real_input_not_a_mock() -> None:
    """Textual owns behaviour, we own appearance.

    The composer used to be a `Static` that painted a fake prompt: it could not
    be typed into, and it reimplemented a widget Textual already ships. This
    pins the behaviour we now inherit for free.
    """
    from textual.widgets import Input

    from reflection_ai_py_demo.ui import Composer

    app = ShowcaseApp()
    async with app.run_test(size=(88, 26)) as pilot:
        app.push_screen(screens.ComponentScreen("composer"))
        await pilot.pause()
        await pilot.pause()

        composer = list(app.screen.query("Composer"))[0]
        field = composer.query_one(Input)

        composer.focus()
        await pilot.pause()
        await pilot.press("h", "e", "y")
        await pilot.pause()
        assert composer.value == "hey", "composer is not really editable"

        # Controlled from outside, like any real input.
        composer.value = "set externally"
        await pilot.pause()
        assert field.value == "set externally"

        # The event contract is re-exported, so parents can handle it.
        assert Composer.Changed is Input.Changed
        assert Composer.Submitted is Input.Submitted


@pytest.mark.asyncio
async def test_status_line_updates_in_place() -> None:
    """Reactive props, not constructor-baked state.

    A component whose fields are private attributes cannot be updated - callers
    have to destroy and rebuild it. This is the contract that prevents that.
    """
    from reflection_ai_py_demo.ui import StatusLine

    app = ShowcaseApp()
    async with app.run_test(size=(88, 26)) as pilot:
        app.push_screen(screens.ComponentScreen("status-line"))
        await pilot.pause()
        await pilot.pause()

        line = list(app.screen.query(StatusLine))[0]
        before = str(line.render())

        line.message = "Now something else"
        line.status = "danger"
        await pilot.pause()

        after = str(line.render())
        assert after != before, "reactive assignment did not repaint"
        assert "Now something else" in after


def test_no_hardcoded_glyphs_outside_tokens() -> None:
    """Rule 5: drawing characters are tokens too.

    A literal box-drawing character in a component breaks the ASCII fallback
    silently - the terminal that cannot render it is exactly the terminal that
    asked for ASCII. `ProgressBar` shipped with a hardcoded block for a while.
    """
    import pathlib

    root = pathlib.Path(__file__).parent.parent / "src"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        if path.name == "tokens.py":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#")[0]
            for char in code:
                # Box drawing, blocks, and geometric shapes.
                if 0x2500 <= ord(char) <= 0x25FF:
                    offenders.append(f"{path.name}:{number} U+{ord(char):04X}")
    assert not offenders, f"hardcoded glyphs: {offenders}"


@pytest.mark.asyncio
async def test_ascii_mode_leaks_nothing() -> None:
    """The fallback has to be total, or it is not a fallback."""
    from reflection_ai_py_demo import ui

    ui.set_unicode(False)
    try:
        app = ShowcaseApp()
        async with app.run_test(size=(88, 26)) as pilot:
            for entry_id in ("progress-bar", "status-line", "spinner"):
                app.push_screen(screens.ComponentScreen(entry_id))
                await pilot.pause()
                await pilot.pause()
                rendered = " ".join(str(widget.render()) for widget in app.screen.query("Static"))
                leaked = sorted({hex(ord(c)) for c in rendered if 0x2500 <= ord(c) <= 0x25FF})
                assert not leaked, f"{entry_id} leaked {leaked} in ASCII mode"
                app.pop_screen()
                await pilot.pause()
    finally:
        ui.set_unicode(True)


def test_spinner_frame_sets_have_ascii_counterparts() -> None:
    """Same reason the glyphs do: a frame the console cannot draw shows nothing."""
    assert set(tokens.FRAMES) == set(tokens.FRAMES_ASCII)
    for name, frame_set in tokens.FRAMES_ASCII.items():
        for frame in frame_set:
            assert all(ord(c) < 128 for c in frame), f"{name} frame {frame!r} is not ASCII"


# --------------------------------------------------------------------------
# Hand-off ergonomics
# --------------------------------------------------------------------------


def test_component_props_use_named_types_not_bare_str() -> None:
    """A designer should get autocomplete, not a guess.

    A prop typed `str` accepts anything and fails at mount with a `KeyError`.
    Every constrained prop must carry its `Literal` vocabulary so an editor can
    offer the valid values and a typechecker can reject the rest.
    """
    import inspect

    from reflection_ai_py_demo import ui

    constrained = {
        (ui.StatusLine, "status"),
        (ui.Badge, "variant"),
        (ui.Badge, "intent"),
        (ui.Surface, "border"),
        (ui.Spinner, "speed"),
        (ui.VStack, "gap"),
        (ui.HStack, "gap"),
    }
    for component, prop in constrained:
        annotation = inspect.signature(component.__init__).parameters[prop].annotation
        assert annotation != "str", f"{component.__name__}.{prop} is a bare str"


def test_a_bad_prop_value_names_the_alternatives() -> None:
    """The error message is the documentation for anyone exploring by hand."""
    from reflection_ai_py_demo.ui import StatusLine

    with pytest.raises(ValueError) as caught:
        StatusLine("hi", status="succes")  # type: ignore[arg-type]

    message = str(caught.value)
    assert "status=" in message, "error does not name the prop"
    assert "success" in message, "error does not list the valid values"


def test_widgets_that_draw_text_declare_component_classes() -> None:
    """Rule 1, sharpened: use Textual's extension points, not a private dialect.

    A widget that builds its own `rich.Text` must colour it through
    `COMPONENT_CLASSES` + `get_component_rich_style()`, the way stock widgets
    like `Switch` and `Input` do. The alternative - reading
    `app.current_theme.variables` by hand - bakes colours in at paint time and
    needs a bespoke theme watcher to stay correct. That watcher (`_Painted`)
    existed here until component classes replaced it.
    """
    from reflection_ai_py_demo import ui

    drawing = (
        ui.StatusLine,
        ui.ProgressBar,
        ui.Spinner,
        ui.Shimmer,
        ui.KeyHintBar,
    )
    for component in drawing:
        assert component.COMPONENT_CLASSES, (
            f"{component.__name__} builds text but declares no COMPONENT_CLASSES"
        )


def test_no_component_reads_the_theme_by_hand() -> None:
    """`current_theme.variables` in a component is the anti-pattern this replaced."""
    import pathlib

    root = pathlib.Path(__file__).parent.parent / "src" / "reflection_ai_py_demo" / "ui"
    offenders = [
        f"{path.name}:{number}"
        for path in root.rglob("*.py")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if "current_theme.variables" in line.split("#")[0]
    ]
    assert not offenders, f"components reading the theme directly: {offenders}"


@pytest.mark.asyncio
async def test_theme_flip_recolours_without_a_watcher() -> None:
    """The payoff: Textual re-resolves component styles on every repaint."""
    app = ShowcaseApp()
    async with app.run_test(size=(88, 26)) as pilot:
        app.push_screen(screens.ComponentScreen("status-line"))
        await pilot.pause()
        await pilot.pause()

        line = list(app.screen.query("StatusLine"))[0]
        dark = line.get_component_rich_style("statusline--mark").color

        await pilot.press("ctrl+t")
        await pilot.pause()
        await pilot.pause()

        light = line.get_component_rich_style("statusline--mark").color
        assert dark != light, "component style did not follow the theme"


# --------------------------------------------------------------------------
# Atomic hierarchy (ui/primitives -> ui/components -> ui/patterns)
# --------------------------------------------------------------------------


def test_layers_only_depend_downwards() -> None:
    """A layer may import from below it, never from above or sideways.

    This is what keeps the hierarchy real rather than a naming convention: if
    `components/` could import from `patterns/`, "atomic" would mean nothing.
    """
    import pathlib

    root = pathlib.Path(__file__).parent.parent / "src" / "reflection_ai_py_demo" / "ui"
    forbidden = {
        "primitives": ("..components", "..patterns", ".components", ".patterns"),
        "components": ("..patterns", ".patterns"),
        "patterns": (),
    }
    for layer, banned in forbidden.items():
        for path in (root / layer).glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in banned:
                assert f"from {token}" not in text, f"ui/{layer}/{path.name} imports upwards ({token})"


def test_primitives_and_components_do_not_compose() -> None:
    """The layer rule is mechanical: a `compose()` over our widgets = a pattern.

    Anything below `patterns/` must draw itself. This is the check that would
    have caught `Composer` and `Thinking` sitting among the atoms, which is the
    confusion this structure exists to remove.
    """
    import inspect

    from reflection_ai_py_demo.ui import components, primitives

    for module in (primitives, components):
        for name in module.__all__:
            obj = getattr(module, name)
            if not inspect.isclass(obj):
                continue
            source = inspect.getsource(obj)
            assert "def compose(" not in source, f"{name} composes other widgets - it belongs in ui/patterns/"


def test_patterns_actually_compose() -> None:
    """The converse: a pattern that composes nothing is really a component.

    A pattern is either a widget with `compose()`, or a helper that yields our
    widgets (`header`). Both arrange other components rather than drawing.
    """
    import inspect

    from reflection_ai_py_demo.ui import patterns

    for name in patterns.__all__:
        source = inspect.getsource(getattr(patterns, name))
        arranges = "def compose(" in source or "yield " in source
        assert arranges, f"{name} composes nothing - move it down a layer"


def test_every_surface_can_carry_body_text() -> None:
    """A background is only usable if text can sit on it.

    `bg_raised` on the light scheme was `slate_300` for a while, which put body
    text at 3.63:1 - and nothing caught it, because the contrast tests only
    checked `text` against `bg`. Any surface an element may use as a background
    has to hold text.
    """
    for scheme in (DARK, LIGHT):
        for surface in ("bg", "bg_subtle", "bg_raised", "input_bg"):
            ratio = _contrast(scheme.hex("text"), scheme.hex(surface))
            assert ratio >= 4.5, f"text on {surface} is {ratio:.2f}:1"


def test_raised_surface_sits_between_subtle_and_bg() -> None:
    """The three surfaces have to keep their order in both themes.

    `bg_subtle` recedes furthest from `bg`; `bg_raised` sits between them. On
    light this was violated for a while - `bg_raised` was `slate_300`, further
    from paper than `bg_subtle`, so the two swapped depth when the theme flipped
    and body text on the raised surface fell to 3.63:1.
    """

    def luminance(hex_colour: str) -> float:
        channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    for scheme in (DARK, LIGHT):
        base = luminance(scheme.hex("bg"))
        subtle = luminance(scheme.hex("bg_subtle"))
        raised = luminance(scheme.hex("bg_raised"))
        assert abs(subtle - base) > abs(raised - base) or raised > base, (
            "bg_raised should sit between bg_subtle and bg, or above bg entirely"
        )


# --------------------------------------------------------------------------
# No dead branches in the token layer
# --------------------------------------------------------------------------


def test_space_and_border_tables_are_published_to_css() -> None:
    """A token table nothing reads is a comment with syntax.

    `SPACE` and `BORDERS` sat unread for a long time while every stylesheet
    hardcoded its own numbers and border names - two sources of truth that
    agreed only by luck. They are published as CSS variables now, and this
    checks the wiring rather than trusting it.
    """
    from reflection_ai_py_demo.ui.theme import css_variables

    for scheme in (DARK, LIGHT):
        published = css_variables(scheme)
        for name in tokens.SPACE:
            assert f"space-{name}" in published, f"SPACE['{name}'] reaches no stylesheet"
        for name in tokens.BORDERS:
            assert f"rule-{name}" in published, f"BORDERS['{name}'] reaches no stylesheet"


def test_stylesheets_use_the_spacing_scale() -> None:
    """Spacing in a stylesheet should name a step, not a number.

    A bare `padding: 0 1` works, but it puts the scale in two places. The one
    exception is `0`, which needs no token.
    """
    import pathlib
    import re

    root = pathlib.Path(__file__).parent.parent / "src" / "reflection_ai_py_demo"
    offenders: list[str] = []
    pattern = re.compile(r"(padding|margin|margin-top|margin-bottom|margin-left|margin-right):\s*([^;]+);")
    for path in list(root.rglob("*.py")) + list(root.rglob("*.tcss")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = pattern.search(line)
            if not match:
                continue
            values = match.group(2).split()
            # A literal is fine only when it is zero - every other step is a token.
            if any(v.isdigit() and v != "0" for v in values):
                offenders.append(f"{path.name}:{number} {match.group(0).strip()}")
    assert not offenders, f"hardcoded spacing (use $space-*): {offenders}"


def test_no_ansi_fallback_is_claimed_anywhere() -> None:
    """We do not implement a 16-colour fallback, so nothing should say we do.

    Every `ColorToken` used to carry an ANSI name that no code path read, while
    the docs described it as a guaranteed fallback. Textual already degrades
    colour via `App.ansi_color`; a hand-maintained second mapping could only
    drift from it.
    """
    assert not hasattr(tokens.PALETTE.brand, "ansi"), "ColorToken grew an ansi field again"
    assert not hasattr(DARK, "ansi"), "Scheme grew an ansi() accessor again"
