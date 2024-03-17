import customtkinter as ctk
import http.client
import urllib.parse
import threading
import json

from libqtile import configurable
from libqtile.log_utils import logger

class _App:

    def __init__(
            self,
            title = "TkDict",
            x=0,
            y=0,
            width=300,
            height=200,
                 ):
        self.app = ctk.CTk()
        self.app.title(title)
        self.app.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.lock = threading.RLock()

        self.configurate()

    def configurate(self):
        self.left_frame = ctk.CTkFrame(self.app, width = 200, fg_color=self.white)
        self.right_frame = ctk.CTkFrame(self. app, fg_color=self.white)
        self.left_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=(10,5), pady=10)
        self.right_frame.pack(side=ctk.LEFT, expand=True, fill=ctk.BOTH, padx=(5,10), pady=10)

        self.word = ctk.StringVar()
        self.word.trace("w", lambda name, index, mode, sv=self.word: self.match(sv))

        self.search = ctk.CTkFrame(self.left_frame)
        self.search.pack(side=ctk.TOP, fill=ctk.X, pady=(0,5))
        
        self.search_bar = ctk.CTkEntry(self.search, textvariable=self.word, width=200)
        self.search_bar.pack(side=ctk.TOP, fill=ctk.X, pady=(0,5))
        self.search_bar.focus()
        
        self.search_match = ctk.CTkFrame(self.search, fg_color=self.white, width=200)
        self.search_match.pack(side=ctk.TOP, fill=ctk.BOTH, pady=(5,0))


        self.app.bind("<Up>", lambda _: self.search_focus_next(True))
        self.app.bind("<Down>", lambda _: self.search_focus_next())
        self.app.bind("<Return>", lambda _: self.query())
        self.app.bind('<FocusOut>', lambda _: self.app.destroy())
        self.app.bind("<Escape>", lambda _: self.select_search_bar_or_quite())
        
        self.current_foucs = 0
        self.current_select_word = ""

        self.extras = []
        self.workers = []

    def search_focus_next(self, neg=None):
        widgets = self.search_match.winfo_children()
        max_pos = len(widgets)
        if not max_pos: return
        try:
            if self.current_foucs:
                widgets[self.current_foucs - 1].configure(fg_color=self.white)
        except:
            pass
        
        if self.current_foucs == 0 and neg:
            self.current_foucs = max_pos
        elif self.current_foucs >= max_pos and not neg:
            self.current_foucs = 1 if max_pos else 0
        else:
            self.current_foucs += -1 if neg else 1
        node = widgets[self.current_foucs - 1]
        self.current_select_word = node.cget("text")
        node.configure(fg_color="blue")

    def select_search_bar_or_quite(self):
        if self.search_bar.select_present() or not self.word.get():
            self.app.destroy()
        else:
            self.search_bar.select_range(0, ctk.END)

    @staticmethod
    def request(path):
        conn = http.client.HTTPConnection("127.0.0.1", 42985)
        conn.request("GET", path)
        res = conn.getresponse()
        return json.loads(res.read())
        
    def match(self, var):
        word = var.get()
        self.current_foucs = 0
        self.current_select_word = word
        data = self.request("/match?word=" + urllib.parse.quote(word))

        for widget in self.search_match.winfo_children():
            widget.destroy()
        self.current_foucs = 0
            
        for each in data["data"]:
            btn = ctk.CTkLabel(
                self.search_match,
                text=each,
                corner_radius=0,
                fg_color=self.white,
                text_color=self.black,
                wraplength=180,
            )
            btn.pack(side=ctk.TOP, fill=ctk.X, pady=0)
        self.search.configure(width=200)

    @staticmethod
    def assemble_item(widget, data):
        wword = ctk.CTkLabel(widget, text=data["word"], anchor=ctk.W)
        wword.cget("font").configure(size=20)
        wword.pack(padx=10, pady=(10,0), fill=ctk.X)

        pho = data.get("phonetic")
        if pho:
            wpho = ctk.CTkLabel(widget, text="[%s]" % pho, anchor=ctk.W)
            wpho.configure(text_color="gray")
            wpho.pack(padx=20, fill=ctk.X)

        defs = data["definition"]
        lst = defs
        if isinstance(defs, str):
            lst = defs.split("\n")
            
        for df in lst:
            wd = ctk.CTkLabel(widget, text=df.strip(), anchor=ctk.W)
            wd.pack(padx=15, fill=ctk.X)

        exc = data.get("exchange")
        if exc:
            wexc = ctk.CTkLabel(widget, text=exc, anchor=ctk.W)
            wexc.cget("font").configure(slant="italic")
            wexc.pack(padx=15, fill=ctk.X)

    def query(self):
        word = self.current_select_word if self.current_select_word else self.word.get()
        data = self.request("/query?word=" + urllib.parse.quote(word))

        self.lock.acquire()
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        if data:
            self.assemble_item(self.right_frame, data["data"])

        ## get extra querying result asynchronously
        for w in self.workers:
            if w.is_alive():
                w.running.clear()
        self.workers.clear()
        self.lock.release()
        
        for extra in self.extras:
            worker = Worker(
                self.right_frame,
                self.lock,
                word,
                extra
            )
            worker.daemon = True
            worker.start()
            
        self.search_bar.select_range(0, ctk.END)
            
    def run(self):
        logger.warn("app running")
        self.extras = self.request("/extras")["data"]
        self.app.mainloop()

    def stop(self):
        self.app.destroy()

class TkDict(configurable.Configurable):

    defaults = [
        ('x', 1920-600-20, 'x position on screen to start drawing notifications.'),
        ('y', 64, 'y position on screen to start drawing notifications.'),
        ('width', 600, 'Width of notifications.'),
        ('height', 400, 'Height of notifications.'),
        ("foreground", "#ffffff", "Widget's foreground"),
        ("background", "#000000", "widget's background"),
    ]

    white = "#ffffff"
    black = "#000000"

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(TkDict.defaults)
        self._app = None
        self._show = False

        self._configure()

    def _configure(self, qtile, bar):
        logger.warn("ee")
        
        self._app = _App(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
        )
        logger.warn("dd")
        t = threading.Thread(target=self._app.run,daemon=True)
        t.start()
        logger.warn("tkinter started.")

    def finalize(self):
        if self._app is not None:
            try:
                self._app.stop()
                logger.warn("tkinter stoped.")
            except:
                pass

    

if __name__ == "__main__":
    tkdict = TkDict()
    tkdict.run()
