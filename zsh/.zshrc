# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ******************************************************************************
# Terminal integration
# ******************************************************************************
source ~/.iterm2_shell_integration.zsh

# ******************************************************************************
# Lazy-load NVM (saves ~300ms shell startup)
# Instead of sourcing nvm.sh on every shell, wrap the commands in functions
# that load the real nvm on first use and then forward the call.
# ******************************************************************************
nvm() { unset -f nvm node npm npx; [[ -s "$HOME/.nvm/nvm.sh" ]] && . "$HOME/.nvm/nvm.sh"; nvm "$@"; }
node() { unset -f nvm node npm npx; [[ -s "$HOME/.nvm/nvm.sh" ]] && . "$HOME/.nvm/nvm.sh"; node "$@"; }
npm() { unset -f nvm node npm npx; [[ -s "$HOME/.nvm/nvm.sh" ]] && . "$HOME/.nvm/nvm.sh"; npm "$@"; }
npx() { unset -f nvm node npm npx; [[ -s "$HOME/.nvm/nvm.sh" ]] && . "$HOME/.nvm/nvm.sh"; npx "$@"; }

# ******************************************************************************
# Lazy-load virtualenvwrapper (saves ~200ms shell startup)
# Same pattern: defer the heavy `source virtualenvwrapper.sh` until first use.
# ******************************************************************************
export WORKON_HOME="${HOME}/.virtualenvs"
export VIRTUALENVWRAPPER_PYTHON="/opt/homebrew/bin/python3"  # CHANGEME: your python3 path
export VIRTUALENVWRAPPER_ENV_BIN_DIR="bin"
_load_venvwrapper() { unset -f workon mkvirtualenv rmvirtualenv; source /opt/homebrew/bin/virtualenvwrapper.sh; }
workon() { _load_venvwrapper; workon "$@"; }
mkvirtualenv() { _load_venvwrapper; mkvirtualenv "$@"; }
rmvirtualenv() { _load_venvwrapper; rmvirtualenv "$@"; }

# ******************************************************************************
# Workspace
# ******************************************************************************
export WORKSPACE="$HOME/workspace"

# ******************************************************************************
# Aliases
# ******************************************************************************

# Notification after long-running commands: `sleep 10; alert`
function alert() {
  local cmd=$(fc -ln -1 | sed 's/^\s*//')
  osascript -e "display notification \"$cmd\" with title \"Terminal\""
}

# Modern CLI replacements (install via brew)
alias cat=bat
alias ls=lsd
alias grep=rg
alias c=clear
alias c.="printf '%s' \"\$PWD\" | pbcopy"  # Copy current path to clipboard

# ******************************************************************************
# Key bindings
# ******************************************************************************
bindkey -e
bindkey '\e\e[C' forward-word
bindkey '\e\e[D' backward-word

# ******************************************************************************
# Oh My Zsh
# ******************************************************************************
# Docker CLI completions (fpath before oh-my-zsh compinit)
fpath=($HOME/.docker/completions $fpath)

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
zstyle ':omz:update' mode auto
ENABLE_CORRECTION="true"
COMPLETION_WAITING_DOTS="true"
plugins=(
	zsh-autosuggestions
	zsh-syntax-highlighting
	zsh-completions
	zsh-interactive-cd
	aliases
	aws
	brew
	docker
	fzf
	git
	helm
	kubectl
	kubectx
	macos
	pip
	python
	urltools
	web-search
)

source $ZSH/oh-my-zsh.sh

export LANG=en_US.UTF-8
export EDITOR='nano'

[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ******************************************************************************
# GPG (for signed commits)
# ******************************************************************************
export GPG_TTY=$(tty)

# ******************************************************************************
# API tokens — read from files, never hardcoded
# CHANGEME: set up your own token files or remove these
# ******************************************************************************
# export SOME_API_TOKEN="$(<~/.tokens/some-service)"
# export GITHUB_TOKEN="$(<~/.github/token)"

# ******************************************************************************
# zoxide (smarter cd — learns your most-used directories)
# ******************************************************************************
eval "$(zoxide init zsh)"
