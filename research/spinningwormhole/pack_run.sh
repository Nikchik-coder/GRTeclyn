#!/usr/bin/env bash
# Pack finished spinning-wormhole runs into results/spinningwormhole/campaign/<group>/<run>/:
# the evolution's streams (data/*.dat), the consumer's small_data, the params as run
# (evolution_params.txt), the launch banner, preflight.json, run_manifest.json and the last
# 200 lines of run.log -- the same set the Step 0/1 holds were packed with -- every file
# scrubbed of machine paths (grteclyn_wrapper/packaging/scrub_paths.py).  Frames and movies
# stay in the run directory.  A run whose manifest still says "running" (live, or its consumer
# still draining) is refused: a partial pack is git pollution.
#
#   research/spinningwormhole/pack_run.sh <group> <run dir> [<run dir> ...]
#   e.g. research/spinningwormhole/pack_run.sh symmetric_massless/01_t0_checks/L128_A1/ve024b \
#            runs/spinning_wormhole/symmetric_massless/01_t0_checks/L128_A1/ve024b/t0conv_*
# <group> is the run's folder under runs/spinning_wormhole/ -- <family>/<NN_study>[/<set>]
# [/<spin>] (decided 2026-10-13) -- so the packed tree mirrors the run tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOGS="${ROOT}/runs/spinning_wormhole/logs"
(( $# >= 2 )) || { sed -n '2,14p' "$0" >&2; exit 2; }
group="$1"; shift
rc=0
for run in "$@"; do
  run="${run%/}"
  name="$(basename "${run}")"
  status="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("status", ""))' \
            "${run}/run_manifest.json")"
  if [[ "${status}" == "running" ]]; then
    echo "[pack] ${name}: manifest says running (live or draining) -- not packed" >&2
    rc=1
    continue
  fi
  dest="${ROOT}/results/spinningwormhole/campaign/${group}/${name}"
  mkdir -p "${dest}"
  cp "${run}"/data/*.dat "${dest}/"
  # a run launched with --profile none has no consumer and so no small_data/
  [[ -d "${run}/small_data" ]] && find "${run}/small_data" -maxdepth 1 -type f -exec cp {} "${dest}/" \;
  cp "${run}/params.txt" "${dest}/evolution_params.txt"
  cp "${run}/preflight.json" "${run}/run_manifest.json" "${dest}/"
  # grep -m, not | head: under pipefail a head that closes early kills grep with SIGPIPE
  # (exit 141) and set -e stops the pack before the scrub (2026-10-13)
  grep -m 40 -E '^\[(swh|preflight|manifest)\]' "${LOGS}/${name}.log" > "${dest}/launch_banner.txt"
  tail -n 200 "${run}/run.log" > "${dest}/run_tail.log"
  ROOT="${ROOT}" python3 "${ROOT}/grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py" "${dest}"/*
  echo "[pack] ${name} (${status}) -> ${dest#"${ROOT}"/} ($(ls "${dest}" | wc -l) files)"
done
exit "${rc}"
