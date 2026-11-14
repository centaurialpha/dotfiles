from dbus_fast import Message
from libqtile.lazy import lazy
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.hardware import (
    battery_name,
    cpu_sensor_tag,
    has_nvidia,
)
from custom.theme import (
    ICON_FONT,
    ICON_SIZE,
    colors,
)
from custom.widgets.blocks import (
    BLOCK_PADDING,
    icon_block,
    right_deco,
    separator,
)
from custom.widgets.dbus import watch_properties

SYSTEM_MONITOR = "st -e htop"
UPOWER_DISPLAY_DEVICE = "/org/freedesktop/UPower/devices/DisplayDevice"


def make_temperature() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uedae",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.system),
        ),
        widget.ThermalSensor(
            decorations=right_deco(),
            format="{temp:.0f}{unit}",
            tag_sensor=cpu_sensor_tag(),
            padding=BLOCK_PADDING,
            update_interval=5,
        ),
        separator(),
    ]


def make_memory() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\uec87",
            mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.system),
        ),
        widget.Memory(
            mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
            decorations=right_deco(),
            padding=BLOCK_PADDING,
            format="{Available:.1f}{mm}",
            measure_mem="G",
            update_interval=5,
        ),
        separator(),
    ]


def make_storage() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\ued0e",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.system),
        ),
        widget.DF(
            decorations=right_deco(),
            format="{r:.0f}%",
            visible_on_warn=False,
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]


def make_cpu() -> list[_Widget]:
    return [
        widget.TextBox(
            text="\ueb5b",
            mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            **icon_block(colors.system),
        ),
        widget.CPU(
            mouse_callbacks={"Button1": lazy.spawn(SYSTEM_MONITOR)},
            update_interval=5.0,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
            format="{load_percent:.0f}%",
        ),
        separator(),
    ]


def make_gpu() -> list[_Widget]:
    """
    Empty on machines without NVIDIA.
    """
    if not has_nvidia():
        return []
    return [
        widget.TextBox(
            text="GPU",
            **icon_block(colors.system),
        ),
        widget.NvidiaSensors(
            update_interval=5.0,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
        ),
        separator(),
    ]


def make_system() -> list[_Widget]:
    return [
        *make_temperature(),
        *make_memory(),
        *make_storage(),
        *make_cpu(),
        *make_gpu(),
    ]


class BatteryBlock(widget.Battery):
    """
    Redraws on UPower changes instead of polling.
    """

    async def _config_async(self) -> None:
        await super()._config_async()
        await watch_properties(self._on_change, path=UPOWER_DISPLAY_DEVICE)

    def _on_change(self, _message: Message) -> None:
        self.force_update()


def make_battery(notify: bool) -> list[_Widget]:
    """
    notify warns below 10%.
    """
    return [
        BatteryBlock(
            battery=battery_name(),
            show_short_text=False,
            **icon_block(colors.device),
            format="{char}",
            font=ICON_FONT,
            fontsize=ICON_SIZE,
            discharge_char="\ueaaa",
            charge_char="\uee0a",
            empty_char="\ueaa8",
            full_char="\ueaa6",
            not_charging_char="\ueaac",
            low_foreground=colors.fail,
            update_interval=None,
            notify_below=10 if notify else None,
            notification_timeout=30,
        ),
        BatteryBlock(
            battery=battery_name(),
            show_short_text=False,
            decorations=right_deco(),
            padding=BLOCK_PADDING,
            format="{percent:2.0%}",
            update_interval=None,
        ),
        separator(),
    ]
