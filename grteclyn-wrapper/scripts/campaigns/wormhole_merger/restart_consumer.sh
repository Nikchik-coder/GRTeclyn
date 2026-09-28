#!/usr/bin/env bash
# Restart a LIVE run's plotfile consumer with extra flags; the evolution is not touched.
#
# Usage, on the node that runs the evolution:
#   restart_consumer.sh [--dry-run] <run dir> <flag> ...   restart with <flag> ... appended
#   restart_consumer.sh --check <run dir>                   validate a restart (read-only)
#   e.g. restart_consumer.sh runs/wormhole_merger/<run> --horizon-half 3.0 --horizon-common-level 3
#
# The new watcher gets the old watcher's exact command line and environment, with
# <flag> ... appended (argparse keeps the last value of a repeated option) and
# --keep-existing-frames.
#
# Why this exists (2026-09-28): the level-5 fly-by rerun went up with the default
# horizon window (half 2.5, common level 1) where its old run had 3.0 / level 3, and
# the head-on's common scan loses the remnant MOTS past its edge.  Both are consumer
# flags, so the fix must not cost the evolution anything.  What a safe restart needs:
#   1. --keep-existing-frames: a consumer clears every requested field's frames at
#      startup, so a plain restart deletes the run's PNGs (see run_single.sh's drain).
#   2. No index-0 plotfile on scratch: the consumer then takes the run for restarted
#      and truncates every small_data stream (plotfiles._should_auto_reset).  Refused.
#   3. Kill only while idle: every plotfile on scratch is in consume_state.json and the
#      watcher sits in its poll sleep.  consumer.log cannot tell: "Processed N
#      plotfile(s)." is not flushed until the next batch starts, so the log looks busy
#      while the consumer idles (measured: ~1.5 min of work per plotfile).
#   4. Kill the pid, never the group: the consumer shares its process group with the
#      evolution and run_single.sh.
#   5. The new watcher stopped when the evolution exits.  run_single.sh kills only the
#      consumer it started and then drains the last plotfiles with the launch flags;
#      a hand-started watcher left running would race that drain and never exit.
# Processes are found by /proc/<pid>/cwd, as in stop_campaign.sh: the run dir is in
# no argv.
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
VENV_BIN="${WRAPPER_DIR}/.venv/bin"
PY="${VENV_BIN}/python"

MODE=restart
case "${1:-}" in
  --dry-run) MODE=dry; shift ;;
  --check) MODE=check; shift ;;
