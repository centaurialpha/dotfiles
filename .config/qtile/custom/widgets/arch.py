import asyncio
import subprocess
from pathlib import Path
from typing import Any

from libqtile.lazy import lazy
from libqtile.widget.base import _Widget
from qtile_extras.widget.image import Image

from custom.theme import ICON_SIZE
from custom.widgets.blocks import (
    BLOCK_PADDING,
    separator,
)

UPGRADE_COMMAND = "st -e sh -c 'sudo pacman -Syu; read -p \"Press Enter to close\" _'"

# arch.svg lives at the config root, two levels above custom/widgets/
ARCH_LOGO = Path(__file__).resolve().parents[2] / "arch.svg"
ARCH_BLUE = "#1793d1"
LAUNCHER = 'j4-dmenu-desktop --no-generic -x --dmenu="dmenu -i" --usage-log=' + str(
    Path.home() / ".cache/j4-dmenu-desktop.log"
)

ARCH_UPDATES_COLOUR = "#ffa066"
UPDATES_INTERVAL = 1800
IMPORTANT_PACKAGES = frozenset({"linux", "linux-lts", "linux-zen", "qtile", "python"})
UPDATES_PILE_UP = 30


def needs_attention(pending: list[str]) -> bool:
    """
    Many pending updates or an important package among them
    """
    return len(pending) >= UPDATES_PILE_UP or not IMPORTANT_PACKAGES.isdisjoint(pending)


def pending_packages() -> list[str]:
    result = subprocess.run(
        ["checkupdates"], check=False, capture_output=True, text=True
    )
    # Each line: "name old_version -> new_version"
    return [line.split()[0] for line in result.stdout.splitlines() if line.strip()]


def has_updates() -> bool:
    return needs_attention(pending_packages())


class ArchLogo(Image):
    """
    Middle click runs pacman -Syu
    """

    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self.add_callbacks({"Button2": self.upgrade})

    def timer_setup(self) -> None:
        self._periodic_check()

    def _periodic_check(self) -> None:
        self.check()
        self.timeout_add(UPDATES_INTERVAL, self._periodic_check)

    def check(self) -> None:
        self.qtile.run_in_executor(has_updates).add_done_callback(self._paint)

    def _paint(self, future: asyncio.Future[bool]) -> None:
        self.colour = ARCH_UPDATES_COLOUR if future.result() else ARCH_BLUE
        self.draw()

    def upgrade(self) -> None:
        self.qtile.run_in_executor(
            lambda: subprocess.run(UPGRADE_COMMAND, shell=True, check=False)
        ).add_done_callback(lambda _: self.check())


def make_arch() -> list[_Widget]:
    return [
        ArchLogo(
            filename=str(ARCH_LOGO),
            mask=True,
            colour=ARCH_BLUE,
            margin_x=0,
            margin_y=(28 - ICON_SIZE) // 2,
            padding=BLOCK_PADDING,
            mouse_callbacks={
                "Button1": lazy.spawn(LAUNCHER),
            },
        ),
        separator(),
    ]
