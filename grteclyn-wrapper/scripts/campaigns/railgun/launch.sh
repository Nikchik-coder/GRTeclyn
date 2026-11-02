#!/usr/bin/env bash
# First unperturbed canonical-ring evolutions use the established supervisor,
# full preflight and plotfile consumer. Start this foreground wrapper inside
# capped_job.sh so the memory/thread/time caps include every child process.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
DATA="" NAME="" GPU="" BINARY="" CHECKPOINTS=""
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-dir) DATA="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --gpu) GPU="$2"; shift 2 ;;
    --binary) BINARY="$2"; shift 2 ;;
    --checkpoints) CHECKPOINTS="$2"; shift 2 ;;
    --preflight-only) EXTRA+=(--preflight-only); shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -n "${DATA}" && -n "${NAME}" && -n "${GPU}" && -n "${BINARY}" && "${CHECKPOINTS}" == off ]] || {
  echo "required: --data-dir DIR --name NAME --gpu ID --binary EXE --checkpoints off" >&2; exit 2;
}
[[ "${NAME}" =~ ^[A-Za-z0-9._-]+$ && "${GPU}" =~ ^[0-9]+$ ]] || exit 2
export SWH_CAMPAIGN_DIR="${REPO}/runs/railgun/evolution"
export SWH_PREFLIGHT_CONFIG="${HERE}/preflight_campaign.json"
export SWH_REGISTRY="${SWH_CAMPAIGN_DIR}/runs_registry.tsv"
TEMPLATE="${SWH_CAMPAIGN_DIR}/templates/${NAME}.txt"
cd "${REPO}"
"${REPO}/grteclyn-wrapper/.venv/bin/python" -m \
  grteclyn_wrapper.optimisation.railgun.evolution_pilot \
  --data-dir "${DATA}" --template "${TEMPLATE}" --checkpoints off
# Required before every start; the operator also checks other card occupants.
nvidia-smi
FIELDS="$(sed 's/#.*//' "${HERE}/frames_default.txt" | tr '\n' ' ')"
exec bash "${HERE}/../spinning_wormhole/launch.sh" \
  --template "${TEMPLATE}" --name "${NAME}" --gpu "${GPU}" --binary "${BINARY}" \
  --profile smoke --subdir pilot --keep-last 3 --foreground \
  "${EXTRA[@]}" \
  --consume-args "--frames-fields ${FIELDS} --frames-axis z --frames-coord 16 --frames-zoom 16 --frames-center 16 16 16 --frames-cache-slices --frames-auto-zlim --frames-blank-edge 2 --no-psi4" \
  --what 'Unperturbed omega=0.70 regular-centre canonical ring, t<=2; no stability claim'
