from dbus_fast import Message
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.hardware import wifi_interface
from custom.theme import (
    ICON_FONT,
    ICON_SIZE,
    colors,
    inline_icon,
)
from custom.widgets.blocks import (
    BLOCK_PADDING,
    icon_block,
    right_deco,
    separator,
)
from custom.widgets.dbus import watch_properties

IWD_STATION = "net.connman.iwd.Station"
WLAN_SIGNAL_INTERVAL = 300


class WlanBlock(widget.Wlan):
    """
    Redraws on iwd state changes and polls signal strength every 5 minutes
    """

    async def _config_async(self) -> None:
        await super()._config_async()
        await watch_properties(self._on_change, bus_name="net.connman.iwd")

    def _on_change(self, message: Message) -> None:
        if message.body[0] == IWD_STATION:
            self.force_update()


def make_net() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uea7c",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.network),
        ),
        widget.Net(
            interface=wifi_interface(),
            format=inline_icon("\uea6d")
            + "{down:4.1f}{down_suffix:<2} "
            + inline_icon("\uea7a")
            + "{up:4.1f}{up_suffix:<2}",
            update_interval=5,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]


def make_wlan() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uee01",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.network),
        ),
        WlanBlock(
            interface=wifi_interface(),
            format="{essid} {percent:2.0%}",
            disconnected_message="offline",
            update_interval=WLAN_SIGNAL_INTERVAL,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]
