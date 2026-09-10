#!/usr/bin/env bash
# BinaryWormholeMerger -- THE campaign launcher.  One script for every arm.
#
#   bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh \
#        --template <params file> --name <run name> --gpu <id> --profile <name> [options]
#
# WHY THIS EXISTS.  Until 2026-09-10 each arm got its own launch_*.sh under
# runs/wormhole_merger/ -- thirty of them, 18 to 58 lines each, all the same
# eight steps with four values changed.  Nothing about a new arm is new code:
# it is a template, a name, a card, and what the consumer should extract.  So
# those are arguments, the consumer flags are named profiles in
# lib/consumer_profiles.sh, and the launch policy (dry run, restart suffix,
# registry line, detach, where the log goes) lives here once.  The old scripts
# are archived in runs/wormhole_merger/00_archive/ with a table in README.md
# mapping each to its command line here.
#
# WHAT IT DOES NOT DO.  It does not run the binary.  run_single.sh does, and
# that separation is load-bearing: AMReX writes parameters_and_version.txt
# into the CURRENT WORKING DIRECTORY with the absolute paths it was handed, so
# the binary is only ever started from inside a run directory under runs/,
# which is gitignored.  This script resolves and delegates; run_single.sh
# clones the params, rewrites the output paths onto node-local scratch,
# registers launcher.pid and starts the consumer sidecar.
#
# OPTIONS
#   --template FILE   params template; a bare name resolves against
#                     runs/wormhole_merger/templates_scan/, a path is used as
#                     given (the BBH control lives in Examples/BinaryBH/)
#   --name NAME       run name.  With --restart, run_single.sh appends
#                     _r<step>, and this script accounts for that when it
#                     builds paths that must point INTO the run directory
#   --gpu ID          CUDA device.  Check who else is on the card first:
#                     other people's runs share these GPUs
#   --profile NAME    consumer profile (see lib/consumer_profiles.sh):
#                     headon | headon-scout | orbit | orbit-modes | bbh | chi | none
#   --consume-args S  raw consumer flags, replacing the profile entirely.  The
#                     escape hatch for a one-off that no profile covers; if you
#                     reach for it twice, add a profile instead
#   --zoom N          frame window width in code units (default 32)
#   --coord N         slice coordinate along the slice normal (default 32,
#                     the box centre; the consumer's own default is 0, the
#                     DOMAIN BOUNDARY, which renders featureless frames
#                     without erroring)
#   --keep-last N     plotfiles to keep on scratch (default 3)
#   --restart DIR     checkpoint directory to continue from
#   --binary PATH     evolution binary; default is the campaign pin below
#   --max-level N     override max_level (run_single.sh rewrites
#                     regrid_interval to match; AMReX aborts otherwise)
#   --what TEXT       the registry line.  Default: the template's first
#                     comment line, which is why every template starts with one
#   --foreground      run attached (dies with the shell; for probes only)
#   --dry-run         resolve and print everything, touch nothing
#
# EXAMPLES
#   the level-3 down-step from a kept level-5 checkpoint (queue 1i, 2026-09-09):
#     ... launch.sh --template params_v1_lvl3down_d8_t100.txt \
#         --name merge_headon_flip_d8_v1_lvl3down_t100 --gpu 0 --profile headon \
#         --zoom 40 --keep-last 3 \
#         --restart /tmp/grteclyn_scratch/_keep_lvl5/BinaryWormholeChk03500
#   a one-step placement probe, attached, no consumer:
#     ... launch.sh --template params_place_d8_step1.txt --name place_d8_step1 \
#         --gpu 1 --profile none --keep-last 1 --foreground
set -euo pipefail

# The campaign pin.  Arms are compared against each other, so they must run the
# SAME binary; the live build product changes under other work.  Frozen copies
# live in runs/wormhole_merger/bin/.  Change this only when the whole campaign
# moves to a new build, and say so in research/merger/GPU_PLAN.md.
DEFAULT_BINARY='runs/wormhole_merger/bin/main3d_boost_2026-09-08.ex'

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
CAMPAIGN="${REPO}/runs/wormhole_merger"
TEMPLATES="${CAMPAIGN}/templates_scan"

TEMPLATE="" NAME="" GPU="" PROFILE="" CONSUME_RAW="" ZOOM=32 COORD=32 KEEP_LAST=3
RESTART="" BINARY="" MAX_LEVEL="" WHAT="" FOREGROUND=0 DRYRUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template)   TEMPLATE="$2"; shift 2 ;;
    --name)       NAME="$2"; shift 2 ;;
    --gpu)        GPU="$2"; shift 2 ;;
    --profile)    PROFILE="$2"; shift 2 ;;
    --consume-args) CONSUME_RAW="$2"; shift 2 ;;
    --zoom)       ZOOM="$2"; shift 2 ;;
    --coord)      COORD="$2"; shift 2 ;;
    --keep-last)  KEEP_LAST="$2"; shift 2 ;;
    --restart)    RESTART="$2"; shift 2 ;;
    --binary)     BINARY="$2"; shift 2 ;;
    --max-level)  MAX_LEVEL="$2"; shift 2 ;;
    --what)       WHAT="$2"; shift 2 ;;
    --foreground) FOREGROUND=1; shift ;;
    --dry-run)    DRYRUN=1; shift ;;
    -h|--help)    sed -n '2,60p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)            echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
done
for req in TEMPLATE NAME GPU PROFILE; do
  [[ -n "${!req}" ]] || { echo "missing --${req,,} (try --help)" >&2; exit 2; }
