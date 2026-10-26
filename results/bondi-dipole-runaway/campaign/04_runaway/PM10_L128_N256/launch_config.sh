#!/usr/bin/env bash
# PM10_L128_N256 (PM10-L128): the paper's wavezone_pair_d10_L128_N256_lev0 -- PM10 in the doubled box at the same
# cell size (dx 0.5), four extraction spheres -- on the RK-fixed binary (c12664fd) and fresh data from the fixed
# GRTresna (GRTresna_bondi_fix), 2026-10-23.  Otherwise the paper's run: box, stars, separation, sponge 48 -> 60,
# extraction at 16 24 32 40 with the higher-l modes, solve box 256 at 512, tolerance (dx as N 128 on L 64), gauge,
# dt, plot cadence (0.8), stop time.  12 solve ranks instead of 32 (the container's CPU quota is 24).
# Frames on with the slice cache, the whole box (no zoom), as decided 2026-10-23; no checkpoints.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTRESNA_ROOT="$(cd "${REPO}/.." && pwd)/GRTresna_bondi_fix" \
GRTECLYN_FRAMES=1 GRTECLYN_FRAMES_CACHE_SLICES=1 \
RL_PUMP_TARGET_WIDTH=0.26748955019623744 BONDI_EXTRA="rl_pump_target_amp=0.08 constraint_shells_dt=0.1" \
BONDI_BINARY="${REPO}/runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex" \
BONDI_GPU=1 BONDI_STOP_TIME=200 BONDI_NFULL=256 BONDI_LFULL=128 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_SPONGE_INNER=48 BONDI_SPONGE_OUTER=60 \
BONDI_RADII="16 24 32 40" BONDI_EXTRACTION_RADII="16 24 32 40" BONDI_PSI4_HIGHER_L=1 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_GRTRESNA_DOMAIN_L=256 BONDI_GRTRESNA_N=512 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=12 \
BONDI_GRTRESNA_TIMEOUT=43200 \
BONDI_RUNS_DIR="${BONDI_RUNS_DIR:-${REPO}/runs/bondi/staging/PM10_L128_N256}" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
