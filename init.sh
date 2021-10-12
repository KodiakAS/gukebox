#!/usr/bin/env bash

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail

CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

source "${CUR_DIR}/tokens.sh"

source "${CUR_DIR}/logging.sh"
source "${CUR_DIR}/util.sh"
source "${CUR_DIR}/parallel.sh"

gb::log::enable_errexit
