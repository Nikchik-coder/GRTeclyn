#!/usr/bin/env bash
# Restart from the stronger accepted field after a separate campaign go.
set -euo pipefail
{
    case "${1-}" in
        0) card=0; seed=271 ;;
        1) card=1; seed=272 ;;
        *) echo 'Select card 0 (seed 271) or card 1 (seed 272).'; exit 2 ;;
    esac
    py=grteclyn-wrapper/.venv/bin/python
    source_field=results/railgun/studies/ergoregion-max-validate271/finalists/01/accepted.npz
    config="grteclyn-wrapper/scripts/campaigns/railgun/configs/ergoregion_max_r2_seed${seed}.json"
    out="runs/railgun/single-ring/scans/ergoregion-max-r2-seed${seed}-20261102"
    report="runs/railgun/checks/ergoregion-max-r2-seed${seed}-20261102.xml"
    [[ ! -e "$out" && ! -e "$report" ]] || { echo 'Existing evidence; select a new approved run.'; exit 2; }
    uuid=$(nvidia-smi --id="$card" --query-gpu=uuid --format=csv,noheader)
    processes=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
    [[ "$processes" != *"$uuid"* ]] || { echo "GPU $card occupied; nothing started."; exit 2; }
    nvidia-smi --id="$card"
    df -h /tmp/grteclyn_scratch
    du -sh /tmp/grteclyn_scratch/*
    mkdir -p runs/railgun/checks
    "$py" -m grteclyn_stationary.railgun.ergoregion_cma "$config" \
        --source "$source_field" --out "$out" --gpu "$card" --dry-run > "${report%.xml}-plan.json"
    export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="$card" WH_JAC_CHUNK=128
    export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
    export MPLCONFIGDIR="/tmp/grteclyn_mpl_${card}"
    "$py" -m pytest -q --junitxml="$report" \
        grteclyn-wrapper/tests/stationary/test_railgun_ergoregion_cma.py \
        grteclyn-wrapper/tests/stationary/test_railgun_ergoregion_scan.py \
        grteclyn-wrapper/tests/stationary/test_railgun_frequency.py \
        grteclyn-wrapper/tests/stationary/test_railgun_geometry.py \
        grteclyn-wrapper/tests/stationary/test_railgun_diagnostics.py
    exec "$py" -u -m grteclyn_stationary.railgun.ergoregion_cma "$config" \
        --source "$source_field" --out "$out" --gpu "$card"
}
