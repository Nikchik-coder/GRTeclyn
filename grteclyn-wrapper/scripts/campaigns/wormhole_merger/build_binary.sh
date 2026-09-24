#!/usr/bin/env bash
# Build a campaign binary that says which commit it is.
#
#   bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/build_binary.sh \
#        [--tag NAME] [--jobs N] [--note TEXT] [--allow-dirty] [--clean] [--dry-run]
#
# WHY THIS EXISTS.  Until 2026-09-24 the frozen binaries in runs/wormhole_merger/bin/
# were named by date and feature (main3d_boost_2026-09-08.ex) and reported
# "GRTeclyn version (unknown)", so nothing tied a run to the source it ran.  The
# campaign pin predated the quadrupole seed, AMReX ignored the seed key without a
# word, and four "quadrupole" arms ran without their quadrupole (GPU_PLAN,
# 2026-09-23 evening).  A binary built here:
#   - is compiled from a CLEAN tree (Source/, the example, Tools/GNUMake) unless
#     --allow-dirty, in which case the name says -dirty and the diff is kept
#     beside the binary as <name>.patch;
#   - carries its commit inside it (GRTECLYN_VERSION, printed at start-up and
#     written to every run's parameters_and_version.txt);
#   - is named main3d_<tag>_<commit>[-dirty]_<date>.ex;
#   - gets a row in results/merger/binaries.tsv (tracked: runs/ is not).
#
# It builds in its own object directory (tmp_build_dir/pin, gitignored) under
# its own executable name, so the example's live build product
# (main3d.gnu.MPI.CUDA.ex), which other work rebuilds, is never touched.  The
# first build there is a full one (~20-40 min on 32 jobs); later ones are
# incremental with correct header dependencies.
#
# OPTIONS
#   --tag NAME      short word for what the build is for (default: build)
#   --jobs N        make -j (default 32)
#   --note TEXT     free text for the manifest row
#   --allow-dirty   build from uncommitted source (name gets -dirty, diff kept)
#   --clean         wipe tmp_build_dir/pin first (full rebuild)
#   --dry-run       print what would happen, build nothing
#   WHM_BUILD_FLAGS make flags (default: USE_CUDA=TRUE USE_MPI=TRUE COMP=gnu CUDA_ARCH=90,
#                   what every campaign binary since 2026-09-02 was built with)
# The whole body is one { ... } block ending in `exit`: bash parses it
# entirely before running it, so editing this file can never reach a live
# run.  (bash otherwise reads a script by byte offset as it goes; an edit
# made under a live run on 2026-09-24 would have had that run read the new
# file at the old offset when its evolution ended.)  Keep it that way.
{
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
EXAMPLE="${REPO}/Examples/BinaryWormholeMerger"
BIN_DIR="${REPO}/runs/wormhole_merger/bin"
LOG_DIR="${REPO}/runs/wormhole_merger/logs"
MANIFEST="${REPO}/results/merger/binaries.tsv"
AMREX="$(cd -- "${REPO}/../amrex" 2>/dev/null && pwd || true)"
FLAGS="${WHM_BUILD_FLAGS:-USE_CUDA=TRUE USE_MPI=TRUE COMP=gnu CUDA_ARCH=90}"
BUILD_SUB="tmp_build_dir/pin"          # relative to the example; gitignored

TAG="build" JOBS=32 NOTE="" ALLOW_DIRTY=0 CLEAN=0 DRYRUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)         TAG="$2"; shift 2 ;;
    --jobs)        JOBS="$2"; shift 2 ;;
    --note)        NOTE="$2"; shift 2 ;;
    --allow-dirty) ALLOW_DIRTY=1; shift ;;
    --clean)       CLEAN=1; shift ;;
    --dry-run)     DRYRUN=1; shift ;;
    -h|--help)     sed -n '2,35p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)             echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
done
[[ "${TAG}" =~ ^[A-Za-z0-9]+$ ]] || { echo "--tag must be letters and digits only" >&2; exit 2; }

# --- what goes into the binary, and is it committed? -------------------------
SRC_PATHS=(Source Examples/BinaryWormholeMerger Tools/GNUMake)
dirty_list="$(git -C "${REPO}" status --porcelain --untracked-files=no -- "${SRC_PATHS[@]}")"
commit="$(git -C "${REPO}" rev-parse --short=8 HEAD)"
version="${commit}"
if [[ -n "${dirty_list}" ]]; then
  if (( ! ALLOW_DIRTY )); then
    echo "[build] uncommitted changes in the source that goes into the binary:" >&2
    echo "${dirty_list}" | sed 's/^/[build]   /' >&2
    echo "[build] commit them, or pass --allow-dirty (the name will say -dirty)." >&2
    exit 1
  fi
  version="${commit}-dirty"
fi
amrex_version="unknown"
if [[ -n "${AMREX}" ]]; then
  amrex_version="$(git -C "${AMREX}" describe --abbrev=8 --dirty --always 2>/dev/null || echo unknown)"
fi
today="$(date -u +%F)"
NAME="main3d_${TAG}_${version}_${today}.ex"
DEST="${BIN_DIR}/${NAME}"

