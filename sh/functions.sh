function cup {
        for i in $(host $1 | awk '{ if (substr($4,1,1) ~ /[0-9]/ ) print $4 }' | sort); do
                ping -c 1 -W 1 $i > /dev/null
                if [[ $? -ne 0 ]]; then
                        host $i | awk '{printf "%-40s" ENVIRON["CBold"] ENVIRON["CRed"] "down\n" ENVIRON["CClear"], $5}'
                else
                        host $i | awk '{printf "%-40s" ENVIRON["CBold"] ENVIRON["CGreen"] "up\n" ENVIRON["CClear"], $5}'
                fi
        done
}

function ccmd {
        for i in $(host $1 | awk '{ if (substr($4,1,1) ~ /[0-9]/) print $4 }'); do
                ping -c 1 -w 1 $i > /dev/null
                if [[ $? -ne 0 ]]; then
                        host $i | awk '{printf "%-40s" ENVIRON["CBold"] ENVIRON["CRed"] "down\n" ENVIRON["CClear"], $5}'
                else
                        echo ""
                        echo "Running $2 on $(host $i | awk '{print $5}')"
                        ssh root@$i $2
                        echo ""
                fi
        done
}

function ssr {
        ssh root@$1
}

function myip {
    curl -s https://canihazip.com | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
}

function bkp {
    cp $1{,.bkp}
}

function fdiff {
    if [[ $(which colordiff) ]]; then
        colordiff -y -W $COLUMNS $1 $2 | less -R
    else
        diff -y -W $COLUMNS $1 $2 | less -R
    fi
}
