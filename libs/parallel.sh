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

# run the given command asynchronously and pop/push tokens
function gb::run_with_lock() {
    local job_file=${1}
    local max_jobs=${2}
    shift
    shift
    local running_jobs=0

    gb::mkpipe

    while IFS= read -r job; do
        if [ -z "${job}" ]; then
            continue
        fi

        if ((running_jobs < max_jobs)); then
            running_jobs=$((running_jobs + 1))
            echo "start a new job: $job"
            ("$@" && echo "done") >&${GB_FREE_FD} &
        else
            IFS= read -r ans <&${GB_FREE_FD}
            echo "job output: $ans"
            echo "start a new job: $job"
            ("$@" && echo "done") >&${GB_FREE_FD} &
        fi
    done <"${job_file}"

    while IFS= read -r ans; do
        running_jobs=$((running_jobs - 1))
        echo "job output: $ans"
        if ((running_jobs == 0)); then
            break
        fi
    done <&${GB_FREE_FD}

    exec {GB_FREE_FD}<&-
}
