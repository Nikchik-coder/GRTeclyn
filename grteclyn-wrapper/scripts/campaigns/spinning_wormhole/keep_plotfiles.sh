#!/usr/bin/env bash
# Keep a LIVE run's plotfiles from a given step on, before its consumer deletes them.
#
#   bash .../keep_plotfiles.sh <run dir> <first step> [--dest DIR] [--poll S]
#   bash .../keep_plotfiles.sh --status <run dir> [--dest DIR]
#
# WHY.  The consumer keeps only the last three plotfiles (--keep-last 3), but
# late analyses -- oriented horizon scans, flow finders, offline core profiles --
# run on full plotfiles.  keep_checkpoints.sh does this for checkpoints; this
# does it for plotfiles.
#
# It HARD-LINKS (cp -al) into DEST, by default /tmp/grteclyn_scratch/_keep_<run>_plt
# (the _keep prefix tells every pruner these are not disposable).  A link costs no
# space while the consumer still holds the plotfile, keeps it when the consumer
# deletes its name, and touches nothing in the run.  A plotfile is linked once the
# next one exists (AMReX has finished writing it) or once the evolution has exited,
# which also catches the ones left at a crash; then the keeper exits.  Run it on the
# node that runs the evolution, after the run is up: liveness is the evolution's
# process, found by /proc/<pid>/cwd as in stop_campaign.sh.
set -uo pipefail
SELF="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"

usage() {
  echo "usage: keep_plotfiles.sh <run dir> <first step> [--dest DIR] [--poll S]" >&2
  echo "       keep_plotfiles.sh --status <run dir> [--dest DIR]" >&2
  exit 2
}
STATUS=0
if [[ "${1:-}" == "--status" ]]; then
  STATUS=1
  shift
fi
[[ $# -ge 1 ]] || usage
RUN="$(cd -- "$1" 2>/dev/null && pwd -P)" || { echo "no such run dir: $1" >&2; exit 2; }
shift
FIRST=""
if [[ "${STATUS}" == 0 ]]; then
  [[ "${1:-}" =~ ^[0-9]+$ ]] || usage
  FIRST="$1"
  shift
fi
DEST=""
POLL=60
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) DEST="${2:?}"; shift 2 ;;
    --poll) POLL="${2:?}"; shift 2 ;;
    *) usage ;;
  esac
done
NAME="$(basename -- "${RUN}")"
SCR="$(readlink -f -- "${RUN}/scratch")"
DEST="${DEST:-$(dirname -- "${SCR}")/_keep_${NAME}_plt}"
LOG="${RUN}/keep_plotfiles.log"

# pids whose cwd is exactly the run dir and whose command line matches $1
pids_in_run() {
  local pat="$1" pid cwd cmd
  for pid in /proc/[0-9]*; do
    pid="${pid#/proc/}"
    [[ "${pid}" == "$$" || "${pid}" == "${PPID}" ]] && continue
    cwd="$(readlink "/proc/${pid}/cwd" 2>/dev/null)" || continue
    [[ "${cwd}" == "${RUN}" ]] || continue
    cmd="$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null)" || continue
    [[ "${cmd}" =~ ${pat} ]] && printf '%s\n' "${pid}"
  done
}
mapfile -t KEEPERS < <(pids_in_run '^bash -c .* keep_plotfiles ')

if [[ "${STATUS}" == 1 ]]; then
  echo "keeper : ${KEEPERS[*]:-none running}"
  echo "dest   : ${DEST}"
  echo "kept   : $(ls -1 "${DEST}" 2>/dev/null | grep -E 'Plt[0-9]+$' | tr '\n' ' ')"
  echo "size   : $(du -sh "${DEST}" 2>/dev/null | cut -f1)"
  tail -n 3 "${LOG}" 2>/dev/null
  exit 0
fi

[[ -d "${SCR}" ]] || { echo "scratch not visible from this node: ${RUN}/scratch" >&2; exit 1; }
mapfile -t EVO < <(pids_in_run '^[^ ]+ params\.txt')
[[ ${#EVO[@]} -gt 0 ]] || { echo "no live evolution in ${RUN} on this node" >&2; exit 1; }
[[ ${#KEEPERS[@]} -eq 0 ]] || { echo "a keeper already runs for this run: ${KEEPERS[*]}" >&2; exit 1; }
mkdir -p -- "${DEST}" || exit 1

cd "${RUN}" || exit 1
setsid nohup bash -c '
  scr="$1"; dest="$2"; first=$((10#$3)); evo="$4"; poll="$5"
  echo "[keep] $(date -u +%FT%TZ) plotfiles from step ${first} -> ${dest} (evolution ${evo})"
  while :; do
    alive=0
    for p in ${evo}; do kill -0 "${p}" 2>/dev/null && alive=1; done
    mapfile -t plts < <(ls -1 "${scr}" 2>/dev/null | grep -E "Plt[0-9]+$" | sort)
    for ((i = 0; i < ${#plts[@]}; i++)); do
      name="${plts[i]}"
      (( 10#${name##*Plt} >= first )) || continue
      [[ -e "${dest}/${name}" ]] && continue
      (( i + 1 < ${#plts[@]} || alive == 0 )) || continue
      [[ -f "${scr}/${name}/Header" ]] || continue
      rm -rf -- "${dest}/${name}.partial"
      if cp -al -- "${scr}/${name}" "${dest}/${name}.partial" && mv -- "${dest}/${name}.partial" "${dest}/${name}"; then
        echo "[keep] $(date -u +%FT%TZ) linked ${name}"
      else
        echo "[keep] $(date -u +%FT%TZ) FAILED to link ${name}"
      fi
    done
    if (( alive == 0 )); then
      echo "[keep] $(date -u +%FT%TZ) evolution exited; keeper done"
      exit 0
    fi
    sleep "${poll}"
  done
' keep_plotfiles "${SCR}" "${DEST}" "${FIRST}" "${EVO[*]}" "${POLL}" >> "${LOG}" 2>&1 < /dev/null &

sleep 3
exec bash "${SELF}" --status "${RUN}" --dest "${DEST}"
