#!/usr/bin/env bash
{
set -euo pipefail
card="${1:?GPU required}"; out="${2:?output required}"
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="$card" JAX_ENABLE_X64=true
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false WH_JAC_CHUNK=256
PY=grteclyn-wrapper/.venv/bin/python
"$PY" -m pytest -q grteclyn-wrapper/tests/optimisation/test_ringwormhole_continuation.py \
    grteclyn-wrapper/tests/optimisation/test_railgun_throat_ergoregion.py \
    grteclyn-wrapper/tests/optimisation/test_railgun_throat.py \
    grteclyn-wrapper/tests/optimisation/test_railgun_throat_validation.py \
    grteclyn-wrapper/tests/optimisation/test_equilibration_memory.py \
    grteclyn-wrapper/tests/optimisation/test_solver_core.py \
    grteclyn-wrapper/tests/optimisation/test_fixed_area_study.py
exec "$PY" -u -m grteclyn_wrapper.optimisation.ringwormhole_continuation \
    --config grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108_continuation.json --out "$out" --gpu "$card" --run
}
