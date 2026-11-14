from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path

from libqtile import (
    hook,
    qtile,
)
from libqtile.backend.base import Window
from libqtile.config import Match
from libqtile.core.manager import Qtile

from custom.groups import (
    MUSIC_APPS,
    go_to_group,
    pin_media_to_laptop,
)

# Like dwm's swallow patch: the terminal that launches a graphical app hides
# until the app closes
TERMINAL = Match(wm_class="st-256color")
NO_SWALLOW = (
    TERMINAL,
    Match(wm_class="firefox"),
    Match(title="Event Tester"),
)


def setup_laptop_screen() -> None:
    """
    When booting up or connecting a monitor, the notebook shows "media" again
    """
    if not isinstance(qtile, Qtile):
        return
    pin_media_to_laptop(qtile)


def open_browser_on_main(client: Window) -> None:
    """
    Every new firefox window is displayed in the main
    """
    if not isinstance(qtile, Qtile):
        return
    if client.match(Match(wm_class="firefox")):
        go_to_group(qtile, "browser")


def move_spotify(client: Window) -> None:
    """
    Spotify sets WM_CLASS after mapping the window, so Group.matches doesn't grab it
    """
    if client.group is None or client.group.name == "spotify":
        return
    if any(client.match(m) for m in MUSIC_APPS):
        client.togroup("spotify")


def force_float(client: Window) -> None:
    """
    Pritunl is not flagged as a dialog, so match it by class or title
    """
    if (
        client.match(Match(wm_class="pritunl"))
        or "pritunl" in (client.name or "").lower()
    ):
        client.enable_floating()


def parent_pid(pid: int) -> int:
    """
    Parent PID from /proc, or 0 if the process is gone
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return 0
    return int(stat.rpartition(")")[2].split()[1])


@dataclass
class Swallower:
    """
    Remember which terminal each app hid to return it when the app closes
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
        # The terminal may have been closed while hidden
        if not isinstance(qtile, Qtile) or terminal is None:
            return
        if terminal.wid not in qtile.windows_map:
            return
        terminal.minimized = False
        if terminal.group is not None:
            terminal.group.focus(terminal)


def register_hooks() -> None:
    """
    qtile clears hooks on every reload and config.py registers them again
    """
    hook.subscribe.startup_once(setup_laptop_screen)
    hook.subscribe.screens_reconfigured(setup_laptop_screen)
    hook.subscribe.client_managed(open_browser_on_main)
    hook.subscribe.client_name_updated(move_spotify)
    hook.subscribe.client_new(force_float)

    swallower = Swallower()
    hook.subscribe.client_managed(swallower.on_managed)
    hook.subscribe.client_killed(swallower.on_killed)
