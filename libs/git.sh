#!/usr/bin/env bash

function gb::git::show_root() {
    git rev-parse --show-toplevel
}

function gb::git::get_last_tag() {
    git describe --abbrev=0
}

function gb::git::count_commits_ahead_last_tag() {
    git describe --long | awk -F "-" '{ print $(NF-1) }'
}
