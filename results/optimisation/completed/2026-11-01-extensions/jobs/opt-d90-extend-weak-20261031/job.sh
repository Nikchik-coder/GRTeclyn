#!/usr/bin/env bash
cd . || exit 97
ulimit -v 209715200
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4
export XLA_FLAGS="--xla_force_host_platform_device_count=1 --xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
echo "[capped_job] start $(date -u +%FT%TZ) threads=4 mem=200G timeout=14400s"
timeout --signal=TERM --kill-after=30 14400 env PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/grteclyn_scratch/_cache/mpl grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.commands.optimize_potential results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0031.json --x0 0.01\,0\,0\,0 --m-min 0 --m-max 0.20 --m-step 0.005 --nx 150 --ny 30 --engine cma --stall-ok 1e-9 --maxfev 800 --q-min -2 --q-max 8 --seed 227 --gpu 0 --refine-best final --out runs/optimisation/d90_extension_20261031/weak.tsv 
code=$?
echo "[capped_job] end $(date -u +%FT%TZ) exit=$code"
echo "$code" > runs/capped_jobs/opt-d90-extend-weak-20261031/exit_code
