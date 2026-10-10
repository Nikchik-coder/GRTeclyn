#!/usr/bin/env bash
# SpinningWormhole -- single-run launcher.
#
# One run of Examples/SpinningWormhole through the campaign contract
# (scripts/campaigns/README.md): launcher.pid registered for stop_campaign.sh,
# .dat streams on the runs dir (NFS), plotfiles/checkpoints on node-local /tmp
# scratch.  Never invoke the binary on a params file directly -- clone-and-
# rewrite here is what keeps plotfiles off NFS and the run stoppable.
#
# "Never directly" also includes quick throwaway tests, and that is not a style
# preference.  AMReX writes `parameters_and_version.txt` into the binary's
# CURRENT WORKING DIRECTORY on every run, and that file records the absolute
# output_path / plot_file / check_file it was given.  Run the binary from the
# repo root or from the example directory and you have just written your home
# directory into a tracked location; it reached a commit that way on
# 2026-08-27.  This launcher cd's into the run directory under runs/, which is
# gitignored, so the artefact lands somewhere harmless.  Machine paths come
# from the .env overlay below, so nothing here has to know them.
#
# Usage (attached, foreground -- detach only with explicit permission):
#   bash scripts/campaigns/spinning_wormhole/run_single.sh
# Overrides:
#   SWH_PARAMS    params template, resolved against Examples/SpinningWormhole
#                 if not an existing path (default params_test.txt)
#   SWH_GPU       CUDA device (default 0).  With SWH_RANKS > 1 this is a
#                 COMMA-SEPARATED list of physical ids, one per rank, e.g. "0,1"
#   SWH_RANKS     MPI ranks for the evolution (default 1 = no mpirun).  Use it
#                 only to buy VRAM headroom for a grid that will not fit on one
#                 card: throughput is unchanged, memory genuinely splits.  Must
#                 equal the number of ids in SWH_GPU, and needs the MPI binary
#                 (main3d.*.MPI.*.ex)
#   SWH_RUNS_DIR  campaign root (default <repo>/runs/spinning_wormhole)
#   SWH_NAME      run name (default: params basename without .txt)
#   SWH_EXE       evolution binary (default: newest main3d.*.ex in the example)
#   SWH_MAX_LEVEL override max_level in the cloned params, rewriting
#                 regrid_interval to match (AMReX aborts if it does not carry
#                 exactly max_level values)
#   SWH_RESTART   absolute path to an AMReX checkpoint directory
#                 (.../SpinningWormholeChkNNNNN).  Injects `amr.restart` into
#                 the cloned params -- the ONLY key AMReX actually reads for
#                 this; the root-level `restart_file` key is a trap (never
#                 loaded, so its existence check runs on an empty path and
#                 aborts).  Appends _rNNNNN to the run name, so the
#                 continuation gets its own run dir and scratch and never
#                 clobbers the parent run's streams.
#   SWH_DRYRUN=1  resolve and print everything, touch nothing, exit
#   SWH_CONSUME   run the plotfile consumer sidecar (default 1)
#   SWH_CONSUME_ARGS  extra consumer flags, e.g. "--shell-fields chi phi"
#   SWH_KEEP_PLOTFILES=1  keep the heavy HDF5 on scratch (no --delete)
#   SWH_KEEP_LAST  plotfiles the consumer leaves behind (default 3)
#   SWH_WHAT      one line on what the run is for ->
#                 results/spinningwormhole/runs_registry.tsv
#   SWH_REGISTRY  that registry's path, if not the default above
#   SWH_FRAMES_FIELDS  frame fields when SWH_CONSUME_ARGS names none
#                 (default: the campaign's full set, frames_default.txt)
#                 ("none": no frames at all -- needs SWH_FRAMES_SUBSET)
#   SWH_FRAMES_SUBSET="<reason>"  the ONLY way to launch with fewer frame
#                 fields than frames_default.txt: the preflight refuses a
#                 subset without it, and records the reason (run_manifest.json)
#   SWH_PROC_LABEL  what this run calls itself in the machine's process table
#                 (default "test").  See "Process table" below
#   SWH_PROC_ALIAS=0  run the binary from its real path instead of the neutral
#                 copy (the GPU process list then shows the campaign path)
#   SWH_PROC_BIN_DIR  where the neutral copies live (default /tmp/ml_jobs/bin)
#   SWH_PREFLIGHT  full (default) | static | off -- see "Preflight" below
#   SWH_PREFLIGHT_ONLY=1  run the preflight, report, remove the run dir, stop
#                 (its t = 0 frames are kept in logs/preflight_frames/)
#
# Process table.  The cards are shared, and `ps aux` / `nvidia-smi` are
# readable by anyone who can see this machine's processes, so what a run calls
# itself there is a launch-time decision like any other.  Every long-lived
# process of a run is started from the run directory with RELATIVE paths and a
# neutral argv[0]: `test params.txt` (evolution), `test_post post.py ...`
# (consumer), `tee run.log`.  The GPU process list shows the executable's real
# path, which argv[0] cannot change, so the binary runs from a copy under
# SWH_PROC_BIN_DIR named after the label and the binary's own checksum -- one
# copy per distinct binary, reused by every later run.  What this does NOT
# hide: the username, that the cards are busy, and the directory names on the
# shared filesystem.  Nothing here changes what is computed; the real binary
# and the real paths are logged in the run's own log.
#
# Stop:  bash scripts/campaigns/stop_campaign.sh [--dry-run] <runs_dir>
#
# Plotfiles stream through the consumer sidecar while the run is going
# (grteclyn-wrapper/README.md, "ALWAYS extract frames on the fly"): reductions
# land in <run dir>/small_data on NFS and the heavy HDF5 is deleted from
# scratch behind them.  SWH_CONSUME=0 turns it off for a t = 0 probe whose
# plotfile you want to keep and analyse yourself.
#
# Deciding WHAT to extract is a launch-time decision and cannot be revisited:
# deletion is ledger-gated, so anything not extracted during the run is gone
# with the plotfile.  Pass extra extractions through SWH_CONSUME_ARGS.
#
# The whole body is one { ... } block ending in `exit`: bash parses it
# entirely before running it, so editing this file can never reach a live
# run.  (bash otherwise reads a script by byte offset as it goes; an edit
# made under a live run on 2026-09-24 would have had that run read the new
# file at the old offset when its evolution ended.)  Keep it that way.
{
set -euo pipefail

# A launch that dies before the evolution starts must die LOUDLY (2026-10-03:
# a set -e kill between two echo lines left a stub run dir and an idle card
# for 25 minutes with nothing in any log).  Until the evolution is launched,
# any exit -- an uncaught error above all -- names its line and command here,
# in the same detached log every launch is polled on.
SWH_EVOLUTION_STARTED=0
trap 'rc=$?; if [[ "${SWH_EVOLUTION_STARTED}" != "1" && "${rc}" != "0" ]]; then
  echo "[swh] !! LAUNCH FAILED before the evolution started (exit ${rc})" >&2
  echo "[swh] !! at line ${LINENO}: ${BASH_COMMAND}" >&2
  echo "[swh] !! nothing is running; the run dir (if made) is a stub" >&2
fi' EXIT
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SELF_DIR="${SCRIPT_DIR}"   # this directory, resolved BEFORE anything moves us
WRAPPER_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"

# Machine paths come from the gitignored .env overlay, never from this file and
# never from wherever the caller happened to be standing.  env.sh leaves
# already-exported variables alone, so SWH_*/GRTECLYN_SCRATCH overrides still
# win.  Sourcing it is also what makes REPO_ROOT authoritative rather than a
# guess from BASH_SOURCE.
# shellcheck source=../../lib/env.sh
source "${WRAPPER_DIR}/scripts/lib/env.sh"
# env.sh computes a SCRIPT_DIR of its own and, being sourced, overwrites ours:
# SCRIPT_DIR now points at scripts/lib rather than at this directory.  Restore it
# from the copy taken above -- every relative source below (launcher_common.sh)
# resolves against it.  Not re-derived from BASH_SOURCE: when this script is
# invoked by a relative name (which it is, so that the process table shows no
# campaign path) a re-derivation resolves against the current directory, and
# env.sh has already moved us to the repo root by this point.
SCRIPT_DIR="${SELF_DIR}"
REPO_ROOT="${GRTECLYN_ROOT:-$(cd -- "${WRAPPER_DIR}/.." && pwd)}"
EXAMPLE_DIR="${REPO_ROOT}/Examples/SpinningWormhole"
# The preflight is the SHARED engine (campaigns/lib/preflight.py, 2026-10-10:
# one engine for every campaign); this campaign's facts live in
# preflight_campaign.json beside this script.
CAMPAIGNS_LIB="$(cd -- "${SELF_DIR}/../lib" && pwd)"
PREFLIGHT_PY="${CAMPAIGNS_LIB}/preflight.py"
PREFLIGHT_CFG="${SELF_DIR}/preflight_campaign.json"
# The campaign's frame fields (SWH_FRAMES_FULL, from frames_default.txt): the
# default below and what the preflight holds every launch to.  Stops here if
# the list is missing.
# shellcheck source=lib/consumer_profiles.sh
source "${SELF_DIR}/lib/consumer_profiles.sh"

PARAMS="${SWH_PARAMS:-params_test.txt}"
GPU="${SWH_GPU:-0}"
RANKS="${SWH_RANKS:-1}"
RUNS_DIR="${SWH_RUNS_DIR:-${REPO_ROOT}/runs/spinning_wormhole}"
SCRATCH_ROOT="${GRTECLYN_SCRATCH:-/tmp/grteclyn_scratch}"

# Resolve the params template: an existing path wins, else the example dir.
if [[ -f "${PARAMS}" ]]; then
  TEMPLATE="$(cd -- "$(dirname -- "${PARAMS}")" && pwd)/$(basename -- "${PARAMS}")"
elif [[ -f "${EXAMPLE_DIR}/${PARAMS}" ]]; then
  TEMPLATE="${EXAMPLE_DIR}/${PARAMS}"
else
  echo "[swh] params template not found: ${PARAMS}" >&2
  exit 1
fi

NAME="${SWH_NAME:-$(basename "${TEMPLATE}" .txt)}"
if [[ -n "${SWH_RESTART:-}" ]]; then
  if [[ ! -d "${SWH_RESTART}" || ! -f "${SWH_RESTART}/Header" ]]; then
    echo "[swh] SWH_RESTART is not a checkpoint directory: ${SWH_RESTART}" >&2
    exit 1
  fi
  # Suffix from the checkpoint's step number: .../SpinningWormholeChk02000 ->
  # _r02000.  Never doubled: a --name that already carries this restart's
  # suffix is kept as is (2026-10-03: a merger extension launched as
  # ..._r04000_r04000, and every path the launch derived -- the consumer's
  # horizon track among them -- split between the two spellings).
  if [[ "${NAME}" == *"_r${SWH_RESTART##*Chk}" ]]; then
    echo "[swh] name already ends _r${SWH_RESTART##*Chk} -- keeping it (no double suffix)"
  else
    NAME="${NAME}_r${SWH_RESTART##*Chk}"
  fi
fi
RUN_DIR="${RUNS_DIR}/${NAME}"
SCRATCH_DIR="${SCRATCH_ROOT}/${NAME}"

# Evolution binary: explicit override, else the newest built .ex in the example.
if [[ -n "${SWH_EXE:-}" ]]; then
  EXE="${SWH_EXE}"
else
  EXE="$(ls -t "${EXAMPLE_DIR}"/main3d.*.ex 2>/dev/null | head -n 1 || true)"
fi
if [[ -z "${EXE}" || ! -x "${EXE}" ]]; then
  echo "[swh] no built binary in ${EXAMPLE_DIR} (main3d.*.ex) -- build first," >&2
  echo "[swh] or point SWH_EXE at one." >&2
  exit 1
fi

echo "[swh] name     : ${NAME}"
echo "[swh] template : ${TEMPLATE}"
echo "[swh] binary   : ${EXE}"
echo "[swh] gpu      : ${GPU}"
echo "[swh] run dir  : ${RUN_DIR}          (NFS: params, log, .dat streams)"
echo "[swh] scratch  : ${SCRATCH_DIR}      (node-local: plotfiles, checkpoints)"

# ---------------------------------------------------------------------------
# The plotfile consumer's flags.  Built BEFORE the preflight, which checks the
# frame list they carry and renders it from the t = 0 plotfile.  Fills
# consumer_args and FRAMES_SOURCE from the params file given: the run's clone,
# or the template on a dry run.
# ---------------------------------------------------------------------------
swh_consumer_args() {
  local params_file="$1"
  local -a center_vals
  # --frames-out defaults to a directory inside the wrapper SOURCE tree, which is
  # not gitignored, so frames from every run pile up there and are invisible from
  # the run directory.  Anchor them next to the run they came from.
  # Relative, because the consumer is started from RUN_DIR and its command line
  # is public (see "Process table"): "scratch" is the link made below.
  consumer_args=(--data scratch --out small_data --frames-out frames)

  # The consumer's --center defaults to (0,0,0), but the campaign templates put
  # the physics at center = L/2.  Nothing errors when they disagree: the
  # extractions still run, they just run in the far field, and --areal-radius
  # happily reports r/sqrt(chi) ~ r off in the asymptotically flat region as if
  # it were the throat (measured 2026-08-28 on a stage-1 drainhole: 0.845 at
  # r = 0.829, against a throat of areal radius 3.890 at r = 1.618).  Read the
  # centre off the params the run is actually using so the two cannot disagree.
  # It goes in BEFORE SWH_CONSUME_ARGS, so an explicit --center there still wins.
  if grep -qE "^center[[:space:]]*=" "${params_file}"; then
    # shellcheck disable=SC2207
    center_vals=($(grep -E "^center[[:space:]]*=" "${params_file}" \
                   | head -n 1 | sed -e 's/#.*//' -e 's/.*=//'))
    if [[ "${#center_vals[@]}" -eq 3 ]]; then
      consumer_args+=(--center "${center_vals[@]}")
      echo "[swh] consumer centre: ${center_vals[*]} (from the run's params)"
    else
      echo "[swh] WARNING: could not parse 'center' from params (got ${#center_vals[@]} values);" >&2
      echo "[swh]          consumer will use its (0,0,0) default -- pass --center yourself." >&2
    fi
  fi
  if [[ "${SWH_KEEP_PLOTFILES:-0}" == "0" ]]; then
    consumer_args+=(--delete --keep-last "${SWH_KEEP_LAST:-3}")
  fi
  # shellcheck disable=SC2206
  consumer_args+=(${SWH_CONSUME_ARGS:-})

  # A profile hands over absolute paths into the run, and so does a hand-written
  # SWH_CONSUME_ARGS.  Fold both back to RUN_DIR-relative: the consumer runs
  # there, and the command line is public.
  local i other rest
  for i in "${!consumer_args[@]}"; do
    case "${consumer_args[i]}" in
      "${RUN_DIR}")    consumer_args[i]="." ;;
      "${RUN_DIR}"/*)  consumer_args[i]="${consumer_args[i]#"${RUN_DIR}"/}" ;;
      "${SCRATCH_DIR}")   consumer_args[i]="scratch" ;;
      "${SCRATCH_DIR}"/*) consumer_args[i]="scratch/${consumer_args[i]#"${SCRATCH_DIR}"/}" ;;
      *spinning_wormhole/*/*)
        # A path into a run that is NOT this run.  When the other name is this
        # run's own name with a missing or extra _r<step> suffix, it is the
        # restart-suffix trap (2026-10-03: a merger extension's --horizon-track
        # named the un-suffixed run and the consumer tracked a stream that never
        # existed): repoint it to this run.  A genuinely different run is kept,
        # loudly -- a cross-run reference must be deliberate.
        rest="${consumer_args[i]#*spinning_wormhole/}"
        other="${rest%%/*}"
        if [[ "${other}" != "${NAME}" ]]; then
          if [[ "${NAME}" == "${other}"_r* || "${other}" == "${NAME}"_r* ]]; then
            consumer_args[i]="${consumer_args[i]//spinning_wormhole\/${other}\//spinning_wormhole/${NAME}/}"
            echo "[swh] consumer arg repointed: '${other}' -> '${NAME}' (restart-suffix trap)"
          else
            echo "[swh] WARNING: consumer arg points at another run ('${other}', this run is '${NAME}')" >&2
            echo "[swh]          kept as given -- make sure that is deliberate: ${consumer_args[i]}" >&2
          fi
        fi
        ;;
    esac
  done

  # Frames for EVERY field worth a movie, every launch.  The consumer deletes
  # the plotfiles behind the frames it renders, so a field not rendered live
  # has no movie, ever (the merger's chi-only ladder of 2026-09-08 and F4 of
  # 2026-09-25 both lost movies for good that way).  A launch that does not
  # name --frames-fields in SWH_CONSUME_ARGS gets the campaign's full set
  # (frames_default.txt), with the slice cache (one fixed colour scale per run
  # through rerender_frames.py) and per-frame auto limits.  SWH_FRAMES_FIELDS
  # changes the list; an explicit --frames-fields in SWH_CONSUME_ARGS wins over
  # both -- and either way the preflight refuses a list that misses a default
  # field unless SWH_FRAMES_SUBSET says why.
  local frames_default="${SWH_FRAMES_FIELDS:-${SWH_FRAMES_FULL}}"
  if [[ "${SWH_FRAMES_FIELDS:-}" == "none" ]]; then
    # No frames at all (launch.sh --frames-fields none): a study that keeps
    # none.  The preflight still refuses it unless SWH_FRAMES_SUBSET says why.
    FRAMES_SOURCE="none (SWH_FRAMES_FIELDS=none)"
    echo "[swh] frames   : none (SWH_FRAMES_FIELDS=none)"
    return 0
  elif [[ " ${SWH_CONSUME_ARGS:-} " != *" --frames-fields "* ]]; then
    # shellcheck disable=SC2206
    consumer_args+=(--frames-fields ${frames_default})
    [[ " ${SWH_CONSUME_ARGS:-} " == *"--frames-cache-slices"* ]] || consumer_args+=(--frames-cache-slices)
    [[ " ${SWH_CONSUME_ARGS:-} " == *"--frames-auto-zlim"* ]] || consumer_args+=(--frames-auto-zlim)
    if [[ -n "${SWH_FRAMES_FIELDS:-}" ]]; then
      FRAMES_SOURCE="SWH_FRAMES_FIELDS"
    else
      FRAMES_SOURCE="campaign default (frames_default.txt)"
    fi
    echo "[swh] frames   : ${frames_default} (${FRAMES_SOURCE})"
  else
    FRAMES_SOURCE="--frames-fields in SWH_CONSUME_ARGS"
    echo "[swh] frames   : as given in SWH_CONSUME_ARGS"
  fi
  if [[ " ${SWH_CONSUME_ARGS:-} " != *"--frames-zoom"* ]]; then
    echo "[swh] WARNING: no --frames-zoom in SWH_CONSUME_ARGS -- frames will show the whole box" >&2
  fi
}

