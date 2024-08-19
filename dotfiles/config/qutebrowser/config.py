import os
from qutebrowser.utils import log

# c = c  # noqa: F821 pylint: disable=E0602,C0103
# config = config  # noqa: F821 pylint: disable=E0602,C0103

config.load_autoconfig()

c.content.proxy = "socks://127.0.0.1:7891"
c.content.default_encoding = 'utf-8'
c.content.javascript.clipboard = "access"
c.content.autoplay = False


c.url.default_page = "about:blank"
c.url.start_pages = "about:blank"
c.url.searchengines = {
    "DEFAULT": "https://duckduckgo.com/?q={}",
    "arch": "https://wiki.archlinux.org/?search={}",
    "google": "https://google.com/search?hl=en&q={}",
    "github": "https://github.com/search?q={}&type=repositories",
    "anna": "https://annas-archive.org/search?q={}",
}

c.downloads.location.directory = os.path.expanduser("~/Downloads/")
c.downloads.location.prompt = False
c.downloads.remove_finished = 5

c.statusbar.widgets = ["keypress","search_match","url","scroll","progress"]
c.zoom.default = "125%"

c.completion.open_categories = ["quickmarks", "history"]

c.tabs.last_close = "blank"
c.tabs.title.format = "{audio}{current_title}"

config.source('binding.py')
config.source('dracula-theme.py')
# config.source('styles.py')
