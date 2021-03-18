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

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

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
    Key([mod], "d", lazy.spawn("dmenu_run"))
]


group_names = [
    ("WWW", {'layout': 'bsp'}),
    ("DEV", {'layout': 'bsp'}),
    ("CHAT", {'layout': 'bsp'}),
    ("SYS", {'layout': 'bsp'}),
    ("EMAIL", {'layout': 'bsp'}),
    ("VBOX", {'layout': 'bsp'}),
    ("MUS", {'layout': 'bsp'}),
    ("VID", {'layout': 'bsp'}),
    ("GFX", {'layout': 'bsp'})
]

groups = [Group(name, **kwargs) for name, kwargs in group_names]

for i, (name, kwargs) in enumerate(group_names, 1):
    keys.append(Key([mod], str(i), lazy.group[name].toscreen()))  # Switch to another group
    keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(name)))  # Send current window to another group


LAYOUT_KWARGS = {
    'border_focus': '#ffa000',
    'border_width': 1,
    'margin': 5
}
layouts = [
    # layout.Tile(**LAYOUT_KWARGS),
    layout.Bsp(**LAYOUT_KWARGS),
    # layout.MonadTall(**LAYOUT_KWARGS),
]

widget_defaults = dict(
    font='Hermit',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

# Custom separator
sep_widget = widget.Sep(linewidth=2, size_percent=60, padding=10, foreground='#ffa000')



def init_widgets() -> list:
    return [
            widget.GroupBox(
                this_current_screen_border='#ffa000',
                borderwidth=2,
                rounded=False
            ),
            widget.Prompt(
                prompt='run: ',
                cursor_color='#ffa000',
                foreground='#ffa000'
            ),
            widget.WindowName(max_chars=40, format='{state}{class}'),
            widget.Chord(
                chords_colors={
                    'launch': ("#ff0000", "#ffffff"),
                },
                name_transform=lambda name: name.upper(),
            ),
            widget.CurrentLayout(),
            widget.Pomodoro(),
            widget.TextBox(
                foreground='#9c9c9c',
                text=' '),
            widget.DF(visible_on_warn=False),
            widget.TextBox(
                text=' ',
                foreground='#42a5f5'
            ),
            widget.Memory(
                update_interval=5.0,
            ),
            widget.TextBox(
                foreground='#fbc02d',
                text=' '),
            widget.CPU(
                update_interval=5.0
            ),
            widget.TextBox(
                foreground='#61c766',
                text=' '),
            widget.Battery(
                format='{char} {percent:2.0%}'),
            widget.TextBox(
                foreground='#ba68c8',
                text=' '),
            widget.ThermalSensor(),
            widget.TextBox(
                foreground='#6c77bb',
                text=' '),
            widget.Clock(
                format='%d-%m-%Y %A %I:%M %p'
            ),
            widget.TextBox(
                text=' ',
                foreground='#ec7875',
            ),
            widget.Volume(),
    ]

# NOTE: waffle siji icons font is needed
screens = [
    Screen(
        top=bar.Bar(init_widgets(), 24),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
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
wmname = "LG3D"


@hook.subscribe.client_new
def client_new(client):
    if client.name in ('qutebrowser', 'firefox'):
        client.togroup('WWW')
    elif client.name == 'Slack':
        client.togroup('CHAT')


@hook.subscribe.startup_once
def autostart():
    autostart_script = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.call([autostart_script])
