import os
from qutebrowser.utils import log

# c = c  # noqa: F821 pylint: disable=E0602,C0103
# config = config  # noqa: F821 pylint: disable=E0602,C0103

config.load_autoconfig()

c.content.proxy = "socks://127.0.0.1:7891"
c.content.default_encoding = 'utf-8'
c.content.javascript.clipboard = "access"

c.url.default_page = "about:blank"
c.url.start_pages = "about:blank"

c.downloads.location.directory = os.path.expanduser("~/Downloads/") 
c.downloads.location.prompt = False

c.zoom.default = "125%"

c.completion.open_categories = ["quickmarks", "history"]

config.source('binding.py')
config.source('dracula-theme.py')
# config.source('styles.py')
