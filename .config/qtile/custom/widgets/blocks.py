from collections.abc import Callable
from typing import Any

from libqtile.widget.base import _TextBox
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

from custom.theme import (
    ICON_FONT,
    ICON_SIZE,
    TEXT_FONT,
    colors,
)

RADIUS = 2

MENU_STYLE: dict[str, Any] = {
    "menu_font": TEXT_FONT,
    "menu_fontsize": 13,
    "menu_foreground": colors.text,
    "menu_foreground_disabled": colors.inactive,
    "menu_background": colors.surface,
    "menu_border_width": 0,
    "highlight_colour": colors.accent,
    "highlight_radius": RADIUS,
    "separator_colour": colors.inactive,
}

BLOCK_PADDING = 6


def left_deco(color: str, radius: list[int] | None = None) -> list[RectDecoration]:
    """
    Color block behind the icon, rounded to the left only
    """
    corners = radius or [RADIUS, 0, 0, RADIUS]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


FILLED_ICONS = False


def icon_block(color: str, radius: list[int] | None = None) -> dict[str, Any]:
    fill = color if FILLED_ICONS else colors.value_block
    style: dict[str, Any] = {
        "foreground": colors.icon_fg if FILLED_ICONS else color,
        "decorations": left_deco(fill, radius),
    }
    # Standalone blocks center the icon, pill halves do not
    if radius is None:
        style["padding"] = BLOCK_PADDING
    return style


def right_deco(color: str = colors.value_block) -> list[RectDecoration]:
    """
    Color block behind the value, rounded to the right only
    """
    corners = [0, RADIUS, RADIUS, 0]
    return [RectDecoration(colour=color, radius=corners, filled=True, padding_y=3)]


def follow_icon(target: _TextBox, glyph: str, color: str) -> widget.GenPollText:
    """
    Icon block showing only while `target` has text
    """
    return widget.GenPollText(
        func=lambda: glyph if target.text else "",
        update_interval=None,
        font=ICON_FONT,
        fontsize=ICON_SIZE,
        **icon_block(color),
    )


def follow_separator(target: _TextBox) -> widget.GenPollText:
    """
    Separator that disappears along with `target`, so as not to leave a double gap
    """
    return widget.GenPollText(
        func=lambda: " " if target.text else "",
        update_interval=None,
        fontsize=11,
        padding=0,
    )


def separator() -> widget.Spacer:
    return widget.Spacer(length=7)


def status_icon(glyph: str, color: str) -> str:
    return f'<span foreground="{color}">{glyph}</span>'


def status_block(
    name: str,
    func: Callable[[], str],
    interval: float | None,
    on_click: Any,
    block_class: type[widget.GenPollText] = widget.GenPollText,
    **block_config: Any,
) -> tuple[widget.GenPollText, widget.Spacer]:
    """
    block_config goes straight to the widget, e.g. the D-Bus path/prop/render
    """
    return (
        block_class(
            **block_config,
            name=name,
            func=func,
            update_interval=interval,
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            padding=BLOCK_PADDING,
            decorations=left_deco(colors.value_block, radius=[RADIUS] * 4),
            mouse_callbacks={"Button1": on_click},
        ),
        separator(),
    )
