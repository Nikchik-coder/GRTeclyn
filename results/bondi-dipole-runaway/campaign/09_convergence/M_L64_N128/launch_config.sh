#!/usr/bin/env bash
# The paper's control_lone_phantom_L64_N128_lev0 (the negative-mass star 5 units off centre, t 200) at N 128, for the
# single-star convergence study (2026-10-23): the RK-fixed binary (c12664fd) and the fixed solve pipeline
# (GRTresna_bondi_fix: matched matter, joined table lapse, converter's outer-layer fix).  Otherwise the paper's run:
# box, star, offset, sponge, gauge, dt, plot cadence (0.8), stop time; the solve tolerance scales as dx^4.
# Frames off, no checkpoints.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=0 RL_PUMP_TARGET_WIDTH=0.26748955019623744 \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_EXTRA="constraint_shells_dt=0.1" \
BONDI_GPU=0 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=4e-05 \
BONDI_GRTRESNA_MAXIMAL_SLICING=1 \
BONDI_EXOTIC=1 BONDI_OMEGA=0.7603 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=8 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/rkfix_lone_m_L64_N128_lev0_t200" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_single_selfgrav.sh"
