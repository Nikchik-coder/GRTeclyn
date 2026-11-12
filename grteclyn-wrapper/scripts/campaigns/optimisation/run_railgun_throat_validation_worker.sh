#!/usr/bin/env bash
# Read the complete worker before execution, including during later Git pulls.
{
set -euo pipefail
card="${1:?GPU required}"; out="${2:?output required}"
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="$card" JAX_ENABLE_X64=true
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false WH_JAC_CHUNK=256
PY=grteclyn-wrapper/.venv/bin/python
"$PY" -c 'import json; from grteclyn_stationary.ringwormhole.workflow import read_restart; read_restart(json.load(open("grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat_validation.json")))'
"$PY" -m pytest -q grteclyn-wrapper/tests/stationary/test_railgun_throat.py \
    grteclyn-wrapper/tests/stationary/test_railgun_throat_validation.py \
    grteclyn-wrapper/tests/stationary/test_equilibration_memory.py \
    grteclyn-wrapper/tests/stationary/test_solver_core.py \
    grteclyn-wrapper/tests/stationary/test_fixed_area_study.py \
    grteclyn-wrapper/tests/stationary/test_wormhole_ring_study.py
exec "$PY" -u -m grteclyn_stationary.ringwormhole.workflow \
    --config grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat_validation.json --out "$out" --gpu "$card" --run
}