if [[ "${SWH_DRYRUN:-0}" != "0" ]]; then
  # The no-GPU half of the preflight, on the template as it stands (before the
  # overrides below): contradictory settings, keys the binary cannot read, and
  # the frame list the consumer would get.
  swh_consumer_args "${TEMPLATE}"
  SWH_CONSUMER_ARGV="$(printf '%q ' "${consumer_args[@]}")"
  export SWH_CONSUMER_ARGV SWH_FRAMES_SOURCE="${FRAMES_SOURCE}"
  pf_py="${WRAPPER_DIR}/.venv/bin/python"; [[ -x "${pf_py}" ]] || pf_py="$(command -v python3)"
  "${pf_py}" "${PREFLIGHT_PY}" --campaign-config "${PREFLIGHT_CFG}" \
      --mode static --exe "${EXE}" --params "${TEMPLATE}" \
      --workdir "${SCRATCH_ROOT}/_preflight_dryrun" \
    || echo "[swh] the preflight would REFUSE this launch (above)" >&2
  echo "[swh] dry run -- nothing launched."
  exit 0
fi

if [[ -d "${RUN_DIR}" ]]; then
  echo "[swh] ${RUN_DIR} already exists -- delete it or set SWH_NAME/SWH_RUNS_DIR" >&2
  exit 1
