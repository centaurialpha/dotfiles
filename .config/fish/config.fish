if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

set -gx TERM xterm-256color
# Aliases
# Neo Vim
alias vim="nvim"
alias v="nvim"
# Dot files
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME' # dotfiles management
# Turn on bluetooth
alias bon='sudo ~/turn_on_bluetooth.sh'
# Bat
alias cat='bat --style=plain,grid,header --theme=Dracula'
