pfetch

## EXPORT
export SPACESHIP_ROOT=/usr/lib/spaceship-prompt # Installed by AUR
export FZF_DEFAULT_COMMAND="rg --files --follow -g '!*.pyc'" # Ignore pyc files with RipGrep
export TERM="xterm-256color"
export HISTORY_IGNORE="(ls|cd|pwd|exit|sudo reboot|history|cd -|cd ..)"

HISTFILE=~/.cache/zsh/history
HISTSIZE=1000
SAVEHIST=1000

bindkey  "^[[H"   beginning-of-line
bindkey  "^[[4~"   end-of-line
bindkey  "^[[P"   delete-char
bindkey "^[[1;5C" forward-word
bindkey "^[[1;5D" backward-word

source ~/.zsh-scripts/interactive-cd.zsh # Load zsh-syntax-highlighting
source ~/.zsh-scripts/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh
source ~/.zsh-scripts/autosuggestions/zsh-autosuggestions.zsh 2>/dev/null # Load zsh-autosuggestions
source /home/gabox/.config/broot/launcher/bash/br
# Load completions
fpath=(~/.zsh-scripts/completions/src $fpath)
autoload -U compinit; compinit

# Add ~/.local/bin to PATH
PATH=~/.local/bin:$PATH

# Aliases
alias {v,vim}='nvim'
alias pacman='sudo pacman' # Arch pkg system
alias bon='sudo ~/turn_on_bluetooth.sh' # Turn on bluetooth
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME' # dotfiles management
alias cat='bat --style=plain,grid,header --theme=Dracula' # Bat instead of cat
# ls to exa
alias ls='exa -al --group-directories-first'
alias la='exa -a --group-directories-first'
alias ll='exa -l --group-directories-first'
alias lt='exa -aT --group-directories-first'
# Git
alias addall='git add .'
alias pull='git pull origin'
alias push='git push origin'
alias gstat='git status'

# SPACESHIP CONFIG
SPACESHIP_USER_SHOW=always
SPACESHIP_EXEC_TIME_SHOW=false
# Colors
SPACESHIP_USER_COLOR="#ffb86c"
SPACESHIP_CHAR_COLOR_SUCCESS="#50fa7b"
SPACESHIP_CHAR_COLOR_FAILURE="#ff5555"
SPACESHIP_CHAR_COLOR_SECONDARY="#f1fa8c"
SPACESHIP_DIR_COLOR="#8be9fd"
SPACESHIP_GIT_BRANCH_COLOR="#bd93f9"
SPACESHIP_GIT_STATUS_COLOR="#ff5555"
SPACESHIP_BATTERY_SHOW=false
SPACESHIP_PROMPT_ADD_NEWLINE=false
SPACESHIP_PROMPT_SEPARATE_LINE=false
SPACESHIP_CHAR_SYMBOL=❯
SPACESHIP_CHAR_SUFFIX=" "
SPACESHIP_HG_SHOW=false
SPACESHIP_PACKAGE_SHOW=false
SPACESHIP_NODE_SHOW=false
SPACESHIP_RUBY_SHOW=false
SPACESHIP_ELM_SHOW=false
SPACESHIP_ELIXIR_SHOW=false
SPACESHIP_XCODE_SHOW_LOCAL=false
SPACESHIP_SWIFT_SHOW_LOCAL=false
SPACESHIP_GOLANG_SHOW=false
SPACESHIP_PHP_SHOW=false
SPACESHIP_RUST_SHOW=false
SPACESHIP_JULIA_SHOW=false
SPACESHIP_DOCKER_SHOW=false
SPACESHIP_DOCKER_CONTEXT_SHOW=false
SPACESHIP_AWS_SHOW=false
SPACESHIP_CONDA_SHOW=false
SPACESHIP_PYENV_SHOW=false
SPACESHIP_DOTNET_SHOW=false
SPACESHIP_EMBER_SHOW=false
SPACESHIP_KUBECONTEXT_SHOW=false
SPACESHIP_TERRAFORM_SHOW=false
SPACESHIP_TERRAFORM_SHOW=false
SPACESHIP_VI_MODE_SHOW=false
SPACESHIP_JOBS_SHOW=false

if [ -f /etc/bash.command-not-found ]; then
    . /etc/bash.command-not-found
fi

autoload -U promptinit; promptinit
prompt spaceship

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

