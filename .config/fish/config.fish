fish_add_path --global --path --move ~/.local/bin

set -g fish_greeting

set -gx GPG_TTY (tty)
set -gx _JAVA_AWT_WM_NONREPARENTING 1
set -gx AWT_TOOLKIT MToolkit

alias vim="nvim"
alias v="nvim"
alias ls="eza"

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
set -gx PNPM_HOME $HOME/.local/share/pnpm
fish_add_path --global --path $PNPM_HOME/bin
# pnpm end

function invclaude
    env CLAUDE_CONFIG_DIR="$HOME/.claude-invera" claude $argv
end

# Pi
fish_add_path --global --path $HOME/.npm-global/bin
