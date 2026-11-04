#!/usr/bin/env bash
# Run through capped_job.sh after the bounded metric-coefficient recovery go.
{
set -euo pipefail
CARD="${1:?GPU card required}" OUT="${2:?New output directory required}"
CONFIG="research/railgun/studies/ergoregion_smooth_spectral_372.json"
[[ "${CARD}" == 0 ]] || { echo 'This recovery is assigned to card 0.' >&2; exit 2; }
[[ ! -e "${OUT}" ]] || { echo 'Existing evidence is immutable.' >&2; exit 2; }
PY=grteclyn-wrapper/.venv/bin/python
UUID=$(nvidia-smi --id="${CARD}" --query-gpu=uuid --format=csv,noheader)
[[ -n "${UUID}" ]] || exit 2
PROCESSES=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
[[ "${PROCESSES}" != *"${UUID}"* ]] || { echo "GPU ${CARD} is occupied; nothing started." >&2; exit 2; }
nvidia-smi --id="${CARD}"
df -h /tmp/grteclyn_scratch
du -sh /tmp/grteclyn_scratch/*
mkdir -p runs/railgun/checks
REPORT="runs/railgun/checks/$(basename -- "${OUT}")"
[[ ! -e "${REPORT}.xml" ]] || { echo 'Existing test evidence is immutable.' >&2; exit 2; }
"${PY}" -m grteclyn_wrapper.optimisation.railgun.smooth_spectral_recovery \
  --config "${CONFIG}" --dry-run > "${REPORT}-plan.json"
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="${CARD}" WH_JAC_CHUNK=128
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
"${PY}" -m pytest -q --junitxml="${REPORT}.xml" \
  grteclyn-wrapper/tests/optimisation/test_solver_core.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_smooth_cubic.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_smooth_spectral.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_axis_audit.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_regular_dragging.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_dragging_falloff.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_372_handoff.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_evolution.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_evolution_amr.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_interpolation.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_geometry.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_transport.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_smooth_origin.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_smooth_origin_device.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_source_refinement.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_372_recovery.py
exec "${PY}" -u -m grteclyn_wrapper.optimisation.railgun.smooth_spectral_recovery \
  --gpu "${CARD}" --config "${CONFIG}" --out "${OUT}"
}
