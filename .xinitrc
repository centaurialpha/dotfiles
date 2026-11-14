#!/bin/bash
# WM=dwm startx picks the WM, plain startx uses ~/.config/wm (qtile or dwm, not versioned)
WM=${WM:-$(cat ~/.config/wm 2>/dev/null)}
WM=${WM:-qtile}

source /etc/X11/xinit/xinitrc.d/50-systemd-user.sh

export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=$WM
export XDG_SESSION_DESKTOP=$WM
xrdb -merge ~/.Xresources

eval "$(gnome-keyring-daemon --start --components=secrets)"
export SSH_AUTH_SOCK

~/.local/bin/monitor-setup
feh --bg-fill ~/.local/share/wallpapers/current &
picom -b
dunst &

bar_pids=()
case "$WM" in
dwm)
  # dwmblocks builds the status and sb-listen redraws it on each event
  dwmblocks &
  bar_pids+=($!)
  sb-listen &
  bar_pids+=($!)
  session=(~/.local/bin/dwm)
  ;;
*)
  session=(qtile start)
  ;;
esac

systemctl --user start graphical-session.target
"${session[@]}"
[ ${#bar_pids[@]} -gt 0 ] && kill "${bar_pids[@]}" 2>/dev/null
systemctl --user stop graphical-session.target
