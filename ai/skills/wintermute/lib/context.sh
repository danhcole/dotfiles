#!/usr/bin/env bash
# Print a short summary of repo state for the wintermute router.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "not a git repo"
    exit 0
fi

branch=$(git branch --show-current)
base=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
base=${base:-$(git rev-parse --verify --quiet main >/dev/null && echo main || echo master)}

echo "branch: ${branch:-detached}"
echo "base: $base"
echo "staged files: $(git diff --cached --name-only | wc -l | tr -d ' ')"
echo "unstaged files: $(git diff --name-only | wc -l | tr -d ' ')"
echo "untracked files: $(git ls-files --others --exclude-standard | wc -l | tr -d ' ')"
if [[ -n $branch && $branch != "${base#origin/}" ]]; then
    echo "commits ahead of base: $(git rev-list --count "$base..HEAD" 2>/dev/null || echo '?')"
fi
