from typing import Any

from libqtile import bar
from libqtile.config import Screen
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.hardware import connected_monitors
from custom.layouts import MARGIN
from custom.theme import (
    TEXT_FONT,
    colors,
)
from custom.widgets.arch import make_arch
from custom.widgets.claude import make_claude
from custom.widgets.core import (
    make_clock,
    make_display,
    make_group_box,
    make_layout_icon,
    make_tray,
    make_window_name,
)
from custom.widgets.hemara import make_hemara
from custom.widgets.media import (
    make_music,
    make_volume,
)
from custom.widgets.network import (
    make_net,
    make_wlan,
)
from custom.widgets.system import (
    make_battery,
    make_system,
)
from custom.widgets.toggles import (
    make_dnd,
    make_docker,
    make_picom,
    make_power,
)

BAR_HEIGHT = 28

WIDGET_DEFAULTS: dict[str, Any] = {
    "font": TEXT_FONT,
    "fontsize": 14,
    "padding": 2,
    "foreground": colors.text,
}


def make_bar(items: list[_Widget]) -> bar.Bar:
    return bar.Bar(
        [widget.Spacer(length=MARGIN), *items, widget.Spacer(length=MARGIN)],
        BAR_HEIGHT,
        background=colors.bg,
    )


def _primary_top() -> list[_Widget]:
    # With the monitor plugged in, the laptop bar shows these
    laptop_only = (
        [*make_display(), *make_battery(notify=True)]
        if connected_monitors() < 2
        else []
    )
    return [
        *make_arch(),
        *make_layout_icon(),
        *make_group_box(),
        widget.Spacer(),
        *make_clock(),
        widget.Spacer(),
        *make_hemara(),
        *make_picom(),
        *make_dnd(),
        *make_docker(),
        *make_claude(),
        *laptop_only,
        *make_music(),
        *make_volume(),
        *make_tray(),
    ]


def _primary_bottom() -> list[_Widget]:
    return [
        *make_wlan(),
        *make_net(),
        widget.Spacer(),
        *make_window_name(),
        widget.Spacer(),
        *make_power(),
        *make_system(),
    ]


def _laptop_top() -> list[_Widget]:
    return [
        *make_layout_icon(),
        *make_group_box(),
        widget.Spacer(),
        *make_clock(),
        widget.Spacer(),
        *make_display(),
        *make_battery(notify=True),
    ]


def build_screens() -> list[Screen]:
    """
    If there is only one physical screen, qtile uses only the first
    """
    return [
        Screen(top=make_bar(_primary_top()), bottom=make_bar(_primary_bottom())),
        Screen(top=make_bar(_laptop_top())),
    ]
