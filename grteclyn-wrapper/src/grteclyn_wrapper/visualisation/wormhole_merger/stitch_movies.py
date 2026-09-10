#!/usr/bin/env python3
"""Stitch the cached slices of SEVERAL runs into one movie per field, on one
fixed colour scale.  Use it when a run was continued by a restart (a finer
grid, a coarser grid, a different interior fill) and the whole history should
play as one movie.

Usage:
  python -m grteclyn_wrapper.visualisation.wormhole_merger.stitch_movies \\
      [--runs-root DIR] [--out DIR] RUN_1 T_1 RUN_2 [T_2 RUN_3 ...]

  RUN_1 contributes its cached slices with t <= T_1, RUN_2 those with
  T_1 < t <= T_2, and the last run everything after the final switch time.
  --runs-root  where the runs live (default: <repo>/runs/wormhole_merger); a run
               is found by name wherever it is filed (top level or NN_group/)
  --out DIR    where to build (default: <last run>/stitched_from_t0, in the run tree)
  --symlog F   comma-separated fields to draw on a symmetric-log colour scale
               (or "all").  A stitched series spans the whole history, so one
               linear scale is set by the loudest moment -- the merged core --
               and everything quieter is white: on the head-on stitch that is
               the entire approach phase and the whole ringdown wave.  Symlog
               shows both.  Default for the merger fields: "K,phi,Pi,Weyl4_Re:2"
               -- chi and lapse are bounded and read correctly on a linear
               scale.  A field may carry its own range as FIELD:DECADES, and
               Weyl4 needs one: how deep to go depends on what sets the peak.
               A stitch that starts at t = 0 is scaled by the initial-data junk,
               about 3x the merger burst, so the ringdown needs two decades to
               show; a single run starting after the junk reads better at 1.5,
               where two would be mostly the coarse grid's own noise.  Check a
               late frame and adjust rather than trusting either number.
  --symlog-decades N   default range for fields that do not name one (default 2)

Example (2026-09-09, the head-on: level 3 -> level 5 through the merger -> level 3):
  python -m grteclyn_wrapper.visualisation.wormhole_merger.stitch_movies \\
      merge_headon_flip_d8_v1c_latefreeze_t100 22 \\
      merge_headon_flip_d8_v1_lvl5_t100_r02200 35 \\
      merge_headon_flip_d8_v1_lvl3down_t100_r03500

What it does:
  1. under <out>/frames/_slice_cache/<field>/ it SYMLINKS each run's slices for
     its own stretch of time (slice files are slice_NNNN.npz with NNNN = 100 * t,
     so time order is name order), after clearing the previous build's links AND
     its rendered PNGs -- otherwise frames from an earlier, longer segment survive
     at times the new segment does not cover and end up in the movie;
  2. runs grteclyn-wrapper/scripts/plot/rerender_frames.py --movies on that
     folder: every frame of a field is drawn on ONE scale measured over the whole
     stitched series, then make_movies writes <out>/movies/movie_<field>.mp4.
Re-run it after any segment advances; it is idempotent.  Only fields cached by
EVERY segment are stitched.  Frame cadence follows each run's plot interval and
the movie plays at a fixed frame rate, so a segment written every 0.5 units runs
at half speed.  The movies stay in the run tree (runs/ is not in git; do not
copy them into results/).
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_run

# …/GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger
REPO = pathlib.Path(__file__).resolve().parents[5]
RERENDER = REPO / "grteclyn-wrapper" / "scripts" / "plot" / "rerender_frames.py"


def slice_index(path: pathlib.Path) -> int:
    """slice_NNNN.npz -> NNNN (= 100 * t)."""
    return int(path.stem.split("_", 1)[1])


def parse_segments(items: list[str]) -> tuple[list[str], list[float]]:
    """RUN T RUN [T RUN ...] -> (runs, switch times)."""
    if len(items) < 3 or len(items) % 2 == 0:
        raise SystemExit("need RUN_1 T_1 RUN_2 [T_2 RUN_3 ...] (an odd number of items, at least 3)")
    runs = [r.rstrip("/") for r in items[0::2]]
    switches = [float(t) for t in items[1::2]]
    if switches != sorted(switches):
        raise SystemExit(f"switch times must increase: {switches}")
    return runs, switches


def segment_bounds(i: int, switches: list[float]) -> tuple[float | None, float | None]:
    """Lower (exclusive) and upper (inclusive) time of segment i; None = open."""
    lo = switches[i - 1] if i > 0 else None
    hi = switches[i] if i < len(switches) else None
    return lo, hi


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-root", default=str(REPO / "runs" / "wormhole_merger"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--symlog", default="K,phi,Pi,Weyl4_Re:2",
                    help="fields on a symmetric-log scale, 'all', or '' for none")
    ap.add_argument("--symlog-decades", type=float, default=2.0)
    ap.add_argument("segments", nargs="+", metavar="RUN|T", help="RUN_1 T_1 RUN_2 [T_2 RUN_3 ...]")
    args = ap.parse_args(argv)

    runs_root = pathlib.Path(args.runs_root).expanduser().resolve()
    runs, switches = parse_segments(args.segments)
    # runs are resolved by name wherever they are filed (top level or a group)
    run_dirs = [find_run(runs_root, r) for r in runs]
    caches = [d / "frames" / "_slice_cache" for d in run_dirs]
    for c in caches:
        if not c.is_dir():
            raise SystemExit(f"no slice cache under {c.parent}")
    out = pathlib.Path(args.out).expanduser() if args.out else run_dirs[-1] / "stitched_from_t0"
    out = out.resolve()

    print("segments:")
    for i, r in enumerate(runs):
        lo, hi = segment_bounds(i, switches)
        print(f"  {r:<46s} t {lo if lo is not None else 0} .. {hi if hi is not None else 'end'}")

    # fields cached by every segment
    fields = None
    for c in caches:
        names = {p.name for p in c.iterdir() if p.is_dir()}
        fields = names if fields is None else fields & names
    fields = sorted(fields or [])
    if not fields:
        raise SystemExit("no field is cached by every segment")

    (out / "frames" / "_slice_cache").mkdir(parents=True, exist_ok=True)
    for f in fields:
        dst = out / "frames" / "_slice_cache" / f
        dst.mkdir(exist_ok=True)
        for old in dst.glob("slice_*.npz"):
            old.unlink()
        for png in (out / "frames" / f / "frames").glob("*.png"):
            png.unlink()
        counts = []
        for i, c in enumerate(caches):
            lo, hi = segment_bounds(i, switches)
            lo_i = -1 if lo is None else int(round(lo * 100))
            hi_i = 10**9 if hi is None else int(round(hi * 100))
            n = 0
            for p in sorted((c / f).glob("slice_*.npz")):
                s = slice_index(p)
                if lo_i < s <= hi_i:
                    (dst / p.name).symlink_to(p.resolve())
                    n += 1
            counts.append(f"{n} from {runs[i]}")
        print(f"  {f}: " + "; ".join(counts) + f"; total {len(list(dst.glob('slice_*.npz')))}")

    cmd = [sys.executable, str(RERENDER), str(out / "frames"), "--movies"]
    if args.symlog:
        cmd += ["--symlog", args.symlog, "--symlog-decades", str(args.symlog_decades)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    for line in proc.stdout.splitlines() + proc.stderr.splitlines():
        if line.startswith(("[rerender]", "[movie]", "[done]")):
            print(line)
    if proc.returncode != 0:
        print(proc.stderr[-2000:], file=sys.stderr)
        return proc.returncode
    movies = out / "movies"
    print(f"movies: {movies}/")
    for m in sorted(movies.glob("*.mp4")) if movies.is_dir() else []:
        print(f"  {m.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
