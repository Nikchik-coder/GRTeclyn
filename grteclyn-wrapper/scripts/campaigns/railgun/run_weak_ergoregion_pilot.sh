#!/usr/bin/env bash
# Prepared short comparison; start only after the separate run-specific go.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
cd "${REPO}"
CONFIG="grteclyn-wrapper/scripts/campaigns/railgun/configs/evolution_ergoregion_108_pilot.json"
CARD="${1:?card required}" STEM="${2:?new name required}"
BINARY="${3:?binary required}" CHECKPOINTS="${4:?explicit checkpoints policy required}"
[[ "${CARD}" == 0 || "${CARD}" == 1 ]] || exit 2
[[ "${STEM}" =~ ^[A-Za-z0-9._-]+$ && "${CHECKPOINTS}" == off && -x "${BINARY}" ]] || exit 2
PY=grteclyn-wrapper/.venv/bin/python
"${PY}" -m grteclyn_stationary.railgun.evolution_amr plan --config "${CONFIG}" --n 96
UUID=$(nvidia-smi --id="${CARD}" --query-gpu=uuid --format=csv,noheader)
PROCESSES=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
[[ -n "${UUID}" && "${PROCESSES}" != *"${UUID}"* ]] || {
  echo 'Selected GPU is occupied; nothing started.' >&2; exit 2;
}
nvidia-smi --id="${CARD}"
df -h /tmp/grteclyn_scratch
du -sh /tmp/grteclyn_scratch/*
export JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES="${CARD}" WH_JAC_CHUNK=128
export XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false
mkdir -p runs/railgun/checks
REPORT="runs/railgun/checks/${STEM}-gpu${CARD}.xml"
[[ ! -e "${REPORT}" ]] || { echo 'Existing evidence is immutable.' >&2; exit 2; }
"${PY}" -m pytest -q --junitxml="${REPORT}" \
  grteclyn-wrapper/tests/stationary/test_railgun_evolution.py \
  grteclyn-wrapper/tests/stationary/test_railgun_evolution_amr.py \
  grteclyn-wrapper/tests/stationary/test_railgun_interpolation.py \
  grteclyn-wrapper/tests/stationary/test_railgun_geometry.py \
  grteclyn-wrapper/tests/stationary/test_railgun_smooth_origin.py \
  grteclyn-wrapper/tests/stationary/test_railgun_smooth_origin_device.py
if [[ "${CARD}" == 0 ]]; then RESOLUTIONS=(96 128); else RESOLUTIONS=(192); fi
for N in "${RESOLUTIONS[@]}"; do
  NAME="${STEM}-n${N}"
  OUT="runs/railgun/evolution/exports/${NAME}"
  [[ ! -e "${OUT}" && ! -e "runs/railgun/evolution/ergoregion/${NAME}" ]] || exit 2
  # The exporter checks the source archive and the centre before writing cubes.
  # The launcher independently checks the cube hashes and repeats preflight.
  timeout --signal=TERM --kill-after=30 10800 bash -c '
    set -euo pipefail
    "$1" -u -m grteclyn_stationary.railgun.evolution_amr export \
      --config "$2" --n "$3" --out "$4" --gpu "$5"
    exec bash "$6/launch_ergoregion.sh" --config "$2" --n "$3" \
      --data-dir "$4" --gpu "$5" --name "$7" --binary "$8" --checkpoints off
  ' pilot "${PY}" "${CONFIG}" "${N}" "${OUT}" "${CARD}" "${HERE}" "${NAME}" "${BINARY}"
  "${PY}" - "runs/railgun/evolution/ergoregion/${NAME}" <<'PY'
import json
import sys
from pathlib import Path
import numpy as np
run = Path(sys.argv[1])
manifest = json.loads((run/'run_manifest.json').read_text())
data = np.loadtxt(run/'data/constraint_norms.dat', ndmin=2)
if (manifest.get('status') != 'finished' or manifest.get('exit_status') != 0
        or not np.isfinite(data).all() or data[-1, 0] < 2-1e-8):
    raise SystemExit('Previous pilot failed or did not finish t=2; queue stopped.')
PY
done