fi

mkdir -p "${RUN_DIR}" "${SCRATCH_DIR}"

# --- process table (see the header) ----------------------------------------
# Everything below runs from RUN_DIR, so the scratch cell gets a link inside it
# and the consumer can be given "scratch" instead of an absolute path.
PROC_LABEL="${SWH_PROC_LABEL:-test}"
[[ -e "${RUN_DIR}/scratch" ]] || ln -s "${SCRATCH_DIR}" "${RUN_DIR}/scratch"

# The neutral copy the GPU process list will show.  Keyed by the binary's own
# checksum, so two runs on different builds never share one and a rebuild
# never silently reuses the old copy.
EXE_RUN="${EXE}"
if [[ "${SWH_PROC_ALIAS:-1}" != "0" ]]; then
  PROC_BIN_DIR="${SWH_PROC_BIN_DIR:-/tmp/ml_jobs/bin}"
  mkdir -p "${PROC_BIN_DIR}"
  exe_sum="$(md5sum "${EXE}" | cut -c1-8)"
  EXE_RUN="${PROC_BIN_DIR}/${PROC_LABEL}_${exe_sum}"
  if [[ ! -x "${EXE_RUN}" ]]; then
    cp "${EXE}" "${EXE_RUN}.part$$"
    chmod +x "${EXE_RUN}.part$$"
    mv "${EXE_RUN}.part$$" "${EXE_RUN}"
  fi
  echo "[swh] proc     : ${PROC_LABEL} (evolution runs from ${EXE_RUN})"
