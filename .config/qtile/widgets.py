import asyncio
import hashlib
import inspect
import json
import math
import os
import subprocess
import time
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import cairocffi
from dbus_fast import (
    BusType,
    Message,
)
from dbus_fast.aio import MessageBus
from libqtile import (
    bar,
    qtile,
)
from libqtile.core.manager import Qtile
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from libqtile.utils import (
    add_signal_receiver,
    rgb,
    send_notification,
)
from libqtile.widget.base import _TextBox
from qtile_extras import hook as extras_hook
from qtile_extras import widget
from qtile_extras.popup.templates.mpris2 import DEFAULT_LAYOUT
from qtile_extras.popup.toolkit import (
    PopupImage,
    PopupRelativeLayout,
    PopupSlider,
    PopupText,
)
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras.widget.image import Image
from qtile_extras.widget.mpris2widget import Mpris2
from qtile_extras.widget.visualiser import (
    CAVA_DRAW,
    Visualiser,
)

# Kanagawa sobre fondo negro
colors = {
    "bg": "#0a0a0a",
    "value_block": "#2a2a2a",
    "text": "#e8e8e8",
    "inactive": "#555555",
    "accent": "#4f66aa",
    "accent_dim": "#555555",
    "layout": "#98bb6c",
    "ok": "#e8e8e8",
    "fail": "#e46876",
    "icon_fg": "#0a0a0a",
    # Un color apagado por categoría de widget
    "device": "#c0a36e",
    "system": "#87a987",
    "network": "#8ea4a2",
    "media": "#957fb8",
}


# Íconos Pixelarticons (~/.local/share/fonts/pixelarticons.ttf)
ICON_FONT = "pixelart-icons-font"
ICON_SIZE = 16
TEXT_FONT = "Input Mono"
# Baja el ícono dentro de un texto para centrarlo (en 1/1024 pt)
INLINE_ICON_RISE = -2048


def inline_icon(glyph: str) -> str:
    """
    Markup de un ícono dentro de un texto
    """
    return (
        f'<span font="{ICON_FONT} {ICON_SIZE}px"'
        f' rise="{INLINE_ICON_RISE}">{glyph}</span>'
    )


def get_backlight_name() -> str:
    path = "/sys/class/backlight/intel_backlight/"
    bname = "intel_backlight"
    if not os.path.exists(path):
        bname = "amdgpu_bl1"
    return bname


def has_nvidia() -> bool:
    return Path("/sys/module/nvidia").exists()


def battery_name() -> str:
    for supply in sorted(Path("/sys/class/power_supply").iterdir()):
        scope = supply / "scope"
        is_device = scope.exists() and scope.read_text().strip() == "Device"
        if (supply / "type").read_text().strip() == "Battery" and not is_device:
            return supply.name
    return "BAT0"


def cpu_sensor_tag() -> str:
    names = {
        hwmon.read_text().strip() for hwmon in Path("/sys/class/hwmon").glob("*/name")
    }
    return "Tctl" if "k10temp" in names else "Package id 0"


def connected_monitors() -> int:
    return sum(
        status.read_text().strip() == "connected"
        for status in Path("/sys/class/drm").glob("card*-*/status")
    )


RADIUS = 2

MENU_STYLE: dict[str, Any] = {
    "menu_font": TEXT_FONT,
    "menu_fontsize": 13,
    "menu_foreground": colors["text"],
    "menu_foreground_disabled": colors["inactive"],
    "menu_background": colors["bg"],
    "menu_border": colors["accent"],
    "menu_border_width": 2,
    "highlight_colour": colors["accent"],
    "highlight_radius": RADIUS,
    "separator_colour": colors["inactive"],
}

BLOCK_PADDING = 6


def _left_deco(color: str, radius: list[int] | None = None) -> list[RectDecoration]:
    """
    Bloque de color detrás del ícono, redondeado solo a la izquierda
    """
    corners = radius or [RADIUS, 0, 0, RADIUS]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


FILLED_ICONS = False


