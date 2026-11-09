from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path

from libqtile import (
    bar,
    hook,
    layout,
    qtile,
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
    LAUNCHER,
    POWER_MENU,
    TEXT_FONT,
    colors,
    laptop_widgets,
    picom_toggle,
    w_net,
    w_power,
    w_system,
    w_window_name,
    w_wlan,
    widgets,
)

mod = "mod1"  # mod1=Alt;mod2=;mod3=;mod4=super
terminal = "st"  # Suckless st

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
    Key([mod, "shift"], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "c", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key(
        [mod],
        "p",
        lazy.spawn(LAUNCHER),
        desc="Launch apps",
    ),
    Key([mod, "shift"], "p", lazy.spawn("dmenu_run -i"), desc="Run command"),
    Key(
        ["control", "shift"],
        "a",
        lazy.spawn(POWER_MENU),
    ),
    Key([mod], "n", lazy.next_screen()),
    Key([mod], "c", lazy.function(picom_toggle), desc="Toggle picom"),
    Key([mod, "shift"], "space", lazy.window.toggle_floating(), desc="Toggle floating"),
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
    Group(name="media", label="\uede8"),
]

# Con dos pantallas la notebook muestra siempre este grupo y el resto va al principal.
LAPTOP_GROUP = "media"


def pin_media_to_laptop(qtile: Qtile) -> None:
    """
    Pone el grupo de la notebook en la segunda pantalla, si hay dos.
    """
    if len(qtile.screens) > 1:
        qtile.groups_map[LAPTOP_GROUP].toscreen(1)


def go_to_group(qtile: Qtile, name: str) -> None:
    """
    Con dos pantallas, "media" se ve en la notebook y el resto en el principal,
    y el foco va a esa pantalla. Con una sola pantalla, muestra el grupo ahí.
    """
    group = qtile.groups_map[name]
    if len(qtile.screens) < 2:
        group.toscreen()
        return
    screen = 1 if name == LAPTOP_GROUP else 0
    group.toscreen(screen)
    qtile.focus_screen(screen)


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
    "font": TEXT_FONT,
    "fontsize": 14,
    "padding": 2,
    "foreground": colors["text"],
}
extension_defaults = widget_defaults.copy()


def make_bar(items: list) -> bar.Bar:
    """
    Barra con los extremos alineados al margen de las ventanas.
    """
    edge = LAYOUT_KWARGS["margin"]
    return bar.Bar(
        [widget.Spacer(length=edge), *items, widget.Spacer(length=edge)],
        28,
        background=colors["bg"],
    )


all_widgets = widgets.copy()
top_primary = make_bar(all_widgets)
bottom_widgets = [
    *w_wlan,
    *w_net,
    widget.Spacer(),
    *w_window_name,
    widget.Spacer(),
    *w_power,
    *w_system,
]
bottom_bar = make_bar(bottom_widgets)

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

follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
respect_minimize_requests = True

# Algunas apps Java necesitan un nombre de WM conocido.
wmname = "qtile"


floating_layout = layout.Floating(
    border_focus=colors["accent"],
    border_normal=colors["inactive"],
    border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        # default_float_rules include: utility, notification, toolbar, splash, dialog,
        # file_progress, confirm, download and error.
        *layout.Floating.default_float_rules,
        Match(wm_type="dialog"),
        Match(title="pritunl"),
    ],
)


@hook.subscribe.startup_once
@hook.subscribe.screens_reconfigured
def setup_laptop_screen() -> None:
    """
    Al arrancar o conectar un monitor, la notebook vuelve a mostrar "media".
    """
    if not isinstance(qtile, Qtile):
        return
    pin_media_to_laptop(qtile)


@hook.subscribe.client_managed
def open_browser_on_main(client: Window) -> None:
    """
    Cada ventana nueva de firefox o qutebrowser se muestra en el principal.
    """
    if not isinstance(qtile, Qtile):
        return
    if client.match(Match(wm_class="firefox")) or client.match(
        Match(wm_class="qutebrowser")
    ):
        go_to_group(qtile, "browser")


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


@hook.subscribe.client_new
def force_float(client: Window) -> None:
    if (
        client.match(Match(wm_class="pritunl"))
        or "pritunl" in (client.name or "").lower()
    ):
        client.enable_floating()


# Swallow como el parche de dwm: la terminal que lanza una app gráfica se esconde
# hasta que la app se cierra. Las terminales y estas apps no la esconden.
TERMINAL = Match(wm_class="st-256color")
NO_SWALLOW = (
    TERMINAL,
    Match(wm_class="firefox"),
    Match(title="Event Tester"),
)


def parent_pid(pid: int) -> int:
    """
    PID del proceso padre según /proc, 0 si el proceso ya no existe.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return 0
    # El nombre va entre paréntesis y puede tener espacios: se corta después.
    return int(stat.rpartition(")")[2].split()[1])


@dataclass
class Swallower:
    """
    Recuerda qué terminal escondió cada app para devolverla cuando la app se cierra.
    """

    parents: dict[int, Window] = field(default_factory=dict)

    def on_managed(self, client: Window) -> None:
        if not isinstance(qtile, Qtile) or any(client.match(m) for m in NO_SWALLOW):
            return
        terminals = {
            window.get_pid(): window
            for window in qtile.windows_map.values()
            if isinstance(window, Window) and window.match(TERMINAL)
        }
        pid = client.get_pid()
        while pid > 1:
            pid = parent_pid(pid)
            terminal = terminals.get(pid)
            if terminal is not None:
                terminal.minimized = True
                self.parents[client.wid] = terminal
                return

    def on_killed(self, client: Window) -> None:
        terminal = self.parents.pop(client.wid, None)
        # La terminal puede haberse cerrado mientras estaba escondida.
        if not isinstance(qtile, Qtile) or terminal is None:
            return
        if terminal.wid not in qtile.windows_map:
            return
        terminal.minimized = False
        if terminal.group is not None:
            terminal.group.focus(terminal)


swallower = Swallower()
hook.subscribe.client_managed(swallower.on_managed)
hook.subscribe.client_killed(swallower.on_killed)


# Si hay una sola pantalla física, qtile usa solo la primera.
screens = [
    Screen(top=top_primary, bottom=bottom_bar),
    Screen(top=make_bar(laptop_widgets)),
]
