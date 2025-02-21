import traceback
import psutil
import subprocess
import os
import configparser
import re
import asyncio
import time
import threading

from libqtile import bar, layout, qtile, widget, pangocffi
from libqtile.log_utils import logger
from libqtile.command.base import expose_command
from libqtile.utils import guess_terminal
from color import Color
from mpd.asyncio import MPDClient
from mpd.base import ConnectionError
from libqtile.utils import create_task, send_notification
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

class MySep(widget.Sep):
    def __init__(self, padding=5):
        super().__init__(
            linewidth=0,
            padding=padding,
        )


class Date(widget.Clock):

    short_format = "<span foreground=\"{}\" weight=\"bold\">%H:%M</span>".format(Color.Green)
    long_format = "<span foreground=\"{}\">%Y-%m-%d, %a</span> <span foreground=\"{}\">%H:%M</span><span foreground=\"{}\">:%S</span>".format(Color.Yellow, Color.Green, Color.Pink)

    def __init__(self, **config):
        super().__init__(**config)
        self.format = self.short_format

    def mouse_enter(self, x, y):
        self.date_format_to("long")

    def mouse_leave(self, x, y):
        self.date_format_to("short")

    def date_format_to(self, para="short"):
        if para == "short":
            self.format = self.short_format
        elif para == "long":
            self.format = self.long_format
        self.tick()


