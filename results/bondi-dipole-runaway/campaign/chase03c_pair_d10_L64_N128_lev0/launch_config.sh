#!/bin/bash
# 0.3c chase: d=10 runaway pair, recentring box on, t=0..2400 ceiling, GPU 3;
# STOP BY HAND once treadmill.dat reads 0.3c (expected t~2100, ~11.5 h in).
# Initial data reused from the longrun cell (no elliptic solve).
# Checkpoint every 40000 steps (t=400,800,1200,1600,2000); keep Chk120000
# (t=1200) as the science point, prune the rest when the run is done.
# Detaches itself: survives closing this terminal.  Stop it with
#   scripts/campaigns/stop_campaign.sh  (or kill the PID in launcher.pid first).
# NB: plain VAR=value prefixes, deliberately not `env` -- some sandboxed shells
# stub `env` out and the launch dies silently.
CELL_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${CELL_DIR}/../../../.." && pwd)"
BONDI_GPU=3 \
BONDI_STOP_TIME=2400 \
BONDI_SEP=10 \
BONDI_S0_OMEGA=0.75 \
BONDI_S1_OMEGA=0.7603 \
BONDI_MAXLEVEL=0 \
BONDI_SPONGE=1 \
BONDI_PLOT_INTERVAL=400 \
BONDI_TREADMILL=1 \
BONDI_SCRUTINY=1 \
BONDI_GRIDINIT="${REPO_ROOT}/runs/bondi/staging/longrun_pair_d10_t400_L64_N128_lev0/bondi_sg_pair_pm_eqm_w075/initial_data.gridinit" \
BONDI_CHECKPOINT_INTERVAL=40000 \
BONDI_RUNS_DIR="${CELL_DIR}" \
setsid nohup bash "${REPO_ROOT}/grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh" \
  > "${CELL_DIR}/launch.log" 2>&1 &
echo "chase launched detached (pid $!), monitor: tail -f ${CELL_DIR}/launch.log"
