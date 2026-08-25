#!/usr/bin/env bash
# Burn a title bar and an ownership mark into finished campaign movies.
#
# Each output gets:
#   - a dark band above the plot naming the cell and the field, so a movie
#     that has been downloaded and renamed still says what it is;
#   - the playback-speed note, top right -- these are retimed to 2x, and a
#     viewer who does not know that will misread every timescale in them.
#     No frame index is drawn: the plot already carries `t =`, which is the
#     number worth quoting, and a bare integer beside "2x speed" reads as
#     though it qualifies the speed;
#   - a semi-transparent mark placed INSIDE the plot area, on empty
#     background, so cropping it away also crops the axes.
#
# Originals are never modified. Usage:
#   watermark_movies.sh SRC_DIR [DEST_DIR]
# SRC_DIR holds one folder per cell, each holding movie_<field>.mp4.
set -euo pipefail

SRC="${1:?usage: watermark_movies.sh SRC_DIR [DEST_DIR]}"
DEST="${2:-${SRC%/}_watermarked}"
MARK1="${WATERMARK_LINE1:-Gravity Frontiers}"
# Second mark line is optional and empty by default -- set WATERMARK_LINE2 to
# add one (a URL, an affiliation). Empty means the filter is not emitted.
MARK2="${WATERMARK_LINE2:-}"
# Playback speed multiplier. 2 => half the wall-clock, same frames, and the
# header says so. Set SPEED=1 for real time.
SPEED="${SPEED:-2}"
SRC_FPS="${SRC_FPS:-10}"

FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
FONTB=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
[[ -f "$FONT" && -f "$FONTB" ]] || { echo "DejaVu fonts not found" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg not found" >&2; exit 1; }

# Human title for a cell directory name.
cell_title() {
  case "$1" in
    runaway_pair_d08_*)            echo "Bondi dipole runaway — mixed pair, d = 8";;
    runaway_pair_d10_L64_N256_*)   echo "Bondi dipole runaway — mixed pair, d = 10 (fine grid)";;
    runaway_pair_d10_*)            echo "Bondi dipole runaway — mixed pair, d = 10";;
    runaway_pair_d12_*)            echo "Bondi dipole runaway — mixed pair, d = 12";;
    runaway_pair_d16_*)            echo "Bondi dipole runaway — mixed pair, d = 16";;
    longrun_pair_d10_t400_*)       echo "Bondi dipole runaway — d = 10, carried to t = 400";;
    control_pair_pp_*)             echo "Control — two canonical stars, they merge";;
    control_pair_mm_*)             echo "Control — two phantom stars, they merge too";;
    nomill_left_pair_*)            echo "Control — static box, no recentring, to t = 600";;
    chase03c_pair_*)               echo "Recentring box — the 0.3c chase to t = 784";;
    control_lone_phantom_t1000_*)  echo "Control — one lone phantom star, to t = 1000";;
    *)                             echo "${1//_/ }";;
  esac
}

# Human label for a field name (movie_<field>.mp4).
field_label() {
  case "$1" in
    scalar_activity_z)        echo "matter — scalar field activity, mid-plane slice";;
    scalar_activity_proj_y)   echo "matter — scalar field activity, projected along y";;
    scalar_activity_proj_z)   echo "matter — scalar field activity, projected along z";;
    chi_minus_1_z)            echo "geometry — conformal factor chi minus 1, mid-plane slice";;
    chi_z)                    echo "geometry — conformal factor chi, mid-plane slice";;
    phi_lump0_z)              echo "scalar field of star 0, signed, mid-plane slice";;
    shift1_z)                 echo "gauge — shift vector x-component, mid-plane slice";;
    local_speed_z)            echo "local coordinate speed, mid-plane slice";;
    Weyl4_Mag_z)              echo "curvature Psi4 magnitude — near zone only, not a waveform";;
    Weyl4_Re_z)               echo "curvature Psi4 real part — near zone only, not a waveform";;
    Weyl4_Im_z)               echo "curvature Psi4 imaginary part — near zone only, not a waveform";;
    *)                        echo "${1//_/ }";;
  esac
}

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
made=0; failed=0
for celldir in "$SRC"/*/; do
  cell="$(basename "$celldir")"
  outdir="${DEST}/${cell}"; mkdir -p "$outdir"
  title="$(cell_title "$cell")"
  for mv in "$celldir"movie_*.mp4; do
    [[ -e "$mv" ]] || continue
    base="$(basename "$mv")"; field="${base#movie_}"; field="${field%.mp4}"
    # textfile= avoids ffmpeg's filtergraph escaping rules entirely.
    printf '%s' "$title"                                   > "$tmp/t1"
    printf '%s   |   %s' "$(field_label "$field")" "GRTeclyn 3+1 NR" > "$tmp/t2"
    if [[ "$SPEED" == "1" ]]; then printf 'real time'; else printf '%sx speed' "$SPEED"; fi > "$tmp/t5"
    printf '%s' "$MARK1"                                   > "$tmp/t3"
    MARK2_FILTER=""
    if [[ -n "$MARK2" ]]; then
      printf '%s' "$MARK2" > "$tmp/t4"
      MARK2_FILTER=",drawtext=fontfile=${FONT}:textfile=${tmp}/t4:fontcolor=white@0.30:bordercolor=black@0.26:borderw=1:fontsize=12:x=(w-tw)/2:y=h*0.80+26"
    fi
    if ffmpeg -v error -y -i "$mv" -vf "\
setpts=PTS/${SPEED},\
pad=iw:ih+52:0:52:color=0x101418,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t1:fontcolor=white:fontsize=17:x=12:y=9,\
drawtext=fontfile=${FONT}:textfile=${tmp}/t2:fontcolor=0x9AA5B1:fontsize=12:x=12:y=32,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t5:fontcolor=0xE8B44A:fontsize=13:x=w-tw-12:y=11,\
drawtext=fontfile=${FONTB}:textfile=${tmp}/t3:fontcolor=white@0.34:bordercolor=black@0.30:borderw=1:fontsize=22:x=(w-tw)/2:y=h*0.80${MARK2_FILTER}\
" -r "$(awk -v f="$SRC_FPS" -v s="$SPEED" 'BEGIN{print f*s}')" \
         -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart "${outdir}/${base}" 2>"$tmp/err"; then
      made=$((made+1))
    else
      failed=$((failed+1)); echo "[fail] $cell/$base: $(head -1 "$tmp/err")" >&2
    fi
  done
  echo "[done] $cell"
done
echo "[all] wrote $made movie(s) to $DEST, $failed failed"
