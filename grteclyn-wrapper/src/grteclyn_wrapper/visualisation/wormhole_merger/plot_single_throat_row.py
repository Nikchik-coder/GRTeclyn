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
    PACK_ROOT, RUNS_ROOT, figure_dir, find_run,
)

# The amplitude ceiling on panel (c) (reviewer, 2026-09-24: "why is this not
# shown on Fig. 1?").  plot_seed_branches leaves the +-0.1 pair out of its
# branching panel on purpose -- they never branch -- so the canvas draws them
# on top, read from the PACK, in (d)/(e)'s grammar: heaviest weight, dash =
# sign, a cross where the run NaN'd.  What they show: both collapse (the
# oriented scans hold a MOTS from t = 1 and t = 6), the inward push after a
# re-expansion (3.15 -> 3.36 by t = 4) -- the rule "fate opposite to the push"
# fails at -0.1 -- and both die at the compactified origin (NaN in h11 on level
# 3, t = 14.06 / 15.17), as the +0.001 arm does at t = 40.07.  Evidence:
# grteclyn-wrapper/scripts/analysis/merger_feedback/c_eps01_fates.py.
CEILING_ARMS = (("single_eps_p1e1_t100", "+0.1"), ("single_eps_m1e1_t100", "-0.1"))

# The moving throat on panel (a) (the user, 2026-09-30: "update figure 1 with
# the boosted wormhole collapse").  One exact Lorentz-boosted drainhole
# (momentum model 1, p = 0.45, v = 0.41, level 3, the per-throat slicing
# freeze), read from the pack's round-scan A rows (horizon_scan.dat; the scan
# re-centres on the moving pit).  It rides R_star to t ~ 29 (+2.0 % at most),
# then collapses on the resting throat's mode (tau 5.5-5.7 against 5.88) and
# dies at t = 44.67 (NaN in h11): the level-3 branch, carried with the motion.
MOVING_ARM = "single_boost_p045_lbf_t050"


def moving_panel(axD, pack_root) -> None:
    """Panel (d): the boosted throat against the resting level-3 arm, zoomed.

    Overlaying the moving arm on (a) was unreadable (the user, 2026-09-30:
    "it's unclear what is what here"): at the full x-range its hold stretch
    lies on the resting curves and the tag floated over the cluster.  Here
    the two arms get their own window (t <= 47), each named in place; both
    are level 3, so the strip legend's dash grammar does not apply and the
    moving arm is dash-dot.
    """
    import numpy as np
    root = pathlib.Path(pack_root).expanduser()
    campaign = root / "campaign"
    try:
        d = find_run(campaign, MOVING_ARM)
    except FileNotFoundError:
        print(f"  {MOVING_ARM}: not in the pack, skipped"); return
    rows = np.loadtxt(d / "horizon_scan.dat", dtype=str)
    a = rows[rows[:, 1] == "A"][:, [0, 5]].astype(float)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    rest = plot_branches.load(root, plot_branches.ARMS["ml3"], "areal_radius.dat")
    rest = rest[rest[:, 0] <= 47.0]
    axD.axhline(plot_branches.R_EXACT, color=style.MUTED, linewidth=0.8,
                linestyle=(0, (1, 2.5)), zorder=2)
    axD.plot(rest[:, 0], rest[:, 1], color=style.CONTEXT, linewidth=1.4,
             linestyle=(0, ()), zorder=3)
    axD.plot(a[:, 0], a[:, 1], color=style.INK, linewidth=1.6,
             linestyle=(0, (4, 1.2, 1, 1.2)), zorder=3.5)
    axD.plot(a[-1, 0], a[-1, 1], "X", color=style.INK, markersize=5,
             markeredgecolor="white", markeredgewidth=0.8, zorder=4)
    axD.annotate(r"moving, $p=0.45$", (a[int(np.argmax(a[:, 1])), 0],
                 a[:, 1].max()), xytext=(-2, 4), textcoords="offset points",
                 fontsize=7, ha="center", va="bottom")
    # Under the hold stretch (t ~ 24), where the moving arm is on its hump
    # ABOVE R_star: the end of the curve carried the tag into its own fall.
    axD.text(24.0, 3.80, "at rest", fontsize=7, color=style.CONTEXT,
             ha="center", va="top")
    axD.set_xlim(0, 47)
    axD.set_ylim(3.45, 4.05)
    axD.set_xlabel(r"$t$")
    style.edge_label(axD, plot_branches.R_EXACT, r"$R_\star$")
    print(f"  moving   {MOVING_ARM:<28s} t = 0 .. {a[-1, 0]:6.2f}   "
          f"R {a[0, 1]:.4f} -> {a[:, 1].max():.4f} -> {a[-1, 1]:.4f}   (NaN)")


