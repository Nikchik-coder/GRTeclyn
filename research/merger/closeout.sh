#!/usr/bin/env bash
# Close out finished runs of the wormhole-merger campaign, mechanically.
#
#   bash research/merger/closeout.sh <run> [<run> ...]
#
# For every run named (a directory under runs/wormhole_merger/):
#   1. refuses if its launcher is still alive;
#   2. reports what is left on scratch (plotfiles, checkpoints, size) -- it never
#      deletes anything: pruning is done by hand, on the user's word, and logged
#      in runs/wormhole_merger/MANIFEST_CLEANUP_*.md;
#   3. checks the death window of the data streams for NaN rows and prints the
#      last time, so no number is quoted from a polluted row;
#   4. warns if the run has no line in results/merger/runs_registry.tsv (the
#      launcher writes one when WHM_WHAT is set; otherwise append it by hand);
#   5. stitches the movies: from the slice cache on one fixed colour scale when
#      the run has one, else from the live frames.
# Then, once:
#   6. rebuilds the pack (research/merger/pack_results.sh), which regenerates
#      summary.csv/md, INSTABILITY.md, BRANCHES.md and the clock comparison;
#   7. greps the pack and the plan for machine identity (patterns are derived
#      from the environment at run time, so none is written here);
#   8. prints the two edits that remain by hand: the README claim line and the
#      status row in research/merger/GPU_PLAN.md, plus commit and push.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
RUNS="${ROOT}/runs/wormhole_merger"

# Colour scale for the movies.  A single LINEAR scale over a whole run is set by
# the loudest moment -- the merged core -- and every quieter thing in the frame
# renders white: measured 2026-09-10, the level-5 arm's Pi and Weyl4 movies were
# blank for most of their length while the fields were plainly doing something.
# These signed fields get a symmetric-log scale instead (linear near zero so the
# zero crossings stay readable, logarithmic outside), a fixed number of decades
# below the peak.  Weyl4 takes a shallower range because at two decades most of
# its frame is the coarse grid's own noise.  chi and lapse are bounded and read
# correctly on a linear scale, so they are left off.  Override with WHM_SYMLOG,
# or set it empty for the old all-linear behaviour.
WHM_SYMLOG="${WHM_SYMLOG:-K,phi,Pi,chi_minus_1,shift1,Weyl4_Re:1.5,Weyl4_Im:1.5}"
DEST="${ROOT}/results/merger"
SCRATCH="${GRTECLYN_SCRATCH:-/tmp/grteclyn_scratch}"
PY="${ROOT}/grteclyn-wrapper/.venv/bin/python"
[[ -x "${PY}" ]] || PY="$(command -v python3)"

