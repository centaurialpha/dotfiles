import os
import subprocess

from libqtile import bar
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration


def get_backlight_name() -> str:
    path = "/sys/class/backlight/intel_backlight/"
    bname = "intel_backlight"
    if not os.path.exists(path):
        bname = "amdgpu_bl1"
    return bname


def is_msi() -> bool:
    """Check if the machine is my msi or lenovo"""
    output = subprocess.check_output(["lspci"]).decode()
    return "GTX" in output


def _left_deco(color, px=None, py=4):
    return [
        RectDecoration(colour=color, radius=2, filled=True, padding_x=px, padding_y=py)
    ]


def _right_deco(color="#454545"):
    return [
        RectDecoration(colour=color, radius=2, filled=True, padding_x=2, padding_y=4)
    ]


def separator():
    return widget.Sep(linewidth=5, foreground="#1a1b26")


group_box = widget.GroupBox(
    fontsize=16,
    borderwidth=0,
    padding_x=5,
    padding_y=0,
    active="#7e57c2",
    block_highlight_text_color="#7e57c2",
    inactive="#111111",
    foreground="#ffffff",
    this_current_screen_border="#7e57c2",
    this_screen_border="#7e57c2",
    other_current_screen_border="#353446",
    other_screen_border="#353446",
    urgent_border="#ff5555",
    rounded=True,
    disable_drag=True,
)

clock = widget.Clock(format="[%b %d, %H:%M]")

w_display = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#f5c2e7"),
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
        foreground="#0ff0f0",
        fmt="<b>{}</b>",
        format="{name} {class}",
        max_chars=30,
        decorations=_right_deco(color="#010101"),
        padding=8,
        width=bar.CALCULATED,
    ),
)

w_layout = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#89dceb"),
        padding=6,
    ),
    widget.CurrentLayout(padding=8, foreground="#89dceb", decorations=_right_deco()),
)

w_volume = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        foreground="#111111",
        decorations=_left_deco(color="#eba0ac"),
        padding=6,
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
        padding=6,
    ),
    widget.ThermalSensor(
        decorations=_right_deco(),
        format="{temp:.0f}{unit}",
        padding=8,
        foreground="#f9e2af",
        update_interval=5,
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
        low_foreground="#ff0000",
        padding=6,
        update_interval=30,
        notify_below=10,
        notification_timeout=30,
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
        padding=6,
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

w_gpu = ()
if is_msi():
    w_gpu = (
        widget.TextBox(
            text="GPU",
            decorations=_left_deco(color="#76b900"),
            foreground="#ffffff",
            padding=6,
        ),
        widget.NvidiaSensors(
            update_interval=5.0,
            decorations=_right_deco(),
            padding=8,
            foreground="#ffffff",
        ),
        separator(),
    )

w_memory = (
    widget.TextBox(
        text="",
        font="Font Awesome 6 Free Solid",
        decorations=_left_deco(color="#a6e3a1"),
        foreground="#111111",
        padding=6,
    ),
    widget.Memory(
        decorations=_right_deco(),
        padding=8,
        format="{MemFree:.0f}{mm}",
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
        padding=6,
    ),
    widget.DF(
        decorations=_right_deco(),
        format="{r:.0f}%",
        foreground="#cba6f7",
        visible_on_warn=False,
        padding=8,
    ),
    separator(),
)

widgets = [
    *w_layout,
    group_box,
    widget.Spacer(),
    # *w_window_name,
    clock,
    widget.Spacer(),
    *w_display,
    *w_storage,
    *w_battery,
    *w_temperature,
    *w_memory,
    *w_cpu,
    *w_gpu,
    *w_volume,
    widget.Systray(),
]
