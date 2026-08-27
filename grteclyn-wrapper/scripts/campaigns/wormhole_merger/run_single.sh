#!/usr/bin/env bash
# BinaryWormholeMerger -- single-run launcher (research/merger/Plan.md).
#
# One run of Examples/BinaryWormholeMerger through the campaign contract
# (scripts/campaigns/README.md): launcher.pid registered for stop_campaign.sh,
# .dat streams on the runs dir (NFS), plotfiles/checkpoints on node-local /tmp
# scratch.  Never invoke the binary on a params file directly -- clone-and-
# rewrite here is what keeps plotfiles off NFS and the run stoppable.
#
# Usage (attached, foreground -- detach only with explicit permission):
#   bash scripts/campaigns/wormhole_merger/run_single.sh
# Overrides:
#   WHM_PARAMS    params template, resolved against Examples/BinaryWormholeMerger
#                 if not an existing path (default params_test.txt)
#   WHM_GPU       CUDA device (default 0)
#   WHM_RUNS_DIR  campaign root (default <repo>/runs/wormhole_merger)
#   WHM_NAME      run name (default: params basename without .txt)
#   WHM_EXE       evolution binary (default: newest main3d.*.ex in the example)
#   WHM_BARE_MASS override wormhole_bare_mass_A AND _B in the cloned params
#                 (equal-mass ladder knob, Plan.md Phase 3; appends _mXXX to
#                 the run name so ladder rungs never clobber each other)
#   WHM_DRYRUN=1  resolve and print everything, touch nothing, exit
#
# Stop:  bash scripts/campaigns/stop_campaign.sh [--dry-run] <runs_dir>
#
# NOTE there is no plotfile consumer for this example yet: plotfiles STAY on
# scratch.  Copy what the analysis needs off /tmp before any purge -- scratch
# does not survive a node swap.  Budget with `df -h /tmp` before long runs.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
REPO_ROOT="$(cd -- "${WRAPPER_DIR}/.." && pwd)"
EXAMPLE_DIR="${REPO_ROOT}/Examples/BinaryWormholeMerger"

PARAMS="${WHM_PARAMS:-params_test.txt}"
GPU="${WHM_GPU:-0}"
RUNS_DIR="${WHM_RUNS_DIR:-${REPO_ROOT}/runs/wormhole_merger}"
SCRATCH_ROOT="${GRTECLYN_SCRATCH:-/tmp/grteclyn_scratch}"

# Resolve the params template: an existing path wins, else the example dir.
if [[ -f "${PARAMS}" ]]; then
  TEMPLATE="$(cd -- "$(dirname -- "${PARAMS}")" && pwd)/$(basename -- "${PARAMS}")"
elif [[ -f "${EXAMPLE_DIR}/${PARAMS}" ]]; then
  TEMPLATE="${EXAMPLE_DIR}/${PARAMS}"
else
  echo "[whm] params template not found: ${PARAMS}" >&2
  exit 1
fi

NAME="${WHM_NAME:-$(basename "${TEMPLATE}" .txt)}"
if [[ -n "${WHM_BARE_MASS:-}" ]]; then
  NAME="${NAME}_m$(printf '%s' "${WHM_BARE_MASS}" | tr -d '.' )"
fi
RUN_DIR="${RUNS_DIR}/${NAME}"
SCRATCH_DIR="${SCRATCH_ROOT}/${NAME}"

# Evolution binary: explicit override, else the newest built .ex in the example.
if [[ -n "${WHM_EXE:-}" ]]; then
  EXE="${WHM_EXE}"
else
  EXE="$(ls -t "${EXAMPLE_DIR}"/main3d.*.ex 2>/dev/null | head -n 1 || true)"
fi
if [[ -z "${EXE}" || ! -x "${EXE}" ]]; then
  echo "[whm] no built binary in ${EXAMPLE_DIR} (main3d.*.ex) -- build first," >&2
  echo "[whm] or point WHM_EXE at one." >&2
  exit 1
