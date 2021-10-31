#!/usr/bin/env bash

# shellcheck disable=SC1091

CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

source "${CUR_DIR}/../gukebox.sh"

retuen_error() {
    gb::err 127
}

hello() {
    retuen_error
}

hello
