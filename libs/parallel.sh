#!/usr/bin/env bash

# Get file descriptor of current bash process
function gb::get_self_fd() {
    ls /proc/$$/fd
}

# Open a pipe, Only works on bash 4.1+
#
# Vars set:
#   GB_FREE_FD
function gb::mkpipe() {
    gb::check_bash_version "4.1.0"
    mkfifo pipe-$$
    exec {GB_FREE_FD}<>pipe-$$
    rm pipe-$$
}

# Run command parallel in given seconds
#
# Args:
#   $1 - degree of parallelism
#   $2 - running time, 0 means forever
#   $3 - command
function gb::run_command_parallel() {
    local max_jobs=${1}
    local time=${2}
    shift
    shift

    local running_jobs=0
    local end_time=$(($(date +%s) + time))

    gb::mkpipe

    while [ "$(date +%s)" -lt ${end_time} ]; do
        if ((running_jobs < max_jobs)); then
            gb::log::info "[worker-${running_jobs}] START: $*"
            (eval "$*" && echo "${running_jobs}") >&${GB_FREE_FD} &
            running_jobs=$((running_jobs + 1))
        else
            IFS= read -r ans <&${GB_FREE_FD}
            gb::log::info "[worker-${ans}] START: $*"
            (eval "$*" && echo "${ans}") >&${GB_FREE_FD} &
        fi
    done

    exec {GB_FREE_FD}<&-
}

# Read commands from file, and run with parallel
#
# Args:
#   $1 - degree of parallelism
#   $2 - command file path, 1 command per line
function gb::run_command_file_parallel() {
    local max_jobs=${1}
    local job_file=${2}
    local running_jobs=0

    gb::mkpipe

    while IFS= read -r job || [ -n "${job}" ]; do
        if [ -z "${job}" ]; then
            continue
        fi

        if ((running_jobs < max_jobs)); then
            gb::log::info "[worker-${running_jobs}] START: $job"
            (eval "${job}" && echo "${running_jobs}") >&${GB_FREE_FD} &
            running_jobs=$((running_jobs + 1))
        else
            IFS= read -r ans <&${GB_FREE_FD}
            gb::log::info "[worker-${ans}] START: $job"
            (eval "${job}" && echo "${ans}") >&${GB_FREE_FD} &
        fi
    done <"${job_file}"

    while IFS= read -r ans; do
        running_jobs=$((running_jobs - 1))
        if ((running_jobs == 0)); then
            break
        fi
    done <&${GB_FREE_FD}

    exec {GB_FREE_FD}<&-
}
