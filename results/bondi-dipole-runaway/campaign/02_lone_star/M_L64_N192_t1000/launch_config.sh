#!/usr/bin/env bash
# M_L64_N192_t1000: the paper's M-t1000 (control_lone_phantom_t1000_L64_N128_lev0, the negative-mass star 5 units off
# centre carried to t 1000) on the RK-fixed binary (c12664fd), at N 192, 2026-10-24.  N 192 over the paper's N 128:
# at t 200 the star's peak field moves +0.001 % at N 192 and -0.13 % at N 128, and the paper's N 128 run lost 5.4 % of
# its peak by t 1000, so the change over t 1000 is read without the grid's drift.
# Initial data: M at N 192's solve (09_convergence/M_L64_N192), so no solve, and the run repeats M_L64_N192 to t 200;
# rl_pump_target_amp is set here because a gridinit run does not restore it (as M_L64_N256).
# Otherwise M_L64_N192: box, star, offset, sponge, gauge, dt.  Plotfiles every 4 units (600 steps), the paper's
# t 1000 cadence, so the consumer keeps up with frames.  Frames on with the slice cache.  No checkpoints.  Card 0 of
# the first node.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 RL_PUMP_TARGET_WIDTH=0.26748955019623744 \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GRIDINIT="${REPO}/runs/bondi/09_convergence/M_L64_N192/bondi_sg_single_m_w07603/initial_data.gridinit" \
BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_GPU=0 BONDI_STOP_TIME=1000 BONDI_NFULL=192 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=600 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.000395 BONDI_NL_STALL_TOL=7.9e-06 \
BONDI_GRTRESNA_MAXIMAL_SLICING=1 \
BONDI_EXOTIC=1 BONDI_OMEGA=0.7603 \
BONDI_GRTRESNA_N=384 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=8 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/M_L64_N192_t1000}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_single_selfgrav.sh"
