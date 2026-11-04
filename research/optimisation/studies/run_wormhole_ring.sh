#!/usr/bin/env bash
# Print a capped command by default. --run dispatches ONE separately approved case.
set -euo pipefail
case_name="${1:?usage: run_wormhole_ring.sh potential|ring-fixed|ring-spin GPU OUT [--run]}"
card="${2:?GPU required}"
out="${3:?fresh output root required}"
mode="${4:---dry-run}"
[[ $# -le 4 && "$card" =~ ^[0-9]+$ ]] || { echo 'invalid arguments' >&2; exit 2; }
[[ "$mode" == --dry-run || "$mode" == --run ]] || { echo 'expected --run or --dry-run' >&2; exit 2; }
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
args=(results/spinningwormhole/solutions/fam_b/fam_b_0000.json
      --study-config research/optimisation/studies/wormhole_ring.toml
      --nx 150 --ny 30 --engine cma --maxfev 48 --seed 307
      --x0 1.2,2.4326849506,-0.0456837549,1.196847691
      --m-min 0.15 --m-max 2 --m-step 0.1 --q-min -2 --q-max 8
      --walk-max-iter 24 --walk-max-splits 6 --jac-chunk 256
      --gpu "$card" --out "$out/$case_name")
case "$case_name" in
  potential) args+=(--study-case potential-t4) ;;
  ring-fixed) args+=(--study-case boson-k-1-t4-e1) ;;
  ring-spin) args+=(--study-case boson-k-1-t4-e1
                   --free-J --J-min 0 --J-max 0.4 --J-step 0.025) ;;
  *) echo 'case must be potential, ring-fixed or ring-spin' >&2; exit 2 ;;
esac
[[ ! -e "$out/$case_name" ]] || { echo 'output must be fresh' >&2; exit 2; }
command=(bash grteclyn-wrapper/scripts/ops/capped_job.sh start
         "wormhole-ring-$case_name-$(date -u +%Y%m%dT%H%M%S)"
         --gpu --threads 4 --mem 160 --timeout 14400 --
         grteclyn-wrapper/.venv/bin/python -m
         grteclyn_wrapper.optimisation.commands.optimize_potential "${args[@]}")
printf '%q ' "${command[@]}"
printf '\n'
[[ "$mode" == --run ]] || exit 0
# Fail closed; a preview never queries or initializes a GPU.
used="$(nvidia-smi -i "$card" --query-gpu=memory.used --format=csv,noheader,nounits)"
used="${used//[[:space:]]/}"
[[ "$used" =~ ^[0-9]+$ ]] && (( used <= 100 )) || {
  echo "GPU $card unavailable or occupied ($used MiB)" >&2; exit 3;
}
apps="$(nvidia-smi -i "$card" --query-compute-apps=pid --format=csv,noheader,nounits)"
[[ -z "${apps//[[:space:]]/}" ]] || { echo "GPU $card has compute jobs" >&2; exit 3; }
exec "${command[@]}"
