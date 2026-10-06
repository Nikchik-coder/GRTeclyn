#!/usr/bin/env bash
# Named consumer profiles for the wormhole-merger campaign.
#
# WHAT THIS IS FOR.  Every run streams its plotfiles through
# consume_plotfiles (the sidecar run_single.sh starts), and WHAT it asks for
# is a 5-15 flag string.  Between 2026-08-31 and 2026-09-09 that string was
# retyped into each of thirty launch_*.sh scripts, which is how three of them
# ended up with a slice plane that missed the physics and one with no Weyl4.
# The flags are DATA, so they live here, once, under a name.  A new arm picks
# a profile; it does not retype the flags and does not get a new script.
#
# CONTRACT.  Source this AFTER RUN_DIR is set, then call
#   consumer_profile <name> [zoom] [coord] [center]
# It echoes the flag string on stdout.  Unknown name -> exit 2 with the list.
# Zoom is the full window width in code units (32 shows +/-16 around centre);
# center is "x y z", passed straight to --frames-center; empty means the
# renderer's own default, the domain midpoint on every axis.  PASS IT whenever
# the box centre is not L/2 or the window is off-axis: before 2026-09-15 the
# in-plane centre defaulted to z=0 and axis-y frames missed the throat
# entirely -- both queue-2e movies were lost to this, unrecoverably, because
# the slice cache stores only the cropped window.  Eyeball frame 0 against a
# reference run either way (README rule 13).
# coord is the slice coordinate along the slice normal -- NOT optional in
# spirit, because the consumer's default is 0, the domain boundary, and a
# slice that misses the physics renders featureless frames without erroring
# (measured 2026-08-31).  Both default to the box centre convention (32/32).
#
# FRAMES (2026-09-26).  Every profile renders the campaign's full frame set,
# ../frames_default.txt -- the ONE list, which run_single.sh also uses when a
# launch names no --frames-fields and which preflight.py enforces: a launch
# whose frames miss any of it is refused unless WHM_FRAMES_SUBSET="<reason>"
# says why.  A profile adds fields to it, never takes them away, except the
# two below that exist to be subsets and say so (consumer_profile_frames_subset).
# The frames are rendered from the t = 0 plotfile at preflight, before launch.
#
# WHY EACH PROFILE EXISTS.  A profile is a claim about what the run has to
# prove, not a taste in pictures:
#   headon        the Phase-3 head-on arms: psi4 at the three extraction
#                 spheres the in-code integrals use (10/14/18), the common
#                 horizon scanned on level 3 (level 1, the default, is too
#                 coarse to resolve the merged surface), and the full frame
#                 set so the collapse and the wave both have movies.
#   headon-modes  headon plus the scalar-mode decomposition on the same
#                 spheres (10/14/18) -- the head-on's scalar channel was never
#                 recorded (the stream postdates those arms and their
#                 plotfiles are pruned), so the 2026-09-19 re-run measures it.
#                 Same bare-switch spelling as orbit-modes: --scalar-modes,
#                 then --scalar-mode-ells 0 1 2.
#   headon-scout  the first look at a new head-on configuration: horizon
#                 tracking but no wave extraction (nothing has rung yet) and a
#                 tight zoom on the throats.
#   orbit         the inspiral twins and the capture scan: the full field set
#                 (it carries the matter diagnostics that separate a dissolved
#                 throat from a collapsed one, scalar_activity and local_speed).
#   orbit-modes   orbit plus the scalar-mode decomposition, for production
#                 arms that will be analysed spectrally.  NB the consumer takes
#                 --scalar-modes as a BARE SWITCH and the multipoles separately
#                 as --scalar-mode-ells; this profile said "--scalar-modes 0 1 2"
#                 from the day it was written (2026-09-10) and argparse rejected
#                 it, so the consumer died at startup and the run went on without
#                 one -- no frames, no python psi4, and no plotfile deletion.
#                 Caught 2026-09-15 on the first arm that ever used this profile.
#   bbh           the vacuum BBH control: the full set less what needs the
#                 scalar or h_ij, which its plotfiles do not carry (a declared
#                 subset, below).
#   chi           cheap probes and ladders -- one field, one question.  A
#                 subset with no built-in reason: the launch must say why in
#                 WHM_FRAMES_SUBSET, or the preflight refuses it (the ladder
#                 runs of 2026-09-08 were chi-only and lost every other movie).
#   none          one-step probes: no consumer at all (sets WHM_CONSUME=0).
#
# Related: research/merger/Reference.md, and the frame rules the hard way --
# a chi-only launch loses the collapse movies; omitting Weyl4 from the plot
# vars silently produces no wave files at all (the preflight now refuses a
# frame field whose plot variable the params do not write).

