# macOS uses path_helper and /etc/paths.d to load PATH.  We clear and reload it
if [[ -x /usr/libexec/path_helper ]]; then
    PATH=''
    eval `/usr/libexec/path_helper -s`
fi

if [[ -x $(which go) ]]; then
    GOPATH=$(go env GOPATH)
fi
