import json
import math
import os
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

from libqtile import bar
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

# Paleta Kanagawa sobre fondo negro.
colors = {
    "bg": "#0a0a0a",
    "value_block": "#2a2a37",
    "text": "#dcd7ba",
    "inactive": "#54546d",
    "accent": "#957fb8",
    "accent_dim": "#54546d",
    "layout": "#98bb6c",
    "ok": "#dcd7ba",
    "fail": "#e46876",
    "icon_fg": "#0a0a0a",
    # Un color apagado por categoría de widget.
    "device": "#c0a36e",
    "system": "#87a987",
    "network": "#8ea4a2",
}


# Íconos Pixelarticons (~/.local/share/fonts/pixelarticons.ttf), grilla de 24px mostrada a 16.
ICON_FONT = "pixelart-icons-font"
ICON_SIZE = 16


def get_backlight_name() -> str:
    path = "/sys/class/backlight/intel_backlight/"
    bname = "intel_backlight"
    if not os.path.exists(path):
        bname = "amdgpu_bl1"
    return bname


def is_msi() -> bool:
    """
    Check if the machine is my msi or lenovo.
    """
    output = subprocess.check_output(["lspci"]).decode()
    return "GTX" in output


# Radio de las esquinas externas de cada widget (0 = cuadrado).
RADIUS = 2


def _left_deco(color: str, radius: list[int] | None = None) -> list[RectDecoration]:
    """
    Bloque de color detrás del ícono, redondeado solo a la izquierda.
    """
    corners = radius or [RADIUS, 0, 0, RADIUS]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


def _right_deco(color: str = colors["value_block"]) -> list[RectDecoration]:
    """
    Bloque oscuro detrás del valor, redondeado solo a la derecha.
    """
    corners = [0, RADIUS, RADIUS, 0]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


def separator() -> widget.Spacer:
    return widget.Spacer(length=7)


