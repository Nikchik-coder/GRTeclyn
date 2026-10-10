#!/usr/bin/env bash
# Drop restart checkpoints from node-local scratch, per-run policy.
#
# Insured runs keep the newest TWO checkpoints (one-deep leaves nothing to fall
# back on if the process dies partway through writing the newest).  Every other
# run keeps NONE -- they are cheap to restart and their checkpoints are pure
# disk cost.
#
# The insured set is MAIN_RE below.  It starts EMPTY for this campaign (no run
# is insured yet, 2026-10-10): set MAIN_RE in the environment, or widen the
# default here, once a run is many hours deep and losing it would cost more
# than the ~30 GB it holds.  The merger campaign learned the price of an empty
# insured set the hard way: a run died with its only restart point already
# swept and had to be written off.
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
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib/run_tree.sh"   # runs are filed by group
MAIN_RE=${MAIN_RE:-^$}       # matches only an empty name, i.e. no insured run yet (see the header)
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
