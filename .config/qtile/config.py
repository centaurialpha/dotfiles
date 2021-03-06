# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import subprocess

from typing import List  # noqa: F401

from Xlib import display

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

from widgets import widgets

mod = "mod1"  # mod1=Alt;mod2=;mod3=;mod4=super
terminal = 'st'  # Suckless st

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),
    Key([mod], "d", lazy.spawn("dmenu_run")),
    Key([mod], "n", lazy.next_screen())
]


groups = [
    Group(name='dev', label=''),
    Group(name='slack', label=''),
    Group(name='browser', label=''),
    Group(name='jira', label=''),
    Group(name='python', label=''),
    Group(name='sys', label=''),
    Group(name='irc', label=''),
]
for i, group in enumerate(groups, 1):
    keys.append(Key([mod], str(i), lazy.group[group.name].toscreen()))
    keys.append(Key([mod, 'shift'], str(i), lazy.window.togroup(group.name)))


LAYOUT_KWARGS = {
    'border_focus': '#bd93f9',
    'border_width': 1,
    'margin': 20
}
layouts = [
    layout.Stack(**LAYOUT_KWARGS, num_stacks=1),
    layout.MonadTall(**LAYOUT_KWARGS),
    layout.Tile(**LAYOUT_KWARGS),
    layout.MonadWide(**LAYOUT_KWARGS),
    layout.Max(**LAYOUT_KWARGS),
    layout.RatioTile(**LAYOUT_KWARGS),
    layout.Matrix(**LAYOUT_KWARGS),
]

widget_defaults = dict(
    font='Hermit',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

# NOTE: waffle siji icons font is needed
all_widgets = widgets.copy()
top_primary = bar.Bar(all_widgets, 24)
screens = [
    Screen(top=top_primary)
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button1", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "qtile"


def switch_screens(qtile):
    i = qtile.screens.index(qtile.current_screen)
    group = qtile.screens[i - 1].group
    qtile.current_screen.set_group(group)


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.call([autostart_script])


@hook.subscribe.client_new
def client_new(client):
    if client.name in ('qutebrowser', 'firefox'):
        client.togroup('browser')
    elif client.name == 'Slack':
        client.togroup('slack')


def install_secondary_screen(qtile):
    monitors_count = len(qtile.conn.pseudoscreens)
    if monitors_count > 1:
        second_screen_widgets = [
            all_widgets[0],
        ]
        top_secondary = bar.Bar(second_screen_widgets, 24)
        screens.append(Screen(top=top_secondary))

        xrandr_cmd_str = (
            'xrandr --output eDP-1 --mode 1920x1080 --pos 1920x0 '
            '--rotate normal --output DP-1 --off --output HDMI-1 '
            '--off --output DP-2 --off --output HDMI-2 --primary '
            '--mode 1920x1080 --pos 0x0 --rotate normal'
        )
        xrandr_cmd = xrandr_cmd_str.split()
        subprocess.Popen(xrandr_cmd)


def main(qtile):
    install_secondary_screen(qtile)
