#!/usr/bin/env python3
"""Redraw cached slices on a logarithmic scale, into their own directory.

Why this exists alongside ``rescale_frames.py``: that tool picks one *linear*
range per series, which is the right answer for a field whose interesting
values all sit within a factor of a few.  It is the wrong answer for a
wormhole.  chi runs from ~1 in the asymptotically flat region down to ~4e-7 at
the compactified far universe sitting on the grid centre -- six decades -- so
any linear map spends its whole colour range on the outer 10 % of the picture
and paints everything inside the throat solid black.  The one region the run is
about is the one region a linear frame cannot show.

So: read the same slice cache, render with a log (or symmetric-log, for signed
fields) norm, and write to ``frames_log/`` rather than over ``frames/``.  The
linear frames stay exactly as they were -- the two say different things and
both are worth keeping.

    logscale_frames.py <run>/frames [--only chi_z ...] [--ring R] [-j N]

``--ring`` draws a circle of that coordinate radius on every frame.  For a
drainhole it is the difference between a diagnostic and a picture: the throat
is a *ring* at rbar = 1.618 and the compactified origin is a *point* at the
centre, and which of the two goes first is the open question.  Without the ring
drawn on, a blob near the middle of the frame is not evidence of either.

Reads only the cache, writes only PNGs, and can be re-run against a live run as
often as wanted.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

# Signed fields: symmetric-log about zero with a diverging map, or the neutral
# colour lands at a non-zero value and invents a sign asymmetry.
SIGNED_FIELDS = {
    "K", "Weyl4_Re", "Weyl4_Im", "phi", "Pi", "shift1", "shift2", "shift3",
    "chi_minus_1",
}

PRETTY = {
    "chi": r"conformal factor $\chi$",
    "lapse": r"lapse $\alpha$",
    "K": r"trace of extrinsic curvature $K$",
}


def _series_paths(cache_root: str, series: str) -> list[str]:
    return sorted(glob.glob(os.path.join(cache_root, series, "slice_*.npz")))


def _load(path):
    with np.load(path, allow_pickle=False) as z:
        return (
            np.asarray(z["arr"], dtype=np.float64),
            np.asarray(z["extent"], dtype=np.float64),
            float(z["time"]),
        )


def _series_scale(paths: list[str], signed: bool, floor_percentile: float):
    """One scale for the whole series, measured over every cached frame."""
    mags = []
    for path in paths:
        try:
            arr, _, _ = _load(path)
        except (OSError, ValueError, KeyError):
            continue
        finite = np.abs(arr[np.isfinite(arr)])
        finite = finite[finite > 0.0]
        if finite.size:
            mags.append(finite.astype(np.float32).ravel())
    if not mags:
        return None
    values = np.concatenate(mags)
    hi = float(values.max())
    if hi <= 0.0:
        return None
    if signed:
        # linthresh: below this the symlog norm is linear.  Put it where the
        # bulk of the field still is, so the near-zero background does not get
        # stretched into visual noise.
        lin = float(np.percentile(values, floor_percentile))
        lin = max(lin, hi * 1e-8)
        return (lin, hi)
    lo = float(values.min())
    lo = max(lo, hi * 1e-12)  # a hard zero would break LogNorm
    return (lo, hi)


def _render(job):
    frames_dir, out_dir, series, field, axis, signed, scale, ring = job

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm, SymLogNorm

    cache_root = os.path.join(frames_dir, "_slice_cache")
    paths = _series_paths(cache_root, series)
    os.makedirs(out_dir, exist_ok=True)

    if signed:
        lin, hi = scale
        norm = SymLogNorm(linthresh=lin, vmin=-hi, vmax=hi, base=10)
        cmap = "RdBu_r"
    else:
        lo, hi = scale
        norm = LogNorm(vmin=lo, vmax=hi)
        cmap = "magma"

    label = PRETTY.get(field, field)
    written = 0
    for path in paths:
        try:
            arr, extent, time = _load(path)
        except (OSError, ValueError, KeyError):
            continue
        tag = os.path.basename(path).replace("slice_", "").replace(".npz", "")
        out = os.path.join(out_dir, f"frame_{axis}_{tag}.png")

        fig, ax = plt.subplots(figsize=(6.4, 5.6), dpi=110)
        # Centre the axes on the object: the cache stores absolute coordinates,
        # and "1.6 from the centre" is the only reading that matters here.
        cx = 0.5 * (extent[0] + extent[1])
        cy = 0.5 * (extent[2] + extent[3])
        rel = [extent[0] - cx, extent[1] - cx, extent[2] - cy, extent[3] - cy]
        im = ax.imshow(arr, origin="lower", extent=rel, norm=norm, cmap=cmap)
        if ring and ring > 0:
            ax.add_patch(plt.Circle((0.0, 0.0), ring, fill=False, lw=1.0,
                                    ls="--", ec="cyan", alpha=0.9))
            ax.plot([0.0], [0.0], marker="+", ms=8, mew=1.2, color="cyan")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"{label}   log scale   t = {time:.2f}")
        fig.colorbar(im, ax=ax, label=label)
        fig.tight_layout()
        fig.savefig(out)
        plt.close(fig)
        written += 1
    return (series, written, scale)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("frames_dir", help="the run's frames/ directory")
    ap.add_argument("--out", default=None,
                    help="output dir (default: <run>/frames_log)")
    ap.add_argument("--only", nargs="*", default=None,
                    help="limit to these <field>_<axis> series")
    ap.add_argument("--ring", type=float, default=None,
                    help="draw a dashed circle at this coordinate radius")
    ap.add_argument("--linthresh-percentile", type=float, default=50.0,
                    help="for signed fields, where the symlog scale stops "
                         "being linear (default: the median magnitude)")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    args = ap.parse_args(argv)

    frames_dir = os.path.abspath(args.frames_dir)
    cache_root = os.path.join(frames_dir, "_slice_cache")
    if not os.path.isdir(cache_root):
        print(f"no slice cache at {cache_root} -- the run needs "
              "--frames-cache-slices", file=sys.stderr)
        return 2

    out_root = args.out or os.path.join(os.path.dirname(frames_dir), "frames_log")

    jobs = []
    for series in sorted(os.listdir(cache_root)):
        if not os.path.isdir(os.path.join(cache_root, series)):
            continue
        if args.only and series not in args.only:
            continue
        field, _, axis = series.rpartition("_")
        if not field:
            field, axis = series, "z"
        paths = _series_paths(cache_root, series)
        if not paths:
            continue
        signed = field in SIGNED_FIELDS
        scale = _series_scale(paths, signed, args.linthresh_percentile)
        if scale is None:
            print(f"[log] {series}: no finite non-zero data, skipped")
            continue
        jobs.append((frames_dir, os.path.join(out_root, series), series,
                     field, axis, signed, scale, args.ring))
    if not jobs:
        print("no cached series selected", file=sys.stderr)
        return 1

    print(f"[log] {len(jobs)} series -> {out_root}")
    total = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for series, written, scale in pool.map(_render, jobs):
            total += written
            print(f"[log] {series}: {written} frames, scale "
                  f"{scale[0]:.3g} .. {scale[1]:.3g}")
    print(f"[log] {total} frames written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
