# copied from https://gist.github.com/4415470
# Adapted from code found at <https://gist.github.com/1712320>

# Characters
SEGMENT_SEPARATOR="\ue0b0"
PLUSMINUS="\u00b1"
BRANCH="\ue0a0"
DETACHED="\u27a6"
CROSS="\u2718"
LIGHTNING="\u26a1"
GEAR="\u2699"

function prompt_char {
    #git branch >/dev/null 2>/dev/null && echo -e " $BRANCH" && return
    if [ $? -ne 0 ]; then
        echo "%{$CRed%}$CROSS%{$CClear%}"
    else
        echo '$'
    fi
}

GIT_PROMPT_PREFIX="%{$CGreen%} [%{$CClear%}"
GIT_PROMPT_SUFFIX="%{$CGreen%}]%{$CClear%}"
GIT_PROMPT_ORIGIN="%{$CYellow%}$PLUSMINUS%{$CClear%}"
GIT_PROMPT_AHEAD="%{$CRed%}ANUM%{$CClear%}"
GIT_PROMPT_BEHIND="%{$CLBlue%}BNUM%{$CClear%}"
GIT_PROMPT_MERGING="%{$CMagenta%}$LIGHTNING%{$CClear%}"
GIT_PROMPT_UNTRACKED="%{$CRed%}u%{$CClear%}"
GIT_PROMPT_MODIFIED="%{$CYellow%}d%{$CCLear%}"
GIT_PROMPT_STAGED="%{$CGreen%}s%{$CClear%}"

function parse_git_branch() {
  (git symbolic-ref -q HEAD || git name-rev --name-only --no-undefined --always HEAD) 2> /dev/null
}

# Show different symbols as appropriate for various Git repository states
function parse_git_state() {

  # Compose this value via multiple conditional appends.
  local GIT_STATE=""

  local NUM_AHEAD="$(git log --oneline @{u}.. 2> /dev/null | wc -l | tr -d ' ')"
  local NUM_BEHIND="$(git log --oneline ..@{u} 2> /dev/null | wc -l | tr -d ' ')"
  
  if [ "$NUM_AHEAD" -gt 0 ] || [ "$NUM_BEHIND" -gt 0 ]; then
      GIT_STATE=$GIT_STATE$GIT_PROMPT_ORIGIN
  fi

  if [ "$NUM_AHEAD" -gt 0 ]; then
    GIT_STATE=$GIT_STATE${GIT_PROMPT_AHEAD//NUM/$NUM_AHEAD}
  fi

  if [ "$NUM_BEHIND" -gt 0 ]; then
    GIT_STATE=$GIT_STATE${GIT_PROMPT_BEHIND//NUM/$NUM_BEHIND}
  fi

  local GIT_DIR="$(git rev-parse --git-dir 2> /dev/null)"
  if [ -n $GIT_DIR ] && test -r $GIT_DIR/MERGE_HEAD; then
    GIT_STATE=$GIT_STATE$GIT_PROMPT_MERGING
  fi

  if [[ -n $(git ls-files --other --exclude-standard 2> /dev/null) ]]; then
    GIT_STATE=$GIT_STATE$GIT_PROMPT_UNTRACKED
  fi

  if ! git diff --quiet 2> /dev/null; then
    GIT_STATE=$GIT_STATE$GIT_PROMPT_MODIFIED
  fi

  if ! git diff --cached --quiet 2> /dev/null; then
    GIT_STATE=$GIT_STATE$GIT_PROMPT_STAGED
  fi

  if [[ -n $GIT_STATE ]]; then
    echo "$GIT_PROMPT_PREFIX$GIT_STATE$GIT_PROMPT_SUFFIX"
  fi

}

# If inside a Git repository, print its branch and state
function git_prompt_string() {
  local git_where="$(parse_git_branch)"
  [ -n "$git_where" ] && echo "on %{$CBlue%} ${git_where#(refs/heads/|tags/)}$(parse_git_state)%{$CClear%}"
}

# If inside NORMAL mode, show it in right prompt
# Taken from @dougblackio
function zle-line-init zle-keymap-select {
    VIM_PROMPT="%{$CYellow%} [% NORMAL]%  %{$CClear%}"
    RPROMPT="${${KEYMAP/vicmd/$VIM_PROMPT}/(main|viins)/}$(git_prompt_string) $EPS1"
    zle reset-prompt
}

zle -N zle-line-init
zle -N zle-keymap-select
export KEYTIMEOUT=1

PROMPT='%{$CLGreen%}%n%\@%m%{$CClear%}:%{$CLBlue%}%~%{$CClear%}$(prompt_char) '
