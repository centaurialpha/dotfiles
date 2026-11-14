import json
import math
import time
from dataclasses import dataclass
from urllib.request import urlopen

from libqtile.lazy import lazy
from libqtile.widget.base import _Widget
from qtile_extras import widget

from custom.theme import colors
from custom.widgets.blocks import (
    status_block,
    status_icon,
)

GATUS_URL = "http://uptime.home"
HEMARA_GROUPS = ("Producción", "Preproducción")
HEMARA_ICON = "\ued20"


def _group_healthy(endpoints: list[dict], group: str) -> bool:
    results = [
        e["results"][-1]["success"]
        for e in endpoints
        if e["group"] == group and e["results"]
    ]
    return bool(results) and all(results)


def fetch_endpoints() -> list[dict] | None:
    """
    Latest result of each endpoint, or None if Gatus does not answer
    """
    try:
        with urlopen(
            f"{GATUS_URL}/api/v1/endpoints/statuses?pageSize=1", timeout=5
        ) as resp:
            return json.load(resp)
    except (OSError, ValueError):
        return None


def hemara_icons(endpoints: list[dict] | None, blink_on: bool) -> str:
    """
    One icon per environment: light if up, blinking red if down, grey without data
    """
    icons = []
    for group in HEMARA_GROUPS:
        if endpoints is None:
            color = colors.inactive
        elif _group_healthy(endpoints, group):
            color = colors.ok
        else:
            color = colors.fail if blink_on else colors.inactive
        icons.append(status_icon(HEMARA_ICON, color))
    return "".join(icons)


@dataclass
class HemaraPoller:
    """
    Queries Gatus every `refresh` seconds and toggles the blink on each call
    """

    refresh: float = 60
    blink: float = 0.5
    _endpoints: list[dict] | None = None
    _fetched_at: float = -math.inf

    def __call__(self) -> str:
        now = time.monotonic()
        if now - self._fetched_at >= self.refresh - 1:
            self._endpoints = fetch_endpoints()
            self._fetched_at = now
        blink_on = int(now * 2) % 2 == 0
        return hemara_icons(self._endpoints, blink_on)

    @property
    def failing(self) -> bool:
        endpoints = self._endpoints
        if endpoints is None:
            return False
        return not all(_group_healthy(endpoints, group) for group in HEMARA_GROUPS)

    def next_interval(self) -> float:
        return self.blink if self.failing else self.refresh


class HemaraBlock(widget.GenPollText):
    """
    Polls fast while something fails (to blink), slow otherwise
    """

    def poll(self) -> str:
        text = super().poll()
        if isinstance(self.func, HemaraPoller):
            self.update_interval = self.func.next_interval()
        return text


def make_hemara() -> list[_Widget]:
    return list(
        status_block(
            "hemara",
            HemaraPoller(),
            0.5,
            lazy.spawn(f"xdg-open {GATUS_URL}"),
            block_class=HemaraBlock,
        )
    )