done

# --- resolve the template -------------------------------------------------
if [[ -f "${TEMPLATE}" ]]; then
  TEMPLATE_PATH="$(cd -- "$(dirname -- "${TEMPLATE}")" && pwd)/$(basename -- "${TEMPLATE}")"
elif [[ -f "${TEMPLATES}/${TEMPLATE}" ]]; then
  TEMPLATE_PATH="${TEMPLATES}/${TEMPLATE}"
elif [[ -f "${REPO}/${TEMPLATE}" ]]; then
  TEMPLATE_PATH="${REPO}/${TEMPLATE}"
else
  echo "template not found: ${TEMPLATE} (looked in ${TEMPLATES#"${REPO}"/} and as a path)" >&2
  exit 1
fi

# --- resolve the binary ---------------------------------------------------
BINARY="${BINARY:-${DEFAULT_BINARY}}"
[[ "${BINARY}" == /* ]] || BINARY="${REPO}/${BINARY}"
[[ -x "${BINARY}" ]] || { echo "binary missing or not executable: ${BINARY}" >&2; exit 1; }

# --- the run directory, INCLUDING the restart suffix ----------------------
# run_single.sh appends _r<step> when restarting.  Anything that must point
# into the run directory (the horizon track the consumer appends to) has to
# know the final name, so compute it here rather than let a profile guess.
FULL_NAME="${NAME}"
if [[ -n "${RESTART}" ]]; then
  [[ -f "${RESTART}/Header" ]] || { echo "not a checkpoint directory: ${RESTART}" >&2; exit 1; }
  FULL_NAME="${NAME}_r${RESTART##*Chk}"
fi
RUN_DIR="${CAMPAIGN}/${FULL_NAME}"

# --- the consumer flags ---------------------------------------------------
# shellcheck source=lib/consumer_profiles.sh
source "${HERE}/lib/consumer_profiles.sh"
if [[ -n "${CONSUME_RAW}" ]]; then
  CONSUME="${CONSUME_RAW}"
  consumer_profile "${PROFILE}" "${ZOOM}" "${COORD}" >/dev/null   # still validate the name
else
  CONSUME="$(consumer_profile "${PROFILE}" "${ZOOM}" "${COORD}")"
fi

# --- the registry line ----------------------------------------------------
# Every template's first line is a comment saying what the run is for; that is
# the sentence the pack's summary table shows, so it is read, not retyped.
if [[ -z "${WHAT}" ]]; then
  WHAT="$(head -1 "${TEMPLATE_PATH}" | sed 's/^# *//')"
  [[ -n "${RESTART}" ]] && WHAT="${WHAT} -- restarted from ${RESTART##*/} (kept in $(basename "$(dirname "${RESTART}")"))"
fi

# --- hand off -------------------------------------------------------------
LOG_DIR="${CAMPAIGN}/logs"
LOG="${LOG_DIR}/${FULL_NAME}.log"
env_args=(
  "WHM_PARAMS=${TEMPLATE_PATH}"
  "WHM_NAME=${NAME}"
  "WHM_GPU=${GPU}"
  "WHM_KEEP_LAST=${KEEP_LAST}"
  "WHM_RUNS_DIR=${CAMPAIGN}"
  "WHM_EXE=${BINARY}"
  "WHM_WHAT=${WHAT}"
)
[[ -n "${RESTART}" ]]   && env_args+=("WHM_RESTART=${RESTART}")
[[ -n "${MAX_LEVEL}" ]] && env_args+=("WHM_MAX_LEVEL=${MAX_LEVEL}")
if [[ "${PROFILE}" == "none" ]]; then
  env_args+=("WHM_CONSUME=0")
else
  env_args+=("WHM_CONSUME_ARGS=${CONSUME}")
fi

echo "[launch] run      : ${FULL_NAME}"
echo "[launch] template : ${TEMPLATE_PATH#"${REPO}"/}"
echo "[launch] binary   : ${BINARY#"${REPO}"/}"
echo "[launch] gpu      : ${GPU}   profile: ${PROFILE}$( [[ -n "${CONSUME_RAW}" ]] && echo " (OVERRIDDEN by --consume-args)") (zoom ${ZOOM}, coord ${COORD})   keep-last: ${KEEP_LAST}"
[[ -n "${RESTART}" ]] && echo "[launch] restart  : ${RESTART}"
echo "[launch] what     : ${WHAT}"

if (( DRYRUN )); then
  /usr/bin/env "${env_args[@]}" WHM_DRYRUN=1 bash "${HERE}/run_single.sh"
  exit 0
fi

# /usr/bin/env BY PATH, never bare `env`: on 2026-09-10 a shell whose PATH put uv's
# installer directory first resolved `env` to uv's `env` *script* (meant to be
# sourced, not run), which exports PATH and exits 0 without running anything --
# four launches and their dry runs reported success and started nothing.
mkdir -p "${LOG_DIR}"
if (( FOREGROUND )); then
  echo "[launch] attached -- dies with this shell; log also at ${LOG#"${REPO}"/}"
  /usr/bin/env "${env_args[@]}" bash "${HERE}/run_single.sh" 2>&1 | tee "${LOG}"
else
  /usr/bin/env "${env_args[@]}" setsid nohup bash "${HERE}/run_single.sh" > "${LOG}" 2>&1 < /dev/null &
  echo "[launch] detached on gpu ${GPU}; log: ${LOG#"${REPO}"/}"
  echo "[launch] stop it with the run's launcher.pid, never a pkill pattern."
fi
