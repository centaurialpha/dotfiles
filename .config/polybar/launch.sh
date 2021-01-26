#!/bin/bash

## Add this to your wm startup file.

# Terminate already running bar instances
killall -q polybar
# Wait until the processes have been shut down
# while pgrep -u $UID polybar >/dev/null; do sleep 1; done

# polybar main -c ~/.config/polybar/config.ini &
# for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
#     MONITOR=$m polybar main --reload -c ~/.config/polybar/config.ini &
# done
# MONITOR=eDP1 polybar main --reload -c ~/.config/polybar/config.ini &
for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
    echo $m
    if [ "$m" == "HDMI2" ]; then
	xrandr --output VIRTUAL1 --off --output eDP1 --primary --mode 1920x1080 --pos 0x1080 --rotate normal --output DP1 --off --output HDMI2 --mode 1920x1080 --pos 1920x0 --rotate normal --output HDMI1 --off --output DP2 --off
    fi
done

if type "xrandr"; then
  for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
    MONITOR=$m polybar main --reload -c ~/.config/polybar/config.ini &
  done
else
  polybar main --reload -c ~/.config/polybar/config.ini &
fi
