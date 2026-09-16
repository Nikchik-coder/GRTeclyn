#!/usr/bin/env python3
"""Constraints across a glued multi-leg series, and the overlap the legs share.

``plot_merger_constraints`` draws Hamiltonian and momentum in two stacked
panels for several arms.  This module answers a different question about ONE
arm that was run in legs at different resolutions:

  (a) the whole history on one axis, with EVERY step drawn faintly under a
      running median.  The raw trace matters here: a level-3 leg is punctuated
      by isolated one- and two-row regrid spikes -- 22 of them above 0.1, up to
      3.0, on the p = 0.12 spiral -- that a median would hide and a reader
      would otherwise meet as a surprise.  Drawing both says "these are single
      rows, the baseline is the bold line" without editing the data.
  (b) the window BOTH legs cover, one drawn thick and pale under the other, so
      the question "does refinement move the global constraints?" is answered
      by whether the thin curve leaves the thick one.  On the p = 0.12 spiral
      it does not: 1.3 % median difference in the Hamiltonian over t = 36-50,
      straight through the merger excursion.

Usage:
  python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_series_constraints \
      --series v2_spiral_d12_p012_L128_SERIES \
      --leg "level 3:v2_spiral_d12_p012_L128_lvl3_t050" \
      --leg "level 5:v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600" \
      --join 36 --out fig.png
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

STREAM = "constraint_norms.dat"


def resolve(spec: str) -> pathlib.Path:
    p = pathlib.Path(spec).expanduser()
    if p.is_file():
        return p
    base = p if p.is_dir() else find_packed(spec)
    for cand in (base / STREAM, base / "data" / STREAM):
        if cand.exists():
            return cand
    raise SystemExit(f"no {STREAM} under {base}")


def runmed(y: np.ndarray, w: int = 101) -> np.ndarray:
    from numpy.lib.stride_tricks import sliding_window_view
    w = max(3, w | 1)
    return np.median(sliding_window_view(np.pad(y, (w // 2, w // 2), mode="edge"), w), axis=-1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--series", required=True, help="the glued run NAME or its constraint_norms.dat")
    ap.add_argument("--leg", action="append", default=[], metavar="LABEL:NAME",
                    help="a leg, for the overlap panel; give it twice")
    ap.add_argument("--join", type=float, default=None, help="time the later leg takes over")
    ap.add_argument("--overlap", type=float, nargs=2, default=None,
                    metavar=("T0", "T1"), help="window for panel (b); default: where both legs exist")
    ap.add_argument("--median-window", type=int, default=101)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    c = np.loadtxt(resolve(args.series))
    c = c[np.argsort(c[:, 0])]
    t = c[:, 0]
    legs = []
    for spec in args.leg:
        lab, _, name = spec.partition(":")
        d = np.loadtxt(resolve(name))
        legs.append((lab, d[np.argsort(d[:, 0])]))

    style.typography(base=10.0)
    C1, C2 = "#1f4e79", "#7fb3d8"
    nrow = 2 if len(legs) >= 2 else 1
    fig, axes = plt.subplots(nrow, 1, figsize=(7.6, 4.6 * nrow), constrained_layout=True,
                             squeeze=False)
    a = axes[0][0]

    if args.join is not None:
        a.axvspan(t[0], args.join, color=style.GRID, lw=0, zorder=0)
        a.axvline(args.join, color=style.FAINT, ls=(0, (2, 2)), lw=0.8, zorder=1)
    for col, lab, colour in ((1, r"$\|\mathcal{H}\|_{L^2}$", C1),
                             (2, r"$\|\mathcal{M}\|_{L^2}$", C2)):
        a.semilogy(t, c[:, col], color=colour, lw=0.6, alpha=0.30, zorder=3)
        a.semilogy(t, runmed(c[:, col], args.median_window), label=lab,
                   color=colour, lw=2.0, zorder=5)
    a.set_xlim(t[0], t[-1])
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel(r"$\|\,\cdot\,\|_{L^2}$")
    style.legend(a, ncol=2, fontsize=8.5)
    if args.join is not None and legs:
        style.note(a, f"{legs[0][0]}  |  {legs[-1][0]}" if len(legs) > 1 else legs[0][0],
                   loc="lower left")

    if nrow == 2:
        b = axes[1][0]
        lo = max(l[1][0, 0] for l in legs)
        hi = min(l[1][-1, 0] for l in legs)
        if args.overlap:
            lo, hi = args.overlap
        # Thick and pale underneath, thin on top: the question is whether the
        # thin curve ever leaves the thick one.
        for j, (lab, d) in enumerate(legs):
            m = (d[:, 0] >= lo) & (d[:, 0] <= hi)
            first = (j == 0)
            for col, lab, colour in ((1, r"$\|\mathcal{H}\|_{L^2}$", C1),
                                     (2, r"$\|\mathcal{M}\|_{L^2}$", C2)):
                if first:
                    b.semilogy(d[m, 0], d[m, col], color=colour, lw=3.0,
                               alpha=0.28, solid_capstyle="round", zorder=3)
                else:
                    b.semilogy(d[m, 0], d[m, col], color=colour, lw=1.5,
                               label=lab, zorder=5)
        b.set_xlim(lo, hi)
        b.set_xlabel(r"$t\ [M]$")
        b.set_ylabel(r"$\|\,\cdot\,\|_{L^2}$")
        style.legend(b, ncol=2, fontsize=8.5)
        style.note(b, f"thick pale: {legs[0][0]}   thin: {legs[-1][0]}", loc="upper left")
        # The number the panel exists to produce.
        g = legs[0][1]
        f = legs[-1][1]
        mf = (f[:, 0] >= lo) & (f[:, 0] <= hi)
        gi = np.interp(f[mf, 0], g[:, 0], g[:, 1])
        rel = np.abs(f[mf, 1] - gi) / np.maximum(gi, 1e-300)
        print(f"  overlap {lo:.2f}-{hi:.2f}: median |dH|/H = {np.median(rel):.4f}")

    for row in axes:
        row[0].grid(True, which="major", color=style.GRID, lw=0.6)

    out = style.save(fig, args.out)
    print(f"saved {out} (+pdf)")


if __name__ == "__main__":
    main()
