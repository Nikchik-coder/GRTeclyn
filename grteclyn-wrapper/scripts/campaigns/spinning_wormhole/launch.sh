#!/usr/bin/env bash
# SpinningWormhole -- THE campaign launcher.  One script for every arm.
#
#   bash grteclyn-wrapper/scripts/campaigns/spinning_wormhole/launch.sh \
#        --template <params file> --name <run name> --gpu <id> --profile <name> [options]
#
# WHY THIS EXISTS.  Same shape as the merger campaign's launcher: nothing about
# a new arm is new code -- it is a template, a name, a card, and what the
# consumer should extract.  Those are arguments, the consumer flags are named
# profiles in lib/consumer_profiles.sh, and the launch policy (dry run, restart
# suffix, registry line, detach, where the log goes) lives here once.
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
#                     runs/spinning_wormhole/templates/, a path is used as given
#   --name NAME       run name.  With --restart, run_single.sh appends
#                     _r<step>, and this script accounts for that when it
#                     builds paths that must point INTO the run directory
#   --gpu ID          CUDA device.  Check who else is on the card first:
#                     other people's runs share these GPUs
#   --profile NAME    consumer profile (see lib/consumer_profiles.sh):
#                     hold | none
#                     Every profile renders the campaign's full frame set,
#                     frames_default.txt.  The preflight REFUSES a launch whose
#                     frames miss a field of that set unless
#                     SWH_FRAMES_SUBSET="<reason>" is in the environment (the
#                     reason goes into run_manifest.json), and renders every
#                     frame field from the t = 0 plotfile before anything starts
#   --frames-fields L the profile's frames, cut to the fields L ("chi", "chi K")
#                     or to none at all ("none": every --frames-* flag dropped).
#                     Needs SWH_FRAMES_SUBSET="<reason>" in the environment,
#                     which the preflight records; for a study that keeps no
#                     frames or reads one field only
#   --consume-args S  raw consumer flags, replacing the profile entirely.  The
#                     escape hatch for a one-off that no profile covers; if you
#                     reach for it twice, add a profile instead
#   --zoom N          frame window width in code units (default 32)
#   --coord N         slice coordinate along the slice normal (default 32,
#                     the box centre; the consumer's own default is 0, the
#                     DOMAIN BOUNDARY, which renders featureless frames
#                     without erroring)
#   --center X Y Z    centre of the frame window (and the spectral MOTS), all
#                     three coordinates.  The renderer defaults to the domain
#                     midpoint, which is right for every [0, L] box -- but on a
#                     box whose centre is not L/2, or whenever the window is
#                     off-axis, SAY IT.  Either way: eyeball frame 0
#   --keep-last N     plotfiles to keep on scratch (default 3)
#   --restart DIR     checkpoint directory to continue from
#   --binary PATH     evolution binary.  REQUIRED while the campaign has no
#                     pinned binary (DEFAULT_BINARY below is empty); with
#                     --restart, the parent run's own binary (its
#                     run_manifest.json), and a refusal if that cannot be found
#   --max-level N     override max_level (run_single.sh rewrites
#                     regrid_interval to match; AMReX aborts otherwise)
#   --what TEXT       the registry line.  Default: the template's first
#                     comment line, which is why every template starts with one
#   --label NAME      what the run calls itself in the machine's process table
#                     (default "test").  The cards are shared and `ps aux` is
#                     public, so every process of a run is started from the run
#                     directory with relative paths and this name: "test
#                     params.txt", "test_post post.py ...".  It hides the
#                     subject, not the usage.  run_single.sh, "Process table"
#   --preflight MODE  full (default; or $SWH_PREFLIGHT) | static | off.
#                     run_single.sh checks the final params against the binary
#                     before anything starts: contradictory settings, keys the
#                     binary does not read, the background table on disk, and
#                     whether a seed changes the t = 0 data.  static skips the
#                     two GPU start-ups; off skips every check of the binary
#                     (the frame list is still checked).  Either is recorded in
#                     run_manifest.json
#   --preflight-only  run the preflight attached, print the verdict, launch
#                     nothing (the run dir is removed again; its t = 0 frames
#                     are kept in runs/spinning_wormhole/logs/preflight_frames/)
#   --foreground      run attached (dies with the shell; for probes only)
#   --dry-run         resolve and print everything, touch nothing (includes the
#                     no-GPU half of the preflight, on the template)
#
# EXAMPLES
#   will this template run as written on this binary? (seconds, launches nothing):
#     ... launch.sh --template params_equilibrium_L128_t200.txt \
#         --name check_t200 --gpu 1 --profile none \
#         --binary runs/spinning_wormhole/bin/<build>.ex --preflight-only
#   a production hold run:
#     ... launch.sh --template params_equilibrium_L128_t200.txt \
#         --name swh_equilibrium_L128_t200 --gpu 0 --profile hold --zoom 32 \
#         --binary runs/spinning_wormhole/bin/<build>.ex
set -euo pipefail

