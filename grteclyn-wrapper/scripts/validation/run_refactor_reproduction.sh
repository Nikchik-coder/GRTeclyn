#!/usr/bin/env bash
# Invoke through capped_job.sh with 4 threads, 64 GiB and a one-hour timeout.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
out="${1:?usage: run_refactor_reproduction.sh OUTPUT_DIRECTORY}"
mkdir -p "${out}"
out="$(cd "${out}" && pwd)"
baseline=2f1c450604956cc31d927ae096490e291aa81cef
revision="$(git -C "${repo}" rev-parse HEAD)"
py="${repo}/grteclyn-wrapper/.venv/bin/python"
driver="${repo}/grteclyn-wrapper/scripts/validation/refactor_reproduction.py"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES="" JAX_ENABLE_X64=true
export WH_JAC_CHUNK=128 MPLBACKEND=Agg
export MPLCONFIGDIR="${out}/matplotlib"
mkdir -p "${out}/baseline" "${out}/wheels" "${out}/installed" "${out}/work"
git -C "${repo}" archive "${baseline}" grteclyn-wrapper/src | tar -x -C "${out}/baseline"
uv build --wheel --out-dir "${out}/wheels" "${repo}/grteclyn-wrapper/packages/stationary"
uv build --wheel --out-dir "${out}/wheels" "${repo}/grteclyn-wrapper"
uv pip install --python "${py}" --no-deps --target "${out}/installed" "${out}"/wheels/*.whl
sha256sum "${out}"/wheels/*.whl > "${out}/wheel-sha256.txt"
cd "${out}/work"
for case in spin spherical accepted_ring rejected_ring boson application; do
    for version in legacy wheel; do
        if [[ "${version}" == legacy ]]; then
            package_path="${out}/baseline/grteclyn-wrapper/src"
            source_revision="${baseline}"
        else
            package_path="${out}/installed"
            source_revision="${revision}"
        fi
        echo "[case] ${version} ${case} $(date -u +%FT%TZ)"
        PYTHONPATH="${package_path}" "${py}" -u "${driver}" run \
            --case "${case}" --version "${version}" --repo "${repo}" \
            --revision "${source_revision}" --out "${out}" \
            > "${out}/${version}-${case}.log" 2>&1
        tail -n 1 "${out}/${version}-${case}.log"
    done
done
"${py}" "${driver}" compare --out "${out}"