def icon_block(color: str, radius: list[int] | None = None) -> dict[str, Any]:
    fill = color if FILLED_ICONS else colors["value_block"]
    style: dict[str, Any] = {
        "foreground": colors["icon_fg"] if FILLED_ICONS else color,
        "decorations": _left_deco(fill, radius),
    }
    # Solo la mitad izquierda de una pastilla; los bloques sueltos centran el ícono.
    if radius is None:
        style["padding"] = BLOCK_PADDING
    return style


def _right_deco(color: str = colors["value_block"]) -> list[RectDecoration]:
    corners = [0, RADIUS, RADIUS, 0]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


def follow_icon(target: _TextBox, glyph: str, color: str) -> widget.GenPollText:
    """
    Bloque de ícono que se muestra solo mientras `target` tiene texto
    """
    return widget.GenPollText(
        func=lambda: glyph if target.text else "",
        update_interval=None,
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(color),
    )


def follow_separator(target: _TextBox) -> widget.GenPollText:
    """
    Separador que desaparece junto con `target`, para no dejar un hueco doble
    """
    return widget.GenPollText(
        func=lambda: " " if target.text else "",
        update_interval=None,
        fontsize=11,
        padding=0,
    )


def separator() -> widget.Spacer:
    return widget.Spacer(length=7)


def make_group_box() -> widget.GroupBox:
    return widget.GroupBox(
        fontsize=ICON_SIZE,
        font=ICON_FONT,
        borderwidth=0,
        padding_x=8,
        padding_y=3,
        active=colors["text"],
        block_highlight_text_color=colors["text"],
        inactive=colors["inactive"],
        this_current_screen_border=colors["accent"],
        this_screen_border=colors["accent_dim"],
        other_current_screen_border=colors["accent_dim"],
        other_screen_border=colors["accent_dim"],
        urgent_border=colors["fail"],
        rounded=True,
        disable_drag=True,
        highlight_method="block",
    )


CLOCK_FORMATS = ("[%b %d, %H:%M]", "[%a %d/%m/%Y]")


def make_clock() -> widget.Clock:
    clock = widget.Clock(format=CLOCK_FORMATS[0], update_interval=60)

    def toggle() -> None:
        short, full = CLOCK_FORMATS
        clock.format = full if clock.format == short else short
        clock.tick()

    clock.mouse_callbacks = {"Button1": toggle}
    return clock


class BacklightBlock(widget.Backlight):
    async def _config_async(self) -> None:
        await super()._config_async()
        self._monitor = await asyncio.create_subprocess_exec(
            "udevadm",
            "monitor",
            "--udev",
            "--subsystem-match=backlight",
            stdout=asyncio.subprocess.PIPE,
        )
        self._watch = asyncio.create_task(self._on_events())

    async def _on_events(self) -> None:
        if self._monitor.stdout is None:
            return
        async for line in self._monitor.stdout:
            if b" change " in line:
                self.force_update()

    def finalize(self) -> None:
        self._watch.cancel()
        self._monitor.kill()
        super().finalize()


def make_display() -> tuple[widget.TextBox, BacklightBlock, widget.Spacer]:
    return (
        widget.TextBox(
            text="\uec5d",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors["device"]),
        ),
        BacklightBlock(
            backlight_name=get_backlight_name(),
            change_command="brightnessctl set {0}%",
            update_interval=None,
            decorations=_right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    )


w_window_name = (
    widget.WindowName(
        format="{name}",
        empty_group_string="",
        max_chars=80,
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
        width=bar.CALCULATED,
    ),
)

GATUS_URL = "http://uptime.home"
HEMARA_GROUPS = ("Producción", "Preproducción")
HEMARA_ICON = "\ued20"


def _status_icon(glyph: str, color: str) -> str:
    return f'<span foreground="{color}">{glyph}</span>'


def _group_healthy(endpoints: list[dict], group: str) -> bool:
    results = [
        e["results"][-1]["success"]
        for e in endpoints
        if e["group"] == group and e["results"]
    ]
    return bool(results) and all(results)


def fetch_endpoints() -> list[dict] | None:
    try:
        with urlopen(
            f"{GATUS_URL}/api/v1/endpoints/statuses?pageSize=1", timeout=5
        ) as resp:
            return json.load(resp)
    except (OSError, ValueError):
        return None


