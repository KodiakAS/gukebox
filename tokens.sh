#!/usr/bin/env bash

function gb::err() {
    local code=${1:-1}
    return "${code}"
}

function gb::not_empty() {
    [[ -n ${1-} ]] || gb::err 1
}
