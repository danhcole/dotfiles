# SSH-agent setup
if [[ ! $(ssh-add -l | grep -e 'dan.*cole' ) ]]; then
    ssh-add
fi
