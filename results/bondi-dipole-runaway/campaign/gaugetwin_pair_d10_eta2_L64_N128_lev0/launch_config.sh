#!/usr/bin/env bash
# Referee response, run A: the gauge twin.  The headline N=128 cell with ONE
# parameter changed -- Gamma-driver damping doubled via BONDI_EXTRA="eta=2.0".
# Everything else is byte-identical to runaway_pair_d10_L64_N128_lev0's launch,
# including a fresh elliptic solve with the same tolerances (the archived
# gridinit was pruned, and the solve is deterministic at fixed settings).
#
# GATE.  Drift and fitted a within a few percent of +2.8815 / 1.4481e-04:
# under ~2% closes major 1 by run ("gauge-limited? no"); a double-digit shift
# means the headline needs a gauge-spread error bar -- a real finding either way.
#
# CHECK FIRST.  grep eta <cell>/evolution_params.txt must show 2.0 before a
# null result is trusted: a knob that silently did nothing reproduces the
# original perfectly.
set -euo pipefail
REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "${REPO}"
BONDI_GPU=1 BONDI_STOP_TIME=200 BONDI_NFULL=128 BONDI_LFULL=64 BONDI_MAXLEVEL=0 \
BONDI_PLOT_INTERVAL=80 BONDI_SCRUTINY=1 BONDI_SPONGE=1 BONDI_SEP=10 \
BONDI_NL_TOL=0.002 BONDI_NL_STALL_TOL=0.00004 \
BONDI_S0=0 BONDI_S1=1 BONDI_S0_OMEGA=0.75 BONDI_S1_OMEGA=0.7603 \
BONDI_EXTRA="eta=2.0" \
BONDI_GRTRESNA_N=256 BONDI_GRTRESNA_MAXLEVEL=0 BONDI_GRTRESNA_RANKS=32 BONDI_GRTRESNA_TIMEOUT=21600 \
BONDI_RUNS_DIR="${REPO}/runs/bondi/staging/gaugetwin_pair_d10_eta2_L64_N128_lev0" \
  bash "${REPO}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh"
