#!/usr/bin/env bash
# Execute under capped_job.sh after the separate stationary-refinement go.
{
set -euo pipefail
CARD="${1:?GPU card required}" OUT="${2:?New output directory required}"
[[ "${CARD}" == 0 || "${CARD}" == 1 ]] || exit 2
[[ ! -e "${OUT}" ]] || { echo 'Existing evidence is immutable.' >&2; exit 2; }
PY=grteclyn-wrapper/.venv/bin/python
UUID=$(nvidia-smi --id="${CARD}" --query-gpu=uuid --format=csv,noheader)
PROCESSES=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
[[ "${PROCESSES}" != *"${UUID}"* ]] || { echo "GPU ${CARD} is occupied; nothing started." >&2; exit 2; }
nvidia-smi --id="${CARD}"
df -h /tmp/grteclyn_scratch
du -sh /tmp/grteclyn_scratch/*
mkdir -p runs/railgun/checks
REPORT="runs/railgun/checks/$(basename -- "${OUT}")"
[[ ! -e "${REPORT}.xml" ]] || { echo 'Existing test evidence is immutable.' >&2; exit 2; }
"${PY}" -m grteclyn_wrapper.optimisation.railgun.evolution_source_refinement \
  --dry-run > "${REPORT}-plan.json"
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="${CARD}" WH_JAC_CHUNK=128
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
"${PY}" -m pytest -q --junitxml="${REPORT}.xml" \
  grteclyn-wrapper/tests/optimisation/test_railgun_source_refinement.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_geometry.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_evolution.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_interpolation.py
exec "${PY}" -u -m grteclyn_wrapper.optimisation.railgun.evolution_source_refinement \
  --gpu "${CARD}" --out "${OUT}"
}