# Every profile keeps the slice cache and auto colour limits: the live watcher
# locks the colour scale from the FIRST plotfile, which under-ranges any field
# that grows, and only a cached slice can be re-scaled over the finished run.
_WHM_FRAME_TAIL='--frames-cache-slices --frames-auto-zlim'

# The campaign's frame fields, from ../frames_default.txt (field per line,
# "# why" comments).  Read once, at source time, so a missing or empty file
# stops the launcher here instead of producing a launch with no frames.
_WHM_FRAMES_FILE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)/frames_default.txt"
whm_frames_default() {
  [[ -r "${_WHM_FRAMES_FILE}" ]] || { echo "missing ${_WHM_FRAMES_FILE}" >&2; return 2; }
  local list
  list="$(sed -e 's/#.*//' "${_WHM_FRAMES_FILE}" | tr -s ' \t\n' ' ')"
  list="${list# }"; list="${list% }"
  [[ -n "${list}" ]] || { echo "no fields in ${_WHM_FRAMES_FILE}" >&2; return 2; }
  echo "${list}"
}
# The default set less the named fields (a declared subset, e.g. the vacuum control).
whm_frames_without() {
  local f out=""
  for f in ${WHM_FRAMES_FULL}; do
    [[ " $* " == *" ${f} "* ]] || out+="${f} "
  done
  echo "${out% }"
}
WHM_FRAMES_FULL="$(whm_frames_default)"

# The common MOTS itself on every plotfile, before the consumer deletes it (2026-10-01): the
# round scan reads a deformed remnant 4-11 % low, and an offline finder needed every plotfile
# kept.  Every binary profile carries it; the run's last plotfiles get it in the end-of-run
# drain too (consumer_args.extra, consume_plotfiles/README.md).
# Head-on: the defaults (level 3, +-4.5, l <= 6, seeds 3.2 / 2.6), checked end to end on leg 3
# replayed (MOTS-e2e: rows equal the offline finder to 8e-8).
_WHM_MOTS_HEADON='--mots-spectral'
# Orbits: the remnant forms larger and less round and the level boxes follow the pair, so
# level 2 at +-6, l <= 8 (+-9 fell off level 2 on the spiral at t = 49); the live spiral and
# fly-by run this window since 2026-10-01.  A plotfile with no common MOTS costs a cold
# search from the seeds (~2 min at level 2), inside a production plot interval (15-26 min).
_WHM_MOTS_ORBIT='--mots-spectral --mots-spectral-level 2 --mots-spectral-half 6 --mots-spectral-lmax 8 --mots-spectral-seeds 5.0 3.5'

