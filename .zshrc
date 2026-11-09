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
source ~/.zsh/prompt.zsh
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

# fzr
# diable if atuin is installed
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

[ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env"
