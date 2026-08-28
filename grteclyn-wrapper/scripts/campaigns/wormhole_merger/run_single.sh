#!/usr/bin/env bash
# BinaryWormholeMerger -- single-run launcher (research/merger/Plan.md).
#
# One run of Examples/BinaryWormholeMerger through the campaign contract
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
#   WHM_MAX_LEVEL override max_level in the cloned params, rewriting
#                 regrid_interval to match (AMReX aborts if it does not carry
#                 exactly max_level values)
#   WHM_SIGMA     override the Kreiss-Oliger coefficient `sigma` in the cloned
#                 params (appends _sgN to the run name).  A first-class knob for
#                 drainhole data, not a tuning detail: measured 2026-08-28, the
#                 inherited sigma = 2.0 kills a unigrid drainhole at t = 0.22 by
#                 driving chi in the single innermost cell to the min_chi floor
#                 while its neighbour is still at 3e-2, and CCZ4 divides by chi.
#                 sigma = 0 survives and is 20x more accurate AT THE THROAT.
#   WHM_LAPSE_TYPE override wormhole_initial_lapse_type in the cloned params
#                 (appends _lapseN to the run name).  The collar A/B of
#                 FIx.md Stage 1.3 is this knob and nothing else: 5 is the
#                 drainhole's bare static lapse, 6 is that lapse times the
#                 origin-isolating collar.
#   WHM_DRYRUN=1  resolve and print everything, touch nothing, exit
#   WHM_CONSUME   run the plotfile consumer sidecar (default 1)
#   WHM_CONSUME_ARGS  extra consumer flags, e.g. "--shell-fields chi phi"
#   WHM_KEEP_PLOTFILES=1  keep the heavy HDF5 on scratch (no --delete)
#   WHM_KEEP_LAST  plotfiles the consumer leaves behind (default 3)
#
# Stop:  bash scripts/campaigns/stop_campaign.sh [--dry-run] <runs_dir>
#
# Plotfiles stream through the consumer sidecar while the run is going
# (grteclyn-wrapper/README.md, "ALWAYS extract frames on the fly"): reductions
# land in <run dir>/small_data on NFS and the heavy HDF5 is deleted from
# scratch behind them.  WHM_CONSUME=0 turns it off for a t = 0 probe whose
# plotfile you want to keep and analyse yourself.
#
# Deciding WHAT to extract is a launch-time decision and cannot be revisited:
# deletion is ledger-gated, so anything not extracted during the run is gone
# with the plotfile.  Pass extra extractions through WHM_CONSUME_ARGS.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"

# Machine paths come from the gitignored .env overlay, never from this file and
# never from wherever the caller happened to be standing.  env.sh leaves
# already-exported variables alone, so WHM_*/GRTECLYN_SCRATCH overrides still
# win.  Sourcing it is also what makes REPO_ROOT authoritative rather than a
# guess from BASH_SOURCE.
# shellcheck source=../../lib/env.sh
source "${WRAPPER_DIR}/scripts/lib/env.sh"
# env.sh computes a SCRIPT_DIR of its own and exports it, so after sourcing it
# SCRIPT_DIR points at scripts/lib rather than at this directory.  Re-derive it:
# every relative source below (launcher_common.sh) resolves against it.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${GRTECLYN_ROOT:-$(cd -- "${WRAPPER_DIR}/.." && pwd)}"
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
if [[ -n "${WHM_LAPSE_TYPE:-}" ]]; then
  NAME="${NAME}_lapse${WHM_LAPSE_TYPE}"
fi
if [[ -n "${WHM_SIGMA:-}" ]]; then
  NAME="${NAME}_sg$(printf '%s' "${WHM_SIGMA}" | tr -d '.')"
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

# Initial-lapse override.  The lapse is not a free gauge choice for a drainhole:
# alpha = e^{u} is part of the static solution, so type 5 makes the data an exact
# fixed point of the evolved system and type 6 multiplies in the origin-isolating
# collar, which deliberately breaks that.  Comparing the two is the whole of
# FIx.md Stage 1.3, so it gets an override rather than a forked params file --
# a duplicated 130-line template would drift and the comparison would stop being
# an A/B.
if [[ -n "${WHM_SIGMA:-}" ]]; then
  key=sigma
  n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
  if [[ "${n}" != "1" ]]; then
    echo "[whm] WHM_SIGMA needs '${key}' exactly once in the template (found ${n})" >&2
    exit 1
  fi
  sed -i "s|^${key}[[:space:]]*=.*|${key} = ${WHM_SIGMA}|" "${RUN_PARAMS}"
  echo "[whm] dissipation override: ${key} = ${WHM_SIGMA}"