# The campaign pin.  Arms are compared against each other, so they must run the
# SAME binary; the live build product changes under other work.  Frozen copies
# live in runs/spinning_wormhole/bin/.  The pin is the campaign's first build
# (2026-10-10, commit bfb65e8e, the smoke-test fixes; binaries.tsv row 2).
# Change it only when the whole campaign moves to a new build, and say so in
# the campaign STATUS.
DEFAULT_BINARY='runs/spinning_wormhole/bin/main3d_smoke_bfb65e8e_2026-10-10.ex'

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
CAMPAIGN="${REPO}/runs/spinning_wormhole"
TEMPLATES="${CAMPAIGN}/templates"

TEMPLATE="" NAME="" GPU="" PROFILE="" CONSUME_RAW="" ZOOM=32 COORD=32 CENTER="" KEEP_LAST=3
RESTART="" BINARY="" MAX_LEVEL="" WHAT="" FOREGROUND=0 DRYRUN=0 LABEL="test"
PREFLIGHT="${SWH_PREFLIGHT:-full}" PREFLIGHT_ONLY=0 FRAMES_FIELDS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template)   TEMPLATE="$2"; shift 2 ;;
    --name)       NAME="$2"; shift 2 ;;
    --gpu)        GPU="$2"; shift 2 ;;
    --profile)    PROFILE="$2"; shift 2 ;;
    --consume-args) CONSUME_RAW="$2"; shift 2 ;;
    --frames-fields) FRAMES_FIELDS="$2"; shift 2 ;;
    --zoom)       ZOOM="$2"; shift 2 ;;
    --coord)      COORD="$2"; shift 2 ;;
    --center)     CENTER="$2 $3 $4"; shift 4 ;;
    --keep-last)  KEEP_LAST="$2"; shift 2 ;;
    --restart)    RESTART="$2"; shift 2 ;;
    --binary)     BINARY="$2"; shift 2 ;;
    --max-level)  MAX_LEVEL="$2"; shift 2 ;;
    --what)       WHAT="$2"; shift 2 ;;
    --label)      LABEL="$2"; shift 2 ;;
    --preflight)  PREFLIGHT="$2"; shift 2 ;;
    --preflight-only) PREFLIGHT_ONLY=1; shift ;;
    --foreground) FOREGROUND=1; shift ;;
    --dry-run)    DRYRUN=1; shift ;;
    -h|--help)    sed -n '2,94p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)            echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
done
for req in TEMPLATE NAME GPU PROFILE; do
  [[ -n "${!req}" ]] || { echo "missing --${req,,} (try --help)" >&2; exit 2; }
done
case "${PREFLIGHT}" in
  full|static|off) ;;
  *) echo "--preflight must be full, static or off (got '${PREFLIGHT}')" >&2; exit 2 ;;
esac

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
# A restart continues a run, so by default it continues on that run's binary:
# a leg on another build would splice two codes into one record.  The parent is
# the checkpoint's scratch directory (/tmp/grteclyn_scratch/<run>/...Chk<step>);
# its run_manifest.json names the binary.  A kept copy (_keep_*/...) has no
# manifest: then say --binary.
if [[ -n "${BINARY}" ]]; then
  BINARY_FROM="--binary"
