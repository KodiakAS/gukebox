#!/usr/bin/env bash

function gb::err() {
    return 1
}

function gb::not_empty() {
    [[ -n ${1-} ]] || gb::err
}