class MPD(widget.base._TextBox):
    defaults = [
        ("host", "localhost", "Host of mpd server"),
        ("port", 6600, "Port of mpd server"),
        ("step", 5, "Volume change for up an down commands in percentage."),
        ("format", "{icon} {info}", "formatter"),
        ("format_info", "{title}-{artist}", "formatter for info."),
        ("state_icon",
         {"play": "",
          "pause": "",
          "stop": "",},
         "Icons for different states"),
        ("format_icon", "{}", "formatter for icon."),
        ("maxchars", 0, "max chars of INFO, excluding icon."),
        ("no_connect", "NO CONNECT", "Message to show when there is no connection.")
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(MPD.defaults)
        self.client = None
        self.state = None

        self.add_callbacks({
            "Button1": self.toggle,
            "Button2": self.gui,
            "Button3": self.stop,
            "Button4": self.previous,
            "Button5": self.next,
        })

    async def _config_async(self):
        self.client = MPDClient()

        await self.client.connect(self.host, self.port)
        await self._update()
        try:
            async for events in self.client.idle(['player', 'playlist', 'output']):
                await self._update()
        except ConnectionError:
            pass

    async def _update(self):
        info = await self.client.status()
        self.state = info["state"]
        icon = self.format_icon.format(self.state_icon.get(self.state, ""))

        try:
            cur = await self.client.currentsong()
            title = cur["title"]
            artist = cur["artist"]
            info = self.format_info.format(title=title, artist=artist)
            if self.maxchars > 0:
                info = info[:self.maxchars]

            info = pangocffi.markup_escape_text(info)
            text =self.format.format(icon=icon, info=info)

        except:
            text = ""
        self.update(text)

    def finalize(self):
        super().finalize()
        try:
            self.client.disconnect()
        except:
            pass

    @expose_command()
    def toggle(self):
        if not self.state or\
           self.state == "stop":
            self.client.play()
        else:
            self.client.pause()

    @expose_command()
    def stop(self):
        self.client.stop()

    @expose_command()
    def next(self):
        self.client.next()

    @expose_command()
    def previous(self):
        self.client.previous()

    @expose_command()
    def gui(self):
        self.qtile.spawn("emacs -f simple-mpc --name SIMPLEMPC")


class PulseVolume(widget.PulseVolume):

    defaults = [
        ("step", 5, "Volume change for up an down commands in percentage."),
    ]

    def __init__(self, **config):
        widget.pulse_volume.PulseVolume.__init__(self, **config)
        self.add_defaults(PulseVolume.defaults)

    def _update_drawer(self):
        if self.emoji:
            if len(self.emoji_list) < 4:
                self.emoji_list = ["\U0001f507", "\U0001f508", "\U0001f509", "\U0001f50a"]
                logger.warning(
                    "Emoji list given has less than 4 items. Falling back to default emojis."
                )

            if self.volume <= 0:
                self.text = self.emoji_list[0]
            elif self.volume <= 30:
                self.text = self.emoji_list[1]
            elif self.volume < 80:
                self.text = self.emoji_list[2]
            elif self.volume >= 80:
                self.text = self.emoji_list[3]
            self.text = "<span foreground=\"{}\">{}</span>".format(Color.Cyan, self.text)
            self.text += " {}%".format(self.volume) if self.volume > 0 else\
                " <span foreground=\"{}\">MUTE</span>".format(Color.Gray)
        else:
            if self.volume == -1:
                self.text = "M"
            else:
                self.text = "{}%".format(self.volume)

class NetInterface(widget.base.InLoopPollText):

    defaults = [
        ("interfaces", [], "Priority for detecting network interface.")
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(NetInterface.defaults)
        self.wireless = False
        self.connected = False

        self.add_callbacks({
            "Button1": self.gui
        })

    def poll(self):
        text = "Error: no interface detected"
        if self.interfaces:
            text = "No connected"
            self.wireless = False
            self.connected = False
            stats = psutil.net_if_stats()
            for interface in self.interfaces:
                if interface in stats:
                    intf = stats[interface]
                    if intf.isup:
                        self.connected = True
                        self.wireless = interface.startswith("wlan")

                        if self.wireless:
                            out = subprocess.check_output(["nmcli","-f","GENERAL.CONNECTION","d","show",interface])
                            name = out.decode().split(" ")[-1].strip()
                            if name != "--":
                                text = name
                        else:
                            text = interface
                        break
        return text

    def tick(self):
        text = self.poll()
        if self.connected:
            if self.wireless:
                text = "<span foreground=\"{}\">󰖩 </span>".format(Color.Pink) + text
            else:
                text = "<span foreground=\"{}\">󰛳 </span>".format(Color.Pink) + text
        else:
            text = "<span foreground=\"{}\">󰲛 </span><span foreground=\"{}\">{}</span>".format(Color.Pink, Color.Gray, text)
        self.update(text)

    @expose_command()
    def gui(self):
        cmd = [guess_terminal(),"-e","nmtui"]
        subprocess.Popen(cmd)


class AppCompleter(widget.prompt.AbstractCompleter):

    app_dir = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        "~/.local/share/applications/",
    ]

    def __init__(self, qtile) -> None:
        # self.qtile = qtile
        self.thisfinal = None  # type: str | None
        self.lookup = None  # type: list[tuple[str, str]] | None
        self.offset = -1
        self.apps = {}

    def actual(self) -> str | None:
        """Returns the current actual value"""
        return self.thisfinal

    def reset(self) -> None:
        self.lookup = None
        self.offset = -1

    def complete(self, txt: str, aliases: dict[str, str] | None = None) -> str:
        ## TODO: sort by frequency
        if self.lookup is None:
            self.get_apps()

            self.lookup = []
            self.offset = -1

            for k,v in self.apps.items():
                if k.startswith(txt):
                    self.lookup.append((k,v))

        self.offset += 1
        if self.offset >= len(self.lookup):
            self.offset = 0
        ret = self.lookup[self.offset]
        self.thisfinal = ret[1]
        return ret[0]

    def get_apps(self):
        for path in self.app_dir:
            fpath = os.path.expanduser(path)
            if os.path.isdir(fpath):
                for each in os.listdir(fpath):

                    config = configparser.ConfigParser(interpolation=None)
                    config.read(os.path.join(fpath, each))
                    if not config.has_section("Desktop Entry"):
                        continue

                    sec = config["Desktop Entry"]
                    if sec.get("Hidden") or sec.get("NoDisplay"):
                        continue

                    name = sec.get("Name")
                    exec = sec.get("Exec")

                    if name and exec:
                        self.apps[name.lower()] = re.sub("%[a-zA-Z]", "", exec)


class AppLauncher(widget.Prompt):
    defaults = [
        ("prompt",
         " ",
         "Text displayed at the prompt"),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(AppLauncher.defaults)
        self.text = "<span foreground=\"{}\">{}</span>".format(Color.Gray, self.prompt)
        self.completers["app"] = AppCompleter

    def start_input(
        self,
        _prompt,
        callback,
        complete=None,
        strict_completer=True,
        allow_empty_input=False,
        aliases: dict[str, str] | None = None,
    ) -> None:
        if self.cursor and self.cursorblink and not self.active:
            self.timeout_add(self.cursorblink, self._blink)
        self.display = "<span foreground=\"{}\">{} </span>".format(Color.Yellow, self.prompt)
        self.active = True
        self.user_input = ""
        self.archived_input = ""
        self.show_cursor = self.cursor
        self.cursor_position = 0
        self.callback = callback
        self.aliases = aliases
        self.completer = self.completers[complete](self.qtile)
        self.strict_completer = strict_completer
        self.allow_empty_input = allow_empty_input
        self._update()
        self.bar.widget_grab_keyboard(self)
        if self.record_history:
            self.completer_history = self.history[complete]
            self.position = len(self.completer_history)

    def _update(self) -> None:
        if self.active:
            self.text = self.archived_input or self.user_input
            cursor = pangocffi.markup_escape_text(" ")
            if self.cursor_position < len(self.text):
                txt1 = self.text[: self.cursor_position]
                txt2 = self.text[self.cursor_position]
                txt3 = self.text[self.cursor_position + 1 :]
                for text in (txt1, txt2, txt3):
                    text = pangocffi.markup_escape_text(text)
                txt2 = self._highlight_text(txt2)
                self.text = "{0}{1}{2}{3}".format(txt1, txt2, txt3, cursor)
            else:
                self.text = pangocffi.markup_escape_text(self.text)
                self.text += self._highlight_text(cursor)
            self.text = self.display + self.text
        else:
            self.text = "<span foreground=\"{}\">{}</span>".format(Color.Gray, self.prompt)
        self.bar.draw()

    def _trigger_complete(self) -> None:
        # Trigger the auto completion in user input
        assert self.completer is not None
        self.user_input = self.completer.complete(self.user_input, self.aliases)
        self.cursor_position = len(self.user_input)


class MailBox(widget.base._TextBox):
    defaults = [
        (
            "update_interval",
            120,
            "Update interval in seconds, if none, the widget updates only once.",
        ),
        ("maildir_path", "~/Mail", "path to the Maildir folder"),
        ("icon", ["󰧬 ", "󰇰 "], "Icons for new message and normal."),
        ("format", "{icon}{num}", "Formatter")
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(MailBox.defaults)
        self.news = 0
        self.maildir_path = os.path.expanduser(self.maildir_path)
        self.running = threading.Event()

    def handler(self, event):
        if event.is_directory and event.src_path.endswith("new"):
            self._update()

    def watchdog_task(self):
        observer = Observer()
        handler = FileSystemEventHandler()
        handler.on_any_event = self.handler
        observer.schedule(handler, self.maildir_path, recursive=True)
        observer.start()
        try:
            while observer.is_alive() and self.running.is_set():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()

    def _configure(self, qtile, bar):
        super()._configure(qtile, bar)

        self._update()
        self.running.set()
        task = threading.Thread(target=self.watchdog_task, daemon=True)
        task.start()

    def _scan(self):
        self.news = 0
        for account in os.listdir(self.maildir_path):
            fp1 = os.path.join(self.maildir_path, account)
            for each in os.listdir(fp1):
                fp2 = os.path.join(fp1, each, "new")
                self.news += len(os.listdir(fp2))

    def _update(self):
        self._scan()
        text = self.format.format(
            icon = "<span foreground=\"{}\">{}</span>".format(Color.Yellow, self.icon[0 if self. news else 1]),
            num = self.news
        )
        self.update(text)

    def finalize(self):
        super().finalize()
        self.running.clear()

    @expose_command()
    def send_notification(self, _from=None):
        if self.news:
            send_notification(
                "Offlineimap{}".format("[%s]" % _from if _from else ""),
                "{}: new message(s)".format(self.news),
            )


mybar = bar.Bar(
    [

        MySep(),

        widget.GroupBox(
            highlight_method="block",
            foreground=Color.White,
            this_current_screen_border=Color.Pink,
            block_highlight_text_color=Color.Black,
            inactive=Color.DarkGray,
            borderwidth=0,
            margin_x=2,
            urgent_border=Color.Red,
        ),

        MySep(),

        # widget.KeyboardLayout(
        #     configured_keyboards=['us', 'us colemak'],
        #     fmt="<span foreground=\"%s\">󰥻 </span>{}" % Color.Green,
        #     display_map = {
        #         "us": "qwerty",
        #         "us colemak": "colemak"
        #     },
        # ),

        widget.CurrentLayout(
            fmt="<span foreground=\"%s\"> </span>{}" % Color.Purple,
        ),

        MySep(),

        widget.Chord(
            foreground=Color.Green,
            fmt="{}->",
        ),

        # MySep(),

        # AppLauncher(
            # record_history=False,
            # prompt=" ",
        # ),

        widget.Spacer(),

        Date(
            fontsize=18,
        ),

        widget.Spacer(),

        # MPD(
        #     font="LXGW WenKai",
        #    maxchars=20,
        #    format_info = "{title}",
        #    fontsize=15,
        #    format_icon = "<span foreground=\"%s\">{}</span>" % Color.Cyan,
        #    state_icon= {
        #        'pause': '󰝛',
        #        'play': '󰝚',
        #        'stop': ''
        #    },
        #    no_connect = "<span foreground=\"%s\">NO CONNECTION</span>" % Color.Gray,
        #),

        MySep(),

        # MailBox(),

        # MySep(),

        # NetInterface(
        #     interfaces = ["enp0s31f6", "wlan0"],
        #     update_interval=5.7
        # ),

        # MySep(),

        # widget.Memory(
        #     fmt="<span foreground=\"%s\">󰆼 </span>{}" % Color.Purple,
        #     format="{MemUsed:.1f}{mm}/{MemTotal:.1f}{mm}",
        #     measure_mem="G",
        #     update_interval=5.3,
        # ),

        MySep(),

        PulseVolume(
            emoji=True,
            emoji_list = ["󰸈", "󰕿", "󰖀", "󰕾"]
        ),

        MySep(),

        widget.Backlight(
            fmt="<span foreground=\"%s\">󰖨 </span>{}" % Color.Orange,
            backlight_name="intel_backlight",
            change_command="brightnessctl set {0}%",
            step=5
        ),

        MySep(),

        widget.Battery(
            charge_char="<span foreground=\"{}\">󰂄</span>".format(Color.Green),
            full_char="<span foreground=\"{}\">󰁹</span>".format(Color.Green),
            discharge_char="<span foreground=\"{}\">󰁿</span>".format(Color.Yellow),
            not_charging_char="<span foreground=\"{}\">󰁿</span>".format(Color.Yellow),
            empty_char="<span foreground=\"{}\">󰂎</span>".format(Color.Red),
            unknown_char="<span foreground=\"{}\">󱟨</span>".format(Color.Gray),
            format="{char} {percent:2.0%}",
            low_percentage=0.2,
            low_foreground=Color.Red,
        ),

        MySep(),

        widget.Systray(),

        MySep(),
    ],
    24,
    background=Color.Black)
