#! /usr/bin/env bash
# originally posted at https://askubuntu.com/a/1412554/720005
# shellcheck disable=SC1090

# Invoke this script by calling:
# # bash <(curl https://raw.githubusercontent.com/pop-os/repolib/HEAD/quick-install.sh)

set -e

has() { command -v "$1" > /dev/null; }

if ! has apt-manage; then
    export DEBIAN_FRONTEND=noninteractive

    apt-get update

    # Try differnt ways of installing apt-manage
    # First let's hope there is package ready for installation
    apt-get install --yes apt-manage || true

    # If it still doesn't exist, let's get it from repo
    if ! has apt-manage; then
        mkdir -p /tmp

        # Initialize some useful variables
        PKG_VER='2.0.0'
        PKG="python3-repolib_${PKG_VER}_all.deb"
        URL="https://github.com/pop-os/repolib/releases/download/${PKG_VER}/$PKG"

        if [ ! -e "/tmp/$PKG" ]; then
            PREREQ_PKG=(curl python3-gnupg python3-debian ca-certificates)
            # Grab VERSION_ID and ID from /etc/os-release
            . <(grep -E '^(VERSION_)?ID=' /etc/os-release)

            # Make sure we're using the right mix.
            # Debian requires some missing packages.
            [[ "$ID" == 'debian' ]] \
            && PREREQ_PKG+=( debhelper dh-python python3-all \
                python3-setuptools python3-gnupg python3-debian zstd )

            apt-get install --yes --no-install-recommends "${PREREQ_PKG[@]}"
            
            curl -Lo "/tmp/$PKG" "$URL"

            # If Running on Debian, zstd compression isn't supported by pkg.
            # The code below repackages the deb packages using xz instead.
            if [[ "$ID" == 'debian' ]]; then
                echo "We're on debian, so repackaging without zstd compression..."
                rm -r /tmp/repolib.tmp 2>/dev/null || true
                mkdir -p /tmp/repolib.tmp && pushd /tmp/repolib.tmp/ >/dev/null \
                && mv "/tmp/${PKG}" "${PKG}.tmp" \
                && ar x "${PKG}.tmp" \
                && zstd -d < control.tar.zst | xz > control.tar.xz \
                && zstd -d < data.tar.zst | xz > data.tar.xz \
                && ar -m -c -a sdsd "/tmp/${PKG}" debian-binary control.tar.xz data.tar.xz \
                && popd >/dev/null
            fi
        fi

        # Install the package
        apt-get install --yes "/tmp/$PKG"
    fi
fi

apt-manage "${@:---help}"
