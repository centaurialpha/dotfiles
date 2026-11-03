#!/bin/bash
# exec ~/.local/bin/startdwm
source /etc/X11/xinit/xinitrc.d/50-systemd-user.sh

export XDG_SESSION_TYPE=x11
xrdb -merge ~/.Xresources

case "$WM" in
i3)
  ~/.config/i3/monitor-setup.sh
  export XDG_CURRENT_DESKTOP=i3
  export XDG_SESSION_DESKTOP=i3
  exec i3
  ;;
*)
  export XDG_CURRENT_DESKTOP=Qtile
  export XDG_SESSION_DESKTOP=Qtile

  eval "$(gnome-keyring-daemon --start --components=secrets)"
  export SSH_AUTH_SOCK

  systemctl --user start graphical-session.target

  qtile start

  systemctl --user stop graphical-session.target
  ;;
esac
