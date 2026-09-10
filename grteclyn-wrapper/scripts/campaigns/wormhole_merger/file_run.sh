#!/usr/bin/env bash
# File closed-out runs into their physics group under runs/wormhole_merger.
#
#   bash .../file_run.sh --group 04_binary_headon [--dry-run] RUN [RUN ...]
#
# WHY.  A run lands at the top level while it is on a card, because every
# tool that watches it knows it by name.  Once it is closed out it belongs
# with its question -- one throat, two throats at rest, the head-on, the
# spiral, the fly-by, the vacuum control -- so that the directory reads as
# the paper does and not as the order things were tried.  The groups are the
# NN_name folders; `lib/run_tree.sh` resolves a name wherever it is filed,
# so the move changes no tool's interface.
#
# WHAT IT DOES, per run: refuses a live run (launcher.pid alive); moves the
# directory; then repairs every symlink in the tree that pointed into the old
# location (the stitched movie builds symlink other runs' slice caches by
# absolute path).  The scratch directory is keyed by NAME and is untouched.
# The packed copy under results/merger/campaign/ follows the run tree at the
# next pack_results.sh; git mv it by hand if the pack is not being rebuilt.
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${HERE}/../../../.." && pwd)"
CAMPAIGN="${REPO}/runs/wormhole_merger"
# shellcheck source=lib/run_tree.sh
source "${HERE}/lib/run_tree.sh"

GROUP="" DRY=0 RUNS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --group)   GROUP="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) RUNS+=("$1"); shift ;;
  esac
done
[[ -n "${GROUP}" && ${#RUNS[@]} -gt 0 ]] || { sed -n '2,6p' "${BASH_SOURCE[0]}"; exit 2; }
[[ "${GROUP}" =~ ^[0-9][0-9]_[a-z_]+(/[a-z_]+)?$ ]] || { echo "group must look like 04_binary_headon[/subfolder]: ${GROUP}" >&2; exit 2; }

dest_root="${CAMPAIGN}/${GROUP}"
moved=()
for run in "${RUNS[@]}"; do
  run="${run%/}"; run="$(basename "${run}")"
  src="$(run_tree_find "${CAMPAIGN}" "${run}")" || { echo "  no such run: ${run}" >&2; continue; }
  if [[ -f "${src}/launcher.pid" ]] && kill -0 "$(cat "${src}/launcher.pid" 2>/dev/null)" 2>/dev/null; then
    echo "  LIVE, not filed: ${run}" >&2; continue
  fi
  if [[ "${src}" == "${dest_root}/${run}" ]]; then echo "  already filed: ${GROUP}/${run}"; continue; fi
  echo "  ${src#"${CAMPAIGN}"/}  ->  ${GROUP}/${run}"
  if (( ! DRY )); then
    mkdir -p "${dest_root}"
    mv "${src}" "${dest_root}/${run}"
    moved+=("${src}|${dest_root}/${run}")
  fi
done

# Repair symlinks that pointed into a moved run (absolute targets).
if (( ${#moved[@]} )); then
  fixed=0
  while IFS= read -r -d '' link; do
    target="$(readlink "${link}")"
    [[ -e "${link}" ]] && continue          # still resolves
    for pair in "${moved[@]}"; do
      old="${pair%%|*}"; new="${pair##*|}"
      if [[ "${target}" == "${old}"/* ]]; then
        ln -sfn "${new}/${target#"${old}"/}" "${link}"; fixed=$((fixed+1)); break
      fi
    done
  done < <(find "${CAMPAIGN}" -type l -print0 2>/dev/null)
  echo "  symlinks repaired: ${fixed}"
fi