def hemara_icons(endpoints: list[dict] | None, blink_on: bool) -> str:
    icons = []
    for group in HEMARA_GROUPS:
        if endpoints is None:
            color = colors["inactive"]
        elif _group_healthy(endpoints, group):
            color = colors["ok"]
        else:
            color = colors["fail"] if blink_on else colors["inactive"]
        icons.append(_status_icon(HEMARA_ICON, color))
    return "".join(icons)


@dataclass
class HemaraPoller:
    """
    Consulta Gatus cada `refresh` segundos y en cada llamada alterna el "titileo"
    """

    refresh: float = 60
    blink: float = 0.5
    _endpoints: list[dict] | None = None
    _fetched_at: float = -math.inf

    def __call__(self) -> str:
        now = time.monotonic()
        if now - self._fetched_at >= self.refresh - 1:
            self._endpoints = fetch_endpoints()
            self._fetched_at = now
        blink_on = int(now * 2) % 2 == 0
        return hemara_icons(self._endpoints, blink_on)

    @property
    def failing(self) -> bool:
        endpoints = self._endpoints
        if endpoints is None:
            return False
        return not all(_group_healthy(endpoints, group) for group in HEMARA_GROUPS)

    def next_interval(self) -> float:
        return self.blink if self.failing else self.refresh


class HemaraBlock(widget.GenPollText):
    def poll(self) -> str:
        text = super().poll()
        if isinstance(self.func, HemaraPoller):
            self.update_interval = self.func.next_interval()
        return text


def _status_block(
    name: str,
    func: Callable[[], str],
    interval: float | None,
    on_click: Any,
    block_class: type[widget.GenPollText] = widget.GenPollText,
) -> tuple[widget.GenPollText, widget.Spacer]:
    return (
        block_class(
            name=name,
            func=func,
            update_interval=interval,
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            padding=BLOCK_PADDING,
            decorations=_left_deco(colors["value_block"], radius=[RADIUS] * 4),
            mouse_callbacks={"Button1": on_click},
        ),
        separator(),
    )


TOGGLE_REFRESH = 0.5


@dataclass(frozen=True)
class Toggle:
    command: str
    widget_name: str

    def __call__(self, *_args: object) -> None:
        if not isinstance(qtile, Qtile):
            return
        qtile.spawn(self.command)
        status = qtile.widgets_map[self.widget_name]
        qtile.call_later(TOGGLE_REFRESH, status.force_update)


w_hemara = _status_block(
    "hemara",
    HemaraPoller(),
    0.5,
    lazy.spawn(f"xdg-open {GATUS_URL}"),
    block_class=HemaraBlock,
)

PICOM_TOGGLE = "sh -c 'pkill -x picom || picom -b'"
PICOM_ICON = "\uea54"


def picom_status() -> str:
    running = (
        subprocess.run(
            ["pgrep", "-x", "picom"], check=False, capture_output=True
        ).returncode
        == 0
    )
    return _status_icon(PICOM_ICON, colors["ok"] if running else colors["inactive"])


picom_toggle = Toggle(PICOM_TOGGLE, "picom")
w_picom = _status_block("picom", picom_status, None, picom_toggle)

DND_TOGGLE = "dunstctl set-paused toggle"
BELL_ICON = "\ueab4"
BELL_OFF_ICON = "\ueab0"


def dnd_status() -> str:
    result = subprocess.run(
        ["dunstctl", "is-paused"], check=False, capture_output=True, text=True
    )
    return dnd_icon(result.stdout.strip() != "false")


def dnd_icon(paused: bool) -> str:
    if paused:
        return _status_icon(BELL_OFF_ICON, colors["inactive"])
    return _status_icon(BELL_ICON, colors["ok"])


class DndBlock(widget.GenPollText):
    async def _config_async(self) -> None:
        await super()._config_async()
        await add_signal_receiver(
            self._on_change,
            session_bus=True,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path="/org/freedesktop/Notifications",
        )

    def _on_change(self, message: Message) -> None:
        _interface, changed, _invalidated = message.body
        if "paused" in changed:
            self.update(dnd_icon(changed["paused"].value))