elif [[ -n "${RESTART}" ]]; then
  parent="$(basename "$(dirname "${RESTART%/}")")"
  manifest="$(find "${CAMPAIGN}" -maxdepth 4 -path "*/${parent}/run_manifest.json" -print -quit 2>/dev/null || true)"
  if [[ -n "${manifest}" ]]; then
    BINARY="$(python3 -c 'import json, sys; print((json.load(open(sys.argv[1])).get("binary") or {}).get("path") or "")' "${manifest}" 2>/dev/null || true)"
  fi
  if [[ -z "${BINARY}" ]]; then
    echo "--restart without --binary: no run_manifest.json names the binary ${parent} ran on." >&2
    echo "  Pass --binary explicitly (results/spinningwormhole/binaries.tsv lists the frozen builds)." >&2
    exit 2
  fi
  BINARY_FROM="the parent run's binary (${manifest#"${REPO}"/})"
elif [[ -z "${DEFAULT_BINARY}" ]]; then
  echo "this campaign has no pinned binary yet (DEFAULT_BINARY is empty): --binary is required." >&2
  echo "  Build one with build_binary.sh (it lands in runs/spinning_wormhole/bin/ and gets a row" >&2
  echo "  in results/spinningwormhole/binaries.tsv), then launch with --binary <that path>." >&2
  exit 2
else
  BINARY="${DEFAULT_BINARY}"
  BINARY_FROM="campaign pin"
