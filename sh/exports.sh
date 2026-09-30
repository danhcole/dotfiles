# Setup terminal, and turn on colors
export TERM=xterm-256color
export CLICOLOR=1
export PAGER='less'
export EDITOR='nvim'
export GPG_TTY=$(tty)
export GO111MODULE='on'

export ENVOY_TEST_CHEF_CONFIG='${HOME}/git/xgen-cloud/chef-repo/com/.chef'
export ENVOY_TEST_CHEF_REPO='${HOME}/git/xgen-cloud/chef-repo'

# GKE auth
export USE_GKE_GCLOUD_AUTH_PLUGIN=True

# wezterm BS
export WEZTERM_CONFIG_DIR=$HOME/.config/wezterm
export WEZTERM_CONFIG_FILE=$HOME/.config/wezterm/wezterm.lua

# Kube
export KUBECONFIG="/Users/danhcole/git/xgen-cloud/kube-resources/.kube/config:/Users/danhcole/git/xgen-cloud/kube-resources/.kube/rmckubeconfig:/Users/danhcole/git/xgen-cloud/kube-resources/.kube/slskubeconfig:/Users/danhcole/.kube/config"