w_dnd = _status_block(
    "dnd", dnd_status, None, lazy.spawn(DND_TOGGLE), block_class=DndBlock
)

POWER_ICONS = {
    "power-saver": ("\ued50", colors["layout"]),
    "balanced": ("\ued4f", colors["ok"]),
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
    glyph, colour = POWER_ICONS.get(profile, ("\ued4f", colors["inactive"]))
    return _status_icon(glyph, colour)


def power_status() -> str:
    result = subprocess.run(
        ["powerprofilesctl", "get"], check=False, capture_output=True, text=True
    )
    return power_icon(result.stdout.strip())


class PowerProfileBlock(widget.GenPollText):
    async def _config_async(self) -> None:
        await super()._config_async()
        await add_signal_receiver(
            self._on_change,
            session_bus=False,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path=POWER_PROFILES_PATH,
        )

    def _on_change(self, message: Message) -> None:
        _interface, changed, _invalidated = message.body
        if "ActiveProfile" in changed:
            self.update(power_icon(changed["ActiveProfile"].value))


w_power = _status_block(
    "power",
    power_status,
    None,
    lazy.spawn(POWER_TOGGLE),
    block_class=PowerProfileBlock,
)

DOCKER_BLUE = "#2496ed"
DOCKER_ICONS = {
    "active": ("\ueb77", DOCKER_BLUE),
    "activating": ("\ueb77", colors["layout"]),
    "deactivating": ("\ueb78", colors["layout"]),
    "failed": ("\ueb78", colors["fail"]),
}
DOCKER_UNIT_PATH = "/org/freedesktop/systemd1/unit/docker_2eservice"
DOCKER_TOGGLE = (
    "sh -c 'if systemctl is-active -q docker.service;"
    " then systemctl --no-ask-password stop docker.socket;"
    " systemctl --no-ask-password stop docker.service;"
    " else systemctl --no-ask-password start docker.service; fi'"
)


def docker_icon(state: str) -> str:
    glyph, colour = DOCKER_ICONS.get(state, ("\ueb78", colors["inactive"]))
    return _status_icon(glyph, colour)


def docker_status() -> str:
    result = subprocess.run(
        ["systemctl", "is-active", "docker.service"],
        check=False,
        capture_output=True,
        text=True,
    )
    return docker_icon(result.stdout.strip())


class DockerBlock(widget.GenPollText):
    async def _config_async(self) -> None:
        await super()._config_async()
        self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        await self._bus.call(
            Message(
                destination="org.freedesktop.systemd1",
                path="/org/freedesktop/systemd1",
                interface="org.freedesktop.systemd1.Manager",
                member="Subscribe",
            )
        )
        await add_signal_receiver(
            self._on_change,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path=DOCKER_UNIT_PATH,
            use_bus=self._bus,
            preserve=True,
        )

    def _on_change(self, message: Message) -> None:
        _interface, changed, _invalidated = message.body
        if "ActiveState" in changed:
            self.update(docker_icon(changed["ActiveState"].value))

    def finalize(self) -> None:
        self._bus.disconnect()
        super().finalize()


w_docker = _status_block(
    "docker",
    docker_status,
    None,
    lazy.spawn(DOCKER_TOGGLE),
    block_class=DockerBlock,
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
    "waiting": ("■", colors["fail"]),
    "working": ("■", CLAUDE_ORANGE),
    "done": ("■", CLAUDE_IDLE),
}
CLAUDE_STALE = 12 * 3600
CLAUDE_SIGNAL_PATH = "/dev/gabox/Claude"
CLAUDE_SIGNAL_INTERFACE = "dev.gabox.Claude"


def claude_accounts() -> tuple[str, ...]:
    if (Path.home() / f".claude-{CLAUDE_WORK}").is_dir():
        return (CLAUDE_PERSONAL, CLAUDE_WORK)
    return (CLAUDE_PERSONAL,)


def claude_states(account: str) -> list[str]:
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
    label: str
    used: int
    resets_at: int
    show_from: int

    def current_used(self, now: float) -> int:
        if self.used < 0:
            return -1
        return 0 if now >= self.resets_at else self.used


def claude_usage(account: str) -> list[UsageWindow]:
    try:
        fields = (CLAUDE_USAGE_DIR / account).read_text().split()
        u5, r5, u7, r7 = (int(field) for field in fields)
    except (FileNotFoundError, ValueError):
        return []
    return [UsageWindow("5h", u5, r5, 0), UsageWindow("7d", u7, r7, 30)]


def usage_color(used: int) -> str:
    if used >= 85:
        return colors["fail"]
    if used >= 60:
        return "#ffa066"
    return colors["text"]


def usage_markup(windows: list[UsageWindow], now: float) -> str:
    parts = []
    for window in windows:
        used = window.current_used(now)
        if used < 0 or used < window.show_from:
            continue
        label = _status_icon(window.label, colors["inactive"])
        parts.append(f"{label} {_status_icon(f'{100 - used}%', usage_color(used))}")
    return " ".join(parts)


def claude_status(account: str) -> str:
    states = claude_states(account)
    squares = "".join(_status_icon(*CLAUDE_STYLES[s]) for s in states)
    parts = (
        _status_icon(CLAUDE_WORK_LABEL, colors["inactive"])
        if account == CLAUDE_WORK
        else "",
        squares or _status_icon("■", colors["inactive"]),
        usage_markup(claude_usage(account), time.time()),
    )
    return " ".join(part for part in parts if part)


class ClaudeBlock(widget.GenPollText):
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


w_claude = (
    ClaudeBlock(
        claude_accounts(),
        name="claude",
        update_interval=None,
        font=TEXT_FONT,
        padding=BLOCK_PADDING,
        decorations=_left_deco(colors["value_block"], radius=[RADIUS] * 4),
    ),
    separator(),
)


def make_layout_icon() -> tuple[widget.CurrentLayout, widget.Spacer]:
    return (
        widget.CurrentLayout(
            mode="icon",
            use_mask=True,
            scale=0.6,
            padding=BLOCK_PADDING,
            foreground=colors["layout"],
        ),
        separator(),
    )


w_volume = (
    widget.TextBox(
        text="\uedeb",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["device"]),
    ),
    widget.PulseVolume(
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
        volume_app="pavucontrol",
        **MENU_STYLE,
    ),
    separator(),
)

