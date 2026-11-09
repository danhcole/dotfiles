# macOS uses path_helper and /etc/paths.d to load PATH.  We clear and reload it
if [[ -x /usr/libexec/path_helper ]]; then
    PATH=''
    eval `/usr/libexec/path_helper -s`
fi

# Go's default GOPATH; avoids forking `go env` (~15ms) on every shell start
export GOPATH="${GOPATH:-$HOME/go}"
