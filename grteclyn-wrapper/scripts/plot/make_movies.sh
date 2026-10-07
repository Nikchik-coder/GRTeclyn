#!/usr/bin/env bash
# Stitch pre-rendered PNG frames into mp4 movies for one or more episode dirs.
#
# Robust to:
#   - gapped frame numbering (frame_z_0000.png, frame_z_0015.png, ...)
#   - mixed PNG pixel sizes (colorbar label width / zoom changes)
#   - unsorted ffmpeg glob demuxer order
#
# Each frame is pasted UNSCALED onto a fixed white canvas (the largest even WxH
# in that series), its bottom-left corner on the canvas's.  The frames are
# bbox-tight PNGs that differ only on the right, where a per-frame colour scale
# changes the width of the colour bar's tick labels, so the plot and the colour
# bar keep the same pixels in every frame.  Stretching each frame to one size
# (the old way) squeezed the wider frames sideways: the colour bar wobbled in
# every movie (2026-10-07).
#
# Usage:
#   make_movies.sh EPISODE_DIR [EPISODE_DIR ...] [--framerate N] [--only chi_z K_z] [--max-frame N]
#
# --max-frame N stitches only frames numbered <= N: the run's trust window
# (rerender_frames.py --t-max turns a time into the frame number).  Later
# frames stay on disk; they are just not in the movie.
#
# For each EPISODE_DIR it looks under <EPISODE_DIR>/frames/<field>_<axis>/frames/
# and writes <EPISODE_DIR>/movies/movie_<field>_<axis>.mp4
set -euo pipefail

FRAMERATE=10
MAX_FRAME=""
ONLY=()
DIRS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framerate) FRAMERATE="$2"; shift 2;;
    --max-frame) MAX_FRAME="$2"; shift 2;;
    --only) shift; while [[ $# -gt 0 && "$1" != --* ]]; do ONLY+=("$1"); shift; done;;
    *) DIRS+=("$1"); shift;;
  esac
done

if [[ ${#DIRS[@]} -eq 0 ]]; then
  echo "Usage: $0 EPISODE_DIR [EPISODE_DIR ...] [--framerate N] [--only chi_z K_z] [--max-frame N]" >&2
  exit 2
fi

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found on PATH" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 not found on PATH" >&2; exit 1; }

want() {  # $1 = folder name; returns 0 if selected
  [[ ${#ONLY[@]} -eq 0 ]] && return 0
  local f; for f in "${ONLY[@]}"; do [[ "$f" == "$1" ]] && return 0; done; return 1
}

# Resize every PNG to fill a fixed even canvas (stretch to WxH), write a sorted
# concat list, encode at constant resolution. Letterboxing alone still looks
# like the image shrinks/grows; fill-scale keeps the plot the same size.
encode_stable_movie() {
  local frames_dir="$1"
  local out="$2"
  local framerate="$3"
  local max_frame="${4:-}"
  python3 - "$frames_dir" "$out" "$framerate" "$max_frame" <<'PY'
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow (PIL) required to stabilize movie frames")

frames_dir = Path(sys.argv[1])
out = Path(sys.argv[2])
framerate = sys.argv[3]
max_frame = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None

def sort_key(p: Path) -> int:
    m = re.search(r"(\d+)\s*$", p.stem)
    return int(m.group(1)) if m else 0

pngs = sorted(frames_dir.glob("*.png"), key=sort_key)
if max_frame is not None:
    pngs = [p for p in pngs if sort_key(p) <= max_frame]
if not pngs:
    sys.exit(0)

sizes = [Image.open(p).size for p in pngs]
# The largest frame sets the canvas (even sides for yuv420p); nothing is scaled.
W = max(w for w, _ in sizes)
H = max(h for _, h in sizes)
W += W % 2
H += H % 2

with tempfile.TemporaryDirectory(prefix="movie_frames_") as tmp:
    tmp_path = Path(tmp)
    list_path = tmp_path / "concat.txt"
    with list_path.open("w", encoding="utf-8") as lst:
        for i, src in enumerate(pngs):
            im = Image.open(src).convert("RGB")
            # Unscaled, bottom-left on bottom-left, white padding right / top.
            canvas = Image.new("RGB", (W, H), (255, 255, 255))
            canvas.paste(im, (0, H - im.size[1]))
            dst = tmp_path / f"frame_{i:05d}.png"
            canvas.save(dst)
            lst.write(f"file '{dst.as_posix()}'\n")
            lst.write(f"duration {1.0 / float(framerate):.8f}\n")
        lst.write(f"file '{dst.as_posix()}'\n")

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(list_path),
        "-vsync", "vfr",
        "-r", str(framerate),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out),
    ]
    subprocess.run(cmd, check=True)

print(f"  canvas={W}x{H} (largest, frames unscaled) from {len(pngs)} frames, {len(set(sizes))} source sizes")
PY
}

made=0
for ep in "${DIRS[@]}"; do
  ep="${ep%/}"
  froot="${ep}/frames"
  movies_dir="${ep}/movies"
  [[ -d "$froot" ]] || { echo "[skip] no frames dir: $froot" >&2; continue; }
  mkdir -p "$movies_dir"
  for fd in "$froot"/*/; do
    field_axis="$(basename "$fd")"
    frames_dir="${fd%/}/frames"
    [[ -d "$frames_dir" ]] || continue
    want "$field_axis" || continue
    shopt -s nullglob
    pngs=("$frames_dir"/*.png)
    shopt -u nullglob
    [[ ${#pngs[@]} -gt 0 ]] || continue
    out="${movies_dir}/movie_${field_axis}.mp4"
    echo "[movie] $ep :: $field_axis (${#pngs[@]} frames${MAX_FRAME:+, up to frame $MAX_FRAME}) -> movies/$(basename "$out")"
    encode_stable_movie "$frames_dir" "$out" "$FRAMERATE" "$MAX_FRAME"
    made=$((made+1))
  done
done
echo "[done] wrote $made movie(s)"
