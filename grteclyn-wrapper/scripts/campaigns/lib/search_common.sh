#!/usr/bin/env bash
# Shared defaults for MAP-Elites (QD) and CMA-ES search loops (stage 0 + 1).
#
# Sourced by scripts/campaigns/qd/run.sh and scripts/campaigns/cmaes/run.sh so
# warm-started CMA-ES refinement uses the same grid, time window, gates, 4D
# geodesic probe, and scoring objective as the QD campaign that produced elites.
#
# Override any variable via the environment before launching either script.

# ---- Matter / search space ---------------------------------------------------
: "${LUMPS:=5}"
: "${SHELL_PROFILE:=compact}"
: "${GRTRESNA_ANSATZ:=shell}"
: "${GRTRESNA_MATTER_SECTOR:=scalar}"
: "${GRTRESNA_MATTER_COUPLING:=canonical}"

# Frame / projection fields depend on matter sector (geometry ansatz unchanged).
if [[ "${GRTRESNA_MATTER_SECTOR}" == "boson_star" ]]; then
  : "${FRAMES_FIELDS:=scalar_activity phi Pi phi_lump0 Pi_lump0 chi chi_minus_1 local_speed shift1 rho_req}"
  : "${PROJECTION_FIELDS:=scalar_activity phi}"
else
  : "${FRAMES_FIELDS:=lump_activity scalar_activity phi_lump_sum Pi_lump_sum chi chi_minus_1 local_speed shift1 rho_req}"
  : "${PROJECTION_FIELDS:=scalar_activity}"
fi

# ---- GRTresna elliptic solve -------------------------------------------------
# Retrofitted 2026-08-26 from the bondi-dipole campaign findings (wrapper
# README rules 1/8/9, research/bondi_dipole/docs/MatterDebugg.md).  Every
# value below is env-overridable, but the DEFAULTS are the corrected ones:
# aligned uniform solve, tightened tolerances, one slicing for every
# candidate, and a genuine-convergence gate.  Overriding any of them back to
# the pre-fix values is a deliberate, visible act.
#
# RANKS is the "use more cores" knob for the bigger aligned solves: 8 ranks at
# N=256 was re-verified 2026-08-19 digit-identical to 1 rank and 6.6x faster
# (~46 min -> ~7 min).  Mind README rule 10: solves starve GPU evolutions
# through memory bandwidth, so cap RANKS x MAX_CONCURRENT_GRTRESNA while
# evolutions are in flight (with no evolution running, several solves may run
# together freely).
: "${RANKS:=8}"
: "${ITERATIONS:=50}"
# Rule 8: 1.0 (one percent) was the old throughput default and silently made
# every campaign a measurement of the error floor.  0.1% / 0.002 are the
# bondi-tightened values.
: "${GRTRESNA_NL_EXIT_TOLERANCE:=0.1}"
: "${GRTRESNA_NL_STALL_TOLERANCE:=0.002}"
: "${GRTRESNA_GRIDINIT_WORKERS:=0}"
# Rule 1: the solve must NOT refine -- refined solve cells re-enter the
# last-source-wins copy and displace the metric.
: "${GRTRESNA_MAX_LEVEL:=0}"
: "${GRTRESNA_REFINE_THRESHOLD:=0.5}"
: "${GRTRESNA_REGRID_RADIUS:=0}"
: "${GRTRESNA_JACOBIAN_CAP:=25.0}"
# Aligned 256^3 uniform solves are heavier than the old 64^3+AMR ones; the
# timeout scales with them (8 ranks at 256^3 measured ~7 min).
: "${GRTRESNA_TIMEOUT:=2400}"
: "${GRTRESNA_MAX_HAM_PCT:=5.0}"
: "${GRTRESNA_MAX_MOM_PCT:=5.0}"
# One construction method for EVERY candidate (K=0 maximal slicing + the
# exotic-safe relaxation), not a side effect of each candidate's exotic
# dials.  Without it, canonical-only candidates are born mid-collapse (CTTK
# K~sqrt(rho) birth kick) while phantom-bearing ones start at rest -- two
# construction methods in one archive.
: "${GRTRESNA_MAXIMAL_SLICING:=1}"
# Rule 8 gate: reject solves that exited by the stalled / iteration-cap door.
: "${GRTRESNA_REQUIRE_CONVERGED:=1}"
# Rule 1 rail: refuse to launch a misaligned solve (checked at startup by the
# CLI context AND per-solve by the runner).
: "${GRTRESNA_REQUIRE_ALIGNED_SOLVE:=1}"
export GRTRESNA_REQUIRE_ALIGNED_SOLVE

