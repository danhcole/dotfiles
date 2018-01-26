# checks (stolen from Mark Nichols, who stole it from zshuery)
if [[ $(uname) = 'Linux' ]]; then
    IS_LINUX=1
fi

if [[ $(uname) = 'Darwin' ]]; then
    IS_MAC=1
fi

if [[ -x `command -v brew` ]]; then
    HAS_BREW=1
fi

if [[ -x `command -v apt-get` ]]; then
    HAS_APT=1
fi

if [[ -x `command -v yum` ]]; then
    HAS_YUM=1
fi