echo "[build] source   : ${commit}$( [[ -n "${dirty_list}" ]] && echo " + uncommitted changes (-dirty)")"
echo "[build] amrex    : ${amrex_version}"
echo "[build] flags    : ${FLAGS}"
echo "[build] objects  : Examples/BinaryWormholeMerger/${BUILD_SUB}$( (( CLEAN )) && echo " (wiped first)")"
echo "[build] output   : runs/wormhole_merger/bin/${NAME}"
[[ -e "${DEST}" ]] && { echo "[build] ${NAME} already exists -- nothing to do (delete it to rebuild)" >&2; exit 1; }
(( DRYRUN )) && { echo "[build] dry run -- nothing built."; exit 0; }

# The machine overlay (grteclyn-wrapper/.env via env.sh) is what puts the
# campaign's OpenMPI on PATH; without it AMReX stops at "Unknown mpi wrapper".
# But env.sh also prepends the GRTresna conda env, whose g++ 15 fails nvcc's
# "gcc <= 12" check (grteclyn-wrapper/README.md, build troubleshooting) -- so
# blank GRTRESNA_ENV first: env.sh never overwrites an already-set variable.
export GRTRESNA_ENV=""
# shellcheck source=../../lib/env.sh
source "${REPO}/grteclyn-wrapper/scripts/lib/env.sh"
command -v mpicxx >/dev/null 2>&1 || { echo "[build] mpicxx not on PATH after env.sh -- set OPENMPI_ROOT in grteclyn-wrapper/.env" >&2; exit 1; }
gxx_major="$(g++ -dumpversion | cut -d. -f1)"
if (( gxx_major > 12 )); then
  echo "[build] host g++ is ${gxx_major}.x (from $(command -v g++)); nvcc needs <= 12 -- fix PATH" >&2
  exit 1
fi
# nvcc is not on the default PATH on these nodes.
if ! command -v nvcc >/dev/null 2>&1 && [[ -x /usr/local/cuda/bin/nvcc ]]; then
  export PATH="/usr/local/cuda/bin:${PATH}"
fi
command -v nvcc >/dev/null 2>&1 || { echo "[build] nvcc not found" >&2; exit 1; }
nvcc_version="$(nvcc --version | tail -n 1)"

mkdir -p "${BIN_DIR}" "${LOG_DIR}"
LOG="${LOG_DIR}/build_${NAME%.ex}.log"
(( CLEAN )) && rm -rf "${EXAMPLE:?}/${BUILD_SUB}"
# The version string is compiled into Main_BinaryWormhole.o only (SetupFunctions.hpp),
# and make does not track -D flags, so that one object is always rebuilt.
find "${EXAMPLE}/${BUILD_SUB}" -name 'Main_BinaryWormhole.o' -delete 2>/dev/null || true
rm -f "${EXAMPLE}"/pin3d.*.ex

echo "[build] building (log: ${LOG#"${REPO}"/}) ..."
t0=$(date +%s)
# GRTECLYN_VERSION on the command line beats Make.defs' own `git describe`, which
# sees the WHOLE tree: a doc edit elsewhere would otherwise stamp -dirty.
# shellcheck disable=SC2086
if ! make -C "${EXAMPLE}" -j "${JOBS}" ${FLAGS} EBASE=pin TMP_BUILD_DIR="${BUILD_SUB}" \
       GRTECLYN_VERSION="${version}" > "${LOG}" 2>&1; then
  echo "[build] make FAILED -- last lines of the log:" >&2
  tail -n 25 "${LOG}" | sed 's/^/[build]   /' >&2
  exit 1
fi
exe="$(ls -t "${EXAMPLE}"/pin3d.*.ex 2>/dev/null | head -n 1 || true)"
[[ -x "${exe}" ]] || { echo "[build] make succeeded but produced no pin3d.*.ex" >&2; exit 1; }
if ! grep -a -q -- "${version}" "${exe}"; then
  echo "[build] the binary does not carry its version string '${version}' -- refusing" >&2
  exit 1
fi

cp "${exe}" "${DEST}.part$$" && chmod +x "${DEST}.part$$" && mv "${DEST}.part$$" "${DEST}"
rm -f "${exe}"
if [[ -n "${dirty_list}" ]]; then
  git -C "${REPO}" diff -- "${SRC_PATHS[@]}" > "${DEST%.ex}.patch"
fi
sha="$(sha256sum "${DEST}" | cut -d' ' -f1)"
minutes=$(( ($(date +%s) - t0 + 59) / 60 ))

if [[ ! -f "${MANIFEST}" ]]; then
  printf '# GENERATED ROWS by build_binary.sh; hand-written rows for binaries built before it.\n' > "${MANIFEST}"
fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "${NAME}" "${sha:0:16}" "${version}" "${amrex_version}" "$(date -u +%FT%TZ)" \
  "${FLAGS}" "${nvcc_version}" "build_binary.sh" "${NOTE}" >> "${MANIFEST}"

echo "[build] done in ~${minutes} min: runs/wormhole_merger/bin/${NAME}"
echo "[build] sha256   : ${sha}"
echo "[build] manifest : results/merger/binaries.tsv (commit it)"
echo "[build] launch with: --binary runs/wormhole_merger/bin/${NAME}"
exit
}
