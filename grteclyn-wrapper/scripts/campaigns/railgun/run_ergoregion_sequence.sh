#!/usr/bin/env bash
# Run inside capped_job.sh: one member on card 1, two sequentially on card 0.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
cd "${REPO}"
MEMBER=0
if [[ "${1:-}" == --member ]]; then MEMBER=1; shift; fi
CONFIG="${1:?configuration required}" CARD="${2:?card required}"
STEM="${3:?new run-name stem required}" BINARY="${4:?binary required}"
[[ "${STEM}" =~ ^[A-Za-z0-9._-]+$ ]] || exit 2
[[ "${CARD}" == 0 || "${CARD}" == 1 ]] || exit 2
[[ -x "${BINARY}" ]] || { echo 'Executable binary required.' >&2; exit 2; }
PY=grteclyn-wrapper/.venv/bin/python
"${PY}" - "${CONFIG}" <<'PY'
import json
import sys
from pathlib import Path
from grteclyn_stationary.railgun.evolution import digest
from grteclyn_stationary.railgun.evolution_amr import load_plan
cfg, _ = load_plan(sys.argv[1], 96)
source = Path(cfg['source'])
if not (source.parent/'evolution_qualification.json').is_file():
    raise SystemExit('The source has no completed centre qualification; nothing started.')
qualification = json.loads((source.parent/'evolution_qualification.json').read_text())
certificate = json.loads((source.parent/'corridor.json').read_text())
if (not qualification['stationary_accepted'] or not qualification['evolution_qualified']
        or qualification['refined_source_sha256'] != digest(source)
        or not certificate['accepted'] or certificate['source_sha256'] != digest(source)
        or certificate['tolerance'] != 1e-8):
    raise SystemExit('A hash-matched, qualified stationary source is required.')
PY
if (( MEMBER )); then
  N="${5:?member resolution required}"
  case "${N}:${CARD}" in 96:0|128:0|192:1) ;; *) exit 2 ;; esac
  UUID=$(nvidia-smi --id="${CARD}" --query-gpu=uuid --format=csv,noheader)
  PROCESSES=$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader)
  [[ -n "${UUID}" && "${PROCESSES}" != *"${UUID}"* ]] || {
    echo 'Selected GPU is unavailable; nothing started.' >&2; exit 2;
  }
  NAME="${STEM}-n${N}"
  OUT="runs/railgun/evolution/exports/${NAME}"
  [[ ! -e "${OUT}" && ! -e "runs/railgun/evolution/ergoregion/${NAME}" ]] || {
    echo 'Existing run evidence is immutable.' >&2; exit 2;
  }
  nvidia-smi --id="${CARD}"
  df -h /tmp/grteclyn_scratch
  du -sh /tmp/grteclyn_scratch/*
  export XLA_PYTHON_CLIENT_PREALLOCATE=false XLA_PYTHON_CLIENT_ALLOCATOR=platform
  "${PY}" -u -m grteclyn_stationary.railgun.evolution_amr export \
    --config "${CONFIG}" --n "${N}" --out "${OUT}" --gpu "${CARD}"
  exec bash "${HERE}/launch_ergoregion.sh" --config "${CONFIG}" \
    --data-dir "${OUT}" --name "${NAME}" --n "${N}" --gpu "${CARD}" \
    --binary "${BINARY}" --checkpoints off
fi
if [[ "${CARD}" == 0 ]]; then RESOLUTIONS=(96 128); else RESOLUTIONS=(192); fi
for N in "${RESOLUTIONS[@]}"; do
  timeout --signal=TERM --kill-after=30 172800 bash "${BASH_SOURCE[0]}" \
    --member "${CONFIG}" "${CARD}" "${STEM}" "${BINARY}" "${N}"
  # An early normal exit must not silently advance the queue.
  "${PY}" - "runs/railgun/evolution/ergoregion/${STEM}-n${N}" <<'PY'
import json
import sys
from pathlib import Path
import numpy as np
run = Path(sys.argv[1])
manifest = json.loads((run/'run_manifest.json').read_text())
data = np.loadtxt(run/'data/constraint_norms.dat', ndmin=2)
if (manifest.get('status') != 'finished' or manifest.get('exit_status') != 0
        or not np.isfinite(data).all() or data[-1, 0] < 50-1e-8):
    raise SystemExit('Previous member did not finish t=50 with finite constraints; queue stopped.')
PY
done