esac
if [[ $# -lt 1 || ( "${MODE}" != check && $# -lt 2 ) ]]; then
  echo "usage: restart_consumer.sh [--dry-run] <run dir> <consumer flag> ..." >&2
  echo "       restart_consumer.sh --check <run dir>" >&2
  exit 2
fi
RUN="$(cd -- "$1" 2>/dev/null && pwd -P)" || { echo "no such run dir: $1" >&2; exit 2; }
shift
EXTRA=("$@")
LOG="${RUN}/consumer.log"

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
evolutions() { pids_in_run '^[^ ]+ params\.txt'; }
watchers() { pids_in_run '^[^ ]+_post post\.py .*--watch'; }
supervisors() { pids_in_run '^bash -c .* restart_consumer '; }
cmdline() { tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null; }
frame_count() { find "${RUN}/frames" -type f 2>/dev/null | wc -l; }

# Streams, scratch and state, read-only.  Exit 1 on a duplicated or backwards row.
streams_report() {
  "${PY}" - "${RUN}" <<'PY'
import json, os, re, sys
run = sys.argv[1]
sd = os.path.join(run, "small_data")
bad = False
num = re.compile(r"[-+]?[\d.]+([eE][-+]?\d+)?$")
for fn in sorted(os.listdir(sd)):
    if not fn.endswith(".dat"):
        continue
    # boundary_flux.dat's header has no '#': keep only rows that start with a number
    rows = [l.split() for l in open(os.path.join(sd, fn)) if l.split() and num.match(l.split()[0])]
    if not rows:
        print(f"  {fn}: empty")
        continue
    keys = [tuple(r[:2]) if fn == "horizon_scan.dat" else (r[0],) for r in rows]
    t = [float(r[0]) for r in rows]
    dup = len(keys) - len(set(keys))
    back = sum(b < a - 1e-9 for a, b in zip(t, t[1:]))
    bad |= bool(dup or back)
    note = (f", {dup} DUPLICATED" if dup else "") + (f", {back} BACKWARDS" if back else "")
    print(f"  {fn}: {len(rows)} rows, t {t[0]:g} .. {t[-1]:g}{note}")
state = json.load(open(os.path.join(sd, "consume_state.json")))
scratch = os.path.join(run, "scratch")
if os.path.isdir(scratch):
    plts = sorted(n for n in os.listdir(scratch) if re.search(r"Plt\d+$", n))
    pend = [n for n in plts if not state.get(n)]
    print(f"  scratch: {' '.join(plts) or 'no plotfiles'}; unprocessed: {' '.join(pend) or 'none'}")
else:
    print("  scratch: not visible from this node")
sys.exit(1 if bad else 0)
PY
}

# Idle: nothing on scratch waits for extraction, and the watcher sleeps in its poll loop.
idle() {
  "${PY}" - "${RUN}" <<'PY' || return 1
import json, os, re, sys
run = sys.argv[1]
state = json.load(open(os.path.join(run, "small_data", "consume_state.json")))
plts = [n for n in os.listdir(os.path.join(run, "scratch")) if re.search(r"Plt\d+$", n)]
sys.exit(1 if any(not state.get(n) for n in plts) else 0)
PY
  [[ "$(cat "/proc/$1/wchan" 2>/dev/null)" == *sleep* ]]
}

if [[ "${MODE}" == check ]]; then
  bad=0
  mapfile -t EVO < <(evolutions)
  mapfile -t W < <(watchers)
  mapfile -t S < <(supervisors)
  echo "run        : ${RUN}"
  echo "evolution  : ${EVO[*]:-none running}   $(grep -a '^\[Level 0 step' "${RUN}/run.log" 2>/dev/null | tail -n 1)"
  echo "watchers   : ${W[*]:-NONE}"
  [[ ${#W[@]} -eq 1 ]] || { echo "!! expected exactly one watcher"; bad=1; }
  echo "supervisor : ${S[*]:-none}"
  marker="$(grep -a '^\[restart_consumer\].*appended:' "${LOG}" | tail -n 1)"
  echo "restart    : ${marker:-never restarted}"
  if [[ -n "${marker}" ]]; then
    flags="${marker#*appended: }"
    if [[ ${#W[@]} -eq 1 && " $(cmdline "${W[0]}")" != *" ${flags} "* ]]; then
      echo "!! the watcher's command line lacks: ${flags}"; bad=1
    fi
    before="$(sed -E 's/.*\(frames ([0-9]+)\).*/\1/' <<< "${marker}")"
    now="$(frame_count)"
    echo "frames     : ${now} (at the restart ${before})"
    [[ "${now}" -ge "${before}" ]] || { echo "!! frames were deleted"; bad=1; }
    errs="$(awk -v m="${marker}" 'f; $0 == m {f = 1}' "${LOG}" | grep -ciE 'traceback|error|warning|resetting')"
    echo "log since  : ${errs} error/warning/reset lines; $(awk -v m="${marker}" 'f; $0 == m {f = 1}' "${LOG}" | grep -c '^\[1/') plotfiles loaded"
    [[ "${errs}" -eq 0 ]] || { awk -v m="${marker}" 'f; $0 == m {f = 1}' "${LOG}" | grep -iE 'traceback|error|warning|resetting' | tail -n 5; bad=1; }
  fi
  echo "streams    :"
  streams_report || bad=1
  [[ "${bad}" -eq 0 ]] && echo "CHECK OK" || echo "CHECK FAILED"
  exit "${bad}"
fi

mapfile -t EVO < <(evolutions)
mapfile -t WATCH < <(watchers)
if [[ ${#EVO[@]} -eq 0 ]]; then
  echo "no live evolution in ${RUN} on this node" >&2
  exit 1
fi
if [[ ${#WATCH[@]} -ne 1 ]]; then
  echo "expected one consumer watcher in ${RUN}, found ${#WATCH[@]}: ${WATCH[*]:-none}" >&2
  exit 1
fi
if compgen -G "${RUN}/scratch/*Plt00000" > /dev/null; then
  echo "an index-0 plotfile is on scratch: a restarted consumer would truncate every stream" >&2
  exit 1
fi
OLD="${WATCH[0]}"
mapfile -d '' -t ARGV < "/proc/${OLD}/cmdline"
mapfile -d '' -t ENVV < "/proc/${OLD}/environ"
LABEL="${ARGV[0]}"
NEW=("${ARGV[@]:1}" "${EXTRA[@]}" --keep-existing-frames)
APPENDED="${EXTRA[*]} --keep-existing-frames"
OLD_PATH=""
for e in "${ENVV[@]}"; do
  [[ "${e}" == PATH=* ]] && OLD_PATH="${e#PATH=}"
done
if [[ ! -x "${VENV_BIN}/${LABEL}" ]]; then
  echo "consumer alias ${VENV_BIN}/${LABEL} missing" >&2
  exit 1
fi

echo "run       : ${RUN}"
echo "evolution : ${EVO[*]}"
echo "watcher   : ${OLD}"
echo "new       : ${LABEL} ${NEW[*]}"
if [[ "${MODE}" == dry ]]; then
  echo "idle now  : $(idle "${OLD}" && echo yes || echo no)"
  echo "(dry run: nothing killed or started)"
  exit 0
fi

echo "waiting for the watcher to be idle (up to 60 min) ..."
ok=0
for _ in $(seq 1 12000); do
  if idle "${OLD}"; then
    sleep 0.3
    if idle "${OLD}"; then ok=1; break; fi
  fi
  sleep 0.3
done
if [[ "${ok}" != 1 ]]; then
  echo "watcher ${OLD} never idle for an hour; nothing changed" >&2
  exit 1
fi

FRAMES_BEFORE="$(frame_count)"
kill "${OLD}" 2>/dev/null
for _ in $(seq 1 30); do
  kill -0 "${OLD}" 2>/dev/null || break
  sleep 1
done
if kill -0 "${OLD}" 2>/dev/null; then
  echo "watcher ${OLD} ignored SIGTERM; nothing started" >&2
  exit 1
fi
echo "[restart_consumer] $(date -u +%FT%TZ) watcher ${OLD} stopped idle (frames ${FRAMES_BEFORE}); appended: ${APPENDED}" \
  >> "${LOG}"

# The old watcher's environment (PYTHONPATH to the wrapper source, PATH with the venv
# first): python finds its venv through the alias looked up on PATH, as in run_single.sh.
cd "${RUN}" || exit 1
env -i "${ENVV[@]}" PATH="${VENV_BIN}:${OLD_PATH}" setsid nohup bash -c '
  label="$1"; evo="$2"; shift 2
  "${label}" "$@" >> consumer.log 2>&1 &
  w=$!
  while kill -0 "${w}" 2>/dev/null; do
    alive=0
    for p in ${evo}; do kill -0 "${p}" 2>/dev/null && alive=1; done
    if [[ "${alive}" == 0 ]]; then
      kill "${w}" 2>/dev/null; wait "${w}" 2>/dev/null
      echo "[restart_consumer] $(date -u +%FT%TZ) evolution exited; watcher ${w} stopped for the launch drain" >> consumer.log
      exit 0
    fi
    sleep 5
  done
  echo "[restart_consumer] $(date -u +%FT%TZ) watcher ${w} exited on its own" >> consumer.log
' restart_consumer "${LABEL}" "${EVO[*]}" "${NEW[@]}" < /dev/null > /dev/null 2>&1 &

sleep 20
mapfile -t WATCH < <(watchers)
if [[ ${#WATCH[@]} -ne 1 || "${WATCH[0]}" == "${OLD}" ]]; then
  echo "!! new watcher not up (found: ${WATCH[*]:-none}); last lines of consumer.log:" >&2
  tail -n 12 "${LOG}" >&2
  exit 1
fi
echo "watcher   : ${WATCH[0]} up (old ${OLD} gone)"
exec bash "${SCRIPT_DIR}/$(basename -- "${BASH_SOURCE[0]}")" --check "${RUN}"