# ---- Evolution grid (dx = L_full / N_full = 64/128 = 0.5) ------------------
: "${GRTRESNA_EVOLUTION_L_FULL:=64.0}"
: "${GRTRESNA_EVOLUTION_N_FULL:=128}"
# GPU evolution AMR cap (QD/CMA-ES stage 0). GRTresna elliptic solve uses GRTRESNA_MAX_LEVEL.
: "${GRTRESNA_EVOLUTION_MAX_LEVEL:=1}"
# Chi-tagging refinement threshold for the GPU evolution (dx*|d2 chi| >= thr).
# Must stay high enough that a broad boson-shell chi well does NOT tag 100% of
# the domain: a full-domain Level 1 (256^3) blows up RK4 storeRKCoarseData and
# segfaults.  0.1 keeps refinement on the central collapse region (~4% of box).
: "${GRTRESNA_EVOLUTION_REGRID_THRESHOLD:=0.1}"
: "${GRTRESNA_DOMAIN_L:=128.0}"
# Rule 1: the solve cell must equal the evolution cell, so the default solve
# N is COMPUTED as N_full * (domain_L / L_full) -- 256 for the standard
# L=64/N=128 evolution solved in an L=128 box.  The old hard-coded 64 gave a
# solve dx of 2.0 against an evolution dx of 0.5: every lump was born off the
# centre of its own well and drifted for no physical reason.
if [[ -z "${GRTRESNA_DOMAIN_NX:-}" ]]; then
  GRTRESNA_DOMAIN_NX=$(awk -v n="${GRTRESNA_EVOLUTION_N_FULL}" \
    -v l="${GRTRESNA_EVOLUTION_L_FULL}" -v d="${GRTRESNA_DOMAIN_L}" \
    'BEGIN{printf "%d", (n * d / l) + 0.5}')
fi
: "${GRTRESNA_DOMAIN_NY:=${GRTRESNA_DOMAIN_NX}}"
# NZ stays empty by default: the domain mapper derives nx (full-z) or nx/2
# (half-z) so dz == dx either way.
: "${GRTRESNA_DOMAIN_NZ:=}"
: "${GRTRESNA_GRIDINIT_NX:=128}"
: "${GRTRESNA_GRIDINIT_NY:=128}"
: "${GRTRESNA_GRIDINIT_NZ:=128}"

# Full-z evolution box (shell ansatz); ring/free may override in legacy scripts.
if [[ -z "${GRTRESNA_FULL_Z+x}" ]]; then
  if [[ "${GRTRESNA_ANSATZ}" == "shell" || "${GRTRESNA_ANSATZ}" == "sh" || "${GRTRESNA_ANSATZ}" == "trajectory" || "${GRTRESNA_MATTER_SECTOR}" == "boson_star" ]]; then
    GRTRESNA_FULL_Z=1
  else
    GRTRESNA_FULL_Z=0
  fi
fi

# ---- Evolution time window ---------------------------------------------------
: "${STOP_TIME:=16.0}"
: "${PLOT_INTERVAL:=320}"

# ---- Pre-GPU solved-geometry FTL gate ----------------------------------------
: "${SOLVED_FTL_F_OP_FLOOR:=1.0e-4}"
: "${SOLVED_FTL_NEAR_LUMINAL_SPEED_FLOOR:=0.95}"
: "${SOLVED_FTL_SUPERLUMINAL_SPEED_FLOOR:=1.01}"
: "${SOLVED_FTL_SUPERLUMINAL_FRACTION_FLOOR:=0.02}"
: "${SOLVED_FTL_MAX_PHYSICAL_COORD_SPEED:=8.0}"
: "${SOLVED_FTL_MAX_PHYSICAL_F_OP:=0.85}"
: "${SOLVED_FTL_REJECTION_SPEED_TARGET:=1.01}"

