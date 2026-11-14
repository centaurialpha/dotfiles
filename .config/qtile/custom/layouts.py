from typing import Any

from libqtile import layout
from libqtile.config import Match
from libqtile.layout.base import Layout

from custom.theme import colors

MARGIN = 5
BORDER_WIDTH = 2

LAYOUT_KWARGS: dict[str, Any] = {
    "border_focus": colors.accent,
    "border_normal": colors.inactive,
    "border_width": BORDER_WIDTH,
    "margin": MARGIN,
}


def build_layouts() -> list[Layout]:
    return [
        layout.Stack(**LAYOUT_KWARGS, num_stacks=1),
        layout.Columns(**LAYOUT_KWARGS, border_on_single=True),
        layout.MonadTall(**LAYOUT_KWARGS),
        layout.Bsp(**LAYOUT_KWARGS, border_on_single=True),
    ]


def build_floating_layout() -> layout.Floating:
    return layout.Floating(
        border_focus=colors.accent,
        border_normal=colors.inactive,
        border_width=BORDER_WIDTH,
        float_rules=[
            # Run the utility of `xprop` to see the wm class and name of an X client.
            # default_float_rules include: utility, notification, toolbar, splash,
            # dialog, file_progress, confirm, download and error
            *layout.Floating.default_float_rules,
            Match(wm_type="dialog"),
            Match(title="pritunl"),
            Match(wm_class="webcam"),
        ],
    )
