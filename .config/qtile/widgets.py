from libqtile import bar

from qtile_extras import widget
from qtile_extras.widget import decorations
from qtile_extras.widget.decorations import PowerLineDecoration, RectDecoration


def _left_deco(color, px=None, py=4):
    return [
        RectDecoration(colour=color, radius=2, filled=True, padding_x=px, padding_y=py)
    ]


def _right_deco(color="#454545"):
    return [
        RectDecoration(
            colour=color, radius=2, filled=True, padding_x=2, padding_y=4
        )
    ]


def separator():
    return widget.Sep(linewidth=5, foreground="#1a1b26")


group_box = widget.GroupBox(
    borderwidth=1,
    padding_y=4,
    padding_x=5,
    highlight_method="block",
    urgent_alert_method="block",
    this_current_screen_border="#7e57c2",
    this_screen_border="#bd93f9",
    other_current_screen_border="#7e57c2",
    block_highlight_text_color="#000000",
    urgent_border="#ff5555",
)

clock = widget.Clock(format="[%b %d, %H:%M]")
# light = widget.Backlight(
#     backlight_name="intel_backlight", change_command="light -S {0:.0f}"
# )

w_window_name = (
    widget.WindowName(
        foreground="#0ff0f0",
        format="{class} - {name}",
        max_chars=100,
        decorations=_right_deco(color="#010101"),
        padding=8,
    ),
)

w_layout = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#89dceb"),
    ),
    widget.CurrentLayout(padding=8, foreground="#89dceb", decorations=_right_deco()),
)

w_volume = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#eba0ac"),
    ),
    widget.Volume(
        decorations=_right_deco(),
        padding=8,
        foreground="#eba0ac",
    ),
    separator(),
)

w_temperature = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#f9e2af"),
        padding=10,
    ),
    widget.ThermalSensor(
        decorations=_right_deco(), padding=8, foreground="#f9e2af", update_interval=5
    ),
    separator(),
)
w_battery = (
    widget.Battery(
        decorations=_left_deco(color="#89b4fa"),
        format="{char}",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        discharge_char="",
        charge_char="",
        empty_char="",
        full_char="",
        low_background="#ff0000",
        padding=5,
        update_interval=30,
    ),
    widget.Battery(
        decorations=_right_deco(),
        padding=8,
        foreground="#89b4fa",
        format="{percent:2.0%}",
        update_interval=30,
    ),
    separator(),
)

w_cpu = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        decorations=_left_deco(color="#fab387"),
        foreground="#111111",
        padding=5,
    ),
    widget.CPU(
        update_interval=5.0,
        decorations=_right_deco(),
        padding=8,
        format="{freq_current}GHz",
        foreground="#fab387",
    ),
    separator(),
)

w_memory = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        decorations=_left_deco(color="#a6e3a1"),
        foreground="#111111",
    ),
    widget.Memory(
        decorations=_right_deco(),
        padding=8,
        format="{MemFree:.2f}{mm}",
        foreground="#a6e3a1",
        measure_mem="G",
        update_interval=5,
    ),
    separator(),
)

w_storage = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        decorations=_left_deco(color="#cba6f7"),
        foreground="#111111",
        padding=5,
    ),
    widget.DF(
        decorations=_right_deco(),
        format="{uf}{m}|{r:.0f}%",
        foreground="#cba6f7",
        visible_on_warn=False,
        padding=8,
    ),
    separator(),
)

widgets = [
    group_box,
    *w_window_name,
    clock,
    widget.Spacer(),
    *w_temperature,
    *w_battery,
    *w_storage,
    *w_cpu,
    *w_memory,
    *w_volume,
    *w_layout,
    widget.Systray(),
]