def ceiling_pair(ax, pack_root) -> None:
    """Draw the eps = +-0.1 arms onto panel (c) after its home module is done.

    The curves end at their last areal reading (t = 13 and 15, the plotfile
    cadence is one unit); the cross sits there, as for the +0.001 arm.  The
    t_x tag is moved to the LEFT of its rule: on the right the -0.1 arm's last
    segment runs through it.  Offsets are in points, so the clearances hold
    on the one-third-page panel.
    """
    campaign = pathlib.Path(pack_root).expanduser() / "campaign"
    ends = {}
    for name, label in CEILING_ARMS:
        try:
            d = find_run(campaign, name)
        except FileNotFoundError:
            print(f"  {name}: not in the pack, skipped"); continue
        a = plot_seed_branches.areal(d)
        if a is None or a.shape[0] < 3:
            continue
        ls = (0, (4, 2.5)) if label.startswith("+") else (0, ())
        ax.plot(a[:, 0], a[:, 1], color=style.INK, linewidth=2.1, linestyle=ls, zorder=3)
        if plot_seed_branches.died(d):
            ax.plot(a[-1, 0], a[-1, 1], "X", color=style.INK, markersize=5,
                    markeredgecolor="white", markeredgewidth=0.8, zorder=4)
        ends[label] = a
        print(f"  {label:>7s}  {name:<24s} t = 0 .. {a[-1, 0]:6.2f}   R {a[0, 1]:.2f} -> "
              f"{a[:, 1].max():.2f} -> {a[-1, 1]:.2f}" + ("   (NaN)" if plot_seed_branches.died(d) else ""))
    # ONE name for the pair, as in (d): right of the lower cross, under the
    # stalled +0.01 line, where the two crosses sit 0.8 apart.  Which is which
    # reads as for the other pairs: the kick offsets R(0) by ~2 eps (+0.1 starts
    # above R_star, -0.1 below) and the dash is the sign.  A second name above
    # +0.1's early hump was tried (2026-09-24): at a third of a page it ran into
    # the gold fit, and floated off the hump when moved clear.
    if ends:
        a = ends.get("-0.1", next(iter(ends.values())))
        ax.annotate(r"$\varepsilon=\pm0.1$", (a[-1, 0], a[-1, 1]), xytext=(5, -1),
                    textcoords="offset points", fontsize=8, ha="left", va="center")
    xlo, xhi = ax.get_xlim()
    for txt in ax.texts:
        if txt.get_text() == r"$t_\times$":
            x, y = txt.get_position()
            txt.set_position((x - 0.024 * (xhi - xlo), y))
            txt.set_horizontalalignment("right")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    # One row again since 2026-09-26 (the user: "extract the measurement
    # plots ... to the single plot in appendix"): the constraint record of
    # these arms, once row two here, is panels (a)/(b) of the appendix's
    # code-health figure (plot_constraint_evolution), drawn by the same
    # plot_seed_branches.figure_panels_constraints.
    fig = plt.figure(figsize=(7.05, 2.55), constrained_layout=True)
    gs = fig.add_gridspec(1, 4)
    axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])
    axC = fig.add_subplot(gs[0, 2]); axD = fig.add_subplot(gs[0, 3])
    plot_branches.figure_panels(axA, axB, pathlib.Path(args.pack_root).expanduser(),
                                legends=False)
    plot_seed_branches.figure_panel(axC, runs_root=args.runs_root)
    ceiling_pair(axC, args.pack_root)
    moving_panel(axD, args.pack_root)
    for ax, letter in zip((axA, axB, axC, axD), "abcd"):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
    # ONE legend for the whole strip, on top (the user, 2026-09-23: the boxed
    # keys in (a)/(b) said the same thing twice and sat on the curves).  It
    # carries what is shared; panel-local identity stays written in place
    # ((c)'s kick names).
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
    style.label_audit(fig)      # prints every text box a drawn line crosses
    png = style.save(fig, out)
    print(f"[single-throat row] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
