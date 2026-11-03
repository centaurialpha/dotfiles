import os
import subprocess

from libqtile import (
    bar,
    hook,
    layout,
    widget,
)
from libqtile.backend.base import Window
from libqtile.config import (
    Click,
    Drag,
    DropDown,
    Group,
    Key,
    Match,
    ScratchPad,
    Screen,
)
from libqtile.core.manager import Qtile
from libqtile.lazy import lazy

from widgets import (
    PICOM_TOGGLE,
    colors,
    w_net,
    w_system,
    w_window_name,
    w_wlan,
    widgets,
)

mod = "mod1"  # mod1=Alt;mod2=;mod3=;mod4=super
terminal = "st"  # Suckless st
# terminal = "kitty"

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="fullscreen jejej"),
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
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload config"),
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
    Key([mod], "c", lazy.spawn(PICOM_TOGGLE), desc="Toggle picom"),
]


groups = [
    Group(name="dev", label="\ued95"),
    Group(
        name="browser",
        label="\uebc6",
        matches=[Match(wm_class="firefox"), Match(wm_class="qutebrowser")],
    ),
    Group(name="slack", label="\uec93", matches=[Match(wm_class="slack")]),
    Group(name="spotify", label="\uecad"),
    Group(
        name="claude", label="\ued05", matches=[Match(wm_class="com.anthropic.Claude")]
    ),
]


def go_to_group(qtile: Qtile, name: str) -> None:
    """
    Muestra el grupo en la pantalla actual. Si ya se ve en la otra pantalla,
    enfoca esa pantalla en vez de intercambiar los grupos entre monitores.
    """
    group = qtile.groups_map[name]
    if group.screen is not None and group.screen is not qtile.current_screen:
        qtile.focus_screen(group.screen.index)
        return
    group.toscreen()


for i, group in enumerate(groups, 1):
    keys.append(Key([mod], str(i), lazy.function(go_to_group, group.name)))
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
    "border_focus": colors["accent"],
    "border_normal": colors["inactive"],
    "border_width": 2,
    "margin": 5,
}
layouts = [
    layout.Stack(**LAYOUT_KWARGS, num_stacks=1),
    layout.Columns(**LAYOUT_KWARGS, border_on_single=True),
    layout.MonadTall(**LAYOUT_KWARGS),
    layout.Bsp(**LAYOUT_KWARGS, border_on_single=True),
]

widget_defaults = {
    "font": "Input Mono",
    "fontsize": 14,
    "padding": 2,
    "foreground": colors["text"],
}
extension_defaults = widget_defaults.copy()


all_widgets = widgets.copy()
top_primary = bar.Bar(all_widgets, 28, background=colors["bg"])
bottom_widgets = [
    *w_wlan,
    *w_net,
    widget.Spacer(),
    *w_window_name,
    widget.Spacer(),
    *w_system,
]
bottom_bar = bar.Bar(bottom_widgets, 28, background=colors["bg"])

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
dgroups_app_rules: list = []
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
        # Match(wm_class="pinentry-qt"),
        # Match(wm_class="main.py"),
        Match(wm_type="dialog"),
        Match(title="pritunl"),
    ]
)


@hook.subscribe.startup_once
def autostart() -> None:
    autostart_script = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.call([autostart_script])


@hook.subscribe.client_name_updated
def move_spotify(client: Window) -> None:
    """
    Spotify setea WM_CLASS después de mapear la ventana, así que Group.matches no la agarra.
    """
    # ponytail: corre en cada cambio de título; si movés Spotify a mano, vuelve sola al cambiar de tema.
    if client.group is None or client.group.name == "spotify":
        return
    if client.match(Match(wm_class="spotify")):
        client.togroup("spotify")


def list_monitors() -> dict:
    try:
        result = subprocess.run(
            ["xrandr", "--listmonitors"], capture_output=True, text=True, check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError:
        return {"count": 0, "monitors": [], "error": "Error ejecutando xrandr"}
    except FileNotFoundError:
        return {"count": 0, "monitors": [], "error": "xrandr no encontrado"}

    lines = output.strip().split("\n")

    monitor_count = 0
    if lines and lines[0].startswith("Monitors"):
        monitor_count = int(lines[0].split(":")[1].strip())

    monitors = []

    for line in lines[1:]:
        if line.strip():
            parts = line.strip().split()

            index = int(parts[0].rstrip(":"))
            name = parts[1].lstrip("+*")

            resolution = parts[2]
            is_primary = "*" in parts[1]

            info = {
                "index": index,
                "name": name,
                "resolution": resolution,
                "is_primary": is_primary,
            }

            monitors.append(info)

    return {
        "count": monitor_count,
        "monitors": monitors,
    }


def init_screens() -> list[Screen]:
    monitors_data = list_monitors()

    if "error" in monitors_data:
        return [Screen(top=top_primary, bottom=bottom_bar)]

    monitors = monitors_data["monitors"]

    edp, hdmi = None, None

    for monitor in monitors:
        if "eDP" in monitor["name"]:
            edp = monitor
        elif "HDMI" in monitor["name"]:
            hdmi = monitor

    if edp is None or hdmi is None:
        return [Screen(top=top_primary, bottom=bottom_bar)]

    xrandr_cmd = [
        "xrandr",
        "--output",
        edp["name"],
        "--mode",
        "1920x1080",
        "--output",
        hdmi["name"],
        "--mode",
        "1920x1080",
        "--primary",
        "--left-of",
        edp["name"],
    ]

    try:
        subprocess.run(xrandr_cmd, check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error configurando xrandr: {e}")

    return [
        Screen(top=top_primary, bottom=bottom_bar),
        Screen(),
    ]


@hook.subscribe.client_new
def force_float(client: Window) -> None:
    if (
        client.match(Match(wm_class="pritunl"))
        or "pritunl" in (client.name or "").lower()
    ):
        client.enable_floating()
        # client.place(100, 100, 200, 300, 2)


screens = init_screens()
