#!/usr/bin/env python3
r"""The single-throat story on one strip: undeclared seed, its rate, declared seed.

The article's first two single-column figures merged into one two-column
``figure*`` at the top of the page (the user, 2026-09-18): panels (a)/(b)
are ``plot_branches``' resolution ladder -- one exact throat, two
resolutions, two fates, and the common exponential mode -- and panel (c) is
``plot_seed_branches``' declared-kick branching at one resolution.  Each
panel is drawn by ITS OWN module (``figure_panels`` / ``figure_panel``), so
this module owns nothing but the canvas, the lettering and the file; any
change to what a panel says belongs in its home module, where the provenance
notes live, and lands here on the next run.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_throat_row

STYLE: the seed-branches grammar on the full 7.05 in width; letter tags
above the frames, as on the collapse pages; the semantics and every number
stay in the caption and in the home modules' console prints.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import (  # noqa: E402
    plot_branches, plot_seed_branches, style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, RUNS_ROOT, figure_dir,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    # Two rows since 2026-09-23 (the user: "add the hamiltonian and momentum
    # constraints data"): the story strip on top, its constraint record below.
    fig = plt.figure(figsize=(7.05, 4.35), constrained_layout=True)
    gs = fig.add_gridspec(2, 6, height_ratios=[1.55, 1.0])
    axA = fig.add_subplot(gs[0, 0:2]); axB = fig.add_subplot(gs[0, 2:4])
    axC = fig.add_subplot(gs[0, 4:6])
    axD = fig.add_subplot(gs[1, 0:3]); axE = fig.add_subplot(gs[1, 3:6])
    plot_branches.figure_panels(axA, axB, pathlib.Path(args.pack_root).expanduser(),
                                legends=False)
    plot_seed_branches.figure_panel(axC, runs_root=args.runs_root)
    plot_seed_branches.figure_panels_constraints(axD, axE, args.pack_root)
    for ax, letter in zip((axA, axB, axC, axD, axE), "abcde"):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
    # ONE legend for the whole strip, on top (the user, 2026-09-23: the boxed
    # keys in (a)/(b) said the same thing twice and sat on the curves).  It
    # carries what is shared; panel-local identity stays written in place
    # ((c)'s kick names, (d)/(e)'s ceiling pair and control).
    from matplotlib.lines import Line2D  # local: only this canvas needs it
    handles = [
        Line2D([], [], color=style.INK, linewidth=1.4, linestyle=(0, (4, 2.5)),
               label="level 3"),
        Line2D([], [], color=style.INK, linewidth=1.4, linestyle=(0, ()),
               label="level 4"),
        Line2D([], [], color=style.GOLD, linewidth=1.9, label="fitted rate"),
        Line2D([], [], color=style.INK, linestyle="None", marker="X",
               markersize=5, markeredgecolor="white", markeredgewidth=0.8,
               label="death (NaN)"),
        Line2D([], [], color=style.INK, linestyle="None", marker="o",
               markersize=3, markeredgecolor="white", markeredgewidth=0.8,
               label="scan loses the throat"),
    ]
    fig.legend(handles=handles, loc="outside upper center", ncol=5,
               fontsize=7.5, frameon=False, handlelength=2.2,
               columnspacing=1.4, handletextpad=0.6)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("01_single_throat", args.pack_root) / "single_throat_instability.png")
    png = style.save(fig, out)
    print(f"[single-throat row] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
