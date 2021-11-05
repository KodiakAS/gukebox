#!/usr/bin/env bash
# Provides logging and exception handling functions.

# Datetime formatted for logging.
function gb::log::__now() {
    date +"[%m%d %H:%M:%S]"
}

# Print out panic message, only using before the script aborted by error
#
# Args:
#   $1 - Message
#   ...
function gb::log::__panic() {
    echo "!!! $(gb::log::__now) ${1-}" >&2
    shift
    for message; do
        echo "    ${message}" >&2
    done
}

# Handler for when we exit automatically on an error.
# Borrowed from kubernetes logging script
function gb::log::__errexit() {
    local err="${PIPESTATUS[*]}"

    # If the shell we are in doesn't have errexit set (common in subshells) then
    # don't dump stacks.
    set +o | grep -qe "-o errexit" || return

    set +o xtrace
    local code="${1:-1}"
    gb::log::error_exit "Error in ${BASH_SOURCE[1]}:${BASH_LINENO[0]}. '${BASH_COMMAND}' exited with status ${err}" "${code}" 1
}

# Handler for exit by command.
function gb::log::__cmdexit() {
    local exit_status=$?

    ((exit_status == 0)) || {
        set +o | grep -qe "-o errexit" || return
        set +o xtrace

        # LINENO in stack frame 1 is always 1 because it has been reseted by bash before trap EXIT
        gb::log::error_exit "Exit by command '${BASH_COMMAND}' in ${BASH_SOURCE[1]}." "${exit_status}" 1
    }
}

# Enable error handler.
# If errexit has been setted, dump stacks and exit on error.
function gb::log::enable_error_handler() {
    trap 'gb::log::__errexit' ERR
    set -o errtrace
}

# Trace abnormal exit, disabled by default.
function gb::log::trace_exit() {
    trap 'gb::log::__cmdexit' EXIT
    set -o errtrace
}

# Log an error and exit.
#
# Args:
#   $1 - Message to log with the error
#   $2 - The error code to return
#   $3 - The number of stack frames to skip when printing.
function gb::log::error_exit() {
    local code="${2:-1}"
    local stack_skip="${3:-0}"
    stack_skip=$((stack_skip + 1))

    local source_file=${BASH_SOURCE[${stack_skip}]}
    local source_line=${BASH_LINENO[$((stack_skip - 1))]}
    gb::log::__panic "Error in ${source_file}:${source_line}"
    [[ -z ${1-} ]] || {
        echo "  ${1}" >&2
    }
    gb::log::stack ${stack_skip}
    echo "Exiting with status ${code}" >&2

    trap - EXIT
    exit "${code}"
}

# Print out the stack trace
#
# Args:
#   $1 - The number of stack frames to skip when printing.
function gb::log::stack() {
    local stack_skip=${1:-0}
    stack_skip=$((stack_skip + 1))
    if [[ ${#FUNCNAME[@]} -gt ${stack_skip} ]]; then
        echo "Call stack:" >&2
        local i
        for ((i = 1; i <= ${#FUNCNAME[@]} - stack_skip; i++)); do
            local frame_no=$((i - 1 + stack_skip))
            local source_file=${BASH_SOURCE[${frame_no}]}
            local source_lineno=${BASH_LINENO[$((frame_no - 1))]}
            local funcname=${FUNCNAME[${frame_no}]}
            echo "  ${i}: ${source_file}:${source_lineno} ${funcname}(...)" >&2
        done
    fi
}

# Raise an error with message ( print error message and return an error code )
# Only works when `errexit` enabled, otherwise just same as `gb::log::error`
#
# Args:
#   $1 - Message
#   ...
function gb::log::raise() {
    gb::log::error "$@"

    # Not using `gb::err` to ignore current function call when print stack
    return 1
}

# Log with level error, if has multiple args, messages after the first
# one will be indented.
#
# Args:
#   $1 - Message
#   ...
#
# Vars required:
#   LOGGER_NAME
function gb::log::error() {
    local logger_name="${LOGGER_NAME-}"
    [[ -z ${logger_name} ]] || logger_name="[${logger_name}]"

    echo "$(gb::log::__now)${logger_name}[ERROR] ${1-}" >&2
    shift
    for message; do
        echo "    ${message}" >&2
    done
}

# Log with level warning
#
# Args:
#   $1 - Message
#   ...
#
# Vars required:
#   LOGGER_NAME
function gb::log::warning() {
    local logger_name="${LOGGER_NAME-}"
    [[ -z ${logger_name} ]] || logger_name="[${logger_name}]"

    for message; do
        echo "$(gb::log::__now)${logger_name}[WARN] ${message}"
    done
}

# Log with level info
#
# Args:
#   $1 - Message
#   ...
#
# Vars required:
#   LOGGER_NAME
function gb::log::info() {
    local logger_name="${LOGGER_NAME-}"
    [[ -z ${logger_name} ]] || logger_name="[${logger_name}]"

    for message; do
        echo "$(gb::log::__now)${logger_name} ${message}"
    done
}

# Log with level info, if has multiple args, messages after the first one will
# be indented.
#
# Args:
#   $1 - Message
#   ...
#
# Vars required:
#   LOGGER_NAME
function gb::log::warnlist() {
    local logger_name="${LOGGER_NAME-}"
    [[ -z ${logger_name} ]] || logger_name="[${logger_name}]"

    echo "$(gb::log::__now)${logger_name}[WARN] ${1-}"
    shift
    for message; do
        echo "    ${message}"
    done
}

# Log with level info, if has multiple args, messages after the first one will
# be indented.
#
# Args:
#   $1 - Message
#   ...
#
# Vars required:
#   LOGGER_NAME
function gb::log::infolist() {
    local logger_name="${LOGGER_NAME-}"
    [[ -z ${logger_name} ]] || logger_name="[${logger_name}]"

    echo "$(gb::log::__now)${logger_name} ${1-}"
    shift
    for message; do
        echo "    ${message}"
    done
}