w_temperature = (
    widget.TextBox(
        text="\uedae",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["system"]),
    ),
    widget.ThermalSensor(
        decorations=_right_deco(),
        format="{temp:.0f}{unit}",
        tag_sensor=cpu_sensor_tag(),
        padding=BLOCK_PADDING,
        update_interval=5,
    ),
    separator(),
)


UPOWER_DISPLAY_DEVICE = "/org/freedesktop/UPower/devices/DisplayDevice"


class BatteryBlock(widget.Battery):
    async def _config_async(self) -> None:
        await super()._config_async()
        await add_signal_receiver(
            self._on_change,
            session_bus=False,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path=UPOWER_DISPLAY_DEVICE,
        )

    def _on_change(self, _message: Message) -> None:
        self.force_update()


BATTERY = battery_name()


def make_battery(
    notify: bool,
) -> tuple[BatteryBlock, BatteryBlock, widget.Spacer]:
    return (
        BatteryBlock(
            battery=BATTERY,
            show_short_text=False,
            **icon_block(colors["device"]),
            format="{char}",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            discharge_char="\ueaaa",
            charge_char="\uee0a",
            empty_char="\ueaa8",
            full_char="\ueaa6",
            not_charging_char="\ueaac",
            low_foreground=colors["fail"],
            update_interval=None,
            notify_below=10 if notify else None,
            notification_timeout=30,
        ),
        BatteryBlock(
            battery=BATTERY,
            show_short_text=False,
            decorations=_right_deco(),
            padding=BLOCK_PADDING,
            format="{percent:2.0%}",
            update_interval=None,
        ),
        separator(),
    )


