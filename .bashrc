# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# Source subconfig scripts

source ~/.bash/aliases.bash
source ~/.bash/colors.bash
source ~/.bash/exports.bash
source ~/.bash/functions.bash
source ~/.bash/prompt.bash
source ~/.bash/history.bash
source ~/.bash/iterm2.bash

# General shell settings

umask 0077

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi
