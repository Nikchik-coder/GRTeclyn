#!/usr/bin/env bash
# Mass law, cell for M = 0.009156 (0.639 x the headline star).
#
# WHY.  The campaign measures a(d) at fixed mass across five separations and
# a(M) only through UNEQUAL-mass pairs.  The equal-mass law it actually wants
# to quote -- a = M / d^2, both stars, same direction -- has therefore never
# been varied in M at all: every equal-|ADM| cell in the pack sits at the one
# mass 0.014350.  This cell and its two siblings put three more equal-mass
# points on the same line, so the exponent in a ~ M^p is fitted rather than
# assumed.
#
# WHY d = 20.  The stars have r99 ~ 5.3-5.9 over this whole mass range, so at
# d = 20 the two 99.9%-mass spheres are still ~4 apart and the overlap excess
# that inflates a at close range is dead: the packed separation series reads
# a*d^2/M = 1.031, 1.011, 1.003, 1.001, 1.002 at d = 8, 10, 12, 16, 20.  It is
# also the one separation where the existing 0.75/0.7603 cell already sits, so
# that cell is the fourth point of this series for free -- same d, same grid,
# same solve, same fit window, nothing to cross-calibrate.
#
# THE PAIRING.  omega_canonical = 0.850 gives M = +0.009156; the phantom
# partner was root-found to omega = 0.859095, matching |ADM| to +0.018%
# (the packed 0.75/0.7603 pair is matched to -0.39%, so this is tighter than
# the series it joins).
#
# GATE.  a*d^2/M within a few percent of 1.00, as the packed d=20 cell reads
# 1.002.  Expected a ~ 2.29e-05 and drift ~ +0.46 over t = 200, several
# hundred times the single-star noise floor.  The deliverable is not this cell
# alone but the four-point slope: p = 1 confirms the law, p far from 1 says the
# acceleration is not simply proportional to mass and the paper must say so.
#
# CHECK FIRST.  omega 0.850 is outside the band the stability scan covered
# (0.75-0.90), so read the matter diagnostics before the geometry: peak
# amplitude and confined fraction steady against this run's own t = 0, per
# rule 3.  A star that is quietly rearranging invalidates its own a.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
GRTECLYN_FRAMES=0 \
BONDI_GPU=3 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=20 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.850 BONDI_S1_OMEGA=0.859095 \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=32 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/masslaw_pair_d20_w0850_L64_N128_lev0" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
