"""Prototype flows - scripted, frame-by-frame walkthroughs.

A component preview answers "what does this look like". A flow answers the
harder question: "what does the product feel like as it moves". Each flow is an
ordered list of frames the reviewer steps through with the arrow keys, so the
sequence can be judged at whatever pace the conversation needs.

Frames are plain data. Nothing here runs a real agent - the point is to review
the choreography, not to execute anything.

Composers in a flow are deliberately left unfocused. Now that `Composer` wraps
a real `Input`, a focused one captures the arrow keys as cursor movement and
the reader can no longer step the flow with them. Flows are for watching; the
Composer preview in the component library is where you type.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Final

from textual.widget import Widget

from ..ui import (
    Badge,
    Composer,
    Divider,
    HStack,
    Panel,
    ProgressBar,
    StatusLine,
    Text,
    Thinking,
)


@dataclass(frozen=True, slots=True)
class Frame:
    """One step of a flow."""

    #: Shown above the frame, so the reviewer knows what they are looking at.
    caption: str
    build: Callable[[], Iterator[Widget]]


@dataclass(frozen=True, slots=True)
class Flow:
    """A named sequence of frames."""

    id: str
    name: str
    summary: str
    frames: tuple[Frame, ...]


# --------------------------------------------------------------------------
# Flow: a task from prompt to result
# --------------------------------------------------------------------------


def _task_idle() -> Iterator[Widget]:
    yield Text("Reflection", variant="title", tone="accent_strong")
    yield Text("Ready.", variant="caption")
    yield Text(" ")
    yield Composer()


def _task_typed() -> Iterator[Widget]:
    yield Text("Reflection", variant="title", tone="accent_strong")
    yield Text("Ready.", variant="caption")
    yield Text(" ")
    yield Composer("Add a retry to the upload client")


def _task_thinking() -> Iterator[Widget]:
    yield Text("Add a retry to the upload client", variant="heading")
    yield Divider()
    yield Thinking("Reading the repository")


def _task_planning() -> Iterator[Widget]:
    yield Text("Add a retry to the upload client", variant="heading")
    yield Divider()
    yield Panel(
        Text("1. Wrap the request in a backoff loop"),
        Text("2. Surface attempts on the status line"),
        Text("3. Cover the retry path with a test"),
        title="Plan",
        accent=True,
    )
    yield Text(" ")
    yield Thinking("Applying edits")


def _task_working() -> Iterator[Widget]:
    yield Text("Add a retry to the upload client", variant="heading")
    yield Divider()
    yield StatusLine("Wrap the request in a backoff loop", status="success")
    yield StatusLine("Surface attempts on the status line", status="success")
    yield StatusLine("Cover the retry path with a test", status="pending")
    yield Text(" ")
    yield ProgressBar(progress=0.66)


def _task_done() -> Iterator[Widget]:
    yield HStack(
        Text("Add a retry to the upload client", variant="heading"),
        Badge("done", intent="success", variant="solid"),
    )
    yield Divider()
    yield StatusLine("Wrap the request in a backoff loop", status="success")
    yield StatusLine("Surface attempts on the status line", status="success")
    yield StatusLine("Cover the retry path with a test", status="success")
    yield Text(" ")
    yield StatusLine("3 files changed", status="info", detail="+48 -6")
    yield Text(" ")
    yield Composer()


TASK_FLOW: Final = Flow(
    id="task",
    name="Task run",
    summary="prompt to plan to result",
    frames=(
        Frame("Idle. The composer waits and nothing else competes.", _task_idle),
        Frame("The prompt is typed. Caret marks the insertion point.", _task_typed),
        Frame("Work starts. The prompt becomes the heading.", _task_thinking),
        Frame("A plan lands before any edit - the accent panel pulls focus.", _task_planning),
        Frame("Steps resolve one at a time, with progress underneath.", _task_working),
        Frame("Done. The summary persists and the composer returns.", _task_done),
    ),
)


# --------------------------------------------------------------------------
# Flow: something goes wrong
# --------------------------------------------------------------------------


def _error_running() -> Iterator[Widget]:
    yield Text("Run the test suite", variant="heading")
    yield Divider()
    yield StatusLine("Collecting tests", status="success", detail="142 found")
    yield Text(" ")
    yield Thinking("Running tests")


def _error_failed() -> Iterator[Widget]:
    yield HStack(
        Text("Run the test suite", variant="heading"),
        Badge("failed", intent="danger", variant="solid"),
    )
    yield Divider()
    yield StatusLine("Collecting tests", status="success", detail="142 found")
    yield StatusLine("3 tests failed", status="danger", detail="upload_client")
    yield Text(" ")
    yield Panel(
        Text("assert response.status == 200", variant="code"),
        Text("AssertionError: got 503", variant="code", tone="danger"),
        title="tests/test_upload.py:88",
    )


def _error_recovered() -> Iterator[Widget]:
    yield Text("Run the test suite", variant="heading")
    yield Divider()
    yield StatusLine("Retried with backoff", status="success", detail="attempt 2")
    yield StatusLine("142 tests passed", status="success")
    yield Text(" ")
    yield Composer()


ERROR_FLOW: Final = Flow(
    id="error",
    name="Failure and recovery",
    summary="how the system reports a problem",
    frames=(
        Frame("A run in progress. Nothing signals trouble yet.", _error_running),
        Frame("Failure. The badge, the status line, and the excerpt agree.", _error_failed),
        Frame("Recovered. The failure is gone, not merely greyed out.", _error_recovered),
    ),
)


# --------------------------------------------------------------------------
# Flow: approving a change
# --------------------------------------------------------------------------


def _approval_asked() -> Iterator[Widget]:
    yield Text("Delete the legacy exporter", variant="heading")
    yield Divider()
    yield Panel(
        Text("This removes 4 files and 1,208 lines."),
        Text("The change cannot be undone from here.", tone="warning"),
        title="Confirm",
        accent=True,
    )
    yield Text(" ")
    yield HStack(
        Badge("y  approve", intent="success"),
        Badge("n  cancel", intent="neutral"),
    )


def _approval_declined() -> Iterator[Widget]:
    yield Text("Delete the legacy exporter", variant="heading")
    yield Divider()
    yield StatusLine("Cancelled. Nothing was changed.", status="info")
    yield Text(" ")
    yield Composer()


APPROVAL_FLOW: Final = Flow(
    id="approval",
    name="Approval gate",
    summary="a destructive action asks first",
    frames=(
        Frame("The ask. Consequence stated before the keys are offered.", _approval_asked),
        Frame("Declined. The outcome is stated plainly, then dismissed.", _approval_declined),
    ),
)


FLOWS: Final[tuple[Flow, ...]] = (TASK_FLOW, ERROR_FLOW, APPROVAL_FLOW)
BY_ID: Final[dict[str, Flow]] = {flow.id: flow for flow in FLOWS}
