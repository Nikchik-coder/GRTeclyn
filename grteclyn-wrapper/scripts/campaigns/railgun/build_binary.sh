#!/usr/bin/env bash
# Canonical complex-scalar evolution, using the campaign build provenance.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
export WHM_BUILD_EXAMPLE=RadialRecipe
export WHM_BINARY_DIR="${REPO}/runs/railgun/evolution/bin"
export WHM_BUILD_LOG_DIR="${REPO}/runs/railgun/evolution/logs"
export WHM_BINARY_MANIFEST="${REPO}/results/railgun/reports/evolution_binaries.tsv"
exec bash "${HERE}/../wormhole_merger/build_binary.sh" --jobs 4 "$@"
