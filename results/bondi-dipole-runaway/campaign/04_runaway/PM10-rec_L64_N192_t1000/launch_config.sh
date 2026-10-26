#!/usr/bin/env bash
# PM10-rec_L64_N192_t1000: the paper's recentring chase (PM10-rec, v1 chase03c_pair_d10_L64_N128_lev0) at N 192 and
# to t 1000, on the RK-fixed binary (c12664fd), 2026-10-24.  An extra run, not for the paper.  The pair stays in the
# L 64 box while the grid follows it (treadmill: each 2-unit drift shifts the data by 6 cells, the trailing face is
# filled with the asymptotic 1/r tail, the sponge rides with the box), so it is followed to v ~ 0.14 c (~71 units
# travelled by t 1000) at the middle resolution, where the stars keep their matter.  An L 128 box at this spacing
# would need N 384 (~150 GB on the card).
# Initial data: PM10 at N 192's solve (11_initial_data/PM10_L64_N192_initial_data), so no solve, and the run repeats
# PM10_L64_N192 until the first shift (t ~ 170).  Otherwise PM10 at N 192: grid, stars, sponge, gauge, dt.  Plotfiles
# every 1.6 units (240 steps; PM10's 0.8) so the second node's consumer keeps up.  Frames on with the slice cache.
# No checkpoints.  Second node, card 0, launched by hand.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 \
RL_PUMP_TARGET_WIDTH=0.26748955019623744 BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GRIDINIT="${REPO}/runs/bondi/11_initial_data/PM10_L64_N192_initial_data/bondi_sg_pair_pm_eqm_w075/initial_data.gridinit" \
BONDI_GPU=0 BONDI_STOP_TIME=1000 BONDI_NFULL=192 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=240 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_TREADMILL=1 BONDI_TREADMILL_THRESHOLD=2.0 BONDI_TREADMILL_CHECK=20 BONDI_TREADMILL_BALL=8.0 BONDI_TREADMILL_FILL=0 \
BONDI_NL_TOL=0.000395 BONDI_NL_STALL_TOL=0.0000079 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_GRTRESNA_N=384 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=8 \
BONDI_GRTRESNA_TIMEOUT=43200 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/PM10-rec_L64_N192_t1000}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
