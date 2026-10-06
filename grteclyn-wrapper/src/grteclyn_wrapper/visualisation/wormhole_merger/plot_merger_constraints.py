#!/usr/bin/env python3
"""Constraint-norm evolution for the merger campaign.

Own module, own output file: reads one or more ``constraint_norms.dat``
(SmallDataIO: time, L2[Ham], L2[Mom]) and draws the two stacked log panels
(Hamiltonian above, momentum below).  Accepts pre-stitched files covering a
restart chain; vertical markers annotate chain joins and the freeze engagement.

Usage:
  python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_merger_constraints \
      --run label:seg[+seg...] [--run ...] \
      --vline 53:freeze --out plots/merger_constraints.png

A segment is a path, a bare run NAME (resolved in the pack wherever it is
filed -- never hard-code a path, the campaign is refiled as it grows), or
``NAME/file.dat`` for one of a run's other streams.  Several segments joined
with ``+`` are STITCHED into one curve: an arm that was continued by restarts
is one history, and the figure has to draw it as one.  Where two segments
overlap the later one wins, so a chain reads

    --run "wide seam:merge_orbit_flip_d12_r03000/constraint_norms__part1_t0-30.5.dat\
+merge_orbit_flip_d12_r03000+freeze_wide_t080_r05000"

Two curves that lie on top of each other is the usual result here, and it is
the result: the arms differ only in the seam width.  So the arms are drawn in
dash order, thinnest on top, and the panel keeps a linear-in-log grid rather
than the dense minor mesh that used to bury the difference.
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_packed  # noqa: E402


def resolve(spec: str) -> pathlib.Path:
    """A path as given, a run NAME (its constraint_norms.dat), or NAME/file."""
    p = pathlib.Path(spec).expanduser()
    if p.exists():
        return p
    name, _, tail = spec.partition("/")
    return find_packed(name) / (tail or "constraint_norms.dat")


def stitch(specs: list[str]) -> np.ndarray:
    """One history out of a restart chain: segments ordered by start time, the
    later one winning wherever two overlap.

    A restarted arm re-runs the units between the checkpoint it resumed from
    and where its parent died (here 50 -> 52), so the segments genuinely
    overlap; taking the later one keeps the branch that was actually continued
    rather than splicing in a dead end.
    """
    segs = sorted((np.loadtxt(resolve(s)) for s in specs), key=lambda a: a[0, 0])
    out = [segs[0]]
    for seg in segs[1:]:
        out[-1] = out[-1][out[-1][:, 0] < seg[0, 0]]
        out.append(seg)
    return np.vstack([s for s in out if len(s)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="append", required=True,
                    metavar="LABEL:PATH", help="label and constraint_norms.dat path (or run name)")
    ap.add_argument("--vline", action="append", default=[],
                    metavar="TIME:LABEL", help="vertical marker, e.g. 53:freeze")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    style.paper(base=10.0)
    fig, (ax_h, ax_m) = plt.subplots(2, 1, figsize=(7.6, 6.4), sharex=True,
                                     constrained_layout=True)
    for i, spec in enumerate(args.run):
        label, path = spec.split(":", 1)
        d = stitch(path.split("+"))
        # Drawn back to front so the first-named arm -- the subject -- sits on
        # top of the ones it is being compared with.
        kw = style.series(i)
        ax_h.semilogy(d[:, 0], d[:, 1], label=label, zorder=6 - i, **kw)
        ax_m.semilogy(d[:, 0], d[:, 2], zorder=6 - i, **kw)

    for spec in args.vline:
        tval, vlab = spec.split(":", 1)
        t = float(tval)
        for ax in (ax_h, ax_m):
            ax.axvline(t, color=style.FAINT, ls=(0, (2, 2)), lw=0.8, zorder=1)
        # Labels alternate high/low so a cluster of markers stays readable
        # instead of overprinting the way it did at t = 45 / 50 / 53.
        ax_h.annotate(vlab, (t, 1.0), xycoords=("data", "axes fraction"),
                      xytext=(2, -3), textcoords="offset points",
                      va="top", ha="left", rotation=90,
                      fontsize=8, color=style.MUTED)

    ax_h.set_ylabel(r"$\|\mathcal{H}\|_{L^2}$")
    ax_m.set_ylabel(r"$\|\mathcal{M}\|_{L^2}$")
    ax_m.set_xlabel(r"$t\ [M]$")
    for ax in (ax_h, ax_m):
        ax.grid(True, which="major", color=style.GRID, lw=0.6)
        ax.grid(True, which="minor", color=style.GRID, lw=0.3, alpha=0.6)
    if len(args.run) > 1:
        style.legend(ax_h)

    out = style.save(fig, args.out)
    print(f"saved {out} (+pdf)")


if __name__ == "__main__":
    main()
