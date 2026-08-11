#!/bin/bash
# exec ~/.local/bin/startdwm
source /etc/X11/xinit/xinitrc.d/50-systemd-user.sh

export XDG_CURRENT_DESKTOP=Qtile
export XDG_SESSION_DESKTOP=Qtile
export XDG_SESSION_TYPE=x11

xrdb -merge ~/.Xresources
exec qtile start