group_box = widget.GroupBox(
    fontsize=ICON_SIZE,
    font=ICON_FONT,
    borderwidth=0,
    padding_x=8,
    padding_y=3,
    active=colors["text"],
    block_highlight_text_color="#000000",
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

clock = widget.Clock(format="[%b %d, %H:%M]")

w_display = (
    widget.TextBox(
        text="\uec5d",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        decorations=_left_deco(colors["device"]),
        padding=6,
    ),
    widget.Backlight(
        backlight_name=get_backlight_name(),
        change_command="brightnessctl set {0}%",
        decorations=_right_deco(),
        padding=8,
    ),
    separator(),
)

w_window_name = (
    widget.WindowName(
        format="{name}",
        max_chars=80,
        decorations=_right_deco(),
        padding=8,
        width=bar.CALCULATED,
    ),
)

# Último resultado de cada monitor en Gatus (la Pi): no le pega a /health,
# Gatus ya lo chequea. Fuera de casa sin VPN queda en gris.
GATUS_URL = "http://uptime.home"
HEMARA_GROUPS = ("Producción", "Preproducción")
HEMARA_ICON = "\ued20"


def _status_icon(glyph: str, color: str) -> str:
    """
    Markup del ícono de estado pintado con el color dado.
    """
    return f'<span foreground="{color}">{glyph}</span>'


def _group_healthy(endpoints: list[dict], group: str) -> bool:
    """
    True si el grupo tiene resultados y el último de cada endpoint fue exitoso.
    """
    results = [
        e["results"][-1]["success"]
        for e in endpoints
        if e["group"] == group and e["results"]
    ]
    return bool(results) and all(results)


def fetch_endpoints() -> list[dict] | None:
    """
    Últimos resultados de Gatus, o None si no responde.
    """
    try:
        with urlopen(
            f"{GATUS_URL}/api/v1/endpoints/statuses?pageSize=1", timeout=5
        ) as resp:
            return json.load(resp)
    except (OSError, ValueError):
        return None


def hemara_icons(endpoints: list[dict] | None, blink_on: bool) -> str:
    """
    Un ícono de servidor por ambiente (prod, pre): claro si anda, gris apagado si
    no llega a Gatus y rojo titilando si falla.
    """
    icons = []
    for group in HEMARA_GROUPS:
        if endpoints is None:
            color = colors["inactive"]
        elif _group_healthy(endpoints, group):
            color = colors["ok"]
        else:
            color = colors["fail"] if blink_on else colors["inactive"]
        icons.append(_status_icon(HEMARA_ICON, color))
    # Sin separador: el margen del ícono alcanza y un espacio cae en otra fuente y se ve como un punto.
    return "".join(icons)


@dataclass
class HemaraPoller:
    """
    Consulta Gatus cada `refresh` segundos y en cada llamada alterna el titileo.
    El widget la llama seguido para animar; la red solo se usa al refrescar.
    """

    refresh: float = 60
    _endpoints: list[dict] | None = None
    _fetched_at: float = -math.inf

    def __call__(self) -> str:
        now = time.monotonic()
        if now - self._fetched_at >= self.refresh:
            self._endpoints = fetch_endpoints()
            self._fetched_at = now
        blink_on = int(now * 2) % 2 == 0
        return hemara_icons(self._endpoints, blink_on)


def _status_block(
    func: Callable[[], str], interval: float, command: str
) -> tuple[widget.GenPollText, widget.Spacer]:
    """
    Bloque de un solo ícono cuyo color refleja el estado, con acción al hacer clic.
    """
    return (
        widget.GenPollText(
            func=func,
            update_interval=interval,
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            padding=6,
            decorations=_left_deco(colors["value_block"], radius=[RADIUS] * 4),
            mouse_callbacks={"Button1": lazy.spawn(command)},
        ),
        separator(),
    )


# Se redibuja cada 0.5 s para el titileo; Gatus se consulta cada 60 s.
w_hemara = _status_block(HemaraPoller(), 0.5, f"xdg-open {GATUS_URL}")

PICOM_TOGGLE = "sh -c 'pkill -x picom || picom -b'"
PICOM_ICON = "\uea54"


def picom_status() -> str:
    """
    Ícono de ventana: claro si picom está corriendo, gris apagado si no.
    """
    running = (
        subprocess.run(
            ["pgrep", "-x", "picom"], check=False, capture_output=True
        ).returncode
        == 0
    )
    return _status_icon(PICOM_ICON, colors["ok"] if running else colors["inactive"])


w_picom = _status_block(picom_status, 2, PICOM_TOGGLE)

w_layout = (
    widget.CurrentLayout(
        mode="icon",
        use_mask=True,
        foreground=colors["icon_fg"],
        scale=0.6,
        padding=6,
        decorations=_left_deco(colors["layout"], radius=[RADIUS] * 4),
    ),
    separator(),
)

w_volume = (
    widget.TextBox(
        text="\uedeb",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        decorations=_left_deco(colors["device"]),
        padding=6,
    ),
    widget.Volume(
        decorations=_right_deco(),
        padding=8,
        update_interval=1,
    ),
    separator(),
)

w_temperature = (
    widget.TextBox(
        text="\uedae",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        decorations=_left_deco(colors["system"]),
        padding=6,
    ),
    widget.ThermalSensor(
        decorations=_right_deco(),
        format="{temp:.0f}{unit}",
        tag_sensor="Tctl",
        padding=8,
        update_interval=5,
    ),
    separator(),
)
w_battery = (
    widget.Battery(
        battery="BATT",
        show_short_text=False,
        decorations=_left_deco(colors["device"]),
        format="{char}",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        discharge_char="\ueaaa",
        charge_char="\uee0a",
        empty_char="\ueaa8",
        full_char="\ueaa6",
        not_charging_char="\ueaac",
        low_foreground=colors["fail"],
        padding=6,
        update_interval=30,
        notify_below=10,
        notification_timeout=30,
    ),
    widget.Battery(
        battery="BATT",
        show_short_text=False,
        decorations=_right_deco(),
        padding=8,
        format="{percent:2.0%}",
        update_interval=30,
    ),
    separator(),
)

w_cpu = (
    widget.TextBox(
        text="\ueb5b",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        decorations=_left_deco(colors["system"]),
        foreground=colors["icon_fg"],
        padding=6,
    ),
    widget.CPU(
        update_interval=5.0,
        decorations=_right_deco(),
        padding=8,
        format="{load_percent:.0f}%",
    ),
    separator(),
)

w_gpu = ()
if is_msi():
    w_gpu = (
        widget.TextBox(
            text="GPU",
            decorations=_left_deco(colors["system"]),
            foreground=colors["icon_fg"],
            padding=6,
        ),
        widget.NvidiaSensors(
            update_interval=5.0,
            decorations=_right_deco(),
            padding=8,
        ),
        separator(),
    )

w_memory = (
    widget.TextBox(
        text="\uec87",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        decorations=_left_deco(colors["system"]),
        foreground=colors["icon_fg"],
        padding=6,
    ),
    widget.Memory(
        decorations=_right_deco(),
        padding=8,
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
        decorations=_left_deco(colors["system"]),
        foreground=colors["icon_fg"],
        padding=6,
    ),
    widget.DF(
        decorations=_right_deco(),
        format="{r:.0f}%",
        visible_on_warn=False,
        padding=8,
    ),
    separator(),
)

widgets = [
    *w_layout,
    group_box,
    widget.Spacer(),
    clock,
    widget.Spacer(),
    *w_hemara,
    *w_picom,
    *w_display,
    *w_battery,
    *w_volume,
    widget.Systray(),
]


def wifi_interface() -> str:
    """
    Primera interfaz wireless en /sys/class/net, o wlan0 si no hay.
    """
    wireless = Path("/sys/class/net").glob("*/wireless")
    return next((path.parent.name for path in wireless), "wlan0")


WIFI = wifi_interface()

w_net = (
    widget.TextBox(
        text="\uea7c",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        decorations=_left_deco(colors["network"]),
        padding=6,
    ),
    widget.Net(
        interface=WIFI,
        format="{down:5.1f}{down_suffix:<2} {up:5.1f}{up_suffix:<2}",
        update_interval=5,
        decorations=_right_deco(),
        padding=8,
    ),
    separator(),
)

w_wlan = (
    widget.TextBox(
        text="\uee01",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        foreground=colors["icon_fg"],
        decorations=_left_deco(colors["network"]),
        padding=6,
    ),
    widget.Wlan(
        interface=WIFI,
        format="{essid} {percent:2.0%}",
        disconnected_message="offline",
        update_interval=30,
        decorations=_right_deco(),
        padding=8,
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
