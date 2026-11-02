#!/usr/bin/env bash
# Invoke through capped_job.sh only after the run-specific go.
set -euo pipefail
{
    py=grteclyn-wrapper/.venv/bin/python
    out=runs/railgun/single-ring/scans/ergoregion-amplitude-20261102
    report=runs/railgun/checks/ergoregion-amplitude-20261102.xml
    resume_args=()
    if [[ $# -eq 1 && "$1" == '--resume-bootstrap' ]]; then
        resume_args=(--resume-bootstrap "$out")
        out="${out}-r2"
        report=runs/railgun/checks/ergoregion-amplitude-r2-20261102.xml
    elif [[ $# -ne 0 ]]; then
        echo 'Expected no arguments or --resume-bootstrap.'
        exit 2
    fi
    [[ ! -e "$out" && ! -e "$report" ]] || { echo 'Existing evidence: choose a new approved run.'; exit 2; }
    card_uuid=$(nvidia-smi --id=0 --query-gpu=uuid --format=csv,noheader)
    processes=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
    if [[ "$processes" == *"$card_uuid"* ]]; then
        echo 'GPU 0 is occupied; no tests or solves started.'
        exit 2
    fi
    nvidia-smi --id=0
    df -h /tmp/grteclyn_scratch
    du -sh /tmp/grteclyn_scratch/*
    export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 WH_JAC_CHUNK=128
    export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
    mkdir -p runs/railgun/checks
    "$py" -m pytest -q --junitxml="$report" \
        grteclyn-wrapper/tests/optimisation/test_railgun_ergoregion_scan.py \
        grteclyn-wrapper/tests/optimisation/test_railgun_frequency.py \
        grteclyn-wrapper/tests/optimisation/test_railgun_geometry.py \
        grteclyn-wrapper/tests/optimisation/test_railgun_diagnostics.py
    exec "$py" -u -m grteclyn_wrapper.optimisation.railgun.ergoregion_scan \
        research/railgun/studies/ergoregion_amplitude.json \
        --source results/railgun/studies/frequency-deep/frequency_01/accepted.npz \
        --out "$out" --gpu 0 "${resume_args[@]}"
}