UPGRADE_COMMAND = "st -e sh -c 'sudo pacman -Syu; read -p \"Enter para cerrar\" _'"

ARCH_LOGO = Path(__file__).with_name("arch.svg")
ARCH_BLUE = "#1793d1"
LAUNCHER = (
    'j4-dmenu-desktop --no-generic -x --dmenu="dmenu -i" --usage-log='
    + os.path.expanduser("~/.cache/j4-dmenu-desktop.log")
)


ARCH_UPDATES_COLOUR = "#ffa066"
UPDATES_INTERVAL = 1800
IMPORTANT_PACKAGES = frozenset({"linux", "linux-lts", "linux-zen", "qtile", "python"})
UPDATES_PILE_UP = 30


def needs_attention(pending: list[str]) -> bool:
    return len(pending) >= UPDATES_PILE_UP or not IMPORTANT_PACKAGES.isdisjoint(pending)


def pending_packages() -> list[str]:
    result = subprocess.run(
        ["checkupdates"], check=False, capture_output=True, text=True
    )
    # Cada línea: "nombre versión_vieja -> versión_nueva".
    return [line.split()[0] for line in result.stdout.splitlines() if line.strip()]


def has_updates() -> bool:
    return needs_attention(pending_packages())


class ArchLogo(Image):
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


w_arch = (
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
)


def music_popup_layout() -> PopupRelativeLayout:
    controls = deepcopy(DEFAULT_LAYOUT.controls)
    for control in controls:
        control.highlight = colors["accent"]
        if isinstance(control, PopupText):
            control.font = TEXT_FONT
            control.foreground = colors["text"]
        elif isinstance(control, PopupSlider):
            control.colour_below = colors["accent"]
            control.colour_above = colors["inactive"]
        elif isinstance(control, PopupImage) and control.mask:
            control.colour = colors["text"]
    return PopupRelativeLayout(
        None,
        width=400,
        height=200,
        controls=controls,
        background=colors["bg"],
        border=colors["accent"],
        border_width=2,
        highlight=colors["accent"],
        close_on_click=False,
    )


UPSTREAM_HASH = "f916c85cbb305b5fc2fb35396858ef4d2c3cd99d0e3ffda9bbe6aefb8cfe24c5"
UPSTREAM_NOTIFY_ID = 4242


def upstream_hash() -> str:
    parts = [
        inspect.getsource(Visualiser._draw),
        CAVA_DRAW.read_text(),
        inspect.getsource(Mpris2._config_async),
        inspect.getsource(Mpris2._check_player),
        inspect.getsource(Mpris2._send_message),
    ]
    return hashlib.sha256("".join(parts).encode()).hexdigest()


def warn_upstream(message: str) -> None:
    send_notification("widgets.py", message, timeout=0, id_=UPSTREAM_NOTIFY_ID)


def check_upstream() -> None:
    current = upstream_hash()
    if current == UPSTREAM_HASH:
        return
    logger.warning("widgets.py: hash nuevo de código privado: %s", current)
    warn_upstream(
        "qtile o qtile-extras cambiaron código que pisan el ecualizador o la"
        " música. Si andan bien, copiá el hash nuevo del log de qtile a"
        " UPSTREAM_HASH."
    )


MPRIS_PREFIX = "org.mpris.MediaPlayer2."


class RunningPlayerMpris2(Mpris2):
    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self.followers: list[widget.GenPollText] = []

    def update(self, text: str) -> None:
        super().update(text)
        for follower in self.followers:
            if follower.configured:
                follower.force_update()

    async def _config_async(self) -> None:
        await super()._config_async()
        if self.objname is not None:
            return
        try:
            await self._attach_running_player()
        except (AttributeError, TypeError, IndexError):
            logger.exception("RunningPlayerMpris2: no se pudo buscar el reproductor")
            warn_upstream("la música no pudo buscar el reproductor al arrancar.")

    async def _attach_running_player(self) -> None:
        reply = await self._send_message(
            "org.freedesktop.DBus",
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            "ListNames",
            "",
            [],
        )
        players = [name for name in reply.body[0] if name.startswith(MPRIS_PREFIX)]
        for name in players:
            self._current_player = name
            await self._check_player()
            if self.is_playing:
                return


