# dotfiles

- OS: [Arch Linux](https://archlinux.org/)
- WM: [Qtile](https://qtile.org/) and my [own](https://github.com/centaurialpha/dwm) build of [dwm](https://dwm.suckless.org/)
- Shell: [fish](https://fishshell.com/) with [hydro](https://github.com/jorgebucaran/hydro) prompt
- Terminal: My [own](https://github.com/centaurialpha/st) build of [st](https://st.suckless.org/)
- Editor: [Neovim](https://neovim.io/), config in its own [repo](https://github.com/centaurialpha/nvim-config)
- Browser: [Firefox](https://www.mozilla.org/firefox/)
- Launcher: My [own](https://github.com/centaurialpha/dmenu) build of [dmenu](https://tools.suckless.org/dmenu/) with [j4-dmenu-desktop](https://github.com/enkore/j4-dmenu-desktop)
- File Manager: [yazi](https://github.com/sxyazi/yazi)
- Compositor: [picom](https://github.com/yshui/picom)
- Notifications: [dunst](https://dunst-project.org/)
- Wallpaper: [feh](https://feh.finalrewind.org/)
- Fonts: Input Mono, Iosevka Term and [pixelarticons](https://github.com/halfmage/pixelarticons)

## Screenshot
![screenshot qtile](screenshot-dotfiles-qtile.png)

## How to install
Managed with [yadm](https://yadm.io/):
```
yadm clone git@github.com:centaurialpha/dotfiles.git
```

Hardware differences between machines (battery name, CPU sensor, NVIDIA,
backlight, monitors) are detected at runtime by the qtile config and
`monitor-setup`, so every machine uses the same files.

### Qtile
`qtile-extras` and `python-pulsectl-asyncio` come from the AUR:
```
paru -S qtile-extras python-pulsectl-asyncio
```

After updating qtile or qtile-extras, restart qtile (reload is not enough).

The bar also uses `brightnessctl`, `pavucontrol` and `wpctl` (PipeWire).

### Choosing the WM
`startx` runs qtile by default. To use dwm:
```
WM=dwm startx
```

The default for each machine goes in `~/.config/wm` (`qtile` or `dwm`), not versioned.

### Other
- Install fisher and plugins: `fisher update`
