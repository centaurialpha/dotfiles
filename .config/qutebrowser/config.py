"""
qutebrowser config, matched to the qtile palette and fonts
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qutebrowser.config.config import ConfigContainer
    from qutebrowser.config.configfiles import ConfigAPI

# Injected by qutebrowser when it loads this file
config: ConfigAPI = globals()["config"]
c: ConfigContainer = globals()["c"]

# Settings changed from the UI stay out; this file is the only source
config.load_autoconfig(False)

BG = "#0a0a0a"
SURFACE = "#1a1a1a"
BLOCK = "#2a2a2a"
TEXT = "#e8e8e8"
INACTIVE = "#555555"
MUTED = "#8a8a8a"
ACCENT = "#1270a8"
ACCENT_SOFT = "#0e4361"
GOLD = "#c0a36e"
GREEN = "#87a987"
RED = "#e46876"
LINK = "#7fb4ca"

TERMINAL = "st"

# qb-work starts qutebrowser with its own basedir and this same file
WORK_PROFILE = "qutebrowser-work" in config.datadir.parts

# General
# start-work.html holds internal links, so it stays out of the public dotfiles
# qb-work changes configdir, so pages are found next to this file instead
HERE = Path(__file__).parent
work_page = HERE / "start-work.html"
start_page = work_page if WORK_PROFILE and work_page.exists() else HERE / "start.html"


# Bookmark groups shown on the start page, the rest only in completion
START_PAGE_GROUPS = (
    "links",
    "hemara envs",
    "hemara infra",
    "hemara services",
    "homelab",
)


def write_bookmarks_script(urls_file: Path, target: Path) -> None:
    """
    Group bookmarks by their "group: " title prefix for the start page
    """
    groups: dict[str, list[dict[str, str]]] = {g: [] for g in START_PAGE_GROUPS}
    for line in urls_file.read_text().splitlines():
        url, _, title = line.partition(" ")
        group, _, name = title.partition(": ")
        if group in groups:
            groups[group].append({"url": url, "title": name or url})
    target.write_text(f"window.BOOKMARKS = {json.dumps(groups)};\n")


# Refreshed on every config load, so new bookmarks show after :config-source
bookmarks_file = HERE / "bookmarks" / "urls"
if not WORK_PROFILE and bookmarks_file.exists():
    write_bookmarks_script(bookmarks_file, HERE / "bookmarks.js")
c.url.start_pages = [start_page.as_uri()]
c.url.default_page = start_page.as_uri()
c.auto_save.session = True
c.session.lazy_restore = True
c.confirm_quit = ["downloads"]
c.editor.command = [TERMINAL, "-e", "nvim", "{file}", "-c", "normal {line}G{column0}l"]
c.downloads.location.directory = "~/Downloads"
c.downloads.location.prompt = False
c.downloads.remove_finished = 5000
c.downloads.position = "bottom"

# yazi as file picker for uploads
YAZI_PICKER = [TERMINAL, "-e", "yazi", "--chooser-file={}"]
c.fileselect.handler = "external"
c.fileselect.single_file.command = YAZI_PICKER
c.fileselect.multiple_files.command = YAZI_PICKER
c.fileselect.folder.command = [TERMINAL, "-e", "yazi", "--cwd-file={}"]

# Privacy and noise
c.content.blocking.method = "auto"
c.content.blocking.adblock.lists = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt",
    "https://secure.fanboy.co.nz/fanboy-cookiemonster.txt",
    "https://secure.fanboy.co.nz/fanboy-annoyance.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt",
]
c.content.cookies.accept = "no-3rdparty"
c.content.autoplay = False
c.content.notifications.enabled = "ask"
c.content.geolocation = "ask"
c.content.pdfjs = True
# Lets "copy" buttons on GitHub and docs reach the clipboard
c.content.javascript.clipboard = "access-paste"
c.input.insert_mode.auto_load = True

# Ask sites for dark theme, never force it
c.colors.webpage.preferred_color_scheme = "dark"
c.colors.webpage.bg = BG

# Fonts
c.fonts.default_family = "Input Mono"
c.fonts.default_size = "10pt"
c.fonts.web.family.fixed = "Iosevka Term"
c.fonts.tabs.selected = "bold default_size default_family"

# Tabs and statusbar
c.tabs.show = "multiple"
c.tabs.last_close = "default-page"
c.tabs.title.format = "{audio}{index} {perc}{current_title}"
c.tabs.title.format_pinned = "{index}"
c.tabs.select_on_remove = "last-used"
c.tabs.padding = {"top": 4, "bottom": 4, "left": 6, "right": 6}
c.tabs.indicator.width = 0
c.tabs.favicons.show = "never"
c.statusbar.padding = {"top": 4, "bottom": 4, "left": 6, "right": 6}
c.statusbar.widgets = ["keypress", "search_match", "url", "scroll", "progress"]
if WORK_PROFILE:
    c.statusbar.widgets = ["text:work", *c.statusbar.widgets]
    c.window.title_format = "work: {perc}{current_title}"
c.completion.height = "30%"
c.completion.shrink = True
c.hints.chars = "asdfghjkl"
c.hints.border = "none"
c.hints.padding = {"top": 1, "bottom": 1, "left": 3, "right": 3}
c.scrolling.smooth = True

# Colors
c.colors.statusbar.normal.bg = BG
c.colors.statusbar.normal.fg = TEXT
c.colors.statusbar.insert.bg = ACCENT
c.colors.statusbar.insert.fg = TEXT
c.colors.statusbar.passthrough.bg = ACCENT_SOFT
c.colors.statusbar.passthrough.fg = TEXT
c.colors.statusbar.command.bg = BG
c.colors.statusbar.command.fg = TEXT
c.colors.statusbar.caret.bg = BLOCK
c.colors.statusbar.caret.selection.bg = BLOCK
c.colors.statusbar.private.bg = SURFACE
c.colors.statusbar.command.private.bg = SURFACE
c.colors.statusbar.progress.bg = ACCENT
c.colors.statusbar.url.fg = TEXT
c.colors.statusbar.url.hover.fg = LINK
c.colors.statusbar.url.success.http.fg = TEXT
c.colors.statusbar.url.success.https.fg = GREEN
c.colors.statusbar.url.error.fg = RED
c.colors.statusbar.url.warn.fg = GOLD

c.colors.tabs.bar.bg = BG
c.colors.tabs.odd.bg = BG
c.colors.tabs.even.bg = BG
c.colors.tabs.odd.fg = INACTIVE
c.colors.tabs.even.fg = INACTIVE
c.colors.tabs.selected.odd.bg = ACCENT
c.colors.tabs.selected.even.bg = ACCENT
c.colors.tabs.selected.odd.fg = TEXT
c.colors.tabs.selected.even.fg = TEXT
c.colors.tabs.pinned.odd.bg = BLOCK
c.colors.tabs.pinned.even.bg = BLOCK
c.colors.tabs.pinned.selected.odd.bg = ACCENT
c.colors.tabs.pinned.selected.even.bg = ACCENT

c.colors.completion.fg = TEXT
c.colors.completion.odd.bg = SURFACE
c.colors.completion.even.bg = SURFACE
c.colors.completion.category.bg = BG
c.colors.completion.category.fg = MUTED
c.colors.completion.category.border.top = BG
c.colors.completion.category.border.bottom = BG
c.colors.completion.item.selected.bg = ACCENT
c.colors.completion.item.selected.fg = TEXT
c.colors.completion.item.selected.border.top = ACCENT
c.colors.completion.item.selected.border.bottom = ACCENT
c.colors.completion.item.selected.match.fg = TEXT
c.colors.completion.match.fg = LINK
c.colors.completion.scrollbar.bg = SURFACE
c.colors.completion.scrollbar.fg = INACTIVE

c.colors.hints.bg = GOLD
c.colors.hints.fg = BG
c.colors.hints.match.fg = INACTIVE
c.colors.keyhint.bg = SURFACE
c.colors.keyhint.fg = TEXT
c.colors.keyhint.suffix.fg = GOLD

c.colors.prompts.bg = SURFACE
c.colors.prompts.fg = TEXT
c.colors.prompts.border = "none"
c.colors.prompts.selected.bg = ACCENT
c.colors.prompts.selected.fg = TEXT

c.colors.messages.info.bg = SURFACE
c.colors.messages.info.fg = TEXT
c.colors.messages.info.border = SURFACE
c.colors.messages.warning.bg = SURFACE
c.colors.messages.warning.fg = GOLD
c.colors.messages.warning.border = SURFACE
c.colors.messages.error.bg = SURFACE
c.colors.messages.error.fg = RED
c.colors.messages.error.border = SURFACE

c.colors.downloads.bar.bg = BG
c.colors.downloads.start.bg = ACCENT_SOFT
c.colors.downloads.stop.bg = ACCENT
c.colors.downloads.error.bg = RED

# Work profile in Invera brand colors, same as the claude-invera status line
INVERA_GREEN = "#28e384"
INVERA_BLUE = "#5a7fff"
# Pure black and bold: dark gray on the brand blue was hard to read
INK = "#000000"
WORK_COLORS = {
    "statusbar.normal.bg": INVERA_BLUE,
    "statusbar.normal.fg": INK,
    "statusbar.command.bg": INVERA_BLUE,
    "statusbar.command.fg": INK,
    "statusbar.insert.bg": INVERA_GREEN,
    "statusbar.insert.fg": INK,
    "statusbar.progress.bg": INVERA_GREEN,
    "statusbar.url.fg": INK,
    "statusbar.url.hover.fg": INK,
    "statusbar.url.success.http.fg": INK,
    "statusbar.url.success.https.fg": INK,
    "tabs.selected.odd.bg": INVERA_BLUE,
    "tabs.selected.odd.fg": INK,
    "tabs.selected.even.bg": INVERA_BLUE,
    "tabs.selected.even.fg": INK,
    "completion.item.selected.bg": INVERA_BLUE,
    "completion.item.selected.fg": INK,
    "completion.item.selected.border.top": INVERA_BLUE,
    "completion.item.selected.border.bottom": INVERA_BLUE,
    "completion.item.selected.match.fg": INK,
}
if WORK_PROFILE:
    for option, color in WORK_COLORS.items():
        config.set(f"colors.{option}", color)
    c.fonts.statusbar = "bold default_size default_family"
    # Google and Atlassian SSO break without third-party cookies
    c.content.cookies.accept = "all"

# Search engines, used as "<key> <query>" in :open
c.url.searchengines = {
    "DEFAULT": "https://duckduckgo.com/?q={}",
    "g": "https://www.google.com/search?q={}",
    "aw": "https://wiki.archlinux.org/index.php?search={}",
    "aur": "https://aur.archlinux.org/packages?K={}",
    "pkg": "https://archlinux.org/packages/?q={}",
    "gh": "https://github.com/search?q={}&type=repositories",
    "py": "https://pypi.org/search/?q={}",
    "pyd": "https://docs.python.org/3/search.html?q={}",
    "yt": "https://www.youtube.com/results?search_query={}",
    "w": "https://es.wikipedia.org/wiki/Special:Search?search={}",
}

# Bindings
config.bind(",M", "hint links spawn --detach mpv {hint-url}")
config.bind(",m", "spawn --detach mpv {url}")
config.bind(",d", "hint links spawn --detach st -e yt-dlp -P ~/Downloads {hint-url}")
config.bind(",t", "config-cycle tabs.show multiple never")
config.bind("<Ctrl-e>", "edit-text", mode="insert")
config.bind("xb", "config-cycle statusbar.show always in-mode")
# Force dark on the current site only, saved per host
config.bind(
    ",D",
    "config-cycle -p -u *://{url:host}/* colors.webpage.darkmode.enabled true false",
)
# Absolute path, qb-work changes configdir
QUTE_RBW = HERE / "userscripts" / "qute-rbw"
config.bind(",p", f"spawn --userscript {QUTE_RBW}")
config.bind(",P", f"spawn --userscript {QUTE_RBW} --password-only")
config.bind(",c", "spawn --detach firefox {url}")
config.bind(",r", "spawn --userscript readability")
# tmux-style tab prefix, replaces the default <Ctrl-a> (navigate increment)
config.unbind("<Ctrl-a>")
config.bind("<Ctrl-a>n", "tab-next")
config.bind("<Ctrl-a>p", "tab-prev")
