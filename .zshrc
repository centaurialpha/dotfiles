pfetch

# Installed by AUR
export SPACESHIP_ROOT=/usr/lib/spaceship-prompt

HISTFILE=~/.cache/zsh/history
HISTSIZE=1000
SAVEHIST=1000

bindkey  "^[[H"   beginning-of-line
bindkey  "^[[4~"   end-of-line
bindkey  "^[[P"   delete-char

# Load zsh-syntax-highlighting
source ~/.zsh-scripts/syntax-highlighting/zsh-syntax-highlighting.zsh 2>/dev/null
# Load zsh-autosuggestions
source ~/.zsh-scripts/autosuggestions/zsh-autosuggestions.zsh 2>/dev/null
# Load completions
fpath=(~/.zsh-scripts/completions/src $fpath)
autoload -U compinit; compinit

# Add ~/.local/bin to PATH
PATH=~/.local/bin:$PATH

# Aliases
alias {v,vim}='nvim'
# dotfiles management
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
# ls with colors
alias ls='ls --color=auto -la'
# Bat instead of cat
alias cat='bat --style=plain,grid,header --theme=Dracula'

SPACESHIP_USER_SHOW=always
SPACESHIP_USER_COLOR=blue
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

autoload -U promptinit; promptinit
prompt spaceship