fi


# Stop handle for scripts/campaigns/stop_campaign.sh.  Registered per RUN dir,
# not the campaign root: several singles run concurrently (one per GPU), and a
# shared pid file would be last-writer-wins.  `stop_campaign.sh <RUN_DIR>`
# targets one rung; sweeping the root still catches workers by path.
source "${SCRIPT_DIR}/../lib/launcher_common.sh"
campaign_register_launcher "${RUN_DIR}"

# Clone the template and re-emit the three path keys (a cloned params file must
# never keep the source run's absolute paths).  Each key must occur exactly
# once, before and after, or the rewrite silently misses.
RUN_PARAMS="${RUN_DIR}/params.txt"
cp "${TEMPLATE}" "${RUN_PARAMS}"
for key in output_path amr.plot_file amr.check_file; do
  n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
  if [[ "${n}" != "1" ]]; then
    echo "[swh] template must define '${key}' exactly once (found ${n})" >&2
    exit 1
  fi
done
sed -i \
  -e "s|^output_path[[:space:]]*=.*|output_path = \"${RUN_DIR}\"|" \
  -e "s|^amr.plot_file[[:space:]]*=.*|amr.plot_file = \"${SCRATCH_DIR}/SpinningWormholePlt\"|" \
  -e "s|^amr.check_file[[:space:]]*=.*|amr.check_file = \"${SCRATCH_DIR}/SpinningWormholeChk\"|" \
  "${RUN_PARAMS}"

