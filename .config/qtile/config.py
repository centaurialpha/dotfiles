import os
import subprocess
from typing import List  # noqa: F401

from libqtile import bar, hook, layout, widget
from libqtile.config import Click, Drag, DropDown, Group, Key, Match, ScratchPad, Screen
from libqtile.lazy import lazy

from widgets import w_window_name, widgets

mod = "mod1"  # mod1=Alt;mod2=;mod3=;mod4=super
terminal = "st"  # Suckless st

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key(
        [mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"
    ),
    Key(
        [mod, "shift"],
        "l",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key(
        [mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"
    ),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "m", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    # Key(
    #     [mod, "shift"],
    #     "Return",
    #     lazy.layout.toggle_split(),
    #     desc="Toggle between split and unsplit sides of stack",
    # ),
    Key([mod, "shift"], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "c", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    # Key([mod], "d", lazy.spawn("dmenu_run -c -l 10 -bw 2")),
    Key(
        [mod],
        "p",
        lazy.spawn("rofi -i -show drun -modi drun -show-icons -display-drun ''"),
    ),
    Key(
        ["control", "shift"],
        "a",
        lazy.spawn(
            'rofi -show power-menu -modi "power-menu:~/.rofi-scripts/power-menu --dry-run --choices=shutdown/reboot/logout"'
        ),
    ),
    Key([mod], "n", lazy.next_screen()),
]


groups = [
    Group(name="dev", label="󰏃"),
    Group(name="slack", label="󰏃"),
    Group(name="browser", label="󰏃"),
    Group(name="sys", label="󰏃"),
    Group(name="vbox", label="󰏃"),
]
for i, group in enumerate(groups, 1):
    keys.append(Key([mod], str(i), lazy.group[group.name].toscreen()))
    keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(group.name)))


groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown("term", "st", width=0.6, height=0.5, x=0.2, y=0.1, opacity=1),
        ],
    )
)

keys.extend(
    [
        Key(["control"], "1", lazy.group["scratchpad"].dropdown_toggle("term")),
    ]
)

LAYOUT_KWARGS = {
    "border_focus": "#957FB8",
    "border_normal": "#717C7C",
    "border_width": 2,
    "margin": 5,
}
layouts = [
    layout.Stack(**LAYOUT_KWARGS, num_stacks=1),
    layout.Bsp(**LAYOUT_KWARGS, border_on_single=True),
    layout.Columns(**LAYOUT_KWARGS, border_on_single=True),
    layout.Floating(**LAYOUT_KWARGS),
    layout.Matrix(columns=2, **LAYOUT_KWARGS),
    layout.Tile(**LAYOUT_KWARGS),
    layout.MonadTall(**LAYOUT_KWARGS),
    layout.MonadThreeCol(**LAYOUT_KWARGS),
    layout.MonadWide(**LAYOUT_KWARGS),
    layout.Max(**LAYOUT_KWARGS),
    layout.RatioTile(**LAYOUT_KWARGS),
    layout.Spiral(**LAYOUT_KWARGS),
    layout.TreeTab(**LAYOUT_KWARGS),
    layout.VerticalTile(**LAYOUT_KWARGS),
]

widget_defaults = dict(
    font="IBM Plex Mono Text",
    fontsize=15,
    padding=2,
)
extension_defaults = widget_defaults.copy()

all_widgets = widgets.copy()
top_primary = bar.Bar(all_widgets, 30, background="#121212")
bottom_widgets = [
    widget.Net(update_interval=5),
    widget.Spacer(),
    *w_window_name,
    widget.Spacer(),
    widget.Wlan(update_interval=30),
]
bottom_bar = bar.Bar(bottom_widgets, 26, background="#121212")
screens = [Screen(top=top_primary, bottom=bottom_bar)]

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button1", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
respect_minimize_requests = True

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
wmname = "qtile"


floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        # default_float_rules include: utility, notification, toolbar, splash, dialog,
        # file_progress, confirm, download and error.
        *layout.Floating.default_float_rules,
        # Match(title="ESPlorer v0.2.0 by 4refr0nt"),
        Match(wm_class="pinentry-qt"),
        Match(wm_class="main.py"),
    ]
)


def switch_screens(qtile):
    i = qtile.screens.index(qtile.current_screen)
    group = qtile.screens[i - 1].group
    qtile.current_screen.set_group(group)


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.call([autostart_script])


@hook.subscribe.client_new
def on_client_new(client):
    if client.name in ("qutebrowser", "firefox"):
        client.togroup("browser")


def get_connected_monitors() -> list[str]:
    # FIXME: con qtile.conn.pseudomonitors era un toque más rápido
    # FIXME: pero dejó de andar(?
    xrandr_cmd = "xrandr | grep -w 'connected' | cut -d ' ' -f 1"
    output = subprocess.check_output(xrandr_cmd, shell=True)
    return output.decode().split()


def init_secondary_screen():
    monitors = get_connected_monitors()
    if len(monitors) > 1:
        second_screen_widgets = [
            widget.Spacer(length=bar.STRETCH),
            all_widgets[3],  # clock
            widget.Spacer(length=bar.STRETCH),
        ]
        top_secondary = bar.Bar(second_screen_widgets, 24, background="#111111")
        screens.append(Screen(top=top_secondary))

        edp, hdmi = monitors
        xrandr_cmd_str = (
            f"xrandr --output {edp} --mode 1920x1080 "
            f"--output {hdmi} --mode 1920x1080 --primary "
            f"--left-of {edp}"
        )
        xrandr_cmd = xrandr_cmd_str.split()
        subprocess.Popen(xrandr_cmd)


if __name__ in ("config", "__main__"):
    init_secondary_screen()
