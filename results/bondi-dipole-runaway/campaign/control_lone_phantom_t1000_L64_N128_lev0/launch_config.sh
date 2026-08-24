#!/usr/bin/env bash
# Referee response, run B: the lone phantom carried to t=1000.  Same cell as
# control_lone_phantom_L64_N128_lev0 (off-centre star, the sharper null), five
# times longer, with a fresh solve at the same settings (archived gridinit was
# pruned).  Plot cadence raised 80 -> 400 and a rolling checkpoint switched on:
# five times longer than anything else in the campaign, and the default cadence
# would have the frame consumer falling behind the GPU.
#
# GATE.  Peak field activity flat to ~1% over the full 1000 (holds to 0.5%
# over 200), min lapse / min chi steady, core drift in the few x 1e-03 band the
# t=200 cell established.  Pass -> the abstract's stability sentence goes back
# to 1000 units.  Fail -> the softened t=400 wording stands, and WHEN it breaks
# is itself a result.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
BONDI_GPU=2 BONDI_STOP_TIME=1000 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=400 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_GRTRESNA_MAXIMAL_SLICING=1 \
BONDI_EXOTIC=1 BONDI_OMEGA=0.7603 \
BONDI_CHECKPOINT_INTERVAL=40000 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=32 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/control_lone_phantom_t1000_L64_N128_lev0" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_single_selfgrav.sh"
