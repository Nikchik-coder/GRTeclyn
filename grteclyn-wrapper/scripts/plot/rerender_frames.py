#!/usr/bin/env python3
"""Redraw cached frames against one fixed colour scale per field.

Run after a simulation has finished, on a run launched with
``--frames-cache-slices``.  Every frame of a series is redrawn against a single
scale measured over the whole series, so the colourbar stops moving and a colour
means the same value in every frame -- which per-frame rescaling cannot give and
a first-frame lock gets wrong once the field grows.

    rerender_frames.py <episode>/frames [--movies] [--corner] [-v]

``--movies`` runs make_movies.sh over the episode afterwards.  ``--symlog``
names fields whose linear scale is dominated by one loud feature, so the quiet
structure elsewhere in the frame is visible too.

The cached slices are kept, so this can be re-run (with a hand-set scale, for
instance) without re-simulating.  Delete ``frames/_slice_cache/`` when the
movies are final.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("frames_dir", help="the episode's frames/ directory")
    ap.add_argument("--movies", action="store_true", help="stitch mp4s afterwards")
    ap.add_argument("--corner", action="store_true", help="corner mode (symmetry-reduced domains)")
    ap.add_argument(
        "--symlog",
        metavar="FIELDS",
        help="comma-separated fields to draw on a symmetric-log colour scale, or "
        "'all'.  Use it for a field whose range is set by one compact loud "
        "feature while the interesting physics is orders of magnitude quieter "
        "-- a merged core against the wave crossing the same slice.  Linear "
        "near zero (so a signed field's zero crossings stay readable), "
        "logarithmic outside.  A field may carry its own range as "
        "FIELD:DECADES, e.g. 'K,phi,Pi,Weyl4_Re:1.5'.",
    )
    ap.add_argument(
        "--symlog-decades",
        type=float,
        default=2.0,
        help="dynamic range a symlog frame shows below its peak (default 2). "
        "Beyond about three the quiet end is the field's numerical noise floor.",
    )
    ap.add_argument(
        "--only",
        metavar="FIELDS",
        help="redraw only these comma-separated fields (default: every cached one)",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
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
        print(
            f"no slice cache at {cache_root}\n"
            "The run must be launched with --frames-cache-slices; frames already "
            "rendered without it cannot be rescaled, because the plotfiles they "
            "came from are gone.",
            file=sys.stderr,
        )
        return 2

    norms = None
    field_decades = {}
    if args.symlog:
        norms = {}
        for item in (f.strip() for f in args.symlog.split(",")):
            if not item:
                continue
            name, _, dec = item.partition(":")
            norms["*" if name == "all" else name] = "symlog"
            if dec:
                field_decades[name] = float(dec)

    used = slice_cache.rerender_all(
        frames_dir, corner=args.corner, verbose=args.verbose, norms=norms,
        decades=args.symlog_decades, field_decades=field_decades,
        only=[f.strip() for f in args.only.split(",")] if args.only else None,
    )
    if not used:
        print("nothing was redrawn", file=sys.stderr)
        return 1
    print(f"[rerender] {len(used)} series redrawn at a fixed scale")

    if args.movies:
        episode = os.path.dirname(frames_dir)
        script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "make_movies.sh"
        )
        subprocess.run(["bash", script, episode], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
