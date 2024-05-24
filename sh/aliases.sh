# Directory listings
if [[ $IS_MAC ]]; then 
    alias ls='ls -G'
else
    alias ls='ls --color'
fi
alias ll='ls -alFh'
alias dus='du -sckx * | sort -nr'

# Git commands (stolen from zanshin.net)
alias ga='git add'
alias gp='git push'
alias gl='git log'
alias gpl="git log --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
alias gs='git status'
alias gd='git diff'
alias gm='git commit -m'
alias gma='git commit -am'
alias gb='git branch'
alias gc='git checkout'
alias gcb='git checkout -b'
alias gra='git remote add'
alias grr='git remote rm'
alias gpu='git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)'
alias gcl='git clone'
alias gta='git tag -a -m'
alias gf='git reflog'
alias gv='git log --pretty=format:'%s' | cut -d " " -f 1 | sort | uniq -c | sort -nr'
alias gsh="git shortlog | grep -E '^[ ]+\w+' | wc -l"
alias gu="git shortlog | grep -E '^[^ ]'"
alias gcm="git checkout master"
alias gca="git commit --amend"

# Common dirs
alias gosre="cd ~/git/xgen-cloud/gosre"
alias tf="cd ~/git/xgen-cloud/gosre/ops/terraform"

# neovim
if [[ $(which nvim) ]]; then
    alias vim='nvim'
    alias vimdiff='nvim -d'
fi

alias aws-relog="aws sso login --profile sre-sso; aws sso login --profile gov"

alias mongod="mongod --dbpath ~/.mongodb/data"

alias kpv="kubectl get pods -o json | jq '.items[].metadata | \"\\(.labels.xgen_app) \\(.labels.\"app.kubernetes.io/version\")\"'"
