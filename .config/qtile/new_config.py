from libqtile import bar
from libqtile.config import Screen


def build_widgets():
    widgets = []

def build_bar():
    BAR_SIZE = 26
    COLOR_BACKGROUND = "#232323"
    BAR_MARGIN = 3

    widgets = []

    return bar.Bar(widgets, BAR_SIZE, background=COLOR_BACKGROUND, margin=BAR_MARGIN)


def build_screen():
    POSITION = "top"
    if POSITION == "top":
        screen = Screen(top=build_bar())
    else:
        screen = Screen(bottom=build_bar())
    return screen


screens = [build_screen()]
