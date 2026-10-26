#!/usr/bin/env bash
# M_L64_N256: the paper's control_lone_phantom_L64_N128_lev0 (the negative-mass star 5 units off centre, t 200) at
# N 256, for the single-star convergence study, on the RK-fixed binary (c12664fd).  It evolves the initial data that
# the first launch solved on 2026-10-23 (11_initial_data/M_L64_N256_initial_data).  That solve stopped at its
# discretisation floor, Ham 2.5e-4 % against the dx^4-scaled request of 1.25e-4 %: the floor falls only as ~dx^1.5
# (7.2e-4 % at N 128, 3.9e-4 % at N 192), so the gate (rule 8) rejected it, and the evolution reuses its gridinit as
# decided 2026-10-23.  Otherwise the first launch: box, star, offset, sponge, gauge, dt, plot cadence (0.8), stop time.
# Frames off, no checkpoints.  rl_pump_target_amp is set here: a gridinit run restores only EVOLUTION_MATTER_KEYS,
# which lack it, and N 128 and N 192 ran with 0.08 (the star's phi_c; the pump is off from t 0).
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=0 RL_PUMP_TARGET_WIDTH=0.26748955019623744 \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_GRIDINIT="${REPO}/runs/bondi/11_initial_data/M_L64_N256_initial_data/bondi_sg_single_m_w07603/initial_data.gridinit" \
BONDI_GPU=0 BONDI_STOP_TIME=200 BONDI_NFULL=256 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=160 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.000125 BONDI_NL_STALL_TOL=2.5e-06 \
BONDI_GRTRESNA_MAXIMAL_SLICING=1 \
BONDI_EXOTIC=1 BONDI_OMEGA=0.7603 \
BONDI_GRTRESNA_N=512 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=8 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/M_L64_N256}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_single_selfgrav.sh"
