#!/usr/bin/env python3
"""Redraw cached frames on a whole-series scale that clips nothing.

Why this exists alongside ``rerender_frames.py``:

``rerender_frames.py`` fixes the colourbar by taking the *envelope of each
frame's own auto-scale*, and that auto-scale is a 99.5th-percentile cut meant
to stop stray outliers setting the range.  For a compact object in a large
mostly-empty box the object itself is a fraction of a percent of the pixels, so
the cut lands inside the object and flattens exactly the structure the movie is
about.  Measured on FMAX-RM: it discarded the top 12% of chi's range, 26% of
local_speed's, and 88% of scalar_activity's.

Checking whether the tail was numerical noise or real structure settled it --
the distributions have no break, they just slide (chi's 99.9/99.99/99.999
percentiles are 1.29/1.34/1.38 against a true max of 1.445).  There is nothing
to reject, so the default here clips nothing at all.

    rescale_frames.py <episode>/frames [--percentile P] [--only chi_z ...] [-j N]

``--percentile`` trades honesty for contrast if a field really does have a
pathological spike; 100 (the default) is the true range.  Signed fields are
scaled symmetrically about zero so the diverging colourmaps stay centred.

Reads only the slice cache, so it can be re-run with a different rule as often
as wanted without re-simulating.
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

# Signed fields drawn with a diverging colourmap: an off-centre scale would put
# the neutral colour at a non-zero value and invent a sign asymmetry.
SYMMETRIC_FIELDS = {
    "Weyl4_Re", "Weyl4_Im", "phi", "Pi",
    "phi_lump0", "Pi_lump0", "phi_lump1", "Pi_lump1", "phi_lump2", "Pi_lump2",
    "chi_minus_1", "shift1", "rho_req",
}


def _series_scale(cache_root: str, field: str, axis: str, percentile: float):
    """Limits over every cached frame of one series, not frame by frame."""
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames import (
        slice_cache,
    )

    paths = slice_cache.cached_series(os.path.dirname(cache_root), field, axis)
    chunks = []
    for path in paths:
        try:
            arr, _, _, _ = slice_cache.load_slice(path)
        except (OSError, ValueError):
            continue
        finite = arr[np.isfinite(arr)]
        if finite.size:
            chunks.append(finite.astype(np.float32).ravel())
    if not chunks:
        return None
    values = np.concatenate(chunks)

    if field in SYMMETRIC_FIELDS:
        mag = (
            float(np.abs(values).max())
            if percentile >= 100.0
            else float(np.percentile(np.abs(values), percentile))
        )
        if mag <= 0.0:
            return None
        return (-mag, mag)

    if percentile >= 100.0:
        lo, hi = float(values.min()), float(values.max())
    else:
        lo = float(np.percentile(values, 100.0 - percentile))
        hi = float(np.percentile(values, percentile))
    if hi <= lo:
        return None
    return (lo, hi)


def _do_series(job):
    frames_dir, field, axis, percentile, corner = job
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src")
    )
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames import (
        slice_cache,
    )

    cache_root = os.path.join(frames_dir, slice_cache.CACHE_DIR_NAME)
    scale = _series_scale(cache_root, field, axis, percentile)
    if scale is None:
        return (f"{field}_{axis}", 0, None)
    written, used = slice_cache.rerender_series(
        frames_dir, field, axis, zlim=scale, corner=corner
    )
    return (f"{field}_{axis}", written, used)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("frames_dir", help="the episode's frames/ directory")
    ap.add_argument("--percentile", type=float, default=100.0,
                    help="upper cut; 100 = clip nothing (default)")
    ap.add_argument("--only", nargs="*", default=None,
                    help="limit to these <field>_<axis> series")
    ap.add_argument("-j", "--jobs", type=int, default=8)
    ap.add_argument("--corner", action="store_true")
    args = ap.parse_args(argv)

    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src")
    )
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames import (
        slice_cache,
    )

    frames_dir = os.path.abspath(args.frames_dir)
    cache_root = os.path.join(frames_dir, slice_cache.CACHE_DIR_NAME)
    if not os.path.isdir(cache_root):
        print(f"no slice cache at {cache_root}", file=sys.stderr)
        return 2

    jobs = []
    for field, axis in slice_cache.cached_fields(frames_dir):
        if args.only and f"{field}_{axis}" not in args.only:
            continue
        jobs.append((frames_dir, field, axis, args.percentile, args.corner))
    if not jobs:
        print("no cached series selected", file=sys.stderr)
        return 1

    print(f"[rescale] {len(jobs)} series, percentile={args.percentile}, jobs={args.jobs}")
    total = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for name, written, used in pool.map(_do_series, jobs):
            if not written:
                print(f"[rescale] {name}: skipped")
                continue
            total += written
            print(f"[rescale] {name}: {written} frames at {used[0]:.6g} .. {used[1]:.6g}")
    print(f"[rescale] {total} frames redrawn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
