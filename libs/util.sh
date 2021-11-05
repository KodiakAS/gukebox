#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# General

# Check variable is not empty
#
# Args:
#   $1 - Target variable
function gb::not_empty() {
    [[ -n ${1-} ]]
}

# Check variable is a number
#
# Args:
#   $1 - Target variable
function gb::is_num() {
    [[ ${1:-string} =~ ^-?[0-9\.]*$ ]]
}

# Check target in array
#
# Args:
#   $1 - The target
#   $2 - Array passed by "${ARRAY[@]}"
function gb::in_array() {
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
#   gb::join , a b c
#   -> a,b,c
function gb::join() {
    local IFS="$1"

    shift
    echo "$*"
}

# Convert strings to upper case
#
# Args:
#   $1 - String
#   ...
function gb::upper() {
    for message; do
        echo "${message}" | tr "[:lower:]" "[:upper:]"
    done
}

# Convert strings to lower case
#
# Args:
#   $1 - String
#   ...
function gb::lower() {
    for message; do
        echo "${message}" | tr "[:upper:]" "[:lower:]"
    done
}

# Compare version
# Version1 = Version2    return 0
# Version1 > Version2    return 1
# Version1 < Version2    return 2
#
# Args:
#   $1 - Version1
#   $2 - Version2
function gb::compare_version() {
    if [[ "${1}" == "${2}" ]]; then
        return 0
    fi

    local IFS=.
    local i
    local ver1
    local ver2

    read -ra ver1 <<<"${1}"
    read -ra ver2 <<<"${2}"

    # fill empty fields in ver1 with zeros
    for ((i = ${#ver1[@]}; i < ${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i = 0; i < ${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Retry command with delay increased gradually
#
# Based on bash-lib:
# https://github.com/cyberark/bash-lib/tree/master/helpers
#
# Retry a command multiple times until it succeeds, with escalating
# delay between attempts.
# Delay is 2 * n + random up to 30s, then 30s + random after that.
# For large numbers of retries the max delay is effectively the retry
# count in minutes.
#
# Args:
#   $1 - Retries
#   $1 - Command
function gb::retry {
    # Maxiumum amount of fixed delay between attempts
    # a random value will still be added.
    local -r max_delay=30
    local rc
    local count
    local retries
    local delay

    if [[ ${#} -lt 2 ]]; then
        gb::log::raise "retry usage: retry <retries> <command>"
    fi

    retries=$1
    shift

    if ! gb::is_num "${retries}"; then
        gb::log::raise "Invalid number of retries: ${retries} for command '${*}'".
    fi

    count=0
    until eval "$@"; do
        rc=$?
        count=$((count + 1))
        if [ "${count}" -lt "${retries}" ]; then
            # There are still retries left, calculate delay and notify user.
            delay=$((2 * count))
            if [[ "${delay}" -gt "${max_delay}" ]]; then
                delay=${max_delay}
            fi

            # Add a random amount to the delay to prevent competing processes
            # from re-colliding.
            interval=$((delay + (RANDOM % count)))
            gb::log::info "'${*}' Retry ${count}/${retries} exited ${rc}, retrying in ${interval} seconds..."
            sleep ${interval}
        else
            gb::log::error "Retry ${count}/${retries} exited ${rc}, no more retries left."
            gb::err ${rc}
            return ${rc}
        fi
    done
    return 0
}

# Retry command with constant delay
#
# Args:
#   $1 - Retries
#   $2 - Interval (seconds)
#   $3 - Command
function gb::retry_with_constant {
    if [[ ${#} -lt 3 ]]; then
        gb::log::error "retry usage: retry <retries> <interval (seconds)> <command>"
    fi

    local retries=$1
    shift
    local interval=$1
    shift

    local count
    local rc
    local interval

    if ! gb::is_num "${retries}"; then
        gb::log::error "Invalid number of retries: ${retries} for command '${*}'"
    fi

    if ! gb::is_num "${interval}"; then
        gb::log::error "Invalid interval in seconds: ${retries} for command '${*}'".
    fi

    count=0
    until eval "$@"; do
        rc=$?
        count=$((count + 1))
        if [ "${count}" -lt "${retries}" ]; then
            gb::log::info "'${*}' Retry ${count}/${retries} exited ${rc}, retrying in ${interval} seconds..."
            sleep "${interval}"
        else
            gb::log::error "Retry ${count}/${retries} exited ${rc}, no more retries left."
            gb::err ${rc}
            return ${rc}
        fi
    done
    return 0
}

# Confirm current user is root
function gb::iam_root() {
    if [[ ${EUID} != 0 ]]; then
        gb::err
        return 1
    fi
}

# Confirm current user is not root
function gb::iam_normal_user() {
    if [[ ${EUID} == 0 ]]; then
        gb::err
        return 1
    fi
}

# shellcheck disable=SC2001
# Get value of flags like "--key=value"
#
# Args:
#   $1 - Flag
function gb::get_flag_value() {
    echo "$1" | sed 's/^--[0-9a-zA-Z_-]*=//'
}

# Comfirm target command exists
#
# Args:
#   $1 - Target command
function gb::cmd_exists() {
    command -v "${1}" &>/dev/null
}

# -----------------------------------------------------------------------------
# File

# Copy the mod of files in src to dst recursively
#
# Args:
#   $1 - src
#   $2 - dst
function gb::copy_tree_mod() {
    gb::not_empty "${1-}"
    gb::not_empty "${2-}"
    local src=${1}
    local dst=${2}

    find "${dst}" -type f -print0 | xargs -0 -I{} sh -c \
        "chmod --reference=${src}/\"\${1##*${dst}/}\" \"\$1"\" -- {} &>/dev/null || true
}

# Find directories
#
# Args:
#   $1 - Target
#   $2 - Ignore hidden (yes or no)
function gb::find_all_dir() {
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
function gb::copy_tree_struct() {
    gb::not_empty "${1-}"
    gb::not_empty "${2-}"
    local src="${1}"
    local dst="${2}"
    local src_abspath
    local new_dirs
    local ignore_hidden=${3:-no}

    if [ -d "${src}" ]; then
        src_abspath="$(cd "$(dirname "${src}")" && pwd)"
        new_dirs=$(cd "${src_abspath}" && gb::find_all_dir "$(basename "${src}")" "${ignore_hidden}")
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
function gb::fast_delete() {
    gb::not_empty "${1-}"
    local blank="/tmp/blank_$$"

    mkdir "${blank}"
    rsync -a --delete "${blank}/" "${1}/"
    rm -rf "${blank}"
}

# -----------------------------------------------------------------------------
# System

# Get current bash version.
function gb::get_bash_version() {
    echo "${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]}.${BASH_VERSINFO[2]}"
}

# Check current bash version is greater than target version
#
# Args:
#   $1 - Target version
function gb::check_bash_version() {
    local target_version=${1-}
    local bash_version

    gb::not_empty "${target_version}"

    bash_version="$(gb::get_bash_version)"
    gb::compare_version "${bash_version}" "${target_version}" || {
        [[ $? == 1 ]] || gb::log::raise "Bash version: ${bash_version} is lower than ${target_version}"
    }
}

# Get CPU core number
function gb::get_core_num() {
    grep -c processor /proc/cpuinfo
}
