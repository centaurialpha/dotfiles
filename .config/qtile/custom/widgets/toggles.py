import subprocess
from dataclasses import dataclass

from libqtile import qtile
from libqtile.core.manager import Qtile
from libqtile.lazy import lazy
from libqtile.widget.base import _Widget

from custom.theme import colors
from custom.widgets.blocks import (
    status_block,
    status_icon,
)
from custom.widgets.dbus import (
    DbusPropertyBlock,
    SystemdUnitBlock,
)

TOGGLE_REFRESH = 0.5


@dataclass(frozen=True)
class Toggle:
    """
    Runs a command and redraws its status widget, for things that do not signal
    over D-Bus
    """

    command: str
    widget_name: str

    @property
    def __name__(self) -> str:
        """
        lazy.function and display_kb expect a name like a function
        """
        return f"toggle_{self.widget_name}"

    def __call__(self, *_args: object) -> None:
        if not isinstance(qtile, Qtile):
            return
        qtile.spawn(self.command)
        status = qtile.widgets_map[self.widget_name]
        qtile.call_later(TOGGLE_REFRESH, status.force_update)


# Picom
PICOM_TOGGLE = "sh -c 'pkill -x picom || picom -b'"
PICOM_ICON = "\uea54"
picom_toggle = Toggle(PICOM_TOGGLE, "picom")


def picom_status() -> str:
    running = (
        subprocess.run(
            ["pgrep", "-x", "picom"], check=False, capture_output=True
        ).returncode
        == 0
    )
    return status_icon(PICOM_ICON, colors.ok if running else colors.inactive)


def make_picom() -> list[_Widget]:
    return list(status_block("picom", picom_status, None, picom_toggle))


# Do not disturb (dunst)
DND_TOGGLE = "dunstctl set-paused toggle"
BELL_ICON = "\ueab4"
BELL_OFF_ICON = "\ueab0"


def dnd_icon(paused: bool) -> str:
    if paused:
        return status_icon(BELL_OFF_ICON, colors.inactive)
    return status_icon(BELL_ICON, colors.ok)


def dnd_status() -> str:
    result = subprocess.run(
        ["dunstctl", "is-paused"], check=False, capture_output=True, text=True
    )
    return dnd_icon(result.stdout.strip() != "false")


def make_dnd() -> list[_Widget]:
    return list(
        status_block(
            "dnd",
            dnd_status,
            None,
            lazy.spawn(DND_TOGGLE),
            block_class=DbusPropertyBlock,
            path="/org/freedesktop/Notifications",
            prop="paused",
            render=dnd_icon,
            session_bus=True,
        )
    )


# Power profile
POWER_ICONS = {
    "power-saver": ("\ued50", colors.layout),
    "balanced": ("\ued4f", colors.ok),
    "performance": ("\ued4e", "#ffa066"),
}
POWER_PROFILES_PATH = "/org/freedesktop/UPower/PowerProfiles"
POWER_TOGGLE = (
    "sh -c 'case $(powerprofilesctl get) in"
    " balanced) powerprofilesctl set performance 2>/dev/null"
    " || powerprofilesctl set power-saver;;"
    " performance) powerprofilesctl set power-saver;;"
    " *) powerprofilesctl set balanced;; esac'"
)


def power_icon(profile: str) -> str:
    glyph, colour = POWER_ICONS.get(profile, ("\ued4f", colors.inactive))
    return status_icon(glyph, colour)


def power_status() -> str:
    result = subprocess.run(
        ["powerprofilesctl", "get"], check=False, capture_output=True, text=True
    )
    return power_icon(result.stdout.strip())


def make_power() -> list[_Widget]:
    return list(
        status_block(
            "power",
            power_status,
            None,
            lazy.spawn(POWER_TOGGLE),
            block_class=DbusPropertyBlock,
            path=POWER_PROFILES_PATH,
            prop="ActiveProfile",
            render=power_icon,
        )
    )


# Docker
DOCKER_BLUE = "#2496ed"
DOCKER_ICONS = {
    "active": ("\ueb77", DOCKER_BLUE),
    "activating": ("\ueb77", colors.layout),
    "deactivating": ("\ueb78", colors.layout),
    "failed": ("\ueb78", colors.fail),
}
DOCKER_UNIT_PATH = "/org/freedesktop/systemd1/unit/docker_2eservice"
DOCKER_TOGGLE = (
    "sh -c 'if systemctl is-active -q docker.service;"
    " then systemctl --no-ask-password stop docker.socket;"
    " systemctl --no-ask-password stop docker.service;"
    " else systemctl --no-ask-password start docker.service; fi'"
)


def docker_icon(state: str) -> str:
    glyph, colour = DOCKER_ICONS.get(state, ("\ueb78", colors.inactive))
    return status_icon(glyph, colour)


def docker_status() -> str:
    result = subprocess.run(
        ["systemctl", "is-active", "docker.service"],
        check=False,
        capture_output=True,
        text=True,
    )
    return docker_icon(result.stdout.strip())


def make_docker() -> list[_Widget]:
    return list(
        status_block(
            "docker",
            docker_status,
            None,
            lazy.spawn(DOCKER_TOGGLE),
            block_class=SystemdUnitBlock,
            unit_path=DOCKER_UNIT_PATH,
            render=docker_icon,
        )
    )
