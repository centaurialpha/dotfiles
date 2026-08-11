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

if status is-interactive
    zoxide init fish | source
end

# pnpm
set -gx PNPM_HOME "/home/gabox/.local/share/pnpm"
if not string match -q -- "$PNPM_HOME/bin" $PATH
  set -gx PATH "$PNPM_HOME/bin" $PATH
end
# pnpm end

# Added by LM Studio CLI tool (lms)
set -gx PATH $PATH /home/gabox/.lmstudio/bin

function clear
    pyroclear
end

function clear-and-repaint
    pyroclear
    commandline -f repaint
end

bind \cl clear-and-repaint