# Refinement-depth override.  This exists because max_level cannot be changed
# on its own: regrid_interval must carry exactly max_level values or AMReX
# aborts with "queryarr too many values requested", so the two keys have to be
# rewritten together.  The interval is taken from the template's first value
# and repeated, which is what the campaign templates do anyway.
if [[ -n "${SWH_MAX_LEVEL:-}" ]]; then
  for key in max_level regrid_interval; do
    n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
    if [[ "${n}" != "1" ]]; then
      echo "[swh] SWH_MAX_LEVEL needs '${key}' exactly once in the template (found ${n})" >&2
      exit 1
    fi
  done
  ri_first="$(grep "^regrid_interval[[:space:]]*=" "${RUN_PARAMS}" \
              | sed -e 's/#.*//' -e 's/.*=//' | awk '{print $1}')"
  if [[ -z "${ri_first}" ]]; then
    echo "[swh] could not read regrid_interval from the template" >&2
    exit 1
  fi
  ri_list=""
  for ((i = 0; i < SWH_MAX_LEVEL; i++)); do ri_list+="${ri_first} "; done
  # max_level = 0 is the unigrid case and it needs ZERO regrid intervals, but
  # `regrid_interval =` with nothing after it is a ParmParse hard error
  # ("no values for definition regrid_interval"), so the key cannot simply be
  # emptied.  A unigrid run never regrids, so the values are dead either way:
  # leave the template's list alone and rewrite only max_level.
  if [[ "${SWH_MAX_LEVEL}" -eq 0 ]]; then
    sed -i -e "s|^max_level[[:space:]]*=.*|max_level = 0|" "${RUN_PARAMS}"
    echo "[swh] refinement override: max_level = 0 (unigrid; regrid_interval left as-is)"
  else
  sed -i \
    -e "s|^max_level[[:space:]]*=.*|max_level = ${SWH_MAX_LEVEL}|" \
    -e "s|^regrid_interval[[:space:]]*=.*|regrid_interval = ${ri_list% }|" \
    "${RUN_PARAMS}"
  echo "[swh] refinement override: max_level = ${SWH_MAX_LEVEL}, regrid_interval = ${ri_list% }"
  fi
fi

# Restart injection.  --restart is the ONE source of amr.restart.  A template
# cloned from a restart leg's packed params carries the parent's own line
# (2026-10-03, in the merger campaign: one launch was refused twice over it --
# once for doubling, once, without the flag, by the preflight probe): a line
# that names the SAME checkpoint as --restart is stripped and re-injected; a
# different one is a real ambiguity and is refused.  A template with
# amr.restart and NO --restart is refused up front with the fix, instead of
# limping into the preflight.
if [[ -n "${SWH_RESTART:-}" ]]; then
  tmpl_restart="$( (grep -E "^amr.restart[[:space:]]*=" "${RUN_PARAMS}" || true) | head -n1 \
                  | sed -e 's/.*=[[:space:]]*//' -e 's/^"//' -e 's/"[[:space:]]*$//')"
  if [[ -n "${tmpl_restart}" && "${tmpl_restart}" != "${SWH_RESTART}" ]]; then
    echo "[swh] template sets amr.restart = ${tmpl_restart}" >&2
    echo "[swh] but --restart gave        ${SWH_RESTART}" >&2
    echo "[swh] refusing the ambiguity -- remove the template's line or drop --restart" >&2
    exit 1
  fi
  if [[ -n "${tmpl_restart}" ]]; then
    sed -i "/^amr.restart[[:space:]]*=/d" "${RUN_PARAMS}"
    echo "[swh] template's own amr.restart (same checkpoint) stripped -- --restart is the one source"
  fi
  printf '\n# restart (set by run_single.sh)\namr.restart = "%s"\n' \
    "${SWH_RESTART}" >> "${RUN_PARAMS}"
  echo "[swh] restart  : ${SWH_RESTART}"
elif grep -qE "^amr.restart[[:space:]]*=" "${RUN_PARAMS}"; then
  echo "[swh] the template carries amr.restart but the launch has no --restart:" >&2
  grep -E "^amr.restart[[:space:]]*=" "${RUN_PARAMS}" | head -n1 | sed 's/^/[swh]   /' >&2
  echo "[swh] relaunch with --restart <that checkpoint> (the name then gets its _r<step>" >&2
  echo "[swh] suffix and the preflight knows it is a restart) -- refusing" >&2
  exit 1
fi

# The consumer's final flags (every params override above applied), and its
# entry point -- here, before the preflight, which renders the t = 0 frames with
# exactly this consumer and these flags.
swh_consumer_args "${RUN_PARAMS}"
CONSUMER_PY="${WRAPPER_DIR}/.venv/bin/python"
CONSUMER_MOD="grteclyn_wrapper.visualisation.process_wave.consume_plotfiles"
CONSUMER_PID=""

