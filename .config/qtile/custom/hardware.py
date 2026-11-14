"""
Detecting differences between my computers (Asus, ThinkPad and MSI)
"""

from functools import cache
from pathlib import Path


@cache
def backlight_name() -> str:
    if Path("/sys/class/backlight/intel_backlight").exists():
        return "intel_backlight"
    return "amdgpu_bl1"


@cache
def has_nvidia() -> bool:
    return Path("/sys/module/nvidia").exists()


@cache
def battery_name() -> str:
    """
    First system battery, ignoring device battery mouse, headphones
    """
    for supply in sorted(Path("/sys/class/power_supply").iterdir()):
        scope = supply / "scope"
        is_device = scope.exists() and scope.read_text().strip() == "Device"
        if (supply / "type").read_text().strip() == "Battery" and not is_device:
            return supply.name
    return "BAT0"


@cache
def cpu_sensor_tag() -> str:
    names = {
        hwmon.read_text().strip() for hwmon in Path("/sys/class/hwmon").glob("*/name")
    }
    return "Tctl" if "k10temp" in names else "Package id 0"


@cache
def wifi_interface() -> str:
    wireless = Path("/sys/class/net").glob("*/wireless")
    return next((path.parent.name for path in wireless), "wlan0")


def connected_monitors() -> int:
    """
    Number of DRM outputs connected. No cache, changes when plugging in a monitor
    """
    return sum(
        status.read_text().strip() == "connected"
        for status in Path("/sys/class/drm").glob("card*-*/status")
    )
