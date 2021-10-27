#!/usr/bin/env bash

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail

CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# Low level modules
source "${CUR_DIR}/libs/common.sh"
source "${CUR_DIR}/libs/logging.sh"
source "${CUR_DIR}/libs/util.sh"

source "${CUR_DIR}/libs/parallel.sh"
source "${CUR_DIR}/libs/git.sh"

gb::log::enable_error_handler
