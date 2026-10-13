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
#   e.g. research/spinningwormhole/pack_run.sh symmetric_massless/01_t0_checks \
#            runs/spinning_wormhole/symmetric_massless/validation/t0conv_*
# <group> is <family>/<NN_study>: the family folder (drainhole/ or symmetric_massless/,
# decided 2026-10-13) first, so the two families never mix.
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
  find "${run}/small_data" -maxdepth 1 -type f -exec cp {} "${dest}/" \;
  cp "${run}/params.txt" "${dest}/evolution_params.txt"
  cp "${run}/preflight.json" "${run}/run_manifest.json" "${dest}/"
  grep -E '^\[(swh|preflight|manifest)\]' "${LOGS}/${name}.log" | head -n 40 > "${dest}/launch_banner.txt"
  tail -n 200 "${run}/run.log" > "${dest}/run_tail.log"
  ROOT="${ROOT}" python3 "${ROOT}/grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py" "${dest}"/*
  echo "[pack] ${name} (${status}) -> ${dest#"${ROOT}"/} ($(ls "${dest}" | wc -l) files)"
done
exit "${rc}"
