"""
Claude Code sessions and usage, read from the files the hooks write.

The hooks send a D-Bus signal on every change, so the widget does not poll.
"""

import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dbus_fast import Message
from libqtile.utils import add_signal_receiver
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.theme import (
    TEXT_FONT,
    colors,
)
from custom.widgets.blocks import (
    BLOCK_PADDING,
    RADIUS,
    left_deco,
    separator,
    status_icon,
)

CLAUDE_RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
CLAUDE_STATE_DIR = CLAUDE_RUNTIME / "claude-state"
CLAUDE_USAGE_DIR = CLAUDE_RUNTIME / "claude-usage"
CLAUDE_PERSONAL = "personal"
CLAUDE_WORK = "invera"
CLAUDE_WORK_LABEL = "inv"
CLAUDE_ORANGE = "#d77757"
CLAUDE_IDLE = "#9a9a9a"
CLAUDE_STYLES = {
    "waiting": ("■", colors.fail),
    "working": ("■", CLAUDE_ORANGE),
    "done": ("■", CLAUDE_IDLE),
}
CLAUDE_STALE = 12 * 3600
CLAUDE_SIGNAL_PATH = "/dev/gabox/Claude"
CLAUDE_SIGNAL_INTERFACE = "dev.gabox.Claude"


def claude_accounts() -> tuple[str, ...]:
    """
    The work account only if its config folder exists.
    """
    if (Path.home() / f".claude-{CLAUDE_WORK}").is_dir():
        return (CLAUDE_PERSONAL, CLAUDE_WORK)
    return (CLAUDE_PERSONAL,)


def claude_states(account: str) -> list[str]:
    """
    Recent session states, most urgent first.
    """
    folder = CLAUDE_STATE_DIR / account
    if not folder.is_dir():
        return []
    cutoff = time.time() - CLAUDE_STALE
    states = []
    for path in folder.iterdir():
        try:
            if path.stat().st_mtime > cutoff:
                states.append(path.read_text().strip())
        except FileNotFoundError:
            continue
    urgency = list(CLAUDE_STYLES)
    return sorted((s for s in states if s in CLAUDE_STYLES), key=urgency.index)


@dataclass(frozen=True, slots=True)
class UsageWindow:
    """
    A usage window (5h or 7d): percent used and reset time.
    """

    label: str
    used: int
    resets_at: int
    show_from: int

    def current_used(self, now: float) -> int:
        if self.used < 0:
            return -1
        return 0 if now >= self.resets_at else self.used


def claude_usage(account: str) -> list[UsageWindow]:
    """
    Usage as written by the statusline script.
    """
    try:
        fields = (CLAUDE_USAGE_DIR / account).read_text().split()
        u5, r5, u7, r7 = (int(field) for field in fields)
    except (FileNotFoundError, ValueError):
        return []
    return [UsageWindow("5h", u5, r5, 0), UsageWindow("7d", u7, r7, 30)]


def usage_color(used: int) -> str:
    if used >= 85:
        return colors.fail
    if used >= 60:
        return "#ffa066"
    return colors.text


def usage_markup(windows: list[UsageWindow], now: float) -> str:
    """
    Remaining percent of each window above its show threshold.
    """
    parts = []
    for window in windows:
        used = window.current_used(now)
        if used < 0 or used < window.show_from:
            continue
        label = status_icon(window.label, colors.inactive)
        parts.append(f"{label} {status_icon(f'{100 - used}%', usage_color(used))}")
    return " ".join(parts)


def claude_status(account: str) -> str:
    states = claude_states(account)
    squares = "".join(status_icon(*CLAUDE_STYLES[s]) for s in states)
    parts = (
        status_icon(CLAUDE_WORK_LABEL, colors.inactive)
        if account == CLAUDE_WORK
        else "",
        squares or status_icon("■", colors.inactive),
        usage_markup(claude_usage(account), time.time()),
    )
    return " ".join(part for part in parts if part)


class ClaudeBlock(widget.GenPollText):
    """
    One square per session plus remaining usage; click switches account.
    """

    def __init__(self, accounts: tuple[str, ...], **config: Any) -> None:
        super().__init__(**config)
        self.accounts = accounts
        self.account = accounts[0]
        self._reset_timer: asyncio.TimerHandle | None = None
        self.add_callbacks({"Button1": self.next_account})

    async def _config_async(self) -> None:
        await super()._config_async()
        await add_signal_receiver(
            self._on_signal,
            session_bus=True,
            signal_name="Changed",
            dbus_interface=CLAUDE_SIGNAL_INTERFACE,
            path=CLAUDE_SIGNAL_PATH,
        )

    def _on_signal(self, _message: Message) -> None:
        self.force_update()

    def next_account(self) -> None:
        index = self.accounts.index(self.account)
        self.account = self.accounts[(index + 1) % len(self.accounts)]
        self.force_update()

    def poll(self) -> str:
        return claude_status(self.account)

    def update(self, text: str) -> None:
        super().update(text)
        if self._reset_timer is not None:
            self._reset_timer.cancel()
        now = time.time()
        windows = claude_usage(self.account)
        upcoming = [w.resets_at for w in windows if w.resets_at > now]
        self._reset_timer = (
            self.timeout_add(min(upcoming) - now + 1, self.force_update)
            if upcoming
            else None
        )


def make_claude() -> list[_Widget]:
    return [
        ClaudeBlock(
            claude_accounts(),
            name="claude",
            update_interval=None,
            font=TEXT_FONT,
            padding=BLOCK_PADDING,
            decorations=left_deco(colors.value_block, radius=[RADIUS] * 4),
        ),
        separator(),
    ]
