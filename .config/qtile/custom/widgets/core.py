import asyncio

from libqtile import bar
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.hardware import backlight_name
from custom.theme import (
    ICON_FONT,
    ICON_SIZE,
    colors,
)
from custom.widgets.blocks import (
    BLOCK_PADDING,
    MENU_STYLE,
    RADIUS,
    icon_block,
    left_deco,
    right_deco,
    separator,
)


def make_group_box() -> list[_Widget]:
    return [
        widget.GroupBox(
            fontsize=ICON_SIZE,
            font=ICON_FONT,
            borderwidth=0,
            padding_x=8,
            padding_y=3,
            active=colors.text,
            block_highlight_text_color=colors.text,
            inactive=colors.inactive,
            this_current_screen_border=colors.accent_soft,
            this_screen_border=colors.accent_dim,
            other_current_screen_border=colors.accent_dim,
            other_screen_border=colors.accent_dim,
            urgent_alert_method="text",
            urgent_text=colors.fail,
            rounded=True,
            disable_drag=True,
            highlight_method="block",
        )
    ]


CLOCK_FORMATS = ("[%b %d, %H:%M]", "[%a %d/%m/%Y]")


def make_clock() -> list[_Widget]:
    """
    Click toggles between time and full date.
    """
    clock = widget.Clock(format=CLOCK_FORMATS[0], update_interval=60)

    def toggle() -> None:
        short, full = CLOCK_FORMATS
        clock.format = full if clock.format == short else short
        clock.tick()

    clock.mouse_callbacks = {"Button1": toggle}
    return [clock]


class BacklightBlock(widget.Backlight):
    """
    Redraws on udev events instead of polling.
    """

    async def _config_async(self) -> None:
        await super()._config_async()
        self._monitor = await asyncio.create_subprocess_exec(
            "udevadm",
            "monitor",
            "--udev",
            "--subsystem-match=backlight",
            stdout=asyncio.subprocess.PIPE,
        )
        self._watch = asyncio.create_task(self._on_events())

    async def _on_events(self) -> None:
        if self._monitor.stdout is None:
            return
        async for line in self._monitor.stdout:
            if b" change " in line:
                self.force_update()

    def finalize(self) -> None:
        self._watch.cancel()
        self._monitor.kill()
        super().finalize()


def make_display() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uec5d",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.device),
        ),
        BacklightBlock(
            backlight_name=backlight_name(),
            change_command="brightnessctl set {0}%",
            update_interval=None,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]


def make_window_name() -> list[_Widget]:
    return [
        widget.WindowName(
            format="{name}",
            empty_group_string="",
            max_chars=80,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
            width=bar.CALCULATED,
        )
    ]


# Icon color according to the active layout, more saturated than the rest of the bar
LAYOUT_COLOURS = {
    "stack": "#ffa066",
    "columns": "#a77bff",
    "monadtall": "#a6e22e",
    "bsp": "#ffd43b",
}


class LayoutIcon(widget.CurrentLayout):
    def draw(self) -> None:
        self.foreground = LAYOUT_COLOURS.get(self.current_layout, colors.layout)
        super().draw()


def make_layout_icon() -> list[_Widget]:
    return [
        LayoutIcon(
            mode="icon",
            use_mask=True,
            scale=0.6,
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]


def make_tray() -> list[_Widget]:
    return [
        widget.StatusNotifier(
            icon_size=ICON_SIZE,
            padding=BLOCK_PADDING,
            decorations=left_deco(colors.value_block, radius=[RADIUS] * 4),
            **MENU_STYLE,
        )
    ]
