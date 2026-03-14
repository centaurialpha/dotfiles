# PATH
fish_add_path --global --path --move ~/.local/bin

# No greeting default
set -g fish_greeting

# Environment variables
set -gx GPG_TTY (tty)
set -gx TERM xterm-256color
set -gx _JAVA_AWT_WM_NONREPARENTING 1
set -gx AWT_TOOLKIT MToolkit

# Aliases
alias vim="nvim"
alias v="nvim"
alias ls="exa"

# Dotfiles
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# yazi wrapper
function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (command cat -- "$tmp"); and test -n "$cwd"; and test "$cwd" != "$PWD"
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
end

function fish_greeting
    if status --is-interactive
        type -q fastfetch; and fastfetch
    end
end
