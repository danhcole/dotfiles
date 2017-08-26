#ZSH Specific Aliases

# Source common aliases
source ~/.sh/aliases.sh

# Directory listings
alias lst="ls -R | grep ":$" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/'"

# Colorize grep
alias grep='grep --color=auto'