from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Match, Screen, KeyChord, Key, Rule
from libqtile.lazy import lazy
from bar import mybar
from plugin import Notifier, TkDict
from color import Color

import os

## ------------------------------
## Key Binding
## ------------------------------

mod = "mod4"
terminal = "st"

keys = [ 
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "m", lazy.next_layout(), desc="Move window focus to other window"),
    # Key([mod], "m", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
    Key([mod], "v", lazy.layout.toggle_split()),
    Key([mod, "shift"], "h", lazy.layout.flip_left(), lazy.shuffle_left(), lazy.layout.swap_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.flip_right(), lazy.layout.shuffle_right(), lazy.layout.swap_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.flip_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.flip_up(), desc="Move window up"),
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "a", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "f", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([], "XF86MonBrightnessUp", lazy.spawn('brightnessctl s +5%')),
    Key([], "XF86MonBrightnessDown", lazy.spawn('brightnessctl s 5%-')),
    Key([], "XF86AudioLowerVolume", lazy.widget["pulsevolume"].decrease_vol()),
    Key([], "XF86AudioRaiseVolume", lazy.widget["pulsevolume"].increase_vol()),
    Key([], "XF86AudioMute", lazy.widget["pulsevolume"].mute()),
    

    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "r", lazy.spawncmd(widget="applauncher", complete="app")),    
    Key([mod], "e", lazy.spawn("emacs")),
    Key([mod], "d", lazy.spawn("/home/mrdust/.pydev/bin/python /home/mrdust/pyproj/dict/client.py")),
    Key([mod], "z", lazy.spawn("light-locker-command -l")),

    KeyChord(
        [mod], "c", [
            ## For coherence
            Key([], "k", lazy.widget["keyboardlayout"].next_keyboard()),
            Key([], "e", lazy.widget["keyboardlayout"].next_keyboard()),

            Key([], "p", lazy.spawn("flameshot gui")),
            Key([], "x", lazy.spawn("keepassxc")),
        ],
        name="command"
    ),

    ## MPC
    KeyChord(
        [mod], "s", [
            Key([], "n", lazy.widget["mpd"].next()),
            Key([], "p", lazy.widget["mpd"].previous()),
            Key([], "g", lazy.widget["mpd"].gui()),
            Key([], "t", lazy.widget["mpd"].toggle()),
            Key([], "s", lazy.widget["mpd"].stop()),
        ],
        name="mpd"
    )
]

## ------------------------------
## Groups
## ------------------------------

groups = [
    Group("1", label=" ",
          layouts=[
              layout.MonadTall(
                  border_focus="#ff5555",
                  new_client_position="bottom",
                  ratio=0.6,
                  single_border_width=0,
              ),
              layout.Max()
          ]),
    Group("2",label=" ",
          layouts=[
              layout.Bsp(
                  border_focus="#ff5555",
                  border_width=2,
              )
          ]),
    Group("3",label=" "),
    Group("4",label=" "),
    Group("5",label=" "),
    Group("6",label=" "),
    Group("7",label=" "),
    Group("8",label=" "),
    Group("9",label=" "),
]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
        ]
    )

## ------------------------------
## Layout
## ------------------------------

layouts = [
    # layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    layout.Bsp(
        border_focus="#ff5555",
        fair=False,
        # margin=5,
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    
    # layout.Matrix(),
    # layout.MonadTall(
    #     border_focus="#ff5555",
    #     new_client_position="bottom"
    # ),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]


## ------------------------------
## Screen
## ------------------------------

widget_defaults = dict(
    font="CodeNewRoman Nerd Font",
    fontsize=16,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=mybar,
        wallpaper="~/Pictures/wallpaper/v2-3ff3d6a85edb2f19d343668d24ed9269_r.jpg",
        wallpaper_mode="fill",
    ),
]


## ------------------------------
## Mouse
## ------------------------------
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

## ------------------------------
## Hooks
## ------------------------------
import os
import subprocess

@hook.subscribe.startup_once
def autostart():
    script = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.run([script])


from libqtile.log_utils import logger

@hook.subscribe.client_new
def client_new_rules(window):
    wm_class = window.window.get_wm_class()
    # logger.warn(wm_class)
    
    if wm_class[0] == "qutebrowser":
        g = qtile.groups_map["1"]
        window.togroup(g.name, switch_group=True)

    elif wm_class[1] == "KeePassXC":
        g = qtile.groups_map["9"]
        window.togroup(g.name, switch_group=True)

    elif wm_class[0] == "SIMPLEMPC":
        window.enable_floating()
        window.set_size_floating(1080, 720)

    elif wm_class[0] == "tk":
        window.enable_floating()

    
    
## ------------------------------
## Floating
## ------------------------------

floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)

## ------------------------------
## Misc
## ------------------------------

notifier = Notifier(
    font="LXGW WenKai",
    width=300,
    height=100,
    y=50,
    x=1600,
    max_windows=4,
    gap=10,
    actions=False,
    background=Color.Black,
    foreground=(Color.White, Color.Yellow, Color.Red),
    border=(Color.White, Color.Yellow, Color.Red),
    border_width=2,
    timeout=(3000, 5000, 0)
)

# tkdict = TkDict()

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_click = False
floats_kept_above = True
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