if [[ $# -eq 0 ]]; then
  sed -n 2,26p "${BASH_SOURCE[0]}"; exit 2
fi

problems=0
for run in "$@"; do
  run="${run%/}"; run="$(basename "${run}")"
  dir="${RUNS}/${run}"
  echo "=================================================================="
  echo "[closeout] ${run}"
  if [[ ! -d "${dir}" ]]; then echo "  no such run directory"; problems=$((problems+1)); continue; fi

  # 1. still running?
  if [[ -f "${dir}/launcher.pid" ]]; then
    pid="$(cat "${dir}/launcher.pid" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "  launcher pid ${pid} is ALIVE -- not a finished run, skipping"; problems=$((problems+1)); continue
    fi
  fi

  # 2. scratch
  if [[ -d "${SCRATCH}/${run}" ]]; then
    nplt=$(find "${SCRATCH}/${run}" -maxdepth 1 -type d -name '*Plt*' | wc -l)
    nchk=$(find "${SCRATCH}/${run}" -maxdepth 1 -type d -name '*Chk*' | wc -l)
    echo "  scratch: $(du -sh "${SCRATCH}/${run}" | cut -f1)  plotfiles ${nplt}  checkpoints ${nchk}  (nothing deleted; prune by hand and log it)"
  else
    echo "  scratch: none"
  fi

  # 3. death window
  for f in "${dir}"/data/*.dat; do
    [[ -f "${f}" ]] || continue
    n_nan=$(tail -n 300 "${f}" | grep -ci 'nan' || true)
    t_end=$(grep -v '^#' "${f}" | tail -n 1 | awk '{print $1}')
    printf "  %-32s last t = %-10s NaN rows in the last 300: %s\n" "$(basename "${f}")" "${t_end:-?}" "${n_nan}"
  done
  if [[ -f "${dir}/run.log" ]]; then
    if grep -q 'NaN' "${dir}/run.log"; then echo "  run.log: NaN abort"; else echo "  run.log: no NaN"; fi
  fi

  # 4. registry
  if grep -qP "^${run}\t" "${DEST}/runs_registry.tsv" 2>/dev/null; then
    echo "  registry: $(grep -P "^${run}\t" "${DEST}/runs_registry.tsv" | cut -f2 | cut -c1-90)..."
  else
    echo "  registry: NOT REGISTERED -- append one line (tab-separated: run, what, caveat, stopped note):"
    echo "     printf '%s\\t%s\\t\\t\\n' '${run}' 'what is different' >> results/merger/runs_registry.tsv"
    problems=$((problems+1))
  fi

  # 5. movies
  if [[ -d "${dir}/frames" ]]; then
    nser=$(find "${dir}/frames" -mindepth 1 -maxdepth 1 -type d ! -name '_*' | wc -l)
    echo "  frames: ${nser} field series"
    if [[ -d "${dir}/frames/_slice_cache" ]]; then
      "${PY}" "${ROOT}/grteclyn-wrapper/scripts/plot/rerender_frames.py" "${dir}/frames" \
        --symlog "${WHM_SYMLOG}" --movies 2>&1 | tail -n 3 | sed 's/^/  /'
    else
      bash "${ROOT}/grteclyn-wrapper/scripts/plot/make_movies.sh" "${dir}" 2>&1 | tail -n 2 | sed 's/^/  /'
    fi
    [[ "${nser}" -le 1 ]] && echo "  WARNING: only ${nser} field rendered -- launch with several (WHM_FRAMES_FIELDS)"
  else
    echo "  frames: NONE (no movies possible)"
  fi
done

# 6. pack
echo "=================================================================="
bash "${ROOT}/research/merger/pack_results.sh" | tail -n 6

# 7. identity grep, patterns from the environment only
# user and host as words; the home directory and every directory between it
# and this checkout as PATH FRAGMENTS ("/name/"), so that ordinary words which
# happen to be directory names do not fire.
pat="\\b$(whoami)\\b"
[[ -n "${HOME:-}" ]] && pat="${pat}|${HOME}"
h="$(hostname 2>/dev/null || true)"; [[ -n "${h}" ]] && pat="${pat}|\\b${h}\\b"
rel="$(dirname "${ROOT}")"; rel="${rel#"${HOME:-/nonexistent}"/}"
IFS=/ read -r -a comps <<< "${rel}"
for c in "${comps[@]}"; do [[ -n "${c}" ]] && pat="${pat}|/${c}/"; done
hits=$(cd "${ROOT}" && git ls-files results/merger research/merger | xargs grep -lE "${pat}" 2>/dev/null || true)
if [[ -n "${hits}" ]]; then
  echo "[closeout] MACHINE IDENTITY in tracked files -- fix before committing:"; echo "${hits}" | sed 's/^/  /'; problems=$((problems+1))
else
  echo "[closeout] identity grep: clean"
fi

# 8. what remains by hand
cat <<TXT
==================================================================
[closeout] by hand, in this order:
  - results/merger/README.md: the Claim/Runs line of the section the run answers
  - research/merger/GPU_PLAN.md: the status row and the queue
  - scratch prune on the user's word, logged in runs/wormhole_merger/MANIFEST_CLEANUP_*.md
  - git add results/merger research/merger; commit (no Co-Authored-By); push to myfork
[closeout] problems flagged: ${problems}
TXT
exit 0
