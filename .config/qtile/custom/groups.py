from libqtile.config import (
    DropDown,
    Group,
    Match,
    ScratchPad,
)
from libqtile.core.manager import Qtile

# Spotify sets WM_CLASS late, which is why there is also the move_spotify hook
MUSIC_APPS = (Match(wm_class="spotify"), Match(wm_class="spotifast"))

# With two screens, the laptop always shows this group
LAPTOP_GROUP = "media"


def build_groups() -> list[Group]:
    return [
        Group(name="dev", label="\ued95"),
        Group(name="browser", label="\uebc6", matches=[Match(wm_class="firefox")]),
        Group(name="slack", label="\uec93", matches=[Match(wm_class="slack")]),
        Group(name="spotify", label="\uecad", matches=list(MUSIC_APPS)),
        Group(
            name="claude",
            label="\ued05",
            matches=[Match(wm_class="com.anthropic.Claude")],
        ),
        Group(name="media", label="\uede8", matches=[Match(wm_class="webcam")]),
        ScratchPad(
            "scratchpad",
            [DropDown("term", "st", width=0.6, height=0.5, x=0.2, y=0.1, opacity=1)],
        ),
    ]


def pin_media_to_laptop(qtile: Qtile) -> None:
    if len(qtile.screens) > 1:
        qtile.groups_map[LAPTOP_GROUP].toscreen(1)


def go_to_group(qtile: Qtile, name: str) -> None:
    """
    Show the group on its screen and focus that screen
    """
    group = qtile.groups_map[name]
    if len(qtile.screens) < 2:
        group.toscreen()
        return
    screen = 1 if name == LAPTOP_GROUP else 0
    group.toscreen(screen)
    qtile.focus_screen(screen)
