#!/bin/bash

feh --bg-fill ~/Pictures/wallpapers/castle.png &
picom --config ~/.config/picom/picom.conf &
dunst -config ~/.config/dunst/dunstrc &
setxkbmap -layout us -variant altgr-intl -option nodeadkeys &
