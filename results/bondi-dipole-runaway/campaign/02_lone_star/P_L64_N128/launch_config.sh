#!/usr/bin/env bash
# P_L64_N128: the paper's control_lone_canonical_L64_N128_lev0 (P, the positive-mass star of the reference pair,
# omega 0.75, alone at the box centre, t 200) on the RK-fixed binary (c12664fd) and the fixed solve pipeline
# (GRTresna_bondi_fix: matched matter, joined table lapse, converter's outer-layer fix), 2026-10-24.  Otherwise the
# paper's run: box, star, position, sponge, gauge, dt, plot cadence (0.8), stop time, solve grid and tolerances.
# It backs test v and Sec. III A for the positive star (decided 2026-10-24: P instead of S0.75-S0.90).
# Frames off, no checkpoints.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=0 RL_PUMP_TARGET_WIDTH=0.26748955019623744 \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_GPU=1 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=0 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=4e-05 \
BONDI_GRTRESNA_MAXIMAL_SLICING=1 \
BONDI_EXOTIC=0 BONDI_OMEGA=0.75 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=4 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/P_L64_N128}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_single_selfgrav.sh"
