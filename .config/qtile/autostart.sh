#!/bin/bash

feh --bg-fill ~/Pictures/wallpapers/winter-city.jpg &
picom --experimental-backends &
dunst -config ~/.config/dunst/dunstrc &
setxkbmap -layout us -variant altgr-intl -option nodeadkeys &