fi

echo "[whm] name     : ${NAME}"
echo "[whm] template : ${TEMPLATE}"
echo "[whm] binary   : ${EXE}"
echo "[whm] gpu      : ${GPU}"
echo "[whm] run dir  : ${RUN_DIR}          (NFS: params, log, .dat streams)"
echo "[whm] scratch  : ${SCRATCH_DIR}      (node-local: plotfiles, checkpoints)"

if [[ "${WHM_DRYRUN:-0}" != "0" ]]; then
  echo "[whm] dry run -- nothing launched."
  exit 0
fi

if [[ -d "${RUN_DIR}" ]]; then
  echo "[whm] ${RUN_DIR} already exists -- delete it or set WHM_NAME/WHM_RUNS_DIR" >&2
  exit 1
fi

mkdir -p "${RUN_DIR}" "${SCRATCH_DIR}"

# Stop handle for scripts/campaigns/stop_campaign.sh.  Registered per RUN dir,
# not the campaign root: several singles run concurrently (one per GPU), and a
# shared pid file would be last-writer-wins.  `stop_campaign.sh <RUN_DIR>`
# targets one rung; sweeping the root still catches workers by path.
source "${SCRIPT_DIR}/../lib/launcher_common.sh"
campaign_register_launcher "${RUN_DIR}"

# Clone the template and re-emit the three path keys (README rule 1: a cloned
# params file must never keep the source run's absolute paths).  Each key must
# occur exactly once, before and after, or the rewrite silently misses.
RUN_PARAMS="${RUN_DIR}/params.txt"
cp "${TEMPLATE}" "${RUN_PARAMS}"
for key in output_path amr.plot_file amr.check_file; do
  n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
  if [[ "${n}" != "1" ]]; then
    echo "[whm] template must define '${key}' exactly once (found ${n})" >&2
    exit 1
  fi
done
sed -i \
  -e "s|^output_path[[:space:]]*=.*|output_path = \"${RUN_DIR}\"|" \
  -e "s|^amr.plot_file[[:space:]]*=.*|amr.plot_file = \"${SCRATCH_DIR}/BinaryWormholePlt\"|" \
  -e "s|^amr.check_file[[:space:]]*=.*|amr.check_file = \"${SCRATCH_DIR}/BinaryWormholeChk\"|" \
  "${RUN_PARAMS}"

# Equal-mass ladder override (both throats; B defaults to A only when unset,
# and the shipped templates set both explicitly, so rewrite both).
if [[ -n "${WHM_BARE_MASS:-}" ]]; then
  for key in wormhole_bare_mass_A wormhole_bare_mass_B; do
    n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
    if [[ "${n}" != "1" ]]; then
      echo "[whm] WHM_BARE_MASS needs '${key}' exactly once in the template (found ${n})" >&2
      exit 1
    fi
    sed -i "s|^${key}[[:space:]]*=.*|${key} = ${WHM_BARE_MASS}|" "${RUN_PARAMS}"
  done
  echo "[whm] bare-mass override: m_A = m_B = ${WHM_BARE_MASS}"
fi

echo "[whm] === launching ${NAME} (attached; Ctrl-C or stop_campaign.sh to stop) ==="
status=0
(
  cd "${RUN_DIR}"
  CUDA_VISIBLE_DEVICES="${GPU}" "${EXE}" "${RUN_PARAMS}"
) 2>&1 | tee "${RUN_DIR}/run.log" || status=$?

if [[ "${status}" -ne 0 ]]; then
  echo "[whm] run FAILED (exit ${status}) -- see ${RUN_DIR}/run.log" >&2
  exit "${status}"
fi

echo "[whm] run complete: ${RUN_DIR}"
echo "[whm] plotfiles are on node-local scratch: ${SCRATCH_DIR}"
echo "[whm] copy what the analysis needs off /tmp before purging."
