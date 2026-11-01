#!/usr/bin/env bash
cd . || exit 97
ulimit -v 209715200
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4
export XLA_FLAGS="--xla_force_host_platform_device_count=1 --xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
echo "[capped_job] start $(date -u +%FT%TZ) threads=4 mem=200G timeout=28800s"
timeout --signal=TERM --kill-after=30 28800 env QUEUE_GPU_MEM_MAX_MB=100 QUEUE_IDLE_EXIT=1 QUEUE_POLL_SEC=30 bash grteclyn-wrapper/scripts/campaigns/lib/gpu_queue.sh runs/optimisation/signchanging_20261031/queue 0 1 
code=$?
echo "[capped_job] end $(date -u +%FT%TZ) exit=$code"
echo "$code" > runs/capped_jobs/opt-signed-potential-queue-20261031/exit_code
