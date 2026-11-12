#!/usr/bin/env bash
# Invoke through capped_job.sh after the CMA study's run-specific go.
set -euo pipefail
{
    py=grteclyn-wrapper/.venv/bin/python
    source_field=runs/railgun/single-ring/scans/ergoregion-amplitude-20261102-r2/amplitude_01/accepted.npz
    out=runs/railgun/single-ring/scans/ergoregion-cma-20261102
    report=runs/railgun/checks/ergoregion-cma-20261102.xml
    [[ ! -e "$out" && ! -e "$report" ]] || { echo 'Existing evidence; choose a new approved run.'; exit 2; }
    card_uuid=$(nvidia-smi --id=0 --query-gpu=uuid --format=csv,noheader)
    processes=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
    if [[ "$processes" == *"$card_uuid"* ]]; then
        echo 'GPU 0 is occupied; nothing started.'
        exit 2
    fi
    nvidia-smi --id=0
    df -h /tmp/grteclyn_scratch
    du -sh /tmp/grteclyn_scratch/*
    mkdir -p runs/railgun/checks
    "$py" -m grteclyn_stationary.railgun.ergoregion_cma \
        grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_cma.json --source "$source_field" \
        --out "$out" --gpu 0 --dry-run > "${report%.xml}-plan.json"
    export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 WH_JAC_CHUNK=128
    export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
    export MPLCONFIGDIR=/tmp/grteclyn_mpl
    "$py" -m pytest -q --junitxml="$report" \
        grteclyn-wrapper/tests/stationary/test_railgun_ergoregion_cma.py \
        grteclyn-wrapper/tests/stationary/test_railgun_ergoregion_scan.py \
        grteclyn-wrapper/tests/stationary/test_railgun_frequency.py \
        grteclyn-wrapper/tests/stationary/test_railgun_geometry.py \
        grteclyn-wrapper/tests/stationary/test_railgun_diagnostics.py
    exec "$py" -u -m grteclyn_stationary.railgun.ergoregion_cma \
        grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_cma.json --source "$source_field" --out "$out" --gpu 0
}
