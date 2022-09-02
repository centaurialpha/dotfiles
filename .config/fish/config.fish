# fish_add_path --global --path --move /usr/local/sbin
# fish_add_path --global --path --move /usr/local/bin
fish_add_path --global --path --move ~/.local/bin

set fish_greeting

if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

set -gx TERM xterm-256color
set -gx _JAVA_AWT_WM_NONREPARENTING 1
set -gx AWT_TOOLKIT MToolkit
set -U fish_color_error ff5555
set -U fish_color_command bd93f9  --bold
set -U fish_color_param ffb86c

# Aliases
# Neo Vim
alias vim="nvim"
alias v="nvim"

alias ls="exa -l"
# Dot files
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME' # dotfiles management
# Bat
alias cat='bat --style=plain,grid,header --theme=Dracula'
