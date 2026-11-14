"""
Overrides private qtile-extras methods, check_upstream warns when they change
"""

import hashlib
import inspect
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import cairocffi
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from libqtile.utils import (
    rgb,
    send_notification,
)
from libqtile.widget.base import _Widget
from qtile_extras import hook as extras_hook
from qtile_extras import widget
from qtile_extras.popup.templates.mpris2 import DEFAULT_LAYOUT
from qtile_extras.popup.toolkit import (
    PopupImage,
    PopupRelativeLayout,
    PopupSlider,
    PopupText,
)
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras.widget.mpris2widget import Mpris2
from qtile_extras.widget.visualiser import (
    CAVA_DRAW,
    Visualiser,
)

from custom.theme import (
    ICON_FONT,
    ICON_SIZE,
    TEXT_FONT,
    colors,
)
from custom.widgets.blocks import (
    BLOCK_PADDING,
    MENU_STYLE,
    follow_icon,
    follow_separator,
    icon_block,
    right_deco,
    separator,
)


class RefocusPopup(PopupRelativeLayout):
    """
    Popup that returns focus to the active window when closed
    """

    def kill(self) -> None:
        super().kill()
        if self.qtile is None:
            return
        group = self.qtile.current_group
        if group.current_window:
            group.focus(group.current_window, warp=False, force=True)


def music_popup_layout() -> PopupRelativeLayout:
    controls = deepcopy(DEFAULT_LAYOUT.controls)
    for control in controls:
        control.highlight = colors.accent
        if isinstance(control, PopupText):
            control.font = TEXT_FONT
            control.foreground = colors.text
        elif isinstance(control, PopupSlider):
            control.colour_below = colors.accent
            control.colour_above = colors.inactive
        elif isinstance(control, PopupImage) and control.mask:
            control.colour = colors.text
    return RefocusPopup(
        None,
        width=400,
        height=200,
        controls=controls,
        background=colors.surface,
        border_width=0,
        highlight=colors.accent,
        close_on_click=False,
        # qtile popups do not get outside clicks, so close on mouse leave
        hide_on_mouse_leave=True,
        hide_interval=0.8,
    )


UPSTREAM_HASH = "f916c85cbb305b5fc2fb35396858ef4d2c3cd99d0e3ffda9bbe6aefb8cfe24c5"
UPSTREAM_NOTIFY_ID = 4242


def upstream_hash() -> str:
    """
    Hash of the private qtile-extras code this module overrides
    """
    parts = [
        inspect.getsource(Visualiser._draw),
        CAVA_DRAW.read_text(),
        inspect.getsource(Mpris2._config_async),
        inspect.getsource(Mpris2._check_player),
        inspect.getsource(Mpris2._send_message),
    ]
    return hashlib.sha256("".join(parts).encode()).hexdigest()


def warn_upstream(message: str) -> None:
    """
    Persistent notification that replaces itself instead of stacking
    """
    send_notification("qtile media", message, timeout=0, id_=UPSTREAM_NOTIFY_ID)


def check_upstream() -> None:
    current = upstream_hash()
    if current == UPSTREAM_HASH:
        return
    logger.warning("media.py: new private code hash: %s", current)
    warn_upstream(
        "qtile or qtile-extras changed private code that the visualiser or the"
        " music widget override. If they still work, copy the new hash from the"
        " qtile log into UPSTREAM_HASH."
    )


MPRIS_PREFIX = "org.mpris.MediaPlayer2."


class RunningPlayerMpris2(Mpris2):
    """
    Attaches at startup to the player that is already playing
    """

    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self.followers: list[widget.GenPollText] = []

    def update(self, text: str) -> None:
        super().update(text)
        for follower in self.followers:
            if follower.configured:
                follower.force_update()

    async def _config_async(self) -> None:
        await super()._config_async()
        if self.objname is not None:
            return
        try:
            await self._attach_running_player()
        except (AttributeError, TypeError, IndexError):
            logger.exception("RunningPlayerMpris2: could not look up the player")
            warn_upstream("The music widget could not find the player at startup.")

    async def _send_message(
        self,
        destination: str,
        interface: str,
        path: str,
        member: str,
        signature: str,
        body: Any,
    ) -> Any:
        """
        Reconnects if the saved connection died
        """
        args = (destination, interface, path, member, signature, body)
        try:
            return await super()._send_message(*args)
        except OSError:
            logger.warning("RunningPlayerMpris2: dbus connection died, reconnecting")
            self.bus = None
            return await super()._send_message(*args)

    async def _attach_running_player(self) -> None:
        reply = await self._send_message(
            "org.freedesktop.DBus",
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            "ListNames",
            "",
            [],
        )
        players = [name for name in reply.body[0] if name.startswith(MPRIS_PREFIX)]
        for name in players:
            self._current_player = name
            await self._check_player()
            if self.is_playing:
                return


