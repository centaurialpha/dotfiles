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

from libqtile import bar
from libqtile.lazy import lazy
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

# Paleta Kanagawa sobre fondo negro, acento azul compartido con dmenu y st.
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
    # Un color apagado por categoría de widget.
    "device": "#c0a36e",
    "system": "#87a987",
    "network": "#8ea4a2",
    "media": "#957fb8",
}


# Íconos Pixelarticons (~/.local/share/fonts/pixelarticons.ttf), grilla de 24px mostrada a 16.
ICON_FONT = "pixelart-icons-font"
ICON_SIZE = 16
TEXT_FONT = "Input Mono"
# Baja el ícono dentro de un texto para centrarlo (en 1/1024 pt).
INLINE_ICON_RISE = -2048


def inline_icon(glyph: str) -> str:
    """
    Markup de un ícono dentro de un texto, del mismo tamaño que los bloques de ícono.
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


def is_msi() -> bool:
    """
    Check if the machine is my msi or lenovo.
    """
    output = subprocess.check_output(["lspci"]).decode()
    return "GTX" in output


# Radio de las esquinas externas de cada widget (0 = cuadrado).
RADIUS = 2
# Padding del ícono y del valor en cada pastilla; su suma es el hueco entre ambos.
VALUE_PADDING = 5
ICON_PADDING = 3


def _left_deco(color: str, radius: list[int] | None = None) -> list[RectDecoration]:
    """
    Bloque de color detrás del ícono, redondeado solo a la izquierda.
    """
    corners = radius or [RADIUS, 0, 0, RADIUS]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


# True: ícono oscuro sobre bloque de color. False: ícono de color sobre bloque gris.
FILLED_ICONS = False


def icon_block(color: str, radius: list[int] | None = None) -> dict[str, Any]:
    """
    Color, fondo y padding del bloque de ícono según FILLED_ICONS.
    """
    fill = color if FILLED_ICONS else colors["value_block"]
    style: dict[str, Any] = {
        "foreground": colors["icon_fg"] if FILLED_ICONS else color,
        "decorations": _left_deco(fill, radius),
    }
    # Solo la mitad izquierda de una pastilla; los bloques sueltos centran el ícono.
    if radius is None:
        style["padding"] = ICON_PADDING
    return style


def _right_deco(color: str = colors["value_block"]) -> list[RectDecoration]:
    """
    Bloque oscuro detrás del valor, redondeado solo a la derecha.
    """
    corners = [0, RADIUS, RADIUS, 0]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


def follow_icon(target: _TextBox, glyph: str, color: str) -> widget.GenPollText:
    """
    Bloque de ícono que se muestra solo mientras `target` tiene texto. Lee el
    atributo del widget, no consulta nada externo.
    """
    return widget.GenPollText(
        func=lambda: glyph if target.text else "",
        update_interval=1,
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(color),
    )


def follow_separator(target: _TextBox) -> widget.GenPollText:
    """
    Separador que desaparece junto con `target`, para no dejar un hueco doble.
    Es un espacio de texto: a 11px de Input Mono mide lo mismo que separator().
    """
    return widget.GenPollText(
        func=lambda: " " if target.text else "",
        update_interval=1,
        fontsize=11,
        padding=0,
    )


def separator() -> widget.Spacer:
    return widget.Spacer(length=7)


def make_group_box() -> widget.GroupBox:
    """
    GroupBox nuevo: qtile no deja usar la misma instancia en dos barras.
    """
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
    """
    Reloj que alterna de formato con clic izquierdo.
    """
    clock = widget.Clock(format=CLOCK_FORMATS[0])

    def toggle() -> None:
        short, full = CLOCK_FORMATS
        clock.format = full if clock.format == short else short
        clock.tick()

    clock.mouse_callbacks = {"Button1": toggle}
    return clock


w_display = (
    widget.TextBox(
        text="\uec5d",
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(colors["device"]),
    ),
    widget.Backlight(
        backlight_name=get_backlight_name(),
        change_command="brightnessctl set {0}%",
        decorations=_right_deco(),
        padding=VALUE_PADDING,
    ),
    separator(),
)

w_window_name = (
    widget.WindowName(
        format="{name}",
        # Sin ventanas no deja el bloque de fondo vacío.
        empty_group_string="",
        max_chars=80,
        decorations=_right_deco(),
        padding=VALUE_PADDING,
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

DND_TOGGLE = "dunstctl set-paused toggle"
BELL_ICON = "\ueab4"
BELL_OFF_ICON = "\ueab0"


def dnd_status() -> str:
    """
    Campana clara si dunst muestra notificaciones, tachada y gris si están pausadas.
    """
    result = subprocess.run(
        ["dunstctl", "is-paused"], check=False, capture_output=True, text=True
    )
    if result.stdout.strip() == "false":
        return _status_icon(BELL_ICON, colors["ok"])
    return _status_icon(BELL_OFF_ICON, colors["inactive"])


w_dnd = _status_block(dnd_status, 2, DND_TOGGLE)


def make_layout_icon() -> tuple[widget.CurrentLayout, widget.Spacer]:
    """
    Ícono del layout activo de la pantalla de su barra.
    """
    return (
        widget.CurrentLayout(
            mode="icon",
            use_mask=True,
            scale=0.6,
            padding=6,
            **icon_block(colors["layout"], radius=[RADIUS] * 4),
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
    # Clic y rueda vienen de qtile; clic derecho abre el mezclador.
    widget.Volume(
        decorations=_right_deco(),
        padding=VALUE_PADDING,
        update_interval=1,
        volume_app="pavucontrol",
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
        tag_sensor="Tctl",
        padding=VALUE_PADDING,
        update_interval=5,
    ),
    separator(),
)


def make_battery(notify: bool) -> tuple[widget.Battery, widget.Battery, widget.Spacer]:
    """
    Bloque de batería. Solo una barra debe avisar, si no llegan dos notificaciones.
    """
    return (
        widget.Battery(
            battery="BATT",
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
            update_interval=30,
            notify_below=10 if notify else None,
            notification_timeout=30,
        ),
        widget.Battery(
            battery="BATT",
            show_short_text=False,
            decorations=_right_deco(),
            padding=VALUE_PADDING,
            format="{percent:2.0%}",
            update_interval=30,
        ),
        separator(),
    )


# checkupdates trabaja sobre una copia de la base de pacman, no la del sistema.
UPGRADE_COMMAND = "st -e sh -c 'sudo pacman -Syu; read -p \"Enter para cerrar\" _'"

updates = widget.CheckUpdates(
    distro="Arch_checkupdates",
    update_interval=1800,
    display_format="{updates}",
    colour_have_updates=colors["text"],
    execute=UPGRADE_COMMAND,
    decorations=_right_deco(),
    padding=VALUE_PADDING,
)

w_updates = (
    follow_icon(updates, "\uecb9", colors["system"]),
    updates,
    follow_separator(updates),
)


def music_popup_layout() -> PopupRelativeLayout:
    """
    Panel de controles de Mpris2 con la paleta y la fuente de la barra.
    """
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


# Cualquier reproductor MPRIS. Clic pausa, rueda cambia de tema, clic derecho abre el panel.
# Cuadros por segundo del ecualizador: menos es más liviano pero menos fluido.
VISUALISER_FPS = 12

music = widget.Mpris2(
    objname=None,
    format="{xesam:artist} - {xesam:title}",
    playing_text="{track}",
    paused_text="{track} [pausa]",
    no_metadata_text="",
    # Tras recargar qtile, el primer evento no trae el tema.
    poll_interval=30,
    scroll=True,
    width=250,
    decorations=_right_deco(),
    padding=VALUE_PADDING,
    popup_layout=music_popup_layout(),
    popup_show_args={"relative_to": 3, "relative_to_bar": True},
    mouse_callbacks={"Button3": lazy.widget["mpris2"].toggle_player()},
)

# Ecualizador de cava entre el ícono y el texto. Solo corre mientras suena algo,
# porque cava y su proceso de dibujo consumen CPU todo el tiempo.
visualiser = widget.Visualiser(
    autostart=False,
    width=36,
    bars=6,
    spacing=2,
    bar_height=14,
    framerate=VISUALISER_FPS,
    bar_colour=colors["media"],
    decorations=[
        RectDecoration(colour=colors["value_block"], radius=0, filled=True, padding_y=3)
    ],
)


# Hueco gris entre ecualizador y texto. Va afuera del texto porque la marquesina
# se dibuja hasta el borde del widget e ignora el padding.
VISUALISER_GAP = 6
visualiser_gap = widget.Spacer(
    length=0,
    decorations=[
        RectDecoration(colour=colors["value_block"], radius=0, filled=True, padding_y=3)
    ],
)


@dataclass
class VisualiserSwitch:
    """
    Prende el ecualizador al reproducir, salvo que esté desactivado a mano.
    """

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

# Ícono aparte para que no se desplace con la marquesina. Clic prende o apaga el ecualizador.
music_icon = follow_icon(music, "\uecad", colors["media"])
music_icon.mouse_callbacks = {"Button1": visualiser_switch.toggle}

w_music = (
    music_icon,
    visualiser,
    visualiser_gap,
    music,
    follow_separator(music),
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
        padding=VALUE_PADDING,
        format="{load_percent:.0f}%",
    ),
    separator(),
)

w_gpu = ()
if is_msi():
    w_gpu = (
        widget.TextBox(
            text="GPU",
            **icon_block(colors["system"]),
        ),
        widget.NvidiaSensors(
            update_interval=5.0,
            decorations=_right_deco(),
            padding=VALUE_PADDING,
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
        padding=VALUE_PADDING,
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
        padding=VALUE_PADDING,
    ),
    separator(),
)

widgets = [
    *make_layout_icon(),
    make_group_box(),
    widget.Spacer(),
    make_clock(),
    widget.Spacer(),
    *w_hemara,
    *w_picom,
    *w_dnd,
    *w_display,
    *make_battery(notify=True),
    *w_music,
    *w_volume,
    widget.Systray(),
]

laptop_widgets = [
    *make_layout_icon(),
    make_group_box(),
    widget.Spacer(),
    make_clock(),
    widget.Spacer(),
    *make_battery(notify=False),
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
        padding=VALUE_PADDING,
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
    widget.Wlan(
        interface=WIFI,
        format="{essid} {percent:2.0%}",
        disconnected_message="offline",
        update_interval=30,
        decorations=_right_deco(),
        padding=VALUE_PADDING,
    ),
    separator(),
)

w_system = [
    # Primero, así al ocultarse no corre al resto.
    *w_updates,
    *w_temperature,
    *w_memory,
    *w_storage,
    *w_cpu,
    *w_gpu,
]
