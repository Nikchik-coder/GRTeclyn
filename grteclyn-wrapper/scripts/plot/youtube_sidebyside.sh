#!/usr/bin/env bash
# Build upload-ready 1080p side-by-side movies: matter (left) beside geometry
# (right), from the CLEAN masters -- never from the already-watermarked copies,
# which would stack two title bars.
#
# Each output carries one header spanning both panels, a per-panel label, the
# playback-speed note, a caption saying what the viewer is looking at, and an
# ownership mark inside EACH panel's plot area (cropping one away also crops
# the data). The mark is outlined so it reads on the light RdBu geometry panel
# as well as the dark viridis matter panel.
#
# Usage: youtube_sidebyside.sh SRC_DIR [DEST_DIR]
set -euo pipefail

SRC="${1:?usage: youtube_sidebyside.sh SRC_DIR [DEST_DIR]}"
DEST="${2:-$(dirname "${SRC%/}")/_youtube}"
MARK="${WATERMARK_LINE1:-Gravity Frontiers}"
SPEED="${SPEED:-2}"
SRC_FPS="${SRC_FPS:-10}"
CREDIT="${CREDIT:-GRTeclyn  ·  3+1 numerical relativity  ·  constraint-solved initial data}"

FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
FONTB=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
command -v ffmpeg >/dev/null || { echo "ffmpeg not found" >&2; exit 1; }

# Cells by their revision names (2026-10-26; the v1 set, on the first-order time integration, is in
# runs/bondi/00_archive/superseded_2026-10-23/movies/).
title_for() {
  case "$1" in
    PM10_L64_N256*)               echo "Bondi dipole runaway — mixed pair, separation 10";;
    PM10_L64_N128_t400*)          echo "Bondi dipole runaway — carried to t = 400";;
    PM10-rec_*_t1000*)            echo "Bondi dipole runaway — followed to t = 1000";;
    PP10_*)                       echo "Control — two positive-mass stars";;
    MM10_*)                       echo "Control — two negative-mass stars";;
    *)                            echo "${1//_/ }";;
  esac
}
# Two caption lines. The physics point of the whole set is WHY the same-sign
# pairs merge: both stars are the same scalar field, so their profiles overlap
# in the self-interaction potential, and that binding term is far stronger than
# gravity and blind to the sign of the mass. The mixed pair has no such term,
# which is what makes it the clean gravitational case. Say so on the frame.
caption1_for() {
  case "$1" in
    PM10_L64_N256*)               echo "A positive-mass and a negative-mass boson star, released at rest. Neither falls toward the other — the pair accelerates off together.";;
    PM10_L64_N128_t400*)          echo "The same mixed pair on a coarser grid, carried twice as long, to t = 400. Both stars keep accelerating in the same direction.";;
    PM10-rec_*_t1000*)            echo "The mixed pair carried to t = 1000; the box moves with it, so the stars stay in view. They travel 63 units and reach 0.11 c.";;
    PP10_*)                       echo "Both masses positive. They attract, fall together, and merge at t = 34.4.";;
    MM10_*)                       echo "Both masses negative. Newtonian gravity says they should repel — they merge anyway, at t = 33.6.";;
    *)                            echo "";;
  esac
}
caption2_for() {
  case "$1" in
    PM10_L64_N256*)               echo "The two stars are different scalar fields with no cross-term in the potential, so no binding force exists between them — gravity is their only interaction.";;
    PM10_L64_N128_t400*)          echo "The gap widens slowly (10 to 10.9) and the acceleration fades: that is the coarse grid's error, about four times smaller on a 1.5× finer grid.";;
    PM10-rec_*_t1000*)            echo "The gap widens from 10 to 13.5 by the end: that is the grid's error, not gravity, and it shrinks quickly as the grid is refined.";;
    PP10_*)                       echo "Both stars are the SAME scalar field, so where their profiles overlap the field itself pulls them together — a direct force much stronger than gravity.";;
    MM10_*)                       echo "Same cause: identical fields overlapping, and that pull is blind to the sign of the mass. What collapses them is not gravity.";;
    *)                            echo "";;
  esac
}

mkdir -p "$DEST"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
OUT_FPS="$(awk -v f="$SRC_FPS" -v s="$SPEED" 'BEGIN{print f*s}')"
made=0; failed=0

for celldir in "$SRC"/*/; do
  cell="$(basename "$celldir")"
  L="${celldir}movie_scalar_activity_z.mp4"
  R="${celldir}movie_chi_minus_1_z.mp4"
  [[ -f "$L" && -f "$R" ]] || { echo "[skip] $cell — needs both matter and geometry" >&2; continue; }

  printf '%s' "$(title_for "$cell")"        > "$tmp/t1"
  printf 'MATTER  ·  scalar field activity' > "$tmp/t2"
  printf 'GEOMETRY  ·  conformal factor'    > "$tmp/t3"
  if [[ "$SPEED" == "1" ]]; then printf 'real time'; else printf '%sx speed' "$SPEED"; fi > "$tmp/t4"
  printf '%s' "$MARK"                       > "$tmp/t5"
  printf '%s' "$(caption1_for "$cell")"     > "$tmp/t6"
  printf '%s' "$(caption2_for "$cell")"     > "$tmp/t8"
  printf '%s' "$CREDIT"                     > "$tmp/t7"

  if ffmpeg -v error -y -i "$L" -i "$R" -filter_complex "\
[0:v]setpts=PTS/${SPEED},scale=-2:860:flags=lanczos[a];\
[1:v]setpts=PTS/${SPEED},scale=-2:860:flags=lanczos[b];\
[a][b]hstack=inputs=2[s];\
[s]scale=1880:-2:flags=lanczos[sc];\
[sc]pad=1920:1080:(ow-iw)/2:118:color=0x0E1216[p];\
[p]drawtext=fontfile=${FONTB}:textfile=${tmp}/t1:fontcolor=white:fontsize=34:x=(w-tw)/2:y=22,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t2:fontcolor=0x7FD4A8:fontsize=20:x=(w/2-tw)/2:y=80,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t3:fontcolor=0x8FB8E8:fontsize=20:x=w/2+(w/2-tw)/2:y=80,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t4:fontcolor=0xE8B44A:fontsize=22:x=w-tw-28:y=24,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t5:fontcolor=white@0.32:bordercolor=black@0.30:borderw=1:fontsize=27:x=w*0.215-tw/2:y=h*0.60,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t5:fontcolor=white@0.42:bordercolor=black@0.34:borderw=1:fontsize=27:x=w*0.695-tw/2:y=h*0.60,\
drawtext=fontfile=${FONT}:textfile=${tmp}/t6:fontcolor=0xD5DEE7:fontsize=21:x=(w-tw)/2:y=h-104,\
drawtext=fontfile=${FONT}:textfile=${tmp}/t8:fontcolor=0x9FB0C0:fontsize=19:x=(w-tw)/2:y=h-70,\
drawtext=fontfile=${FONT}:textfile=${tmp}/t7:fontcolor=0x5C6773:fontsize=16:x=(w-tw)/2:y=h-32[v]" \
      -map "[v]" -r "$OUT_FPS" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow \
      -movflags +faststart "${DEST}/${cell}.mp4" 2>"$tmp/err"; then
    echo "[ok]   ${cell}.mp4"; made=$((made+1))
  else
    echo "[fail] ${cell}: $(head -1 "$tmp/err")" >&2; failed=$((failed+1))
  fi
done
echo "[all] wrote $made file(s) to $DEST, $failed failed"
