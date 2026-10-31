#!/usr/bin/env bash
# Foreground stationary experiments; dispatch only on an idle GPU.
# Run under capped_job.sh (200 GiB virtual cap, four threads) or its GPU queue.
# Usage: bash research/optimisation/studies/run_signed_potential.sh d90|geometry GPU OUT
set -euo pipefail
case_name="${1:?case required}"; card="${2:?GPU required}"; out="${3:?output required}"
[[ "$card" =~ ^[0-9]+$ ]] || { echo 'GPU must be numeric' >&2; exit 2; }
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
common=(--potential-domain endpoint-positive --q-min -8 --q-max 8
        --nx 150 --ny 30 --engine cma --gpu "$card" --out "$out")
case "$case_name" in
  d90)
    arguments=(results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0031.json
      --x0 0.05,-4.2,4.2,0 --m-min 0.001 --m-max 0.20 --m-step 0.01
      --stall-ok 1e-9 --maxfev 400 --seed 239 --refine-best final)
    ;;
  geometry)
    arguments=(results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0000.json
      --study-config research/optimisation/studies/d21_geometry_free_spin.toml
      --study-case potential-t4 --free-J --J-min 0 --J-max 7.7 --J-step 0.5
      --x0 0.5,-4.2,4.2,0 --m-min 0.005 --m-max 1.2 --m-step 0.1
      --maxfev 200 --seed 241 --jac-chunk 512)
    ;;
  *) echo 'case must be d90 or geometry' >&2; exit 2 ;;
esac
# Fail closed on unavailable telemetry, an occupied card, or active compute jobs.
used="$(nvidia-smi -i "$card" --query-gpu=memory.used --format=csv,noheader,nounits)"
used="${used//[[:space:]]/}"
[[ "$used" =~ ^[0-9]+$ ]] && (( used <= 100 )) || {
  echo "GPU $card unavailable or occupied ($used MiB)" >&2; exit 3;
}
apps="$(nvidia-smi -i "$card" --query-compute-apps=pid --format=csv,noheader,nounits)"
[[ -z "${apps//[[:space:]]/}" ]] || { echo "GPU $card has compute jobs" >&2; exit 3; }
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/grteclyn_scratch/_cache/mpl
printf 'signed-potential start=%s case=%s gpu=%s commit=%s\n' \
  "$(date -u +%FT%TZ)" "$case_name" "$card" "$(git rev-parse HEAD)"
printf 'command: %q ' grteclyn-wrapper/.venv/bin/python -m \
  grteclyn_wrapper.optimisation.commands.optimize_potential "${arguments[@]}" "${common[@]}"
printf '\n'
# A hard limit bounds each individual experiment, independently of queue lifetime.
exec timeout --signal=TERM --kill-after=30 14400 \
  grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.commands.optimize_potential \
  "${arguments[@]}" "${common[@]}"
