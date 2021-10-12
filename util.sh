#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# General

# Check target in array
#
# Args:
#   $1 - The target
#   $2 - Array passed by "${ARRAY[@]}"
function gb::util::in_array() {
    local target="$1"
    local element

    shift
    for element; do
        if [[ "${element}" == "${target}" ]]; then
            return 0
        fi
    done
    gb::err
}

# Concat elements by delimiter
#
# Args:
#   $1 - Delimiter
#   $2, $3, ... The elements
#
# Ex:
#   gb::util::join , a b c
#   -> a,b,c
function gb::util::join {
    local IFS="$1"

    shift
    echo "$*"
}

# Convert strings to upper case
#
# Args:
#   $1 - String
#   ...
function gb::util::upper() {
    for message; do
        echo "${message}" | tr "[:lower:]" "[:upper:]"
    done
}

# Convert strings to lower case
#
# Args:
#   $1 - String
#   ...
function gb::util::lower() {
    for message; do
        echo "${message}" | tr "[:upper:]" "[:lower:]"
    done
}

# -----------------------------------------------------------------------------
# File

# Copy the mod of files in src to dst recursively
#
# Args:
#   $1 - src
#   $2 - dst
function gb::util::copy_tree_mod() {
    gb::not_empty "${1-}"
    gb::not_empty "${2-}"
    local src=${1}
    local dst=${2}

    find "${dst}" -type f -print0 | xargs -0 -I{} sh -c \
        "chmod --reference=${src}/\${1##*${dst}/} \$1" -- {} &>/dev/null || true
}

# Find directories
#
# Args:
#   $1 - Target
#   $2 - Ignore hidden (yes or no)
function gb::util::find_all_dir() {
    gb::not_empty "${1-}"
    gb::not_empty "${2-}"

    if [[ "${2}" == "no" ]]; then
        find "${1}" -type d
    else
        find "${1}" -not -path '*/\.*' -type d
    fi
}

# Copy directory structure from src to dst (without files).
#
# Args:
#   $1 - src
#   $2 - dst
#   $3 - Ignore hidden (yes or no)
function gb::util::copy_tree_struct() {
    gb::not_empty "${1-}"
    gb::not_empty "${2-}"
    local src="${1}"
    local dst="${2}"
    local src_abspath
    local new_dirs
    local ignore_hidden=${3:-no}

    if [ -d "${src}" ]; then
        src_abspath="$(cd "$(dirname "${src}")" && pwd)"
        new_dirs=$(cd "${src_abspath}" && gb::util::find_all_dir "$(basename "${src}")" "${ignore_hidden}")
        for dir in ${new_dirs[*]}; do
            mkdir -p "${dst}/${dir}"
        done
    else
        gb::err
    fi
}

# Clean files in target directory by using rsync, faster than rm and find when
# deleteing huge amount of files, and it is recursive (perl unlink is not)
#
# Args:
#   $1 - Target directory
function gb::util::fast_delete() {
    gb::not_empty "${1-}"
    local blank="/tmp/blank_$$"

    mkdir "${blank}"
    rsync -a --delete "${blank}/" "${1}/"
    rm -rf "${blank}"
}

# -----------------------------------------------------------------------------
# System

# Get CPU core number
function gb::util::get_core_num() {
    grep -c processor /proc/cpuinfo
}
