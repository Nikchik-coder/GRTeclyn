#!/usr/bin/env bash
# Entire worker is read before execution, so later Git pulls cannot splice it.
{
set -euo pipefail
card="${1:?GPU required}"; out="${2:?output required}"
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="$card" JAX_ENABLE_X64=true
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false WH_JAC_CHUNK=256
PY=grteclyn-wrapper/.venv/bin/python
"$PY" -m pytest -q grteclyn-wrapper/tests/stationary/test_railgun_throat.py \
    grteclyn-wrapper/tests/stationary/test_fixed_area_study.py \
    grteclyn-wrapper/tests/stationary/test_wormhole_ring_study.py
exec "$PY" -u -m grteclyn_stationary.ringwormhole.workflow \
    --config grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat.json --out "$out" --gpu "$card" --run
}