fi

if [[ -n "${WHM_LAPSE_TYPE:-}" ]]; then
  key=wormhole_initial_lapse_type
  n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
  if [[ "${n}" != "1" ]]; then
    echo "[whm] WHM_LAPSE_TYPE needs '${key}' exactly once in the template (found ${n})" >&2
    exit 1
  fi
  sed -i "s|^${key}[[:space:]]*=.*|${key} = ${WHM_LAPSE_TYPE}|" "${RUN_PARAMS}"
  echo "[whm] lapse override: ${key} = ${WHM_LAPSE_TYPE}"
fi

# Refinement-depth override (Plan.md Phase 2 resolution study, and the origin
# instability it is chasing).  This exists because max_level cannot be changed
# on its own: regrid_interval must carry exactly max_level values or AMReX
# aborts with "queryarr too many values requested", so the two keys have to be
# rewritten together.  The interval is taken from the template's first value
# and repeated, which is what every merger template does anyway.
#
# Refining is not automatically safer here.  The throats are compactified at
# r = 0 -- chi vanishes like r^4 because that point is the other universe's
# spatial infinity -- and CCZ4 divides by chi.  Each extra level halves the
# distance from the innermost cell centre to that point and drops chi there by
# ~16x, so depth makes the origin stencil worse, not better, and the run NaNs
# in h11 on the finest level while the throat itself is still healthy.
if [[ -n "${WHM_MAX_LEVEL:-}" ]]; then
  for key in max_level regrid_interval; do
    n="$(grep -c "^${key}[[:space:]]*=" "${RUN_PARAMS}" || true)"
    if [[ "${n}" != "1" ]]; then
      echo "[whm] WHM_MAX_LEVEL needs '${key}' exactly once in the template (found ${n})" >&2
      exit 1
    fi
  done
  ri_first="$(grep "^regrid_interval[[:space:]]*=" "${RUN_PARAMS}" \
              | sed -e 's/#.*//' -e 's/.*=//' | awk '{print $1}')"
  if [[ -z "${ri_first}" ]]; then
    echo "[whm] could not read regrid_interval from the template" >&2
    exit 1
  fi
  ri_list=""
  for ((i = 0; i < WHM_MAX_LEVEL; i++)); do ri_list+="${ri_first} "; done
  # max_level = 0 is the unigrid case and it needs ZERO regrid intervals, but
  # `regrid_interval =` with nothing after it is a ParmParse hard error
  # ("no values for definition regrid_interval"), so the key cannot simply be
  # emptied.  A unigrid run never regrids, so the values are dead either way:
  # leave the template's list alone and rewrite only max_level.
  if [[ "${WHM_MAX_LEVEL}" -eq 0 ]]; then
    sed -i -e "s|^max_level[[:space:]]*=.*|max_level = 0|" "${RUN_PARAMS}"
    echo "[whm] refinement override: max_level = 0 (unigrid; regrid_interval left as-is)"
  else
  sed -i \
    -e "s|^max_level[[:space:]]*=.*|max_level = ${WHM_MAX_LEVEL}|" \
    -e "s|^regrid_interval[[:space:]]*=.*|regrid_interval = ${ri_list% }|" \
    "${RUN_PARAMS}"
  echo "[whm] refinement override: max_level = ${WHM_MAX_LEVEL}, regrid_interval = ${ri_list% }"
  fi
fi

# ---------------------------------------------------------------------------
# Plotfile consumer sidecar.
# ---------------------------------------------------------------------------
CONSUMER_PY="${WRAPPER_DIR}/.venv/bin/python"
CONSUMER_MOD="grteclyn_wrapper.visualisation.process_wave.consume_plotfiles"
CONSUMER_PID=""
# --frames-out defaults to a directory inside the wrapper SOURCE tree, which is
# not gitignored, so frames from every run pile up there and are invisible from
# the run directory.  Anchor them next to the run they came from.
consumer_args=(--data "${SCRATCH_DIR}" --out "${RUN_DIR}/small_data"
               --frames-out "${RUN_DIR}/frames")