VISUALISER_FPS = 12

music = RunningPlayerMpris2(
    name="mpris2",
    objname=None,
    format="{xesam:artist} - {xesam:title}",
    playing_text="{track}",
    paused_text="{track} [pausa]",
    no_metadata_text="",
    poll_interval=30,
    scroll=True,
    width=250,
    decorations=_right_deco(),
    padding=BLOCK_PADDING,
    popup_layout=music_popup_layout(),
    popup_show_args={"relative_to": 3, "relative_to_bar": True},
    mouse_callbacks={"Button3": lazy.widget["mpris2"].toggle_player()},
)

VISUALISER_COLOURS = (
    colors["media"],
    "#7e9cd8",
    colors["network"],
    colors["system"],
    colors["layout"],
    colors["device"],
)


class StripedVisualiser(Visualiser):
    def __init__(self, colours: tuple[str, ...], **config: Any) -> None:
        super().__init__(**config)
        self._gradient: cairocffi.LinearGradient | None = None
        try:
            self._gradient = self._stripes(colours)
        except AttributeError:
            logger.exception("StripedVisualiser: no se pudieron armar las franjas")

    def _stripes(self, colours: tuple[str, ...]) -> cairocffi.LinearGradient:
        width = self._config_length
        slot = width // self.bars
        pad = (width - slot * self.bars) // 2
        gradient = cairocffi.LinearGradient(0, 0, width, 0)
        for i in range(self.bars):
            colour = rgb(colours[i % len(colours)])
            gradient.add_color_stop_rgba((pad + i * slot) / width, *colour)
            gradient.add_color_stop_rgba((pad + (i + 1) * slot) / width, *colour)
        return gradient

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        if self._gradient is None:
            warn_upstream("no se pudieron armar las franjas, quedó de un solo color.")
            return
        check_upstream()

    def _draw(self) -> None:
        if self._gradient is None:
            super()._draw()
            return
        try:
            self._draw_striped(self._gradient)
        except (AttributeError, TypeError, ValueError, cairocffi.CairoError):
            logger.exception("StripedVisualiser: falló el dibujo, uso el original")
            self._gradient = None
            warn_upstream("falló el dibujo por barra, quedó de un solo color.")
            super()._draw()

    def _draw_striped(self, gradient: cairocffi.LinearGradient) -> None:
        if self._shm is None:
            return
        with self._take_lock():
            surface = cairocffi.ImageSurface.create_for_data(
                bytearray(self._shm[: self._shm_size]),
                cairocffi.FORMAT_ARGB32,
                self._config_length,
                self.bar_height,
            )
        self.drawer.clear(self.background or self.bar.background)
        self.drawer.ctx.set_source(gradient)
        self.drawer.ctx.mask_surface(surface, 0, self.y_offset)
        self.draw_at_default_position()
        self._timer = self.timeout_add(self._interval, self.loop)


visualiser = StripedVisualiser(
    VISUALISER_COLOURS,
    autostart=False,
    bar_colour=colors["media"],
    width=36,
    bars=6,
    spacing=2,
    bar_height=14,
    framerate=VISUALISER_FPS,
    decorations=[
        RectDecoration(colour=colors["value_block"], radius=0, filled=True, padding_y=3)
    ],
)


VISUALISER_GAP = 6
visualiser_gap = widget.Spacer(
    length=0,
    decorations=[
        RectDecoration(colour=colors["value_block"], radius=0, filled=True, padding_y=3)
    ],
)


@dataclass
class VisualiserSwitch:
    visualiser: widget.Visualiser
    gap: widget.Spacer
    player: widget.Mpris2
    enabled: bool = True

    def on_status(self, status: str) -> None:
        running = self.enabled and status == "Playing"
        if running:
            self.visualiser.start()
        else:
            self.visualiser.stop()
        self.gap.length = VISUALISER_GAP if running else 0
        self.gap.bar.draw()

    def toggle(self) -> None:
        self.enabled = not self.enabled
        self.on_status("Playing" if self.player.is_playing else "Paused")