fi
[[ "${BINARY}" == /* ]] || BINARY="${REPO}/${BINARY}"
[[ -x "${BINARY}" ]] || { echo "binary missing or not executable: ${BINARY}" >&2; exit 1; }

# --- the run directory, INCLUDING the restart suffix ----------------------
# run_single.sh appends _r<step> when restarting.  Anything that must point
# into the run directory has to know the final name, so compute it here rather
# than let a profile guess.
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
  consumer_profile "${PROFILE}" "${ZOOM}" "${COORD}" "${CENTER}" >/dev/null   # still validate the name
  FRAMES_SUBSET=""
else
  CONSUME="$(consumer_profile "${PROFILE}" "${ZOOM}" "${COORD}" "${CENTER}")"
  # A profile that exists to be a frame subset says why; the caller's own
  # SWH_FRAMES_SUBSET wins.  (No profile of this campaign is one, yet.)
  FRAMES_SUBSET="$(consumer_profile_frames_subset "${PROFILE}")"
fi

# --frames-fields: cut the profile's frames to a subset, or to none.  The reason
# must come with it (SWH_FRAMES_SUBSET), so the preflight and the manifest say
# why this run has no movie of the fields it dropped.
if [[ -n "${FRAMES_FIELDS}" ]]; then
  [[ -n "${CONSUME_RAW}" ]] && { echo "--frames-fields cuts a profile's frames; with --consume-args write the frame flags yourself" >&2; exit 2; }
  [[ -n "${SWH_FRAMES_SUBSET:-}" ]] || { echo "--frames-fields needs SWH_FRAMES_SUBSET=\"<reason>\" in the environment" >&2; exit 2; }
  read -r -a _toks <<< "${CONSUME}"
  _out=() _i=0
  while (( _i < ${#_toks[@]} )); do
    _t="${_toks[_i]}"
    if [[ "${_t}" == --frames-* ]]; then
      _vals=(); _i=$((_i + 1))
      while (( _i < ${#_toks[@]} )) && [[ "${_toks[_i]}" != --* ]]; do _vals+=("${_toks[_i]}"); _i=$((_i + 1)); done
      [[ "${FRAMES_FIELDS}" == "none" ]] && continue
      if [[ "${_t}" == "--frames-fields" ]]; then _out+=("--frames-fields" ${FRAMES_FIELDS}); else _out+=("${_t}" "${_vals[@]}"); fi
      continue
    fi
    _out+=("${_t}"); _i=$((_i + 1))
  done
  CONSUME="${_out[*]}"
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
  "SWH_PARAMS=${TEMPLATE_PATH}"
  "SWH_NAME=${NAME}"
  "SWH_GPU=${GPU}"
  "SWH_KEEP_LAST=${KEEP_LAST}"
  "SWH_RUNS_DIR=${CAMPAIGN}"
  "SWH_EXE=${BINARY}"
  "SWH_WHAT=${WHAT}"
  "SWH_PROC_LABEL=${LABEL}"
  "SWH_PREFLIGHT=${PREFLIGHT}"
)
(( PREFLIGHT_ONLY )) && env_args+=("SWH_PREFLIGHT_ONLY=1")
[[ -n "${RESTART}" ]]   && env_args+=("SWH_RESTART=${RESTART}")
[[ -n "${FRAMES_SUBSET}" && -z "${SWH_FRAMES_SUBSET:-}" ]] && env_args+=("SWH_FRAMES_SUBSET=${FRAMES_SUBSET}")
[[ -n "${MAX_LEVEL}" ]] && env_args+=("SWH_MAX_LEVEL=${MAX_LEVEL}")
[[ "${FRAMES_FIELDS}" == "none" ]] && env_args+=("SWH_FRAMES_FIELDS=none")
if [[ "${PROFILE}" == "none" ]]; then
  env_args+=("SWH_CONSUME=0")
else
  env_args+=("SWH_CONSUME_ARGS=${CONSUME}")
fi

echo "[launch] run      : ${FULL_NAME}"
echo "[launch] template : ${TEMPLATE_PATH#"${REPO}"/}"
echo "[launch] binary   : ${BINARY#"${REPO}"/}   (${BINARY_FROM})"
echo "[launch] gpu      : ${GPU}   profile: ${PROFILE}$( [[ -n "${CONSUME_RAW}" ]] && echo " (OVERRIDDEN by --consume-args)") (zoom ${ZOOM}, coord ${COORD}, centre ${CENTER:-domain midpoint})   keep-last: ${KEEP_LAST}"
[[ -n "${RESTART}" ]] && echo "[launch] restart  : ${RESTART}"
echo "[launch] what     : ${WHAT}"
echo "[launch] label    : ${LABEL}   (process table: '${LABEL} params.txt', '${LABEL}_post post.py ...')"
echo "[launch] preflight: ${PREFLIGHT}$( (( PREFLIGHT_ONLY )) && echo " -- ONLY: nothing will be launched")"
if [[ -n "${SWH_FRAMES_SUBSET:-}" || -n "${FRAMES_SUBSET}" ]]; then
  echo "[launch] frames   : SUBSET allowed -- ${SWH_FRAMES_SUBSET:-${FRAMES_SUBSET}}"
fi
[[ -n "${FRAMES_FIELDS}" ]] && echo "[launch] frames   : cut to ${FRAMES_FIELDS} (--frames-fields)"

if (( DRYRUN )); then
  /usr/bin/env "${env_args[@]}" SWH_DRYRUN=1 bash "${HERE}/run_single.sh"
  exit 0
fi

# /usr/bin/env BY PATH, never bare `env`: on 2026-09-10 a shell whose PATH put uv's
# installer directory first resolved `env` to uv's `env` *script* (meant to be
# sourced, not run), which exports PATH and exits 0 without running anything --
# four launches and their dry runs reported success and started nothing.
#
# Started from the script's own directory and with a neutral argv[0], so the
# supervisor shows as "<label>_job run_single.sh" rather than a campaign path
# (run_single.sh, "Process table"); the same reason the log is opened by
# redirection or written by a tee standing in the log directory.
mkdir -p "${LOG_DIR}"
# A preflight-only call is a question with an answer in seconds: run attached,
# under its own log name so it never overwrites a real run's log.
if (( PREFLIGHT_ONLY )); then
  FOREGROUND=1
  LOG="${LOG_DIR}/${FULL_NAME}.preflight.log"
fi
if (( FOREGROUND )); then
  echo "[launch] attached -- dies with this shell; log also at ${LOG#"${REPO}"/}"
  ( cd "${LOG_DIR}" \
    && /usr/bin/env "${env_args[@]}" bash -c 'cd "$3" && exec -a "$1" bash "$2"' \
         _ "${LABEL}_job" run_single.sh "${HERE}" 2>&1 | tee "$(basename "${LOG}")" )
else
  ( cd "${HERE}" \
    && /usr/bin/env "${env_args[@]}" setsid nohup \
         bash -c 'exec -a "$1" bash "$2"' _ "${LABEL}_job" run_single.sh \
         > "${LOG}" 2>&1 < /dev/null & )
  echo "[launch] detached on gpu ${GPU}; log: ${LOG#"${REPO}"/}"
  echo "[launch] stop it with the run's launcher.pid, never a pkill pattern."
fi
