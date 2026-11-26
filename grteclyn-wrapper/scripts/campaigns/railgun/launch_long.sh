#!/usr/bin/env bash
# Foreground, supervised extension using the frozen binary and original inputs.
# Run inside capped_job.sh: four threads, 160 GiB, at most three wall hours.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
DATA="" NAME="" GPU="" BINARY="" CHECKPOINTS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-dir) DATA="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --gpu) GPU="$2"; shift 2 ;;
    --binary) BINARY="$2"; shift 2 ;;
    --checkpoints) CHECKPOINTS="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -n "${DATA}" && -n "${NAME}" && -n "${GPU}" && -n "${BINARY}" ]] || exit 2
[[ "${NAME}" =~ ^[A-Za-z0-9._-]+$ && "${GPU}" =~ ^[0-9]+$ ]] || exit 2
[[ "${CHECKPOINTS}" == off || "${CHECKPOINTS}" == on ]] || {
  echo "explicit --checkpoints off or on required" >&2; exit 2;
}
export SWH_CAMPAIGN_DIR="${REPO}/runs/railgun/evolution"
export SWH_PREFLIGHT_CONFIG="${HERE}/preflight_campaign.json"
export SWH_REGISTRY="${SWH_CAMPAIGN_DIR}/runs_registry.tsv"
export SWH_CONSUMER_THREADS=1
TEMPLATE="${SWH_CAMPAIGN_DIR}/templates/${NAME}.txt"
cd "${REPO}"
"${REPO}/grteclyn-wrapper/.venv/bin/python" -m \
  grteclyn_stationary.railgun.evolution_long \
  --data-dir "${DATA}" --reference results/railgun/studies/evolution-070-n192 \
  --template "${TEMPLATE}" --binary "${BINARY}" --checkpoints "${CHECKPOINTS}"
nvidia-smi
FIELDS="$(sed 's/#.*//' "${HERE}/frames_default.txt" | tr '\n' ' ')"
exec bash "${HERE}/../spinning_wormhole/launch.sh" \
  --template "${TEMPLATE}" --name "${NAME}" --gpu "${GPU}" --binary "${BINARY}" \
  --profile smoke --subdir long --keep-last 3 --foreground \
  --consume-args "--frames-fields ${FIELDS} --frames-axis z --frames-coord 16 --frames-zoom 16 --frames-center 16 16 16 --frames-cache-slices --frames-auto-zlim --frames-blank-edge 2 --no-psi4 -j 2" \
  --what 'Unperturbed omega=0.70 ring, N=192, original box, t<=50; exploratory long evolution'
