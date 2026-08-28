"""Every component in the system, each with a self-contained preview.

One entry per component is the whole contract: adding a component to the
showcase means adding a row here, and the router does the rest. Previews stay
small on purpose - a route shows one at a time, which is what stops the app ever
rendering taller than the terminal.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Final, Literal

from textual.widget import Widget

from ..ui import (
    Badge,
    Composer,
    Divider,
    HStack,
    KeyHintBar,
    Panel,
    ProgressBar,
    Shimmer,
    Spinner,
    StatusLine,
    Surface,
    Text,
    Thinking,
)

Group = Literal["Primitives", "Feedback", "Motion", "Interactive"]


@dataclass(frozen=True, slots=True)
class Entry:
    """A component and the preview that sells it."""

    id: str
    name: str
    #: One line, shown beside the name in the list.
    summary: str
    group: Group
    #: Builds the preview. A factory rather than a value, because elements are
    #: single-use: mounting the same instance on a second visit would fail.
    render: Callable[[], Iterator[Widget]]


def _text_preview() -> Iterator[Widget]:
    yield Text("title - the loudest thing on screen", variant="title")
    yield Text("heading - groups a region", variant="heading")
    yield Text("label - uppercased metadata", variant="label")
    yield Text("body - the default reading tone", variant="body")
    yield Text("caption - dimmed secondary detail", variant="caption")
    yield Text(" ")
    yield HStack(
        Text("accent", tone="accent"),
        Text("success", tone="success"),
        Text("warning", tone="warning"),
        Text("danger", tone="danger"),
        Text("info", tone="info"),
        gap="sm",
    )


def _surface_preview() -> Iterator[Widget]:
    yield Surface(Text("subtle - round"), border="subtle")
    yield Surface(Text("solid - single"), border="solid")
    yield Surface(Text("strong - heavy, focused"), border="strong", focused=True)
    yield Surface(Text("emphasis - double"), border="emphasis")
    yield Text("Also: ascii, for consoles without box drawing.", variant="caption")


def _divider_preview() -> Iterator[Widget]:
    yield Divider()
    yield Divider(strong=True)
    yield Divider("labelled")
    yield Text("Fills the parent width.", variant="caption")


def _badge_preview() -> Iterator[Widget]:
    yield Text("subtle", variant="label")
    yield HStack(
        Badge("neutral"),
        Badge("accent", intent="accent"),
        Badge("success", intent="success"),
    )
    yield HStack(
        Badge("warning", intent="warning"),
        Badge("danger", intent="danger"),
        Badge("info", intent="info"),
    )
    yield Text("solid", variant="label")
    yield HStack(
        Badge("passed", intent="success", variant="solid"),
        Badge("failed", intent="danger", variant="solid"),
        Badge("queued", intent="neutral", variant="solid"),
    )


def _status_preview() -> Iterator[Widget]:
    yield StatusLine("Dependencies resolved", status="success", detail="11 packages")
    yield StatusLine("Type check passed", status="success")
    yield StatusLine("Two lint rules disabled", status="warning", detail="see config")
    yield StatusLine("Build failed", status="danger", detail="exit 1")
    yield StatusLine("Waiting for worker", status="pending")
    yield StatusLine("Cache is cold", status="info")


def _progress_preview() -> Iterator[Widget]:
    yield Text("determinate", variant="label")
    yield ProgressBar(progress=0.0)
    yield ProgressBar(progress=0.35)
    yield ProgressBar(progress=0.72)
    yield ProgressBar(progress=1.0)
    yield Text("unlabelled", variant="label")
    yield ProgressBar(progress=0.5, label=False, width=24)


def _spinner_preview() -> Iterator[Widget]:
    yield Text("Four frame sets, one shared tick rate.", variant="caption")
    yield Spinner("dots", variant="dots")
    yield Spinner("line", variant="line")
    yield Spinner("pulse", variant="pulse")
    yield Spinner("bar", variant="bar")


def _shimmer_preview() -> Iterator[Widget]:
    yield Text("A neutral lightness sweep - never a hue change.", variant="caption")
    yield Text(" ")
    yield Shimmer("Reading the repository")
    yield Shimmer("Planning the change")
    yield Shimmer("Applying edits")


def _thinking_preview() -> Iterator[Widget]:
    yield Text("Spinner plus shimmer - the agent's working state.", variant="caption")
    yield Text(" ")
    yield Thinking()
    yield Thinking("Searching the codebase")
    yield Thinking("Running tests")


def _composer_preview() -> Iterator[Widget]:
    yield Text("empty, unfocused", variant="label")
    yield Composer()
    yield Text("empty, focused", variant="label")
    yield Composer(focused=True)
    yield Text("with a value", variant="label")
    yield Composer("Refactor the theme layer", focused=True)


def _panel_preview() -> Iterator[Widget]:
    yield Panel(Text("Grouped content lives here."), title="Context")
    yield Panel(
        Text("An accented panel pulls focus."),
        title="Plan",
        accent=True,
    )


def _keyhint_preview() -> Iterator[Widget]:
    yield Text("The footer affordance.", variant="caption")
    yield Text(" ")
    yield KeyHintBar([("up/down", "move"), ("enter", "select"), ("esc", "back")])
    yield KeyHintBar([("tab", "next field"), ("ctrl+c", "quit")])


REGISTRY: Final[tuple[Entry, ...]] = (
    Entry("text", "Text", "type variants and semantic tones", "Primitives", _text_preview),
    Entry("surface", "Surface", "bordered region, border tokens", "Primitives", _surface_preview),
    Entry("divider", "Divider", "horizontal rule, optional label", "Primitives", _divider_preview),
    Entry("panel", "Panel", "titled surface for grouped content", "Primitives", _panel_preview),
    Entry("badge", "Badge", "status chip, 6 intents x 2 variants", "Feedback", _badge_preview),
    Entry("status-line", "Status line", "glyph, message, detail", "Feedback", _status_preview),
    Entry("progress-bar", "Progress bar", "determinate block-glyph bar", "Feedback", _progress_preview),
    Entry("spinner", "Spinner", "four indeterminate frame sets", "Motion", _spinner_preview),
    Entry("shimmer", "Shimmer", "travelling lightness highlight", "Motion", _shimmer_preview),
    Entry("thinking", "Thinking", "the agent working affordance", "Motion", _thinking_preview),
    Entry("composer", "Composer", "prompt input, three states", "Interactive", _composer_preview),
    Entry("key-hints", "Key hints", "footer key affordances", "Interactive", _keyhint_preview),
)

BY_ID: Final[dict[str, Entry]] = {entry.id: entry for entry in REGISTRY}
