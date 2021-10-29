#!/usr/bin/env bash

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail

GUKEBOX_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# Low level modules
source "${GUKEBOX_HOME}/libs/common.sh"
source "${GUKEBOX_HOME}/libs/logging.sh"
source "${GUKEBOX_HOME}/libs/util.sh"

source "${GUKEBOX_HOME}/libs/parallel.sh"
source "${GUKEBOX_HOME}/libs/git.sh"

gb::log::enable_error_handler
