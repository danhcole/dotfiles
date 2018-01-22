# SSH-agent setup
if [[ ! $(ssh-add -l | grep danhcole)  ]]; then
    ssh-add
fi