consumer_profile() {
  local name="${1:?consumer_profile <name> [zoom] [coord]}"
  local zoom="${2:-32}" coord="${3:-32}" center="${4:-}"
  local center_arg=""
  [[ -n "${center}" ]] && center_arg="--frames-center ${center}"
  local horizon_track="${RUN_DIR:?RUN_DIR must be set before sourcing a profile}/data/binary_throat_diagnostics.dat"

  case "${name}" in
    headon)
      echo "--areal-radius --areal-min-radius 0.5 --radii 10 14 18" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895" \
           "--horizon-common-level 3 --horizon-half 3.0 ${_WHM_MOTS_HEADON}" \
           "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL}"
      ;;
    headon-modes)
      echo "--areal-radius --areal-min-radius 0.5 --radii 10 14 18" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895" \
           "--horizon-common-level 3 --horizon-half 3.0 ${_WHM_MOTS_HEADON}" \
           "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL}" \
           "--scalar-modes --scalar-mode-ells 0 1 2"
      ;;
    headon-scout)
      echo "--areal-radius --areal-min-radius 0.5" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895 ${_WHM_MOTS_HEADON}" \
           "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL}"
      ;;
    orbit)
      echo "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL} ${_WHM_MOTS_ORBIT}"
      ;;
    orbit-modes)
      echo "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL} --scalar-modes --scalar-mode-ells 0 1 2" \
           "${_WHM_MOTS_ORBIT}"
      ;;
    orbit-modes-scan)
      # orbit-modes plus the per-mouth horizon scan in the window the level-5 fly-by
      # merge_orbit_flip_d12_p045_L128_lvl5_t100 ran with (its registry row: half 3.0,
      # common scan on level 3), so its reruns and twins extract the same.  Until
      # 2026-09-28 this profile left the default window (half 2.5, level 1), which
      # moves the scan edge from 2.79 to 2.29 -- inside what the fly-by's mouths reach
      # by t = 30 -- and its mode-3 rerun launched so (consumer restarted at t = 18).
      echo "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL} --scalar-modes --scalar-mode-ells 0 1 2" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895" \
           "--horizon-common-level 3 --horizon-half 3.0 ${_WHM_MOTS_ORBIT}"
      ;;
    bbh)
      echo "--frames-fields $(whm_frames_without phi Pi scalar_activity local_speed)" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL}"
      ;;
    chi)
      echo "--areal-radius --areal-min-radius 0.5" \
           "--frames-fields chi --frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL}"
      ;;
    inflation)
      # The inflation arms (GPU_PLAN 2026-09-25): the areal radius on the full
      # metric, the neck and its two trapping horizons per plotfile, frames
      # whose lapse/chi/phi bars are fixed at their t = 0 range, scalar modes.
      echo "--areal-radius --areal-full-metric --areal-min-radius 0.5 --neck-horizons --radii 40 60 80 120" \
           "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL} --frames-zlim-t0 lapse chi phi" \
           "--scalar-modes --scalar-mode-ells 0 1 2"
      ;;
    inflation-octant)
      # The same on an octant box (lo_boundary = 2 2 2, centre 0 0 0): pass
      # --zoom = the FULL frame width, --coord 0, --center "0 0 0".  Frames are
      # mirrored into the full plane, odd fields (shift, Im Psi4) with their
      # sign (consume_plotfiles/frames/mirror.py; until 2026-09-26 they were
      # dropped, and F4 has no shift or Weyl4 movie).  On the z = 0 slice the
      # fields odd in z (shift3, Im Psi4) vanish; the frame shows the first
      # cell layer.
      echo "--reflect x y z" \
           "--areal-radius --areal-full-metric --areal-min-radius 0.5 --neck-horizons --radii 40 60 80 120" \
           "--frames-fields ${WHM_FRAMES_FULL}" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${center_arg} ${_WHM_FRAME_TAIL} --frames-zlim-t0 lapse chi phi" \
           "--scalar-modes --scalar-mode-ells 0 1 2"
      ;;
    orbit-modes-scan-prod)
      # The production set (the user, 2026-09-28): the mode-3 head-on, spiral and fly-by share
      # the L = 128 box and extract at the same four radii, 14/20/30/44, inside its sponge (r >= 48).
      echo "$(consumer_profile orbit-modes-scan "${zoom}" "${coord}" "${center}") --radii 14 20 30 44"
      ;;
    orbit-modes-prod)
      # The spiral of the production set: orbit-modes-scan-prod plus the areal radius, which the
      # paper's mouth arm v2_spiral_d12_p012_L128_lvl3_t050_mouths recorded (Fig. 15, the clmMouth
      # rows).  The mode-3 spiral launched without the scan or the areal radius and its consumer
      # was restarted with both at t = 18 (2026-09-28).
      echo "$(consumer_profile orbit-modes-scan "${zoom}" "${coord}" "${center}") --radii 14 20 30 44" \
           "--areal-radius --areal-min-radius 0.5"
      ;;
    headon-modes-prod)
      # The head-on of the production set: the shared four plus the old L = 64 run's 10/18, so the
      # old-vs-new comparison has common spheres.  headon-modes' own --radii 10 14 18 comes first;
      # the last one wins.  The common scan's window is 4.0, not headon-modes' 3.0: with 3.0 the old
      # level-5 arm lost the remnant MOTS past the scan edge (r = 2.79) after t = 37, and the mode-3
      # head-on's consumer had to be restarted with 4.0 at t = 18 (2026-09-28).
      # The 3D MOTS comes with headon-modes (_WHM_MOTS_HEADON, above).
      echo "$(consumer_profile headon-modes "${zoom}" "${coord}" "${center}") --radii 10 14 18 20 30 44" \
           "--horizon-half 4.0"
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
  echo "headon headon-modes headon-modes-prod headon-scout orbit orbit-modes orbit-modes-prod orbit-modes-scan orbit-modes-scan-prod bbh chi inflation inflation-octant none"
}

# The reason a profile renders less than the full frame set, when the subset is
# the profile's whole point; launch.sh passes it as WHM_FRAMES_SUBSET unless the
# caller set one.  Empty for every other profile -- chi included: a chi-only
# launch has to say why, each time.
consumer_profile_frames_subset() {
  case "${1:?consumer_profile_frames_subset <name>}" in
    bbh) echo "vacuum BBH control (profile bbh): its plotfiles carry no scalar field and no h_ij, so no phi, Pi, scalar_activity or local_speed frames" ;;
    *)   echo "" ;;
  esac
}