# The consumer's public name (see "Process table").  Python locates its virtual
# environment through argv[0], so simply renaming the process loses every
# installed package ("No module named 'numpy'", measured 2026-09-10).  The
# neutral name is therefore a real symlink inside the venv's own bin directory,
# with that directory first on PATH: python looks the bare name up on PATH,
# resolves the link and finds the environment, and the command line still shows
# no path at all.
CONSUMER_BIN="${CONSUMER_PY}"
if [[ "${SWH_PROC_ALIAS:-1}" != "0" && -x "${CONSUMER_PY}" ]]; then
  ln -sfn "$(basename "${CONSUMER_PY}")" "$(dirname "${CONSUMER_PY}")/${PROC_LABEL}_post"
  PATH="$(dirname "${CONSUMER_PY}"):${PATH}"
  export PATH
  CONSUMER_BIN="${PROC_LABEL}_post"
fi
if [[ "${SWH_CONSUME:-1}" != "0" ]]; then
  if [[ ! -x "${CONSUMER_PY}" ]]; then
    echo "[swh] consumer requested but ${CONSUMER_PY} is missing -- run 'uv sync'" >&2
    exit 1
  fi
  # `python -m <module>` would put the package's dotted name on a public
  # command line, so the module is entered through a one-line file in the run
  # directory instead and the process is named after the run's label.
  cat > "${RUN_DIR}/post.py" <<PY
# written by run_single.sh: entry point for the plotfile consumer
import runpy
runpy.run_module("${CONSUMER_MOD}", run_name="__main__")
PY
fi
# What the preflight checks and renders the frames with (through the
# environment: the process table is public).
SWH_CONSUMER_ARGV="$(printf '%q ' "${consumer_args[@]}")"
SWH_FRAMES_SOURCE="${FRAMES_SOURCE}"
SWH_FRAMES_CMD="${CONSUMER_BIN} post.py"
export SWH_CONSUMER_ARGV SWH_FRAMES_SOURCE SWH_FRAMES_CMD

# ---------------------------------------------------------------------------
# Preflight: refuse a launch the binary would not honour.
# ---------------------------------------------------------------------------
# AMReX ignores a key nothing reads, so a binary older than a feature runs the
# params without it and says nothing (the merger campaign lost four arms and a
# restartless death to exactly that, 2026-09-23/24).  preflight.py checks the
# FINAL params (every override above applied): contradictory settings, the
# background table on disk, keys absent from the binary, keys a 0-step
# start-up of the binary did not read, and -- when the seed is set -- that the
# seed changes the t = 0 data.  A few seconds on the card.
# A refusal removes the run dir and scratch cell (nothing is registered or
# started) and keeps the params and the report under logs/preflight_refused/.
# SWH_PREFLIGHT=static skips the start-ups (a card too full for a second
# process); =off skips every check of the binary.  Both are recorded in
# run_manifest.json.
# The FRAMES, in every mode, off included: the frame list must hold every
# field of frames_default.txt (or SWH_FRAMES_SUBSET says why), and each
# field's plot variable must be written; in full mode the start-up also writes
# its t = 0 plotfile and the consumer renders every frame field from it, with
# this run's flags, into preflight_frames/ -- a field that fails or comes out
# blank refuses the launch.  Those frames are frame 0, before the run exists:
# eyeball them (logs/preflight_frames/ after --preflight-only).
TOOLS_PY="${WRAPPER_DIR}/.venv/bin/python"
[[ -x "${TOOLS_PY}" ]] || TOOLS_PY="$(command -v python3)"
TOOLS_BIN="${TOOLS_PY}"
if [[ "${SWH_PROC_ALIAS:-1}" != "0" && "${TOOLS_PY}" == "${WRAPPER_DIR}/.venv/bin/python" ]]; then
  ln -sfn "$(basename "${TOOLS_PY}")" "$(dirname "${TOOLS_PY}")/${PROC_LABEL}_pre"
  PATH="$(dirname "${TOOLS_PY}"):${PATH}"
  export PATH
  TOOLS_BIN="${PROC_LABEL}_pre"
fi
# Entered through a file in the run dir, like post.py, so the public command
# line shows "<label>_pre pre.py ..." with relative paths only.  The preflight
# is the shared engine; its campaign config travels through the environment
# (CAMPAIGN_PREFLIGHT_CONFIG), not the public command line.
cat > "${RUN_DIR}/pre.py" <<PYTOOLS
# written by run_single.sh: entry point for the launch-time checks
import runpy, sys
tool = sys.argv.pop(1)
runpy.run_path({"preflight": "${PREFLIGHT_PY}",
                "manifest": "${SELF_DIR}/run_manifest.py"}[tool], run_name="__main__")
PYTOOLS
swh_tool() { ( cd "${RUN_DIR:?}" && exec -a "${PROC_LABEL}_pre" "${TOOLS_BIN}" pre.py "$@" ); }

PF_MODE="${SWH_PREFLIGHT:-full}"
case "${PF_MODE}" in
  full|static|off) ;;
  *) echo "[swh] SWH_PREFLIGHT must be full, static or off (got '${PF_MODE}')" >&2; exit 2 ;;
esac
if [[ "${PF_MODE}" == "off" ]]; then
  echo "[swh] preflight: OFF (SWH_PREFLIGHT=off) -- the binary is not checked (the manifest says so);" >&2
  echo "[swh]            the frame list still is (its only override is SWH_FRAMES_SUBSET)" >&2
