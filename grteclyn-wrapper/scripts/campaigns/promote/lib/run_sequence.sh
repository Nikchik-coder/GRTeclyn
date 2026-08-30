#!/usr/bin/env bash
# Run matrix cells strictly one after another, each starting only once the
# previous one has fully exited.
#
#   bash scripts/campaigns/promote/lib/run_sequence.sh \
#       --campaign-dir scripts/campaigns/promote/fgeo_max_cmaes_v2 \
#       FMAX-RC:0 FMAX-RI:0 FMAX-DS:0 FMAX-DS2:0
#
# Sequencing uses run_batch.sh's FOREGROUND=1 mode: replay_eval.py runs as a
# child of this script, so "finished" is its exit status, not a guess derived
# from polling the run directory.  A cell that fails halts the chain.
#
# ---------------------------------------------------------------------------
# This is an orchestrator, and orchestrators outlive the session that made
# them.  On 2026-08-22 a leftover solve_queue.sh quietly launched two cells
# from a dead session.  Everything below marked GUARD exists to make that
# failure mode impossible to repeat:
#
#   GUARD 1  registers launcher.pid, so stop_campaign.sh kills this first
#   GUARD 2  refuses to start when another sequencer is already alive
#   GUARD 3  STOP_SEQUENCE file halts the chain between cells
#   GUARD 4  a failed cell stops the chain (--keep-going to override)
#   GUARD 5  --max-hours deadline, so a hung chain cannot run forever
#   GUARD 6  status file naming the live cell, readable from outside
# ---------------------------------------------------------------------------
set -euo pipefail

LIB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CAMPAIGNS_ROOT="$(cd -- "${LIB_DIR}/../.." && pwd)"
SCRIPTS_ROOT="$(cd -- "${CAMPAIGNS_ROOT}/.." && pwd)"
# shellcheck source=../../../lib/env.sh
source "${SCRIPTS_ROOT}/lib/env.sh"
# shellcheck source=../../lib/launcher_common.sh
source "${CAMPAIGNS_ROOT}/lib/launcher_common.sh"

CAMPAIGN_DIR=""
WAIT_FOR_PID=""
WAIT_POLL_SECONDS="${WAIT_POLL_SECONDS:-60}"
MAX_HOURS="${MAX_HOURS:-48}"
KEEP_GOING=0
CELLS=()

usage() {
  cat >&2 <<'USAGE'
usage: run_sequence.sh --campaign-dir DIR [options] CELL[:GPU] [CELL[:GPU] ...]

  --campaign-dir DIR   campaign holding run.sh + campaign.env.sh (required)
  --wait-for-pid PID   block until this pid exits before the first cell
                       (use it to chain behind a run already in flight)
  --poll-seconds N     how often to check that pid          (default 60)
  --max-hours N        abandon the chain after this long    (default 48)
  --keep-going         carry on after a cell fails          (default: halt)

  CELL[:GPU]           manifest run id, optional first GPU. Cells needing
                       several ranks take GPU..GPU+ranks-1, as run_matrix does.

env: DRY_RUN=1 resolves and prints every cell without launching anything.
USAGE
  exit 2
}

while (($#)); do
  case "$1" in
    --campaign-dir) CAMPAIGN_DIR="${2:-}"; shift 2 ;;
    --wait-for-pid) WAIT_FOR_PID="${2:-}"; shift 2 ;;
    --poll-seconds) WAIT_POLL_SECONDS="${2:-}"; shift 2 ;;
    --max-hours)    MAX_HOURS="${2:-}"; shift 2 ;;
    --keep-going)   KEEP_GOING=1; shift ;;
    -h|--help)      usage ;;
    -*)             echo "[seq] unknown option: $1" >&2; usage ;;
    *)              CELLS+=("$1"); shift ;;
  esac
done

