#!/usr/bin/env bash

# Return an error for error handler
#
# For example, we have a function named func1, it returns an error:
#
#   func1() {
#       # Do something bad
#       return 1
#   }
#
# Output when calling func1 ( error handler enabled ):
#
#   !!! [1027 11:41:54] Error in test.sh:56
#     Error in test.sh:56. 'return 1' exited with status 1
#   Call stack:
#     1: test.sh:56 main(...)
#   Exiting with status 1
#
# It only print the caller of func1 but obviously we want to see func1 itself.
# Now using `gb::err` to replace `return 1`:
#
#   !!! [1027 11:43:20] Error in test.sh:53
#     Error in test.sh:53. 'return "${code}"' exited with status 1
#   Call stack:
#     1: test.sh:53 func1(...)
#     2: test.sh:56 main(...)
#   Exiting with status 1
#
# Everything looking good.
#
# !!! Attention:
#   If using `gb:err` to replace `return 1`, `gb::err` is the function
#   actually returned, not the `func1`. So using `gb::err; return 1` to
#   make the function return correctly when error handler is disabled.
function gb::err() {
    local code=${1:-1}
    return "${code}"
}

# Mark a non-used variable as used, make shellcheck happy
#
# Example:
#   gb::used VARIABLE_USED_BY_EXTERNAL
function gb::used() {
    true
}
