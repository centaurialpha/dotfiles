from libqtile.config import (
    Click,
    Drag,
    Group,
    Key,
    ScratchPad,
)
from libqtile.lazy import lazy

from custom.groups import go_to_group
from custom.widgets.arch import LAUNCHER
from custom.widgets.toggles import (
    DOCKER_TOGGLE,
    picom_toggle,
)

MOD = "mod1"  # Alt
TERMINAL = "st"


def screenshot(flags: str) -> str:
    return (
        "mkdir -p ~/Pictures/screenshots && "
        f"scrot {flags} -l mode=edge,color=#ffff00,width=1,opacity=255 "
        "-F ~/Pictures/screenshots/'%Y-%m-%d-%H%M%S_$wx$h_scrot.png' "
        "-e 'xclip -selection clipboard -t image/png -i $f"
        " && notify-send -i $f Screenshot $f'"
    )


def _window_keys() -> list[Key]:
    return [
        Key([MOD], "h", lazy.layout.left(), desc="Move focus to left"),
        Key([MOD], "l", lazy.layout.right(), desc="Move focus to right"),
        Key([MOD], "j", lazy.layout.down(), desc="Move focus down"),
        Key([MOD], "k", lazy.layout.up(), desc="Move focus up"),
        Key(
            [MOD], "space", lazy.layout.next(), desc="Move window focus to other window"
        ),
        Key([MOD], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
        # Move windows between left/right columns or move up/down in current stack
        # Moving out of range in Columns layout will create new column
        Key(
            [MOD, "shift"],
            "h",
            lazy.layout.shuffle_left(),
            desc="Move window to the left",
        ),
        Key(
            [MOD, "shift"],
            "l",
            lazy.layout.shuffle_right(),
            desc="Move window to the right",
        ),
        Key([MOD, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
        Key([MOD, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
        # Grow windows. If current window is on the edge of screen and direction
        # will be to screen edge, window would shrink
        Key(
            [MOD, "control"],
            "h",
            lazy.layout.grow_left(),
            desc="Grow window to the left",
        ),
        Key(
            [MOD, "control"],
            "l",
            lazy.layout.grow_right(),
            desc="Grow window to the right",
        ),
        Key([MOD, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
        Key([MOD, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
        Key([MOD], "m", lazy.layout.normalize(), desc="Reset all window sizes"),
        Key([MOD], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
        Key([MOD, "shift"], "c", lazy.window.kill(), desc="Kill focused window"),
        Key(
            [MOD, "shift"],
            "space",
            lazy.window.toggle_floating(),
            desc="Toggle floating",
        ),
        Key([MOD], "n", lazy.next_screen(), desc="Focus next screen"),
    ]


def _app_keys() -> list[Key]:
    return [
        Key([MOD, "shift"], "Return", lazy.spawn(TERMINAL), desc="Launch terminal"),
        Key([MOD], "p", lazy.spawn(LAUNCHER), desc="Launch apps"),
        Key([MOD, "shift"], "p", lazy.spawn("dmenu_run -i"), desc="Run command"),
        Key([MOD], "c", lazy.function(picom_toggle), desc="Toggle picom"),
        Key([MOD], "d", lazy.spawn(DOCKER_TOGGLE), desc="Toggle docker"),
        Key([MOD, "control"], "r", lazy.reload_config(), desc="Reload config"),
        Key([MOD, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    ]


def _media_keys() -> list[Key]:
    return [
        Key(
            [],
            "XF86AudioRaiseVolume",
            lazy.spawn("wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 1%+"),
            desc="Volume up",
        ),
        Key(
            [],
            "XF86AudioLowerVolume",
            lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%-"),
            desc="Volume down",
        ),
        Key(
            [],
            "XF86AudioMute",
            lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
            desc="Toggle mute",
        ),
        Key(
            [],
            "Print",
            lazy.spawn(screenshot("-s"), shell=True),
            desc="Screenshot region",
        ),
        Key(
            ["shift"],
            "Print",
            lazy.spawn(screenshot(""), shell=True),
            desc="Screenshot all",
        ),
    ]


def _group_keys(groups: list[Group]) -> list[Key]:
    keys = []
    numbered = [group for group in groups if not isinstance(group, ScratchPad)]
    for i, group in enumerate(numbered, 1):
        keys.append(
            Key(
                [MOD],
                str(i),
                lazy.function(go_to_group, group.name),
                desc=f"Go to {group.name}",
            )
        )
        keys.append(
            Key(
                [MOD, "shift"],
                str(i),
                lazy.window.togroup(group.name),
                desc=f"Send window to {group.name}",
            )
        )
    keys.append(
        Key(
            [MOD],
            "s",
            lazy.group["scratchpad"].dropdown_toggle("term"),
            desc="Toggle dropdown terminal",
        )
    )
    return keys


def build_keys(groups: list[Group]) -> list[Key]:
    return [*_window_keys(), *_app_keys(), *_media_keys(), *_group_keys(groups)]


def build_mouse() -> list[Drag | Click]:
    return [
        Drag(
            [MOD],
            "Button1",
            lazy.window.set_position_floating(),
            start=lazy.window.get_position(),
        ),
        Drag(
            [MOD],
            "Button3",
            lazy.window.set_size_floating(),
            start=lazy.window.get_size(),
        ),
        Click([MOD], "Button1", lazy.window.bring_to_front()),
    ]
