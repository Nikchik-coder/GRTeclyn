#!/usr/bin/env bash
# Run inside capped_job.sh. Export and certification must finish first.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
DATA="" NAME="" GPU="" BINARY="" CHECKPOINTS="" N=""
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-dir) DATA="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --gpu) GPU="$2"; shift 2 ;;
    --n) N="$2"; shift 2 ;;
    --binary) BINARY="$2"; shift 2 ;;
    --checkpoints) CHECKPOINTS="$2"; shift 2 ;;
    --preflight-only) EXTRA+=(--preflight-only); shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -n "${DATA}" && -n "${NAME}" && -n "${BINARY}" && "${CHECKPOINTS}" == off ]] || {
  echo "required: --data-dir DIR --name NAME --n N --gpu ID --binary EXE --checkpoints off" >&2; exit 2;
}
[[ "${NAME}" =~ ^[A-Za-z0-9._-]+$ ]] || exit 2
case "${N}:${GPU}" in
  96:0|128:0|192:1) ;;
  *) echo "approved assignment: N96/N128 on card 0; N192 on card 1" >&2; exit 2 ;;
esac
export SWH_CAMPAIGN_DIR="${REPO}/runs/railgun/evolution"
export SWH_PREFLIGHT_CONFIG="${HERE}/preflight_campaign.json"
export SWH_REGISTRY="${SWH_CAMPAIGN_DIR}/runs_registry.tsv"
TEMPLATE="${SWH_CAMPAIGN_DIR}/templates/${NAME}.txt"
mkdir -p -- "$(dirname -- "${TEMPLATE}")"
cd "${REPO}"
"${REPO}/grteclyn-wrapper/.venv/bin/python" -m \
  grteclyn_wrapper.optimisation.railgun.evolution_amr prepare \
  --out "${DATA}" --n "${N}" --template "${TEMPLATE}" --checkpoints off \
  > "${TEMPLATE}.contract.json.tmp"
mv -- "${TEMPLATE}.contract.json.tmp" "${TEMPLATE}.contract.json"
nvidia-smi
FIELDS="$(sed 's/#.*//' "${HERE}/frames_default.txt" | tr '\n' ' ')"
exec bash "${HERE}/../spinning_wormhole/launch.sh" \
  --template "${TEMPLATE}" --name "${NAME}" --gpu "${GPU}" --binary "${BINARY}" \
  --profile smoke --subdir ergoregion --keep-last 3 --foreground \
  "${EXTRA[@]}" \
  --consume-args "--frames-fields ${FIELDS} --frames-axis z --frames-coord 32 --frames-zoom 2 --frames-center 32 32 32 --frames-cache-slices --frames-auto-zlim --frames-blank-edge 2 --no-psi4" \
  --what 'Strongest accepted ergoregion ring; L64, six levels, Richardson study to t=50, checkpoints OFF'
