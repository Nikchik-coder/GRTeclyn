#!/bin/bash
# Treadmill-free control for the separation question.
#
#   Same solved initial data as the chase (byte-identical payload), declared to
#   sit 10 units further left via the gridinit header's origin -- an exact
#   relabelling of WHERE the initial state lives, done once at t=0, with no
#   shifting during the evolution.  The absorbing shell is pinned to the box
#   centre so it does NOT follow the pair.
#
#   Pair starts at x = 17 (phantom) and 27 (canonical); the leader runs out of
#   clean room near x = 52, i.e. t ~ 550.  No treadmill anywhere in this run.
#
#   Test: gap(t) here vs gap(t) in the chase over t = 400..550.  Agreement
#   clears the treadmill; divergence convicts it.
#
# Usage: bash launch_control.sh [GPU]     (default GPU 1)
set -euo pipefail
GPU="${1:-1}"
REPO="$GRTECLYN_ROOT"
CELL="${REPO}/runs/bondi/staging/nomill_left_pair_d10_L64_N128_lev0"
SCR="/tmp/grteclyn_scratch/nomill_left_pair_d10_L64_N128_lev0"
mkdir -p "${SCR}" "${CELL}/small_data" "${CELL}/frames"

# Consumer: renders frames, writes sector_dynamics.dat, deletes plotfiles.
setsid nohup grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.process_wave.consume_plotfiles --data /tmp/grteclyn_scratch/nomill_left_pair_d10_L64_N128_lev0 --out runs/bondi/staging/nomill_left_pair_d10_L64_N128_lev0/small_data --stop-sim-path runs/bondi/staging/nomill_left_pair_d10_L64_N128_lev0/.stop_sim --radii 8.0 16.0 --n-points 128 --center 32 32 32 --areal-radius -j 1 --verbose --watch --delete --keep-last 2 --ftl-timeseries --ftl-l 8 --confinement-timeseries --confinement-well-width 1.2 --sector-barycenters --matter-model grtresna_bicomplex_scalar --sector-dynamics --sector-dynamics-level 0 --incremental-score --objective-mode weighted --target-stop-time 600 --psi4 --shell-fields chi lapse K --frames-fields scalar_activity phi Pi phi_lump0 Pi_lump0 chi chi_minus_1 local_speed shift1 rho_req Weyl4_Re Weyl4_Im Weyl4_Mag --frames-axis z --frames-center 32 32 32 --frames-out runs/bondi/staging/nomill_left_pair_d10_L64_N128_lev0/frames --projection-fields scalar_activity phi --projection-axes x y z --projection-method mip > "${CELL}/consumer.log" 2>&1 &
echo "consumer pid $!" | tee "${CELL}/consumer.pid"

# Evolution.  Plain VAR=value prefix -- never 'env' (README rule 11).
CUDA_VISIBLE_DEVICES="${GPU}" \
setsid nohup "${REPO}/Examples/RadialRecipe/main3d.gnu.MPI.CUDA.ex" "${CELL}/params.txt" \
  > "${CELL}/run.log" 2>&1 &
echo "evolution pid $! on GPU ${GPU}" | tee "${CELL}/run.pid"
echo "monitor: tail -f ${CELL}/run.log"
