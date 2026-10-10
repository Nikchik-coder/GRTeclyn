#!/usr/bin/env bash
# Where a run lives in runs/spinning_wormhole, by name.
#
# The campaign directory is filed by physics, as in the merger campaign since
# 2026-09-10: a run that is on a card sits at the top level, and once it is
# closed out it moves into its NN_name group folder.  Everything that takes a
# run NAME -- close-out, log tidying, checkpoint keeping and pruning, the movie
# stitcher -- resolves it through here, so nothing else has to know the layout.
#
#   source ".../lib/run_tree.sh"
#   dir="$(run_tree_find "${CAMPAIGN}" "${name}")" || echo "no such run"
#   run_tree_groups "${CAMPAIGN}"      # the group folders, one per line
#
# A name is matched at the top level first, then one and two levels down
# (NN_group/<family>/<arm> is the deepest shape).  Folders whose names start
# with 00_archive, 90_, bin, logs or templates are never runs.

run_tree_find() {
  local root="$1" name="$2" d
  name="${name%/}"; name="$(basename "${name}")"
  [[ -d "${root}/${name}" ]] && { printf '%s\n' "${root}/${name}"; return 0; }
  for d in "${root}"/[0-9][0-9]_*/"${name}" "${root}"/[0-9][0-9]_*/*/"${name}"; do
    [[ -d "${d}" ]] && { printf '%s\n' "${d}"; return 0; }
  done
  return 1
}

# The physics groups (NN_name folders), in order.
run_tree_groups() {
  local root="$1" d
  for d in "${root}"/[0-9][0-9]_*/; do
    [[ -d "${d}" ]] && basename "${d%/}"
  done
}

# Every run directory under the tree: a folder holding params.txt, or a
# log-only stub (LOST.md).  Live runs at the top level are included.
run_tree_runs() {
  local root="$1"
  find "${root}" -mindepth 1 -maxdepth 3 -type d \
       ! -path "${root}/00_archive*" ! -path "${root}/90_*" \
       ! -path "${root}/bin*" ! -path "${root}/logs*" ! -path "${root}/templates*" \
       \( -exec test -f '{}/params.txt' \; -o -exec test -f '{}/LOST.md' \; \) -print \
    | grep -vE '/(frames|movies|data|small_data|plots|templates)(/|$)' | sort
}
