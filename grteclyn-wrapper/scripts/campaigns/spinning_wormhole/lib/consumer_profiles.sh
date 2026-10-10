#!/usr/bin/env bash
# Named consumer profiles for the spinning-wormhole campaign.
#
# WHAT THIS IS FOR.  Every run streams its plotfiles through consume_plotfiles
# (the sidecar run_single.sh starts), and WHAT it asks for is a flag string.
# The flags are DATA, so they live here, once, under a name, exactly as in the
# merger campaign (lib/consumer_profiles.sh there says how retyping those flags
# per launch script cost three runs their slice plane and one its Weyl4).  A
# new arm picks a profile; it does not retype the flags.
#
# CONTRACT.  Source this, then call
#   consumer_profile <name> [zoom] [coord] [center]
# It echoes the flag string on stdout.  Unknown name -> exit 2 with the list.
# Zoom is the full window width in code units (32 shows +/-16 around centre);
# center is "x y z", passed to --frames-center and --mots-spectral-center;
# empty means each tool's own default (the renderer: the domain midpoint on
# every axis).  PASS IT whenever the box centre is not L/2 or the window is
# off-axis.  Eyeball frame 0 against a reference run either way.
# coord is the slice coordinate along the slice normal -- NOT optional in
# spirit, because the consumer's default is 0, the domain boundary, and a
# slice that misses the physics renders featureless frames without erroring
# (measured 2026-08-31 in the merger campaign).  Both default to the box
# centre convention (32/32).
#
# FRAMES.  Every profile renders the campaign's full frame set,
# ../frames_default.txt -- the ONE list, which run_single.sh also uses when a
# launch names no --frames-fields and which preflight.py enforces: a launch
# whose frames miss any of it is refused unless SWH_FRAMES_SUBSET="<reason>"
# says why.  No profile here is a built-in subset; a launch that cuts the list
# must say why, each time.  The frames are rendered from the t = 0 plotfile at
# preflight, before launch.
#
# WHY EACH PROFILE EXISTS.  A profile is a claim about what the run has to
# prove, not a taste in pictures:
#   hold   the production profile: the full frame set plus the spectral MOTS
#          on every plotfile, before the consumer deletes it (the round and
#          oriented scans read a deformed horizon 3-11 % low, 2026-10-01, so
#          horizon numbers come from the 3D finder or not at all).
#   smoke  tiny-box plumbing runs: the full frame set, no psi4 spheres and no
#          MOTS.  The psi4 default radii (14, 30) do not fit an L = 16 box, and
#          on 2026-10-10 that refused every plotfile of the first smoke test --
#          no frames, no pruning; a massless static throat has no MOTS either.
#   none   one-step probes: no consumer at all (sets SWH_CONSUME=0).

# Every profile keeps the slice cache and auto colour limits: the live watcher
# locks the colour scale from the FIRST plotfile, which under-ranges any field
# that grows, and only a cached slice can be re-scaled over the finished run.
_SWH_FRAME_TAIL='--frames-cache-slices --frames-auto-zlim'

# The campaign's frame fields, from ../frames_default.txt (field per line,
# "# why" comments).  Read once, at source time, so a missing or empty file
# stops the launcher here instead of producing a launch with no frames.
_SWH_FRAMES_FILE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)/frames_default.txt"
swh_frames_default() {
  [[ -r "${_SWH_FRAMES_FILE}" ]] || { echo "missing ${_SWH_FRAMES_FILE}" >&2; return 2; }
  local list
  list="$(sed -e 's/#.*//' "${_SWH_FRAMES_FILE}" | tr -s ' \t\n' ' ')"
  list="${list# }"; list="${list% }"
  [[ -n "${list}" ]] || { echo "no fields in ${_SWH_FRAMES_FILE}" >&2; return 2; }
  echo "${list}"
}
SWH_FRAMES_FULL="$(swh_frames_default)"

consumer_profile() {
  local name="${1:?consumer_profile <name> [zoom] [coord] [center]}"
  local zoom="${2:-32}" coord="${3:-32}" center="${4:-}"
  local center_arg="" mots_center_arg=""
  if [[ -n "${center}" ]]; then
    center_arg="--frames-center ${center}"
    mots_center_arg="--mots-spectral-center ${center}"
  fi

  case "${name}" in
    hold)
      echo "--frames-fields ${SWH_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_SWH_FRAME_TAIL}" \
           "--mots-spectral ${mots_center_arg}"
      ;;
    smoke)
      echo "--frames-fields ${SWH_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_SWH_FRAME_TAIL}" \
           "--no-psi4"
      ;;
    none)
      echo ""
      ;;
    *)
      echo "unknown consumer profile: ${name}" >&2
      echo "known: $(consumer_profile_names)" >&2
      exit 2
      ;;
  esac
}

consumer_profile_names() {
  echo "hold smoke none"
}

# The reason a profile renders less than the full frame set, when the subset is
# the profile's whole point; launch.sh passes it as SWH_FRAMES_SUBSET unless the
# caller set one.  No profile of this campaign is a built-in subset: a launch
# that cuts the list has to say why, each time.
consumer_profile_frames_subset() {
  case "${1:?consumer_profile_frames_subset <name>}" in
    *) echo "" ;;
  esac
}