VISUALISER_FPS = 12
VISUALISER_GAP = 6
VISUALISER_COLOURS = (
    colors.media,
    "#7e9cd8",
    colors.network,
    colors.system,
    colors.layout,
    colors.device,
)


class StripedVisualiser(Visualiser):
    """
    Falls back to the original drawing if the stripes fail
    """

    def __init__(self, colours: tuple[str, ...], **config: Any) -> None:
        super().__init__(**config)
        self._gradient: cairocffi.LinearGradient | None = None
        try:
            self._gradient = self._stripes(colours)
        except AttributeError:
            logger.exception("StripedVisualiser: could not build the stripes")

    def _stripes(self, colours: tuple[str, ...]) -> cairocffi.LinearGradient:
        width = self._config_length
        slot = width // self.bars
        pad = (width - slot * self.bars) // 2
        gradient = cairocffi.LinearGradient(0, 0, width, 0)
        for i in range(self.bars):
            colour = rgb(colours[i % len(colours)])
            gradient.add_color_stop_rgba((pad + i * slot) / width, *colour)
            gradient.add_color_stop_rgba((pad + (i + 1) * slot) / width, *colour)
        return gradient

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        if self._gradient is None:
            warn_upstream("Could not build the visualiser stripes, using one colour.")
            return
        check_upstream()

    def _draw(self) -> None:
        if self._gradient is None:
            super()._draw()
            return
        try:
            self._draw_striped(self._gradient)
        except (AttributeError, TypeError, ValueError, cairocffi.CairoError):
            logger.exception("StripedVisualiser: drawing failed, using the original")
            self._gradient = None
            warn_upstream("Striped drawing failed, the visualiser uses one colour.")
            super()._draw()

    def _draw_striped(self, gradient: cairocffi.LinearGradient) -> None:
        if self._shm is None:
            return
        with self._take_lock():
            surface = cairocffi.ImageSurface.create_for_data(
                bytearray(self._shm[: self._shm_size]),
                cairocffi.FORMAT_ARGB32,
                self._config_length,
                self.bar_height,
            )
        self.drawer.clear(self.background or self.bar.background)
        self.drawer.ctx.set_source(gradient)
        self.drawer.ctx.mask_surface(surface, 0, self.y_offset)
        self.draw_at_default_position()
        self._timer = self.timeout_add(self._interval, self.loop)


@dataclass
class VisualiserSwitch:
    """
    Runs the visualiser only while music plays and it was not turned off by hand
    """

    visualiser: widget.Visualiser
    gap: widget.Spacer
    player: widget.Mpris2
    enabled: bool = True

    def on_status(self, status: str) -> None:
        running = self.enabled and status == "Playing"
        if running:
            self.visualiser.start()
        else:
            self.visualiser.stop()
        self.gap.length = VISUALISER_GAP if running else 0
        self.gap.bar.draw()

    def toggle(self) -> None:
        self.enabled = not self.enabled
        self.on_status("Playing" if self.player.is_playing else "Paused")


def _block_background() -> list[RectDecoration]:
    return [
        RectDecoration(colour=colors.value_block, radius=0, filled=True, padding_y=3)
    ]


def make_music() -> list[_Widget]:
    """
    Clicking the icon toggles the visualiser, right click on the title switches
    player
    """
    music = RunningPlayerMpris2(
        name="mpris2",
        objname=None,
        format="{xesam:artist} - {xesam:title}",
        playing_text="{track}",
        paused_text="{track} [paused]",
        no_metadata_text="",
        poll_interval=30,
        scroll=True,
        width=250,
        decorations=right_deco(),
        padding=BLOCK_PADDING,
        popup_layout=music_popup_layout(),
        popup_show_args={"relative_to": 3, "relative_to_bar": True},
        mouse_callbacks={"Button3": lazy.widget["mpris2"].toggle_player()},
    )
    visualiser = StripedVisualiser(
        VISUALISER_COLOURS,
        autostart=False,
        bar_colour=colors.media,
        width=36,
        bars=6,
        spacing=2,
        bar_height=14,
        framerate=VISUALISER_FPS,
        decorations=_block_background(),
    )
    gap = widget.Spacer(length=0, decorations=_block_background())

    switch = VisualiserSwitch(visualiser, gap, music)
    extras_hook.subscribe.mpris_status_change(switch.on_status)

    icon = follow_icon(music, "\uecad", colors.media)
    icon.mouse_callbacks = {"Button1": switch.toggle}
    music_separator = follow_separator(music)
    music.followers = [icon, music_separator]

    return [icon, visualiser, gap, music, music_separator]


def make_volume() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uedeb",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.device),
        ),
        widget.PulseVolume(
            decorations=right_deco(),
            padding=BLOCK_PADDING,
            volume_app="pavucontrol",
            **MENU_STYLE,
        ),
        separator(),
    ]