visualiser_switch = VisualiserSwitch(visualiser, visualiser_gap, music)
extras_hook.subscribe.mpris_status_change(visualiser_switch.on_status)

music_icon = follow_icon(music, "\uecad", colors["media"])
music_icon.mouse_callbacks = {"Button1": visualiser_switch.toggle}
music_separator = follow_separator(music)
music.followers = [music_icon, music_separator]

w_music = (
    music_icon,
    visualiser,
    visualiser_gap,
    music,
    music_separator,
)

SYSTEM_MONITOR = "st -e htop"

w_cpu = (
    widget.TextBox(
        text="\ueb5b",
        mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["system"]),
    ),
    widget.CPU(
        mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
        update_interval=5.0,
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
        format="{load_percent:.0f}%",
    ),
    separator(),
)

w_gpu = ()
if has_nvidia():
    w_gpu = (
        widget.TextBox(
            text="GPU",
            **icon_block(colors["system"]),
        ),
        widget.NvidiaSensors(
            update_interval=5.0,
            decorations=_right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    )

w_memory = (
    widget.TextBox(
        text="\uec87",
        mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["system"]),
    ),
    widget.Memory(
        mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
        format="{Available:.1f}{mm}",
        measure_mem="G",
        update_interval=5,
    ),
    separator(),
)

w_storage = (
    widget.TextBox(
        text="\ued0e",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["system"]),
    ),
    widget.DF(
        decorations=_right_deco(),
        format="{r:.0f}%",
        visible_on_warn=False,
        padding=BLOCK_PADDING,
    ),
    separator(),
)

widgets = [
    *w_arch,
    *make_layout_icon(),
    make_group_box(),
    widget.Spacer(),
    make_clock(),
    widget.Spacer(),
    *w_hemara,
    *w_picom,
    *w_dnd,
    *w_docker,
    *w_claude,
    *(
        (*make_display(), *make_battery(notify=True))
        if connected_monitors() < 2
        else ()
    ),
    *w_music,
    *w_volume,
    widget.StatusNotifier(
        icon_size=ICON_SIZE,
        padding=BLOCK_PADDING,
        decorations=_left_deco(colors["value_block"], radius=[RADIUS] * 4),
        **MENU_STYLE,
    ),
]

laptop_widgets = [
    *make_layout_icon(),
    make_group_box(),
    widget.Spacer(),
    make_clock(),
    widget.Spacer(),
    *make_display(),
    *make_battery(notify=True),
]


def wifi_interface() -> str:
    wireless = Path("/sys/class/net").glob("*/wireless")
    return next((path.parent.name for path in wireless), "wlan0")


WIFI = wifi_interface()

IWD_STATION = "net.connman.iwd.Station"
WLAN_SIGNAL_INTERVAL = 300


class WlanBlock(widget.Wlan):
    async def _config_async(self) -> None:
        await super()._config_async()
        await add_signal_receiver(
            self._on_change,
            session_bus=False,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            bus_name="net.connman.iwd",
        )

    def _on_change(self, message: Message) -> None:
        if message.body[0] == IWD_STATION:
            self.force_update()


w_net = (
    widget.TextBox(
        text="\uea7c",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["network"]),
    ),
    widget.Net(
        interface=WIFI,
        format=inline_icon("\uea6d")
        + "{down:4.1f}{down_suffix:<2} "
        + inline_icon("\uea7a")
        + "{up:4.1f}{up_suffix:<2}",
        update_interval=5,
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
    ),
    separator(),
)

w_wlan = (
    widget.TextBox(
        text="\uee01",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["network"]),
    ),
    WlanBlock(
        interface=WIFI,
        format="{essid} {percent:2.0%}",
        disconnected_message="offline",
        update_interval=WLAN_SIGNAL_INTERVAL,
        decorations=_right_deco(),
        padding=BLOCK_PADDING,
    ),
    separator(),
)

w_system = [
    *w_temperature,
    *w_memory,
    *w_storage,
    *w_cpu,
    *w_gpu,
]
