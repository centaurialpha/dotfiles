#!/bin/bash

# Monitor externo a la izquierda como principal. Sin HDMI conectado falla sin efecto.
xrandr --output HDMI-1 --mode 1920x1080 --primary --left-of eDP-1 --output eDP-1 --mode 1920x1080 2>/dev/null

feh --bg-fill ~/.local/share/wallpapers/current &
picom &
dunst &
