#!/usr/bin/env bash
# Preview only unless the exact coupled case has received its run-specific go.
set -euo pipefail
card="${1:?usage: run_ergoregion108_continuation.sh GPU OUT [--run]}"
out="${2:?fresh output directory required}"
mode="${3:---dry-run}"
[[ $# -le 3 && "$card" =~ ^[0-9]+$ ]] || exit 2
[[ "$mode" == --dry-run || "$mode" == --run ]] || exit 2
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
[[ ! -e "$out" ]] || { echo 'output must be fresh' >&2; exit 2; }
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.ringwormhole_continuation \
    --config grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108_continuation.json --out "$out"
command=(bash grteclyn-wrapper/scripts/ops/capped_job.sh start
         "ringwormhole-cont108-$(date -u +%Y%m%dT%H%M%S)"
         --gpu --threads 4 --mem 160 --timeout 3600 --
         env XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
         PYTHONUNBUFFERED=1
         bash grteclyn-wrapper/scripts/campaigns/ringwormhole/run_ergoregion108_continuation_worker.sh "$card" "$out")
printf '%q ' "${command[@]}"; printf '\n'
[[ "$mode" == --run ]] || exit 0
used="$(nvidia-smi -i "$card" --query-gpu=memory.used --format=csv,noheader,nounits)"
used="${used//[[:space:]]/}"
[[ "$used" =~ ^[0-9]+$ ]] && (( used <= 100 )) || { echo 'GPU occupied or unavailable' >&2; exit 3; }
apps="$(nvidia-smi -i "$card" --query-compute-apps=pid --format=csv,noheader,nounits)"
[[ -z "${apps//[[:space:]]/}" ]] || { echo 'GPU has compute jobs' >&2; exit 3; }
ulimit -c 0
exec "${command[@]}"
