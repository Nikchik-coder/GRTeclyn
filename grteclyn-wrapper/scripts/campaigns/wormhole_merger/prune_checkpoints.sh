#!/usr/bin/env bash
# Drop restart checkpoints from node-local scratch, per-run policy.
#
# Insured runs keep the newest TWO checkpoints (one-deep leaves nothing to fall
# back on if the process dies partway through writing the newest).  Every other
# run keeps NONE -- they are cheap to restart and their checkpoints are pure
# disk cost.
#
# The insured set is the main merger, the Helfer/plain twins, and the t200
# capture scouts: each is many hours deep, so losing one costs more than the
# ~30 GB it holds.  This was learned the hard way -- p025 died at t = 53 with
# its only restart point already swept, so the whole run had to be written off.
#
# Scope is deliberately narrow: a scratch directory is touched only when a
# matching run directory exists under the campaign, so a co-tenant's run on the
# same disk is never a candidate.  Nothing written in the last QUIET_S seconds
# is touched, so a checkpoint still being written is never half-deleted.
#
# DRYRUN=1 prints and deletes nothing.

SCRATCH=${SCRATCH:-/tmp/grteclyn_scratch}
CAMPAIGN=${CAMPAIGN:?campaign runs dir required}
# shellcheck source=lib/run_tree.sh
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/run_tree.sh"   # runs are filed by group since 2026-09-10
MAIN_RE=${MAIN_RE:-^(bbh_control_[a-z0-9_]+|merge_orbit_flip_d12(_r[0-9]+)?|merge_twin_p012_[a-z0-9]+(_lvl[0-9]+)?_t[0-9]+|merge_orbit_flip_d12_p[0-9]+(_[a-z0-9]+)*_t[0-9]+)$}   # main merger + its _rNNNNN restarts, the twins, the t200 scouts, and the _lvlN refinement variants of either
KEEP_MAIN=${KEEP_MAIN:-2}
KEEP_OTHER=${KEEP_OTHER:-0}
QUIET_S=${QUIET_S:-300}
freed=0
lines=()

for d in "$SCRATCH"/*/; do
  name=$(basename "$d")
  run_tree_find "$CAMPAIGN" "$name" >/dev/null || continue   # only runs of this campaign, wherever filed
  if [[ "$name" =~ $MAIN_RE ]]; then keep=$KEEP_MAIN; else keep=$KEEP_OTHER; fi

  mapfile -t chks < <(find "$d" -maxdepth 1 -type d -name '*Chk[0-9]*' -printf '%f\n' 2>/dev/null | sort -V)
  n=${#chks[@]}
  (( n > keep )) || continue

  for (( i = 0; i < n - keep; i++ )); do
    c="$d${chks[$i]}"
    age=$(( $(date +%s) - $(stat -c %Y "$c") ))
    (( age < QUIET_S )) && continue
    sz=$(du -sm "$c" 2>/dev/null | cut -f1)
    if [ -n "$DRYRUN" ]; then
      lines+=("would remove $name/${chks[$i]} (${sz} MB)")
    else
      rm -rf "$c" && { freed=$(( freed + sz )); lines+=("removed $name/${chks[$i]} (${sz} MB)"); }
    fi
  done
done

if (( ${#lines[@]} )); then
  printf '%s\n' "${lines[@]}"
  (( freed )) && echo "freed $(( freed / 1024 )) GB total"
fi

exit 0