fi
pf_status=0
SWH_EXE_NAME="$(basename "${EXE}")" CAMPAIGN_PREFLIGHT_CONFIG="${PREFLIGHT_CFG}" swh_tool preflight \
    --exe "${EXE_RUN}" --argv0 "${PROC_LABEL}" --params params.txt \
    --gpu "${GPU%%,*}" --workdir scratch/_preflight --mode "${PF_MODE}" \
    --frames-out preflight_frames --json preflight.json ${SWH_RESTART:+--restart} || pf_status=$?
if [[ "${pf_status}" -ne 0 ]]; then
  kept="${RUNS_DIR:?}/logs/preflight_refused/${NAME:?}_$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "${kept}"
  cp "${RUN_DIR:?}/params.txt" "${RUN_DIR:?}/preflight.json" "${kept}/" 2>/dev/null || true
  for probe in run control; do
    if [[ -f "${SCRATCH_DIR:?}/_preflight/${probe}/probe.log" ]]; then
      cp "${SCRATCH_DIR:?}/_preflight/${probe}/probe.log" "${kept}/probe_${probe}.log"
    fi
  done
  # The t = 0 frames show what failed: kept, never deleted.
  if [[ -d "${RUN_DIR:?}/preflight_frames" ]]; then
    cp -r "${RUN_DIR:?}/preflight_frames" "${kept}/"
  fi
  rm -rf "${SCRATCH_DIR:?}/_preflight" "${RUN_DIR:?}"
  rmdir "${SCRATCH_DIR:?}" 2>/dev/null || true
  if [[ "${pf_status}" -eq 1 ]]; then
    echo "[swh] !! PREFLIGHT REFUSED THE LAUNCH -- nothing started, nothing registered." >&2
  else
    echo "[swh] !! PREFLIGHT COULD NOT RUN -- nothing started.  SWH_PREFLIGHT=static skips the start-ups." >&2
  fi
  echo "[swh]    params + report kept in runs/spinning_wormhole/${kept#"${RUNS_DIR}"/}" >&2
  exit "${pf_status}"
fi
if [[ "${SWH_PREFLIGHT_ONLY:-0}" != "0" ]]; then
  # The t = 0 frames are the point of asking: kept for the eye, with the report.
  if [[ -d "${RUN_DIR:?}/preflight_frames" ]]; then
    shown="${RUNS_DIR:?}/logs/preflight_frames/${NAME:?}_$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "${shown}"
    cp -r "${RUN_DIR:?}/preflight_frames/." "${shown}/"
    cp "${RUN_DIR:?}/preflight.json" "${shown}/" 2>/dev/null || true
    echo "[swh] t = 0 frames (one per field) kept in runs/spinning_wormhole/${shown#"${RUNS_DIR}"/} -- eyeball them"
  fi
  rm -rf "${SCRATCH_DIR:?}/_preflight" "${RUN_DIR:?}"
  rmdir "${SCRATCH_DIR:?}" 2>/dev/null || true
  echo "[swh] preflight only: PASSED -- nothing launched, run dir removed."
  exit 0
fi
if [[ -d "${RUN_DIR}/preflight_frames" ]]; then
  echo "[swh] t = 0 frames: ${RUN_DIR}/preflight_frames (rendered at preflight; the run's own go to frames/)"
fi

# Register the run: one tab-separated line in the pack's registry, so the
# summary table needs no code edit per run.  Only when the launch says what
# the run is for.
REGISTRY="${SWH_REGISTRY:-${REPO_ROOT}/results/spinningwormhole/runs_registry.tsv}"
if [[ -n "${SWH_WHAT:-}" && -f "${REGISTRY}" ]]; then
  if grep -qP "^${NAME}\t" "${REGISTRY}"; then
    echo "[swh] registry : ${NAME} already registered (SWH_WHAT ignored)"
  else
    printf '%s\t%s\t\t\n' "${NAME}" "${SWH_WHAT}" >> "${REGISTRY}"
    echo "[swh] registry : ${NAME} -> ${REGISTRY#"${REPO_ROOT}"/}"
  fi
fi

# What this run IS -- params, binary and the commit it carries, launcher commit,
# node, card, preflight verdict, t = 0 diagnostics -- written before the first
# step and completed at exit (run_manifest.py; packed beside the streams).
# Revealing values go through the environment, not the public command line.
SWH_MANIFEST_NAME="${NAME}" SWH_MANIFEST_TEMPLATE="${TEMPLATE}" SWH_MANIFEST_EXE="${EXE}" \
  swh_tool manifest start --run-dir . --preflight preflight.json \
  || echo "[swh] WARNING: run_manifest.json not written" >&2

# ---------------------------------------------------------------------------
# Plotfile consumer sidecar (its flags and post.py were made before the preflight).
# ---------------------------------------------------------------------------
if [[ "${SWH_CONSUME:-1}" != "0" ]]; then
  mkdir -p "${RUN_DIR}/small_data"
  (
    cd "${RUN_DIR}"
    exec -a "${PROC_LABEL}_post" "${CONSUMER_BIN}" post.py "${consumer_args[@]}" \
      --watch > consumer.log 2>&1
  ) &
  CONSUMER_PID=$!
  echo "[swh] consumer  : pid ${CONSUMER_PID} -> ${RUN_DIR}/small_data"

  # IS IT ACTUALLY UP?  A consumer that dies at startup -- one bad flag is
  # enough, and argparse exits before it prints anything to the log tail anyone
  # reads -- takes the frames, the python psi4 cross-check AND the plotfile
  # deletion with it, and nothing downstream says so: the evolution runs its
  # full length and scratch fills behind it (measured in the merger campaign,
  # 2026-09-15).  Give it a moment to fail, then look; the cost is a few
  # seconds once per run.
  sleep 8
  if ! kill -0 "${CONSUMER_PID}" 2>/dev/null; then
    echo "[swh] !! THE CONSUMER DIED AT STARTUP -- no frames, no python psi4, and" >&2
    echo "[swh]    NOTHING WILL DELETE PLOTFILES.  Last lines of consumer.log:" >&2
    tail -n 12 "${RUN_DIR}/consumer.log" 2>/dev/null | sed 's/^/[swh]    /' >&2
    echo "[swh]    Fix the consumer arguments (lib/consumer_profiles.sh) and relaunch." >&2
    exit 1
  fi
  if [[ "${SWH_KEEP_PLOTFILES:-0}" == "0" ]]; then
    echo "[swh]            deleting processed plotfiles, keeping last ${SWH_KEEP_LAST:-3}"
  fi
