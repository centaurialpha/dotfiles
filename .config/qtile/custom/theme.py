from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Palette:
    """
    Kanagawa on a black background.
    """

    bg: str = "#0a0a0a"
    value_block: str = "#2a2a2a"
    # Background of menus, popups and notifications, separated by tone, without border
    surface: str = "#1a1a1a"
    text: str = "#e8e8e8"
    inactive: str = "#555555"
    accent: str = "#1270a8"
    accent_soft: str = "#0e4361"
    accent_dim: str = "#2a2a2a"
    layout: str = "#98bb6c"
    ok: str = "#e8e8e8"
    fail: str = "#e46876"
    icon_fg: str = "#0a0a0a"
    device: str = "#c0a36e"
    system: str = "#87a987"
    network: str = "#8ea4a2"
    media: str = "#957fb8"


colors = Palette()

# Pixelarticons icons (~/.local/share/fonts/pixelarticons.ttf)
ICON_FONT = "pixelart-icons-font"
ICON_SIZE = 16
TEXT_FONT = "Input Mono"
# Lower the icon inside a text to center it, at 1/1024 pt
INLINE_ICON_RISE = -2048


def inline_icon(glyph: str) -> str:
    return (
        f'<span font="{ICON_FONT} {ICON_SIZE}px"'
        f' rise="{INLINE_ICON_RISE}">{glyph}</span>'
    )
