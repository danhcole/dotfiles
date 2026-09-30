# SSH-agent setup
KEYS=(id_rsa id_ed25519)

for key in ${KEYS[@]}; do
    [[ -f ~/.ssh/$key ]] || continue
    fp=$(ssh-keygen -lf ~/.ssh/$key.pub 2>/dev/null | awk '{print $2}')
    if [[ -z $fp ]] || ! ssh-add -l 2>/dev/null | grep -qF "$fp"; then
        ssh-add ~/.ssh/$key
    fi
done