# The consumer's --center defaults to (0,0,0), but every merger template puts
# the physics at center = L/2.  Nothing errors when they disagree: the
# extractions still run, they just run in the far field, and --areal-radius
# happily reports r/sqrt(chi) ~ r off in the asymptotically flat region as if it
# were the throat.  Measured 2026-08-28 on a stage-1 drainhole: 0.845 at
# r = 0.829, against a throat of areal radius 3.890 at r = 1.618.  Read the
# centre off the params the run is actually using so the two cannot disagree.
# It goes in BEFORE WHM_CONSUME_ARGS, so an explicit --center there still wins.
if grep -qE "^center[[:space:]]*=" "${RUN_PARAMS}"; then
  # shellcheck disable=SC2207
  center_vals=($(grep -E "^center[[:space:]]*=" "${RUN_PARAMS}" \
                 | head -n 1 | sed -e 's/#.*//' -e 's/.*=//'))
  if [[ "${#center_vals[@]}" -eq 3 ]]; then
    consumer_args+=(--center "${center_vals[@]}")
    echo "[whm] consumer centre: ${center_vals[*]} (from the run's params)"
  else
    echo "[whm] WARNING: could not parse 'center' from params (got ${#center_vals[@]} values);" >&2
    echo "[whm]          consumer will use its (0,0,0) default -- pass --center yourself." >&2
  fi
fi
if [[ "${WHM_KEEP_PLOTFILES:-0}" == "0" ]]; then
  consumer_args+=(--delete --keep-last "${WHM_KEEP_LAST:-3}")
fi
# shellcheck disable=SC2206
consumer_args+=(${WHM_CONSUME_ARGS:-})

if [[ "${WHM_CONSUME:-1}" != "0" ]]; then
  if [[ ! -x "${CONSUMER_PY}" ]]; then
    echo "[whm] consumer requested but ${CONSUMER_PY} is missing -- run 'uv sync'" >&2
    exit 1
  fi
  mkdir -p "${RUN_DIR}/small_data"
  "${CONSUMER_PY}" -m "${CONSUMER_MOD}" "${consumer_args[@]}" --watch \
    > "${RUN_DIR}/consumer.log" 2>&1 &
  CONSUMER_PID=$!
  echo "[whm] consumer  : pid ${CONSUMER_PID} -> ${RUN_DIR}/small_data"
  if [[ "${WHM_KEEP_PLOTFILES:-0}" == "0" ]]; then
    echo "[whm]            deleting processed plotfiles, keeping last ${WHM_KEEP_LAST:-3}"
  fi
fi

echo "[whm] === launching ${NAME} (attached; Ctrl-C or stop_campaign.sh to stop) ==="
status=0
(
  cd "${RUN_DIR}"
  CUDA_VISIBLE_DEVICES="${GPU}" "${EXE}" "${RUN_PARAMS}"
) 2>&1 | tee "${RUN_DIR}/run.log" || status=$?

# Drain before reporting.  The watcher is stopped and then a single one-shot
# pass picks up whatever it had not reached: deletion is ledger-gated, so an
# extraction interrupted by the TERM is retried here rather than lost, and a
# plotfile that never got extracted is never collected.
if [[ -n "${CONSUMER_PID}" ]]; then
  kill "${CONSUMER_PID}" 2>/dev/null || true
  wait "${CONSUMER_PID}" 2>/dev/null || true
  echo "[whm] draining consumer (final pass) ..."
  # --keep-existing-frames is load-bearing here.  The consumer clears the frames
  # for every requested field at startup, which is right for a fresh run and
  # catastrophic for a second pass over the same run: without it this drain
  # deletes every PNG the watcher rendered during the evolution, and if the run
  # aborted there are no plotfiles left to re-render them from.
  "${CONSUMER_PY}" -m "${CONSUMER_MOD}" "${consumer_args[@]}" \
    --keep-existing-frames \
    >> "${RUN_DIR}/consumer.log" 2>&1 || \
    echo "[whm] final consumer pass reported an error -- see ${RUN_DIR}/consumer.log" >&2
fi

if [[ "${status}" -ne 0 ]]; then
  echo "[whm] run FAILED (exit ${status}) -- see ${RUN_DIR}/run.log" >&2
  exit "${status}"
fi

echo "[whm] run complete: ${RUN_DIR}"
if [[ "${WHM_CONSUME:-1}" != "0" ]]; then
  echo "[whm] reductions : ${RUN_DIR}/small_data"
fi
left="$(find "${SCRATCH_DIR}" -maxdepth 1 -name '*Plt*' -type d 2>/dev/null | wc -l)"
echo "[whm] plotfiles left on scratch: ${left} (${SCRATCH_DIR})"
