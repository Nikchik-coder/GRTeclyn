#!/usr/bin/env bash
# Preview only unless the exact coupled case has received its run-specific go.
set -euo pipefail
card="${1:?usage: run_spin_ring.sh GPU OUT [--run] [--flux|CONTROL_PARENT]}"
out="${2:?fresh output directory required}"
mode="${3:---dry-run}"
parent="${4:-}"
module=ringwormhole_spin_ring
config=spin_ring_co_rotating
if [[ "$parent" == --flux ]]; then
    module=ringwormhole_flux
    config=spin_ring_flux
    parent=""
fi
extra=()
wall=3600
if [[ -n "$parent" ]]; then
    extra=(--control-only-from "$parent")
    if [[ "$mode" == --run ]]; then
        : "${RINGWORMHOLE_DEADLINE_UTC:?original approved deadline required}"
        wall=$(( $(date -u -d "$RINGWORMHOLE_DEADLINE_UTC" +%s) - $(date -u +%s) ))
        (( wall > 0 && wall <= 3600 )) || exit 4
    fi
fi
[[ $# -le 4 && "$card" =~ ^[0-9]+$ ]] || exit 2
[[ "$mode" == --dry-run || "$mode" == --run ]] || exit 2
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
[[ ! -e "$out" ]] || { echo 'output must be fresh' >&2; exit 2; }
grteclyn-wrapper/.venv/bin/python -m "grteclyn_wrapper.optimisation.$module" \
    --config "grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/$config.json" --out "$out" "${extra[@]}"
command=(bash grteclyn-wrapper/scripts/ops/capped_job.sh start
         "ringwormhole-spin-ring-$(date -u +%Y%m%dT%H%M%S)"
         --gpu --threads 4 --mem 160 --timeout "$wall" --
         env XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
         PYTHONUNBUFFERED=1
         bash grteclyn-wrapper/scripts/campaigns/ringwormhole/run_spin_ring_worker.sh "$card" "$out" "$parent" "$module" "$config")
printf '%q ' "${command[@]}"; printf '\n'
[[ "$mode" == --run ]] || exit 0
used="$(nvidia-smi -i "$card" --query-gpu=memory.used --format=csv,noheader,nounits)"
used="${used//[[:space:]]/}"
[[ "$used" =~ ^[0-9]+$ ]] && (( used <= 100 )) || { echo 'GPU occupied or unavailable' >&2; exit 3; }
apps="$(nvidia-smi -i "$card" --query-compute-apps=pid --format=csv,noheader,nounits)"
[[ -z "${apps//[[:space:]]/}" ]] || { echo 'GPU has compute jobs' >&2; exit 3; }
ulimit -c 0
exec "${command[@]}"
