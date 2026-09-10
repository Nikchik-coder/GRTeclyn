#!/usr/bin/env bash
# Reduce finished runs' launcher logs to the part that is not already kept.
#
#   bash .../tidy_logs.sh [--apply] [--logs DIR]
#
# WHY.  run_single.sh already tees the evolution's output to <run>/run.log.
# The launcher's own stream captures the SAME bytes a second time, plus about
# sixteen "[whm]" lines that exist nowhere else: which template, which binary,
# which card, which scratch, which consumer flags, and the final plotfile
# count.  That provenance is worth keeping and the duplicate body is not -- on
# 2026-09-10 it was 434 MB at the top of the campaign directory.
#
# So for every launcher log whose run directory holds a run.log: write the
# "[whm]" lines to <run>/launch_banner.txt and delete the log.  A run whose
# directory is gone keeps its banner under 00_archive/launcher_banners/ instead,
# because that banner is then the only record the run ever existed.
#
# It SKIPS live runs (a running launcher.pid, or a log younger than the run.log
# it would be compared against): truncating a log a process still holds open
# leaves a sparse file the writer keeps appending to at the old offset.
#
# Without --apply it only reports.  Run it at close-out, after closeout.sh.
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
CAMPAIGN="${REPO}/runs/wormhole_merger"

APPLY=0
LOGS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --logs)  LOGS="$2"; shift 2 ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

freed=0 kept=0 skipped=0
shopt -s nullglob
# Both shapes: logs/<name>.log (current) and detached_gpuN_<name>.log (before 2026-09-10).
for log in "${CAMPAIGN}"/logs/*.log "${CAMPAIGN}"/detached_gpu*.log; do
  base="$(basename "${log}")"
  name="${base%.log}"; name="${name#detached_gpu?_}"
  run="${CAMPAIGN}/${name}"
  size=$(stat -c %s "${log}")

  if [[ -f "${run}/launcher.pid" ]] && kill -0 "$(cat "${run}/launcher.pid")" 2>/dev/null; then
    echo "  live, skipped: ${base}"; skipped=$((skipped+1)); continue
  fi

  if [[ -f "${run}/run.log" ]]; then
    target="${run}/launch_banner.txt"
  else
    target="${CAMPAIGN}/00_archive/launcher_banners/${name}.txt"
  fi

  if (( APPLY )); then
    mkdir -p "$(dirname "${target}")"
    grep '^\[whm\]' "${log}" > "${target}" || true
    rm -f "${log}"
  fi
  kept=$((kept+1))
  freed=$((freed+size))
  printf '  %-52s %8s -> %s\n' "${base}" "$(numfmt --to=iec "${size}")" "${target#"${CAMPAIGN}"/}"
done

echo "banners written: ${kept}   live skipped: ${skipped}   space: $(numfmt --to=iec "${freed}")"
(( APPLY )) || echo "(report only -- pass --apply to write the banners and delete the logs)"
