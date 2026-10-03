#!/usr/bin/env bash
# restart_consumer.sh <run_dir> [--keep-last N] [--dry-run]
#
# The ONE way to hand-(re)start a run's plotfile-consumer sidecar.  Exists
# because every ad-hoc restart has lost part of the real invocation:
#   2026-10-02  SEED-csm ran 1.5 h with no consumer at all (--profile none
#               silently dropped --consume-args);
#   2026-10-03  the p06 extension's hand-started consumer was given only
#               WHM_CONSUME_ARGS and sat idle: the launcher's LEADING args
#               (--data/--out/--frames-out/--delete/--keep-last) are what
#               point it at the plotfiles, and the --horizon-track path it
#               inherited named the wrong (un-suffixed) run dir.
#
# This script rebuilds the sidecar exactly as run_single.sh does:
#   --data scratch --out small_data --frames-out frames
#   --delete --keep-last N
#   <WHM_CONSUME_ARGS from the run's own run_manifest.json>
#   --watch
# and rewrites the --horizon-track value to THIS run dir's
# data/binary_throat_diagnostics.dat, which is always the right stream.
# It kills the run's existing consumer (matched by cwd) first, appends to
# consumer.log, and verifies the new process survives startup.
set -euo pipefail

RUN_DIR="" KEEP_LAST=3 DRY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep-last) KEEP_LAST="$2"; shift 2 ;;
    --dry-run)   DRY=1; shift ;;
    *)           RUN_DIR="$1"; shift ;;
  esac
done
[[ -n "${RUN_DIR}" && -d "${RUN_DIR}" ]] || { echo "usage: restart_consumer.sh <run_dir> [--keep-last N] [--dry-run]" >&2; exit 2; }
RUN_DIR="$(cd "${RUN_DIR}" && pwd)"
[[ -f "${RUN_DIR}/post.py" ]] || { echo "[consumer] no post.py in ${RUN_DIR} -- not a launched run dir" >&2; exit 2; }
[[ -f "${RUN_DIR}/run_manifest.json" ]] || { echo "[consumer] no run_manifest.json in ${RUN_DIR}" >&2; exit 2; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/../../../.." && pwd)"
CONSUMER_BIN="${REPO_ROOT}/grteclyn-wrapper/.venv/bin/test_post"
[[ -x "${CONSUMER_BIN}" ]] || { echo "[consumer] venv test_post symlink missing: ${CONSUMER_BIN}" >&2; exit 2; }

# WHM_CONSUME_ARGS exactly as the launch recorded them, horizon-track repointed.
mapfile -t EXTRA < <(python3 - "${RUN_DIR}" <<'PY'
import json, shlex, sys
run = sys.argv[1]
m = json.load(open(f"{run}/run_manifest.json"))
def find(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "WHM_CONSUME_ARGS" and isinstance(v, str):
                return v
            r = find(v)
            if r is not None:
                return r
    elif isinstance(d, list):
        for v in d:
            r = find(v)
            if r is not None:
                return r
    return None
args = shlex.split(find(m) or "")
for i, a in enumerate(args):
    if a == "--horizon-track" and i + 1 < len(args):
        args[i + 1] = f"{run}/data/binary_throat_diagnostics.dat"
print("\n".join(args))
PY
)

CMD=( "${CONSUMER_BIN}" post.py
      --data scratch --out small_data --frames-out frames
      --delete --keep-last "${KEEP_LAST}" )
CMD+=( "${EXTRA[@]}" --watch )

if [[ "${DRY}" == "1" ]]; then
  printf '[dry-run] cd %q &&' "${RUN_DIR}"
  printf ' %q' "${CMD[@]}"
  printf ' >> consumer.log 2>&1 &\n'
  exit 0
fi

# Kill the run's current consumer, if any: a test_post whose cwd is this run.
for pid in $(pgrep -f "test_post post.py" || true); do
  if [[ "$(readlink -f "/proc/${pid}/cwd" 2>/dev/null)" == "${RUN_DIR}" ]]; then
    echo "[consumer] stopping old consumer pid ${pid}"
    kill "${pid}" 2>/dev/null || true
  fi
done
sleep 2

cd "${RUN_DIR}"
"${CMD[@]}" >> consumer.log 2>&1 &
PID=$!
echo "[consumer] started pid ${PID} in ${RUN_DIR}"
sleep 8
if ! kill -0 "${PID}" 2>/dev/null; then
  echo "[consumer] !! DIED AT STARTUP -- last consumer.log lines:" >&2
  tail -n 12 consumer.log | sed 's/^/[consumer]    /' >&2
  exit 1
fi
echo "[consumer] alive after 8 s; tail of consumer.log:"
tail -n 3 consumer.log | sed 's/^/[consumer]    /'
