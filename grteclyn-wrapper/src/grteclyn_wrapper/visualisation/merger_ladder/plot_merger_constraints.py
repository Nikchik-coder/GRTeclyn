#!/usr/bin/env python3
"""Constraint-norm evolution for the merger campaign.

Own module, own output file: reads one or more ``constraint_norms.dat``
(SmallDataIO: time, L2[Ham], L2[Mom]) and draws the two stacked log panels
(Hamiltonian above, momentum below).  Accepts pre-stitched files covering a
restart chain; vertical markers annotate chain joins and the freeze engagement.

Usage:
  python -m grteclyn_wrapper.visualisation.merger_ladder.plot_merger_constraints \
      --run label:path/to/constraint_norms.dat [--run ...] \
      --vline 53:freeze --out plots/merger_constraints.png
"""
from __future__ import annotations

import argparse

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="append", required=True,
                    metavar="LABEL:PATH", help="label and constraint_norms.dat path")
    ap.add_argument("--vline", action="append", default=[],
                    metavar="TIME:LABEL", help="vertical marker, e.g. 53:freeze")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plt.rcParams.update({
        "font.family": "serif", "mathtext.fontset": "cm",
        "axes.labelsize": 14, "axes.titlesize": 16,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "axes.linewidth": 1.2,
    })
    fig, (ax_h, ax_m) = plt.subplots(2, 1, figsize=(12, 10), sharex=True,
                                     constrained_layout=True)
    for spec in args.run:
        label, path = spec.split(":", 1)
        d = np.loadtxt(path)
        ax_h.semilogy(d[:, 0], d[:, 1], lw=1.4, label=label)
        ax_m.semilogy(d[:, 0], d[:, 2], lw=1.4, label=label)
    for spec in args.vline:
        tval, vlab = spec.split(":", 1)
        for ax in (ax_h, ax_m):
            ax.axvline(float(tval), color="gray", ls="--", lw=0.9)
        ax_h.text(float(tval), ax_h.get_ylim()[1], " " + vlab, va="top",
                  fontsize=9, color="gray")
    ax_h.set_title(r"Hamiltonian Constraint: $\mathcal{H}$")
    ax_h.set_ylabel(r"$\|\mathcal{H}\|_{L^2}$")
    ax_m.set_title(r"Momentum Constraint: $\mathcal{M}^i$")
    ax_m.set_ylabel(r"$\|\mathcal{M}\|_{L^2}$")
    ax_m.set_xlabel(r"$t$ $[M]$")
    for ax in (ax_h, ax_m):
        ax.grid(True, which="both", ls="--", alpha=0.4)
        ax.legend()
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
