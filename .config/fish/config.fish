fish_add_path --global --path --move ~/.local/bin

set -g fish_greeting

if status is-interactive
    # Commands to run in interactive sessions can go here
end

set -gx GPG_TTY (tty)
set -gx TERM xterm-256color
set -gx _JAVA_AWT_WM_NONREPARENTING 1
set -gx AWT_TOOLKIT MToolkit

# Aliases
# Neo Vim
alias vim="nvim"
alias v="nvim"

function run-nvim-chad
  env NVIM_APPNAME=NvimChad nvim
end

function run-nvim-lazy
  env NVIM_APPNAME=LazyVim nvim
end

function run-nvim-kick
  env NVIM_APPNAME=NvimKickstart nvim
end

alias nvim-chad=run-nvim-chad
alias nvim-lazy=run-nvim-lazy
alias nvim-kickstart=run-nvim-kick
alias ls="exa -l"
# Dot files
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME' # dotfiles management
# Bat
# alias cat='bat --style=plain,grid,header --theme=Dracula'
