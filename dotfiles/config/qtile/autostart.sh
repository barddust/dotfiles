#!/bin/sh

light-locker --no-late-locking --lock-on-suspend --lock-on-lid &
# pgrep -f lxqt-policykit-agent > /dev/null || lxqt-policykit-agent &
dusnt &
fcitx5 --replace -d > /dev/null &
pgrep -f udiskie > /dev/null || udiskie -t &
pgrep -f jieba-server.py > /dev/null || ~/.pydev/bin/python ~/.emacs.d/elpa/jieba/jieba-server.py &
# pgrep -f "dict.+server.py" > /dev/null || ~/.pydev/bin/python ~/pyproj/dict/server.py &
flameshot &
