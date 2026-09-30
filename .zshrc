# Source sub-config scritps
# The following lines were added by compinstall
zstyle :compinstall filename '/Users/danhcole/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall

source ~/.zsh/paths.zsh
source ~/.zsh/checks.zsh
source ~/.zsh/colors.zsh
source ~/.zsh/setopt.zsh
source ~/.zsh/exports.zsh
#source ~/.zsh/prompt.zsh
source ~/.zsh/aliases.zsh
source ~/.zsh/bindkeys.zsh
source ~/.zsh/functions.zsh
source ~/.zsh/history.zsh
source ~/.zsh/zsh_hooks.zsh
source ~/.zsh/ssh.zsh
source ~/.zsh/kube.zsh

# General shell settings

umask 0077

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# fzf
# diable if atuin is installed
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

[ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env"

# starship
eval "$(starship init zsh)"
export STARSHIP_CONFIG=~/.config/starship/starship.toml

# wt (git worktrees)
if command -v wt >/dev/null 2>&1; then eval "$(command wt config shell init zsh)"; fi
export PATH="/Users/danhcole/.local/bin:$PATH"