# ---- Post-load constraint gate (GRTeclyn after gridinit load) ----------------
: "${POSTLOAD_GATE:=1}"
: "${POSTLOAD_MAX_HAM_L2:=1e-2}"
: "${POSTLOAD_MAX_MOM_L2:=1e-2}"
export POSTLOAD_GATE

: "${GRTRESNA_KEEP_SOURCE:=0}"

# ---- Plotfile consumer / FTL probes ------------------------------------------
: "${CONSUMER_RADII:=4 8}"
: "${CONSUMER_KEEP_LAST:=3}"
: "${FTL_L:=8.0}"
: "${OBJECTIVE_MODE:=general_ftl}"

# ---- 4D evolving null-geodesic (search profile) ------------------------------
export GRTECLYN_FRAMES="${GRTECLYN_FRAMES:-0}"
export GRTECLYN_EVOLVING_GEODESIC_MODE="${GRTECLYN_EVOLVING_GEODESIC_MODE:-search}"
export GRTECLYN_METRIC_STACK_N_SPACE="${GRTECLYN_METRIC_STACK_N_SPACE:-33}"
# Always probe all 3 principal axes -- blind search across directions.
export GRTECLYN_GEO_DIRECTIONS="${GRTECLYN_GEO_DIRECTIONS:-x y z}"
if [[ "${OBJECTIVE_MODE}" == "critical_collapse" ]]; then
  export GRTECLYN_EVOLVING_GEODESIC=0
  export GRTECLYN_CENTRAL_TIMESERIES=1
  export GRTECLYN_CENTRAL_BALL=1
  export GRTECLYN_CENTRAL_RADIAL=1
  export GRTECLYN_INCREMENTAL_SCORE=1
  export GRTECLYN_SPLASH_EARLY_TERM=1
  export SPLASH_MODE="${SPLASH_MODE:-discovery}"
  export GRTRESNA_MATTER_COUPLING=canonical
  export GRTRESNA_MATTER_SECTOR=boson_star
  export GRTRESNA_ANSATZ=shell
  export PIN_DIMS="${PIN_DIMS:-grtresna_scalar_sign=1}"
  # Splash QD: no projections unless caller sets PROJECTION_FIELDS (frames usually off).
  : "${PROJECTION_FIELDS:=}"
else
  export GRTECLYN_EVOLVING_GEODESIC="${GRTECLYN_EVOLVING_GEODESIC:-1}"
fi
export GRTECLYN_FRAMES_FIELDS="${FRAMES_FIELDS:-lump_activity scalar_activity phi_lump_sum Pi_lump_sum chi chi_minus_1 local_speed shift1 rho_req}"
export GRTECLYN_PROJECTION_FIELDS="${PROJECTION_FIELDS:-scalar_activity}"
export GRTECLYN_PROJECTION_AXES="${PROJECTION_AXES:-x y z}"
export GRTECLYN_PROJECTION_METHOD="${PROJECTION_METHOD:-mip}"

# ---- Shared CLI argument bundles (call after PYTHON_BIN / WRAPPER_ROOT set) --

ftl_search_common_domain_args() {
  FTL_DOMAIN_ARGS=(
    --grtresna-evolution-l-full "${GRTRESNA_EVOLUTION_L_FULL}"
    --grtresna-evolution-n-full "${GRTRESNA_EVOLUTION_N_FULL}"
    --grtresna-domain-l "${GRTRESNA_DOMAIN_L}"
    --grtresna-domain-nx "${GRTRESNA_DOMAIN_NX}"
    --grtresna-domain-ny "${GRTRESNA_DOMAIN_NY}"
    --grtresna-gridinit-nx "${GRTRESNA_GRIDINIT_NX}"
    --grtresna-gridinit-ny "${GRTRESNA_GRIDINIT_NY}"
    --grtresna-gridinit-nz "${GRTRESNA_GRIDINIT_NZ}"
  )
  if [[ -n "${GRTRESNA_DOMAIN_NZ}" ]]; then
    FTL_DOMAIN_ARGS+=(--grtresna-domain-nz "${GRTRESNA_DOMAIN_NZ}")
  fi
}

ftl_search_common_grtresna_args() {
  FTL_GRTRESNA_ARGS=(
    --grtresna
    --grtresna-ansatz "${GRTRESNA_ANSATZ}"
    --grtresna-matter-sector "${GRTRESNA_MATTER_SECTOR}"
    --grtresna-matter-coupling "${GRTRESNA_MATTER_COUPLING}"
    --grtresna-shell-profile "${SHELL_PROFILE}"
    --grtresna-lumps "${LUMPS}"
    "$([[ "${GRTRESNA_FULL_Z}" == "1" ]] && echo --grtresna-full-z || echo --no-grtresna-full-z)"
    "${FTL_DOMAIN_ARGS[@]}"
    --grtresna-ranks "${RANKS}"
    --grtresna-iterations "${ITERATIONS}"
    --grtresna-nl-exit-tolerance "${GRTRESNA_NL_EXIT_TOLERANCE}"
    --grtresna-nl-stall-tolerance "${GRTRESNA_NL_STALL_TOLERANCE}"
    --grtresna-gridinit-workers "${GRTRESNA_GRIDINIT_WORKERS}"
    --grtresna-timeout "${GRTRESNA_TIMEOUT}"
    --grtresna-max-level "${GRTRESNA_MAX_LEVEL}"
    --grtresna-refine-threshold "${GRTRESNA_REFINE_THRESHOLD}"
    --grtresna-regrid-radius "${GRTRESNA_REGRID_RADIUS}"
    --grtresna-jacobian-cap "${GRTRESNA_JACOBIAN_CAP}"
    "$([[ "${GRTRESNA_MAXIMAL_SLICING}" == "1" ]] && echo --grtresna-maximal-slicing || echo --no-grtresna-maximal-slicing)"
    "$([[ "${GRTRESNA_REQUIRE_CONVERGED}" == "1" ]] && echo --grtresna-require-converged || echo --no-grtresna-require-converged)"
    --grtresna-max-ham-pct "${GRTRESNA_MAX_HAM_PCT}"
    --grtresna-max-mom-pct "${GRTRESNA_MAX_MOM_PCT}"
    --solved-ftl-f-op-floor "${SOLVED_FTL_F_OP_FLOOR}"
    --solved-ftl-near-luminal-speed-floor "${SOLVED_FTL_NEAR_LUMINAL_SPEED_FLOOR}"
    --solved-ftl-superluminal-speed-floor "${SOLVED_FTL_SUPERLUMINAL_SPEED_FLOOR}"
    --solved-ftl-superluminal-fraction-floor "${SOLVED_FTL_SUPERLUMINAL_FRACTION_FLOOR}"
    --solved-ftl-max-physical-coord-speed "${SOLVED_FTL_MAX_PHYSICAL_COORD_SPEED}"
    --solved-ftl-max-physical-f-op "${SOLVED_FTL_MAX_PHYSICAL_F_OP}"
    --solved-ftl-rejection-speed-target "${SOLVED_FTL_REJECTION_SPEED_TARGET}"
  )
  # Boson stars are centered matter blobs without t=0 warp precursors; skip the
  # coordinate solved-FTL gate (same rationale as general_ftl / critical_collapse).
  if [[ "${OBJECTIVE_MODE}" == "general_ftl" ]] \
    || [[ "${OBJECTIVE_MODE}" == "critical_collapse" ]] \
    || [[ "${GRTRESNA_MATTER_SECTOR}" == "boson_star" ]]; then
    FTL_GRTRESNA_ARGS+=(--no-grtresna-solved-ftl-gate)
  fi
  if [[ "${POSTLOAD_GATE}" == "1" ]]; then
    FTL_GRTRESNA_ARGS+=(
      --grtresna-postload-gate
      --postload-max-ham-l2 "${POSTLOAD_MAX_HAM_L2}"
      --postload-max-mom-l2 "${POSTLOAD_MAX_MOM_L2}"
    )
  fi
  if [[ "${GRTRESNA_KEEP_SOURCE}" == "1" ]]; then
    FTL_GRTRESNA_ARGS+=(--grtresna-keep-source)
  fi
}

ftl_search_common_global_args() {
  FTL_GLOBAL_ARGS=(
    --example RadialRecipe
    --set "stop_time=${STOP_TIME}"
    --set "plot_interval=${PLOT_INTERVAL}"
    --set "max_level=${GRTRESNA_EVOLUTION_MAX_LEVEL}"
    --set "regrid_threshold=${GRTRESNA_EVOLUTION_REGRID_THRESHOLD}"
    --consume-plotfiles
    --consumer-delete
    --consumer-keep-last "${CONSUMER_KEEP_LAST}"
    --consumer-radii ${CONSUMER_RADII}
    --ftl-L "${FTL_L}"
  )
}

ftl_search_common_pipeline_args() {
  : "${GPU_SLOTS_PER_DEVICE:=1}"
  : "${CLUSTER_CPU_FRACTION:=0.30}"
  : "${PIPELINE_CPU_SHARE:=1.0}"
  : "${MAX_CONCURRENT_GRTRESNA:=0}"
  : "${USE_PIPELINE:=1}"
  FTL_PIPELINE_ARGS=(
    --gpu-slots-per-device "${GPU_SLOTS_PER_DEVICE}"
    --cluster-cpu-fraction "${CLUSTER_CPU_FRACTION}"
    --pipeline-cpu-share "${PIPELINE_CPU_SHARE}"
    --max-concurrent-grtresna "${MAX_CONCURRENT_GRTRESNA}"
  )
  if [[ "${USE_PIPELINE}" == "0" ]]; then
    FTL_PIPELINE_ARGS+=(--no-pipeline)
  fi
}

ftl_search_common_preflight_tests() {
  echo "Running FTL search preflight pytest gate..."
  local -a PREFLIGHT_TESTS=(
    "${WRAPPER_ROOT}/tests/grtresna/test_grtresna_h5py_dep.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_scalar_lambda_potential.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_grtresna_shell_ansatz.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_boson_star_ansatz.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_matter_selection.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_matter_geometry_consistency.py"
    "${WRAPPER_ROOT}/tests/search/test_ftl_retention.py"
    "${WRAPPER_ROOT}/tests/search/test_optimize_retention.py"
    "${WRAPPER_ROOT}/tests/metrics/ftl/test_ftl_peak_metrics.py"
    "${WRAPPER_ROOT}/tests/metrics/score/test_general_ftl_objective.py"
    "${WRAPPER_ROOT}/tests/metrics/diagnostics/test_central_timeseries_parser.py"
    "${WRAPPER_ROOT}/tests/metrics/score/test_splash_components.py"
    "${WRAPPER_ROOT}/tests/metrics/score/test_critical_collapse_objective.py"
    "${WRAPPER_ROOT}/tests/metrics/score/test_scorer_splash_integration.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_boson_splash_search_space.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_boson_shell_ansatz.py"
    "${WRAPPER_ROOT}/tests/search/test_splash_descriptors.py"
    "${WRAPPER_ROOT}/tests/scripts/test_splash_campaign_env.py"
    "${WRAPPER_ROOT}/tests/core/test_plot_consumer_flags.py"
    "${WRAPPER_ROOT}/tests/metrics/test_splash_early_term.py"
    "${WRAPPER_ROOT}/tests/grtresna/test_splash_wiring.py"
    "${WRAPPER_ROOT}/tests/metrics/diagnostics/test_central_radial_profile.py"
  )
  if [[ "${OBJECTIVE_MODE}" != "critical_collapse" ]]; then
    PREFLIGHT_TESTS+=(
      "${WRAPPER_ROOT}/tests/search/test_descriptors_4d.py"
      "${WRAPPER_ROOT}/tests/search/test_qd_4d_smoke.py"
      "${WRAPPER_ROOT}/tests/metrics/ftl/test_ftl_peak_metrics_4d.py"
      "${WRAPPER_ROOT}/tests/metrics/ftl/test_evolving_geodesic_search_mode.py"
      "${WRAPPER_ROOT}/tests/metrics/score/test_ftl_4d_gate.py"
    )
  fi
  if [[ "${GRTRESNA_ANSATZ}" == "trajectory" ]]; then
    PREFLIGHT_TESTS+=(
      "${WRAPPER_ROOT}/tests/grtresna/test_grtresna_trajectory_ansatz.py"
      "${WRAPPER_ROOT}/tests/grtresna/test_trajectory_boson_ansatz.py"
      "${WRAPPER_ROOT}/tests/search/test_trajectory_speed_cap.py"
    )
  fi
  ${PYTHON_BIN} -m pytest "${PREFLIGHT_TESTS[@]}" -q --tb=short
}
