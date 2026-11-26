#!/usr/bin/env bash
# Campaign-M evolutions use the SpinningWormhole executable contract but keep
# their run products under runs/optimisation/evolution/.
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"

export SWH_CAMPAIGN_DIR="${REPO}/runs/optimisation/evolution"
export SWH_PREFLIGHT_CONFIG="${HERE}/preflight_campaign.json"
export SWH_REGISTRY="${SWH_CAMPAIGN_DIR}/runs_registry.tsv"

exec bash "${HERE}/../spinning_wormhole/launch.sh" "$@"
