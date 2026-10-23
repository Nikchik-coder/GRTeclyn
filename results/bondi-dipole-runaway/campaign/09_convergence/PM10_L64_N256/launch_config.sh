#!/usr/bin/env bash
# The paper's runaway_pair_d10_L64_N256_lev0 (PM10, t 200) on the RK-fixed binary (no FillPatch in specificEvalRHS,
# c12664fd) and the corrected data (facefix: joined lapse, repaired face layer), 2026-10-23.  Otherwise the paper's
# run: grid, stars, separation, sponge, gauge, dt, plot cadence, stop time.  Frames on with the slice cache, as
# in the paper's run (its figure cell).  No checkpoints.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 \
RL_PUMP_TARGET_WIDTH=0.26748955019623744 BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GRIDINIT="${REPO}/runs/bondi/staging/facefix_pair_d10_L64_N256_lev0/bondi_sg_pair_pm_eqm_w075/initial_data.gridinit" \
BONDI_GPU=1 BONDI_STOP_TIME=200 BONDI_NFULL=256 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=160 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.000125 BONDI_NL_STALL_TOL=0.0000025 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_GRTRESNA_N=512 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=12 \
BONDI_GRTRESNA_TIMEOUT=43200 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/rkfix_pair_d10_L64_N256_lev0_t200" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
