#Bash Specific Aliases

# Source common aliases
source ~/.sh/aliases.sh

# Directory listings


# Colorize grep
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Standard Bash LS aliases
alias la='ls -A'
alias l='ls -CF'

# Bash 'alert'
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# .bash_aliases
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi