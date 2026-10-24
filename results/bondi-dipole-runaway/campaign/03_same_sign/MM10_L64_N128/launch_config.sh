#!/usr/bin/env bash
# MM10_L64_N128: the paper's control_pair_mm_d10_L64_N128_lev0 and _frames (MM10: two negative-mass stars 10 apart; one run with frames for both v1 runs) on the RK-fixed binary (c12664fd), with fresh initial data from
# the fixed pipeline (GRTresna_bondi_fix, the joined star lapse, the converter's face-layer fix), 2026-10-24.
# Otherwise the paper's run: grid, stars, separation, sponge, gauge, dt, plot cadence, stop time, solve grid and
# tolerances; the solve runs on fewer ranks (32 before), which does not change it.
# Frames on with the slice cache, as in the paper's run (its movie).  No checkpoints.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 \
RL_PUMP_TARGET_WIDTH=0.26748955019623744 BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GPU=0 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_S0=1 BONDI_S1=1 BONDI_S0_OMEGA=0.7603 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=4 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/MM10_L64_N128}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
