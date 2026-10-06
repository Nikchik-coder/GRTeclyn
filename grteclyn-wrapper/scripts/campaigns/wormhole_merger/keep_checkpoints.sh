#!/usr/bin/env bash
# Copy named checkpoints out of a rolling run, before it deletes them.
#
#   bash .../keep_checkpoints.sh --run <run name> --dest <dir> --steps "03000 03500 04000"
#
# WHY.  Production arms write a ROLLING checkpoint (checkpoint_keep = 1): each
# new one deletes the last, so a checkpoint you want to restart from is gone
# minutes after it lands.  Any arm that will be branched -- a gauge experiment,
# a resolution down-step, a freeze restart -- needs its seed copied out of the
# rolling set while the run continues.  This watches the log and copies.
#
# It COPIES.  Nothing in the run is touched, so it is safe to start and safe to
# kill.  A checkpoint is complete when run.log shows "checkPoint() time" on the
# line after its "CHECKPOINT: file = ..." line; copying before that yields a
# torn directory that AMReX will not restart from.  The copy goes to a .partial
# name and is renamed only on success, so an interrupted copy is never mistaken
# for a seed.
#
# START IT AFTER THE RUN IS UP.  Its "is the run gone?" check is
# "no process AND no checkpoint line in the log" -- both true in the seconds
# before the binary starts, so a keeper started too early gives up on every
# checkpoint immediately and says nothing is coming (measured 2026-09-09).
# Wait for run.log to show "Level 0 step".
#
# OPTIONS
#   --run NAME     run directory name under runs/wormhole_merger/ (its run.log
#                  is what gets watched); also the scratch directory name
#   --dest DIR     where to keep them, OUTSIDE the rolling scratch.  The
#                  convention is /tmp/grteclyn_scratch/_keep_<tag>, because a
#                  name starting with _keep is the signal to every pruner and
#                  to the next person that these are not disposable
#   --steps "..."  space-separated level-0 step numbers, as they appear in the
#                  checkpoint name (BinaryWormholeChk03500 -> 03500)
#   --scratch DIR  scratch root (default /tmp/grteclyn_scratch)
#   --prefix NAME  checkpoint name prefix (default BinaryWormhole)
#   --exe PAT      OBSOLETE since 2026-09-15 -- accepted and ignored.  Liveness
#                  now comes from the run's launcher.pid; see the note below.
#   --poll S       seconds between log checks (default 20)
set -uo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
CAMPAIGN="${REPO}/runs/wormhole_merger"
# shellcheck source=lib/run_tree.sh
source "${HERE}/lib/run_tree.sh"   # a run is found by name wherever it is filed

RUN="" DEST="" STEPS="" SCRATCH=/tmp/grteclyn_scratch PREFIX=BinaryWormhole POLL=20 EXE_PAT=main3d
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)     RUN="$2"; shift 2 ;;
    --dest)    DEST="$2"; shift 2 ;;
    --steps)   STEPS="$2"; shift 2 ;;
    --scratch) SCRATCH="$2"; shift 2 ;;
    --prefix)  PREFIX="$2"; shift 2 ;;
    --exe)     EXE_PAT="$2"; shift 2 ;;    # accepted, unused since 2026-09-15
    --poll)    POLL="$2"; shift 2 ;;
    -h|--help) sed -n '2,40p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)         echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
done
for req in RUN DEST STEPS; do
  [[ -n "${!req}" ]] || { echo "missing --${req,,} (try --help)" >&2; exit 2; }
done

SRC="${SCRATCH}/${RUN}"
RUNDIR="$(run_tree_find "${CAMPAIGN}" "${RUN}" || printf '%s' "${CAMPAIGN}/${RUN}")"
LOG="${RUNDIR}/run.log"
PIDFILE="${RUNDIR}/launcher.pid"
[[ -f "${LOG}" ]] || { echo "no run log at ${LOG} -- is the run up yet?" >&2; exit 1; }

# IS THE RUN STILL UP?  The run's own launcher.pid, which run_single.sh
# registers, is the only reliable answer, and it is now the ONLY one accepted.
#
# What was here before was `pgrep -f "<exe>.*<run>"`, and it could never work in
# either direction.  It cannot MATCH a live run: every process of a run is
# started from inside the run directory with relative paths and a neutral label
# ("test params.txt"), precisely so the run name does not appear in a shared
# machine's process table -- so the keeper decided the run was gone on its first
# poll and gave up on every checkpoint not already written.  And when a pattern
# like that does match, it is as likely to be matching the operator's own shell,
# whose command line contains the pattern -- which would leave the keeper
# polling a dead run forever.  This is the same reason the campaign README
# forbids `pkill -f` patterns outright.
#
# So: no pidfile, no keeper.  Refusing here is better than either failure.
[[ -f "${PIDFILE}" ]] || {
  echo "no ${PIDFILE#"${CAMPAIGN}"/} -- the keeper needs the run's launcher.pid to know" >&2
  echo "whether it is still up.  Start the keeper after the run is up, or pass a run" >&2
  echo "that has one." >&2
  exit 1
}
run_is_live() {
  local pid
  pid="$(cat "${PIDFILE}" 2>/dev/null || true)"
  [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null
}

for STEP in ${STEPS}; do
  CHK="${PREFIX}Chk${STEP}"
  while :; do
    if ! run_is_live \
       && ! grep -q "CHECKPOINT: file = .*${CHK}\$" "${LOG}" 2>/dev/null; then
      echo "$(date +%T) run is gone before ${CHK}; giving up on it"; break
    fi
    if grep -A1 "CHECKPOINT: file = .*${CHK}\$" "${LOG}" 2>/dev/null | grep -q 'checkPoint() time'; then
      echo "$(date +%T) ${CHK} complete, copying"
      if cp -a "${SRC}/${CHK}" "${DEST}/${CHK}.partial" && mv "${DEST}/${CHK}.partial" "${DEST}/${CHK}"; then
        echo "$(date +%T) kept ${DEST}/${CHK} ($(du -sh "${DEST}/${CHK}" | cut -f1))"
      else
        echo "$(date +%T) !!! copy of ${CHK} FAILED"
      fi
      break
    fi
    sleep "${POLL}"
  done
done
echo "$(date +%T) keeper done"