[[ -n "${CAMPAIGN_DIR}" ]] || { echo "[seq] --campaign-dir is required" >&2; usage; }
((${#CELLS[@]})) || { echo "[seq] no cells given" >&2; usage; }

if [[ ! -d "${CAMPAIGN_DIR}" ]]; then
  CAMPAIGN_DIR="${GRTECLYN_ROOT}/grteclyn-wrapper/${CAMPAIGN_DIR}"
fi
CAMPAIGN_DIR="$(cd -- "${CAMPAIGN_DIR}" && pwd)"
RUN_SH="${CAMPAIGN_DIR}/run.sh"
[[ -x "${RUN_SH}" || -f "${RUN_SH}" ]] || { echo "[seq] no run.sh in ${CAMPAIGN_DIR}" >&2; exit 2; }

RUNS_DIR="${RUNS_DIR:-${GRTECLYN_ROOT}/runs/neuralspacetime/hq}"
mkdir -p "${RUNS_DIR}"
LOCK="${RUNS_DIR}/sequence.lock"
STOP_FILE="${RUNS_DIR}/STOP_SEQUENCE"
STATUS="${RUNS_DIR}/sequence.status"
DRY_RUN="${DRY_RUN:-0}"

# --- GUARD 2: one sequencer at a time --------------------------------------
# A stale lock from a killed session must not block forever, so the pid inside
# it is checked for life rather than trusted.
if [[ -f "${LOCK}" ]]; then
  prev="$(cat "${LOCK}" 2>/dev/null || true)"
  if [[ -n "${prev}" ]] && kill -0 "${prev}" 2>/dev/null; then
    echo "[seq] a sequencer is already running (pid ${prev}) -- refusing to start a second." >&2
    echo "[seq] stop it with: bash ${CAMPAIGNS_ROOT}/stop_campaign.sh ${RUNS_DIR}" >&2
    exit 1
  fi
  echo "[seq] clearing stale lock from dead pid ${prev:-?}"
fi

# A stop file left over from a previous chain would silently abort this one.
if [[ -e "${STOP_FILE}" ]]; then
  echo "[seq] stale ${STOP_FILE} present -- remove it before starting." >&2
  exit 1
fi

if [[ "${DRY_RUN}" != "1" ]]; then
  echo $$ > "${LOCK}"
  campaign_register_launcher "${RUNS_DIR}"   # GUARD 1
fi

# --- GUARD 7: never leave the running cell behind --------------------------
# stop_campaign.sh finds real cells on its own (they carry --runs-dir in
# argv), but a bare `kill <sequencer>` must not orphan an evolution either.
# Killing the tree by walking children covers replay_eval.py and everything it
# spawned.  SIGKILL cannot be trapped, so a -9 still needs stop_campaign.sh.
CURRENT_CHILD=""

kill_tree() {
  local pid="$1" sig="${2:-TERM}" child
  for child in $(pgrep -P "${pid}" 2>/dev/null); do
    kill_tree "${child}" "${sig}"
  done
  kill -"${sig}" "${pid}" 2>/dev/null || true
}

cleanup() {
  local rc=$?
  if [[ -n "${CURRENT_CHILD}" ]] && kill -0 "${CURRENT_CHILD}" 2>/dev/null; then
    kill_tree "${CURRENT_CHILD}" TERM
  fi
  [[ "${DRY_RUN}" == "1" ]] || rm -f "${LOCK}"
  # Only drop launcher.pid if it is still ours; a later launcher may own it.
  if [[ -f "${RUNS_DIR}/launcher.pid" ]] && [[ "$(cat "${RUNS_DIR}/launcher.pid" 2>/dev/null)" == "$$" ]]; then
    rm -f "${RUNS_DIR}/launcher.pid"
  fi
  return "${rc}"
}
trap cleanup EXIT

on_signal() {
  local sig="$1"
  echo "[seq] ${sig} received -- stopping the running cell and halting the chain" >&2
  if [[ -n "${CURRENT_CHILD}" ]] && kill -0 "${CURRENT_CHILD}" 2>/dev/null; then
    kill_tree "${CURRENT_CHILD}" TERM
    # Give the evolution a moment to close its plotfiles before insisting.
    sleep 5
    kill -0 "${CURRENT_CHILD}" 2>/dev/null && kill_tree "${CURRENT_CHILD}" KILL
  fi
  exit 143
}
trap 'on_signal SIGTERM' TERM
trap 'on_signal SIGINT'  INT
# SIGHUP is deliberately IGNORED, not trapped.  Closing the editor or dropping
# the ssh session hangs up the terminal, and the whole point of this script is
# to keep running when that happens.  Trapping it here would install a handler
# that *kills* the chain on exactly that event -- the opposite of what is
# wanted -- and would do so even when the caller forgot `nohup`.
trap '' HUP

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

note() {  # GUARD 6
  echo "[seq $(stamp)] $*"
  [[ "${DRY_RUN}" == "1" ]] || echo "$(stamp) $*" >> "${STATUS}"
}

START_EPOCH="$(date +%s)"
deadline_passed() {
  local now elapsed_h
  now="$(date +%s)"
  elapsed_h="$(awk -v a="${now}" -v b="${START_EPOCH}" -v m="${MAX_HOURS}" \
                 'BEGIN{print (((a-b)/3600.0) >= m) ? 1 : 0}')"
  [[ "${elapsed_h}" == "1" ]]
}

note "sequence start: ${#CELLS[@]} cell(s): ${CELLS[*]}"
note "campaign=${CAMPAIGN_DIR#"${GRTECLYN_ROOT}/"} runs_dir=${RUNS_DIR#"${GRTECLYN_ROOT}/"} dry_run=${DRY_RUN}"

# --- optional: chain behind a run already in flight ------------------------
if [[ -n "${WAIT_FOR_PID}" ]]; then
  if ! kill -0 "${WAIT_FOR_PID}" 2>/dev/null; then
    note "wait-for-pid ${WAIT_FOR_PID} is not running; starting immediately"
  else
    note "waiting for pid ${WAIT_FOR_PID} to exit (poll ${WAIT_POLL_SECONDS}s, deadline ${MAX_HOURS}h)"
    while kill -0 "${WAIT_FOR_PID}" 2>/dev/null; do
      if deadline_passed; then
        note "ABORT: ${MAX_HOURS}h deadline reached while waiting for pid ${WAIT_FOR_PID}"
        exit 4
      fi
      if [[ -e "${STOP_FILE}" ]]; then
        note "STOP_SEQUENCE seen while waiting -- exiting before any cell ran"
        rm -f "${STOP_FILE}"
        exit 0
      fi
      sleep "${WAIT_POLL_SECONDS}"
    done
    # Elapsed time is stamped, not assumed: a sleep that silently does not
    # sleep would otherwise look identical to a run that finished at once.
    note "pid ${WAIT_FOR_PID} exited after $(( $(date +%s) - START_EPOCH ))s of waiting"
  fi
fi

# --- the chain -------------------------------------------------------------
rc_overall=0
declare -a SUMMARY=()

for spec in "${CELLS[@]}"; do
  cell="${spec%%:*}"
  gpu="${spec#*:}"
  [[ "${gpu}" == "${spec}" ]] && gpu="0"

  if [[ -e "${STOP_FILE}" ]]; then          # GUARD 3
    note "STOP_SEQUENCE seen -- halting before ${cell}"
    rm -f "${STOP_FILE}"
    SUMMARY+=("${cell} skipped(stopped)")
    break
  fi
  if deadline_passed; then                   # GUARD 5
    note "ABORT: ${MAX_HOURS}h deadline reached -- not starting ${cell}"
    SUMMARY+=("${cell} skipped(deadline)")
    rc_overall=4
    break
  fi

  note "--> ${cell} starting on GPU ${gpu}"
  cell_start="$(date +%s)"
  rc=0
  # FOREGROUND=1 makes replay_eval.py a child of this shell, so the next cell
  # cannot start until this one has actually exited.
  #
  # Backgrounded + `wait` rather than run inline: bash only services traps
  # between commands, so an inline cell would swallow SIGTERM for however many
  # hours it runs.  `wait` is interruptible, which is what lets GUARD 7 stop
  # a cell mid-flight.
  FOREGROUND=1 GPU_ID="${gpu}" DRY_RUN="${DRY_RUN}" \
    bash "${RUN_SH}" "${cell}" &
  CURRENT_CHILD=$!
  wait "${CURRENT_CHILD}" || rc=$?
  CURRENT_CHILD=""
  cell_elapsed=$(( $(date +%s) - cell_start ))

  if ((rc == 0)); then
    note "<-- ${cell} finished ok in ${cell_elapsed}s"
    SUMMARY+=("${cell} ok ${cell_elapsed}s")
  else
    note "<-- ${cell} FAILED rc=${rc} after ${cell_elapsed}s"
    SUMMARY+=("${cell} FAILED(rc=${rc}) ${cell_elapsed}s")
    rc_overall="${rc}"
    if ((KEEP_GOING == 0)); then             # GUARD 4
      note "halting chain (pass --keep-going to continue past failures)"
      break
    fi
  fi
done

note "sequence end after $(( $(date +%s) - START_EPOCH ))s: ${SUMMARY[*]}"
exit "${rc_overall}"