fi

# Multi-GPU: one rank per physical card.  The binding is done INSIDE each rank
# and not by exporting CUDA_VISIBLE_DEVICES="0,1" to the parent, because
# OpenMPI/prterun drops that env often enough that ranks silently pile onto
# card 0.  Each rank reads its own id out of GRTECLYN_GPU_IDS by local rank
# instead.
if [[ "${RANKS}" -gt 1 ]]; then
  IFS="," read -ra _gpu_ids <<< "${GPU}"
  if [[ "${#_gpu_ids[@]}" -ne "${RANKS}" ]]; then
    echo "[swh] ERROR: SWH_RANKS=${RANKS} needs exactly ${RANKS} comma-separated" >&2
    echo "[swh]        ids in SWH_GPU, got '${GPU}' (${#_gpu_ids[@]})." >&2
    exit 2
  fi
  if [[ "${EXE}" != *".MPI."* ]]; then
    echo "[swh] ERROR: SWH_RANKS=${RANKS} needs an MPI binary, but SWH_EXE is" >&2
    echo "[swh]        ${EXE}.  Build with USE_MPI=TRUE USE_CUDA=TRUE." >&2
    exit 2
  fi
  echo "[swh] ranks    : ${RANKS} (MPI), one per card: ${GPU}"
fi

SWH_EVOLUTION_STARTED=1
echo "[swh] === launching ${NAME} (attached; Ctrl-C or stop_campaign.sh to stop) ==="
status=0
# From here on the shell stands in the run directory, so the evolution, the
# log writer and the drain pass all quote relative paths (see "Process table").
cd "${RUN_DIR}"
(
  if [[ "${RANKS}" -gt 1 ]]; then
    GRTECLYN_GPU_IDS="${GPU}" GRTECLYN_EXE="${EXE_RUN}" \
    GRTECLYN_LABEL="${PROC_LABEL}" mpirun -n "${RANKS}" bash -c \
      'IFS="," read -ra _g <<< "${GRTECLYN_GPU_IDS}"; \
       export CUDA_VISIBLE_DEVICES="${_g[${OMPI_COMM_WORLD_LOCAL_RANK:-0}]}"; \
       exec -a "${GRTECLYN_LABEL}" "${GRTECLYN_EXE}" params.txt'
  else
    CUDA_VISIBLE_DEVICES="${GPU}" exec -a "${PROC_LABEL}" "${EXE_RUN}" params.txt
  fi
) 2>&1 | tee run.log || status=$?

# Drain before reporting.  The watcher is stopped and then a single one-shot
# pass picks up whatever it had not reached: deletion is ledger-gated, so an
# extraction interrupted by the TERM is retried here rather than lost, and a
# plotfile that never got extracted is never collected.
if [[ -n "${CONSUMER_PID}" ]]; then
  kill "${CONSUMER_PID}" 2>/dev/null || true
  wait "${CONSUMER_PID}" 2>/dev/null || true
  echo "[swh] draining consumer (final pass) ..."
  # --keep-existing-frames is load-bearing here.  The consumer clears the frames
  # for every requested field at startup, which is right for a fresh run and
  # catastrophic for a second pass over the same run: without it this drain
  # deletes every PNG the watcher rendered during the evolution, and if the run
  # aborted there are no plotfiles left to re-render them from.
  # --stable-seconds 0 is load-bearing too.  The consumer skips a plotfile whose
  # Header is younger than 30 s, a guard against reading one mid-write; this
  # pass starts about a second after the evolution exits, so with the default
  # the run's last plotfile was never extracted (measured 2026-09-14).  The
  # binary has exited, so every plotfile on scratch is complete.
  (
    cd "${RUN_DIR}"
    exec -a "${PROC_LABEL}_post" "${CONSUMER_BIN}" post.py "${consumer_args[@]}" \
      --keep-existing-frames --stable-seconds 0 >> consumer.log 2>&1
  ) || \
    echo "[swh] final consumer pass reported an error -- see ${RUN_DIR}/consumer.log" >&2
fi

swh_tool manifest finish --run-dir . --status "${status}" \
  || echo "[swh] WARNING: run_manifest.json not finished" >&2

if [[ "${status}" -ne 0 ]]; then
  echo "[swh] run FAILED (exit ${status}) -- see ${RUN_DIR}/run.log" >&2
  exit "${status}"
fi

echo "[swh] run complete: ${RUN_DIR}"
if [[ "${SWH_CONSUME:-1}" != "0" ]]; then
  echo "[swh] reductions : ${RUN_DIR}/small_data"
fi
left="$(find "${SCRATCH_DIR}" -maxdepth 1 -name '*Plt*' -type d 2>/dev/null | wc -l)"
echo "[swh] plotfiles left on scratch: ${left} (${SCRATCH_DIR})"
exit
}
