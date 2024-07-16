# SSH-agent setup
KEYS=(id_rsa danhcole-cloud-brs.pem danhcole-cloud-gov.pem sre-ssh-key)

for key in ${KEYS[@]}; do
    if [[ ! $(ssh-add -l | grep -e $key ) ]]; then
        ssh-add /Users/danhcole/.ssh/$key
    fi
done
