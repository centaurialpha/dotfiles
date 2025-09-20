#!/bin/bash
# exec ~/.local/bin/startdwm
source /etc/X11/xinit/xinitrc.d/50-systemd-user.sh

exec qtile start
