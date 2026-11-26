#!/usr/bin/env bash
# Build the shared SpinningWormhole executable for the optimisation campaign,
# keeping the binary, logs and tracked manifest in the optimisation trees.
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"

export SWH_BINARY_DIR="${REPO}/runs/optimisation/evolution/bin"
export SWH_BUILD_LOG_DIR="${REPO}/runs/optimisation/evolution/logs"
export SWH_BINARY_MANIFEST="${REPO}/results/optimisation/binaries.tsv"

exec bash "${HERE}/../spinning_wormhole/build_binary.sh" "$@"
