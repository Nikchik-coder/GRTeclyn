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
#   consumer_profile <name> [zoom] [coord]
# It echoes the flag string on stdout.  Unknown name -> exit 2 with the list.
# Zoom is the full window width in code units (32 shows +/-16 around centre);
# coord is the slice coordinate along the slice normal -- NOT optional in
# spirit, because the consumer's default is 0, the domain boundary, and a
# slice that misses the physics renders featureless frames without erroring
# (measured 2026-08-31).  Both default to the box centre convention (32/32).
#
# WHY EACH PROFILE EXISTS.  A profile is a claim about what the run has to
# prove, not a taste in pictures:
#   headon        the Phase-3 head-on arms: psi4 at the three extraction
#                 spheres the in-code integrals use (10/14/18), the common
#                 horizon scanned on level 3 (level 1, the default, is too
#                 coarse to resolve the merged surface), and six fields so the
#                 collapse and the wave both have movies.
#   headon-scout  the first look at a new head-on configuration: horizon
#                 tracking but no wave extraction (nothing has rung yet) and a
#                 tight zoom on the throats.
#   orbit         the inspiral twins and the capture scan: the full field set,
#                 including the matter diagnostics that separate a dissolved
#                 throat from a collapsed one.
#   orbit-modes   orbit plus the scalar-mode decomposition, for production
#                 arms that will be analysed spectrally.
#   bbh           the vacuum BBH control: no matter fields exist in it.
#   chi           cheap probes and ladders -- one field, one question.
#   none          one-step probes: no consumer at all (sets WHM_CONSUME=0).
#
# Related: research/merger/Reference.md, and the frame rules the hard way --
# a chi-only launch loses the collapse movies; omitting Weyl4 from the plot
# vars silently produces no wave files at all.

# Every profile keeps the slice cache and auto colour limits: the live watcher
# locks the colour scale from the FIRST plotfile, which under-ranges any field
# that grows, and only a cached slice can be re-scaled over the finished run.
_WHM_FRAME_TAIL='--frames-cache-slices --frames-auto-zlim'

consumer_profile() {
  local name="${1:?consumer_profile <name> [zoom] [coord]}"
  local zoom="${2:-32}" coord="${3:-32}"
  local horizon_track="${RUN_DIR:?RUN_DIR must be set before sourcing a profile}/data/binary_throat_diagnostics.dat"

  case "${name}" in
    headon)
      echo "--areal-radius --areal-min-radius 0.5 --radii 10 14 18" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895" \
           "--horizon-common-level 3 --horizon-half 3.0" \
           "--frames-fields chi K lapse phi Pi Weyl4_Re" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL}"
      ;;
    headon-scout)
      echo "--areal-radius --areal-min-radius 0.5" \
           "--horizon-scan --horizon-track ${horizon_track} --horizon-r-exact 3.8895" \
           "--frames-fields chi K lapse phi Pi" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL}"
      ;;
    orbit)
      echo "--frames-fields chi chi_minus_1 K lapse shift1 phi Pi Weyl4_Re Weyl4_Im Weyl4_Mag scalar_activity local_speed" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL}"
      ;;
    orbit-modes)
      echo "--frames-fields chi chi_minus_1 K lapse shift1 phi Pi Weyl4_Re Weyl4_Im Weyl4_Mag scalar_activity local_speed" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL} --scalar-modes 0 1 2"
      ;;
    bbh)
      echo "--frames-fields chi K lapse shift1 Weyl4_Re Weyl4_Im Weyl4_Mag" \
           "--frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL}"
      ;;
    chi)
      echo "--areal-radius --areal-min-radius 0.5" \
           "--frames-fields chi --frames-coord ${coord} --frames-zoom ${zoom} ${_WHM_FRAME_TAIL}"
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
  echo "headon headon-scout orbit orbit-modes bbh chi none"
}
