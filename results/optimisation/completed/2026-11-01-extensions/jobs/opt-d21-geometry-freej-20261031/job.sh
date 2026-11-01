#!/usr/bin/env bash
cd . || exit 97
ulimit -v 230686720
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4
export XLA_FLAGS="--xla_force_host_platform_device_count=1 --xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
echo "[capped_job] start $(date -u +%FT%TZ) threads=4 mem=220G timeout=14400s"
timeout --signal=TERM --kill-after=30 14400 env PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/grteclyn_scratch/_cache/mpl grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.commands.optimize_potential results/spinningwormhole/solutions/fam_a_r1/fam_a_r1_0000.json --study-config research/optimisation/studies/d21_geometry_free_spin.toml --study-case potential-t4 --free-J --J-min 0 --J-max 7.7 --J-step 0.5 --x0 0.5209548187006455\,-0.2537873286726195\,-0.21830120946972714\,0.40780816120814567 --m-min 0.005 --m-max 1.2 --m-step 0.1 --q-min -2 --q-max 8 --nx 150 --ny 30 --engine cma --maxfev 200 --seed 211 --gpu 0 --jac-chunk 512 --out runs/optimisation/geometry_20261031 
code=$?
echo "[capped_job] end $(date -u +%FT%TZ) exit=$code"
echo "$code" > runs/capped_jobs/opt-d21-geometry-freej-20261031/exit_code
