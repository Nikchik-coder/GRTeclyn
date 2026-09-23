#!/usr/bin/env python3
r"""The p = 0.12 spiral's wall: refinement from one checkpoint, then every other start.

The article's Fig. for sec:spiral:wall, a two-column strip since 2026-09-23 (the
user: the gauge arms "have a different start time -- we can have a second plot,
so it is two columns like the other figures").

(a) THE LADDER.  Every arm starts from ONE t = 50 state and raises max_level;
every one dies on an h11 NaN.  The gains saturate: +1.03, +2.51, +0.53, +0.06
units per doubling in the plain family -- sixteen times the resolution buys 4.13
units -- and the half-time-step control gains +0.36 on its own level-5 twin, so
the top of the ladder is saturation evidence, not a converged limit.  The
core-damping family is joined over levels 4-6 only, the rungs that share one
configuration (its level-3 member ran a different, never-engaging window --
see refinement_ladder.dat).

(b) THE SAME WALL, OTHER GAUGES AND OTHER STARTS.  One row per gauge on a
common death clock: the filled dot is level 3 from t = 0 -- 43.6 (-alpha K),
49.0 (-2 alpha^2 K), 52.1 (standard), 61.9 (eta = 4) -- and each open marker a
level-5 arm, tagged with the time t0 at which its level 5 was switched on
(diamond: the doubled box, L = 128).  Planting level 5 earlier buys nothing
within one configuration (standard L = 128: 59.94 from t0 = 0, 60.45 from 36;
eta = 4: 60.04 from 50, 60.05 from 60); eta 4's level 5 dies BELOW its own
level-3 clock; and like for like -- same box, level 5 from t0 = 50 -- the
standard gauge dies at 55.60 (panel (a)'s rung) against eta 4's 60.04.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_ladder

Reads ``campaign/05_binary_spiral/refinement_ladder.dat`` (a) and
``campaign/05_binary_spiral/wall_clocks.dat`` (b), both built from the run logs.

STYLE: seed-branches grammar on the full 7.05 in; letter tags above the frames;
families named in place, offsets in POINTS; no accent -- there is no horizon
instrument on this figure.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "05_binary_spiral"
# The rows of (b), named by the ONE knob each changes off the standard gauge.
# The lapse is evolved as d_t alpha = -c alpha^p (K - 2 Theta) + beta.grad alpha
# (Source/CCZ4/MovingPunctureGauge.hpp; lapse_coeff = c, lapse_power = p), the
# shift by the Gamma-driver with damping eta: standard is c = 2, p = 1, eta = 1
# (1+log).  Two rows change the LAPSE and one the SHIFT, so the axis title
# is the gauge condition, not the lapse; the rows are named by their driver
# (the user, 2026-09-23: these names "were fine"), dropping the CCZ4 Theta
# as the article does.
GAUGE_NAME = {
    "lc1": r"$\partial_t\alpha=-\alpha K$",
    "lp2": r"$\partial_t\alpha=-2\alpha^{2}K$",
    "std": "standard",
    "eta4": r"$\eta=4$",
}


def _rows(path: pathlib.Path) -> list[list[str]]:
    return [ln.split() for ln in path.read_text().splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def _read_ladder(path: pathlib.Path):
    """(level, family, dt_mult, t_death, run) per rung."""
    return [(int(lvl), fam, float(dt), float(t), run)
            for lvl, _cell, fam, dt, t, run in _rows(path)]


def _read_clocks(path: pathlib.Path):
    """(level, gauge, L, t0, t_death, field, run) per arm."""
    return [(int(lvl), g, int(L), float(t0), float(t), f, run)
            for lvl, g, L, t0, t, f, run in _rows(path)]


def _panel_ladder(ax, rows) -> None:
    plain = sorted((r[0], r[3]) for r in rows if r[1] == "plain" and r[2] == 0.02)
    damped = sorted((r[0], r[3]) for r in rows if r[1] == "damped")
    half = [(r[0], r[3]) for r in rows if r[2] == 0.01]
    lp, tp = zip(*plain)
    ld, td = zip(*damped)
    gains = [tp[i + 1] - tp[i] for i in range(len(tp) - 1)]
    print("[spiral ladder] plain:", ", ".join(f"L{l} {t:.2f}" for l, t in plain))
    print("[spiral ladder] damped (joined):", ", ".join(f"L{l} {t:.2f}" for l, t in damped))
    print("[spiral ladder] plain gains per doubling:",
          ", ".join(f"{g:+.2f}" for g in gains),
          f"; halfstep vs its twin {half[0][1] - dict(plain)[half[0][0]]:+.2f}"
          if half else "")

    ax.plot(lp, tp, color=style.INK, lw=1.1, marker="o", ms=4.0,
            mfc=style.INK, mec=style.INK, zorder=4)
    ax.plot(ld, td, color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)), marker="o",
            ms=3.6, mfc=style.GROUND, mec=style.MUTED, zorder=3)
    if half:
        ax.plot([half[0][0]], [half[0][1]], ls="none", marker="D", ms=4.0,
                mfc=style.GROUND, mec=style.INK, mew=1.0, zorder=5)

    # Each gain beside its own segment, on the side away from the line: every
    # segment rises to the right, so up-left for the first two; the upper
    # two go BELOW-right, because up-left of them sit the dt/2 diamond and
    # the damped family's level-6 rung.
    for i, g in enumerate(gains):
        below = i >= 2
        ax.annotate(f"$+{g:.2f}$", (0.5 * (lp[i] + lp[i + 1]), 0.5 * (tp[i] + tp[i + 1])),
                    xytext=(4, -5) if below else (-3, 4), textcoords="offset points",
                    fontsize=7, ha="left" if below else "right",
                    va="top" if below else "bottom", color=style.INK)

    # One key for the three kinds of death point (the user, 2026-09-23: "a
    # legend as on (b), with a description of the different death points"),
    # in the empty lower-right quarter under both lines.
    from matplotlib.lines import Line2D
    key = [Line2D([], [], color=style.INK, lw=1.1, marker="o", ms=4.0,
                  mfc=style.INK, mec=style.INK,
                  label="no matter device (plain)"),
           Line2D([], [], color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)),
                  marker="o", ms=3.6, mfc=style.GROUND, mec=style.MUTED,
                  label="core damping, levels 4--6"),
           Line2D([], [], ls="none", marker="D", ms=4.0, mfc=style.GROUND,
                  mec=style.INK, mew=1.0, label=r"level 5 at $\mathrm{d}t/2$")]
    leg = ax.legend(handles=key, loc="lower right", fontsize=7, frameon=False,
                    handlelength=2.2, handletextpad=0.5, labelspacing=0.35,
                    borderaxespad=0.4, title=r"all from one $t=50$ state",
                    title_fontsize=7, alignment="left")
    leg.get_title().set_color(style.MUTED)

    ax.set_xlim(2.65, 7.35)
    ax.set_ylim(51.4, 57.6)
    ax.set_xticks([3, 4, 5, 6, 7])
    ax.set_xlabel(r"max level $\ell$ (cell $0.5/2^{\ell}$)")
    ax.set_ylabel(r"$t$ of the $h_{11}$ NaN")


def _panel_clocks(ax, clocks) -> None:
    """One row per gauge on a common death clock (the user, 2026-09-23, on
    the first draw -- start time on x with the level-3 walls as full-width
    rules -- "I don't like how it looks").  Level 3 from t = 0 is the filled
    dot; each level-5 arm is an open marker tagged with the time t0 its
    level 5 was switched on (diamond: the doubled box, L = 128); a thin
    rule joins a row's deaths, so each row reads as how far refinement
    moves that gauge's wall, and in which direction."""
    rows = [g for g in ("lc1", "lp2", "std", "eta4")
            if any(c[1] == g for c in clocks)]
    y = {g: i for i, g in enumerate(rows)}
    print("[spiral ladder] level-3 clocks:",
          ", ".join(f"{c[1]} {c[4]:.2f} ({c[5]})" for c in clocks if c[0] == 3))
    print("[spiral ladder] level 5:", ", ".join(
        f"{c[1]} L{c[2]} t0={c[3]:g} -> {c[4]:.3f}" for c in clocks if c[0] == 5))

    for g in rows:
        ts = [c[4] for c in clocks if c[1] == g]
        if len(ts) > 1:
            ax.plot([min(ts), max(ts)], [y[g]] * 2, color=style.FAINT, lw=1.6,
                    solid_capstyle="butt", zorder=2)
    for lvl, g, L, t0, t, _f, _run in clocks:
        if lvl == 3:
            ax.plot(t, y[g], "o", ms=5.0, mfc=style.INK, mec=style.INK, zorder=4)
        else:
            ax.plot(t, y[g], "D" if L == 128 else "o", ms=4.4 if L == 128 else 5.0,
                    mfc=style.GROUND, mec=style.INK, mew=1.0, zorder=5)

    # start-time tags, each on the free side of its own marker (points)
    def tag(t, g, text, dx, dy, ha, va):
        ax.annotate(text, (t, y[g]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=6.8, color=style.MUTED, ha=ha, va=va)
    def starts(sel):
        """ONE tag per marker group: "t0 = 0, 36" under two diamonds half a
        unit apart, not two tags fighting for the same four points."""
        pts = sorted((c[3], c[4]) for c in clocks if c[0] == 5 and sel(c))
        return pts, r"$t_0=" + "$, $".join(f"{a:g}" for a, _ in pts) + "$"
    for sel, dy, va in ((lambda c: c[1] == "std" and c[2] == 64, 6, "bottom"),
                        (lambda c: c[1] == "std" and c[2] == 128, -6, "top"),
                        (lambda c: c[1] == "eta4", 6, "bottom")):
        pts, text = starts(sel)
        if pts:
            g = next(c[1] for c in clocks if c[0] == 5 and sel(c))
            tag(sum(t for _, t in pts) / len(pts), g, text, 0, dy, "center", va)
    # "level 3" said once per joined row: above the standard dot, and beside
    # under the eta = 4 dot, whose top side the t0 tag already holds
    lvl3_std = next((c[4] for c in clocks if c[1] == "std" and c[0] == 3), None)
    if lvl3_std is not None:
        tag(lvl3_std, "std", r"$\ell=3$", 0, 6, "center", "bottom")
    lvl3_eta = next((c[4] for c in clocks if c[1] == "eta4" and c[0] == 3), None)
    if lvl3_eta is not None:
        tag(lvl3_eta, "eta4", r"$\ell=3$", 0, -6, "center", "top")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([GAUGE_NAME[g] for g in rows])
    ax.set_ylabel("gauge condition")
    ax.tick_params(axis="y", which="both", length=0)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlim(42.0, 64.0)
    ax.set_xlabel(r"$t$ of the NaN")
    # the key the caption would otherwise have to carry, in the empty
    # lower-right quarter the staircase leaves
    from matplotlib.lines import Line2D
    key = [Line2D([], [], ls="none", marker="o", ms=5.0, mfc=style.INK,
                  mec=style.INK, label=r"level 3, run from $t=0$"),
           Line2D([], [], ls="none", marker="o", ms=5.0, mfc=style.GROUND,
                  mec=style.INK, label=r"level 5 switched on at $t_0$"),
           Line2D([], [], ls="none", marker="D", ms=4.4, mfc=style.GROUND,
                  mec=style.INK, label=r"the same, doubled box ($L=128$)")]
    leg = ax.legend(handles=key, loc="lower right", fontsize=7, frameon=False,
                    handletextpad=0.3, labelspacing=0.35, borderaxespad=0.4,
                    title=r"standard: $\partial_t\alpha=-2\alpha K$, $\eta=1$",
                    title_fontsize=7, alignment="left")
    leg.get_title().set_color(style.MUTED)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP
    rows = _read_ladder(pack / "refinement_ladder.dat")
    clocks = _read_clocks(pack / "wall_clocks.dat")

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.05, 2.6), constrained_layout=True)
    _panel_ladder(axA, rows)
    _panel_clocks(axB, clocks)
    for ax, letter in ((axA, "a"), (axB, "b")):
        ax.text(0.0, 1.03, f"({letter})", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=9, color=style.INK)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "spiral_refinement_ladder.png")
    png = style.save(fig, out)
    print(f"[spiral ladder] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
