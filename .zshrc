# Source sub-config scritps
# The following lines were added by compinstall
zstyle :compinstall filename '/Users/danhcole/.zshrc'

autoload -Uz compinit
# Rebuild the completion dump at most once a day; otherwise trust the cache
_stale_dump=(~/.zcompdump(N.mh+24))
if (( $#_stale_dump )); then compinit; else compinit -C; fi
unset _stale_dump
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
# Lazy-load nvm: the first call to nvm/node/npm/npx loads it (saves ~0.9s per shell)
_nvm_lazy_load() {
  unset -f nvm node npm npx
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
}
for _cmd in nvm node npm npx; do
  eval "$_cmd() { _nvm_lazy_load; $_cmd \"\$@\"; }"
done
unset _cmd

# fzf
# diable if atuin is installed
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

[ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env"

# starship
eval "$(starship init zsh)"
export STARSHIP_CONFIG=~/.config/starship/starship.toml

# wt (git worktrees)
# Init output is cached and regenerated whenever the wt binary is newer (saves ~50ms)
if (( $+commands[wt] )); then
  _wt_cache=~/.cache/wt-init.zsh
  if [[ ! -s $_wt_cache || $commands[wt] -nt $_wt_cache ]]; then
    mkdir -p ${_wt_cache:h}
    command wt config shell init zsh >| $_wt_cache
  fi
  source $_wt_cache
  unset _wt_cache
fi
