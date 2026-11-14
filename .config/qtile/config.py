import sys

from custom.groups import build_groups
from custom.hooks import register_hooks
from custom.keys import (
    build_keys,
    build_mouse,
)
from custom.layouts import (
    build_floating_layout,
    build_layouts,
)
from custom.screens import (
    WIDGET_DEFAULTS,
    build_screens,
)

groups = build_groups()
keys = build_keys(groups)
mouse = build_mouse()
layouts = build_layouts()
floating_layout = build_floating_layout()
widget_defaults = WIDGET_DEFAULTS
extension_defaults = WIDGET_DEFAULTS.copy()
screens = build_screens()
register_hooks()

follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
respect_minimize_requests = True

# Some Java apps require a known WM name
wmname = "qtile"


def _forget_custom_modules() -> None:
    """
    Drop custom/ from sys.modules so the next reload imports it from scratch

    qtile reloads submodules in first-import order, so a module may reload before
    one it depends on and fail until qtile restarts
    """
    for name in [n for n in sys.modules if n == "custom" or n.startswith("custom.")]:
        del sys.modules[name]


_forget_custom_modules()
