#!/usr/bin/env python3
r"""The placement curve, and the throats' own response to each other.

Two exact drainhole throats simply PLACED at rest already read wider than an
isolated one, and the more so the closer they are: the neighbour's field is on
the ruler.  Eighteen one-step probes (initial data plus one step, scanned at
t = 0) measure that instrumental effect as a function of separation.  Subtract
it from the scout's reading at the separation the scout has reached and what is
left is the throats' OWN response to the interaction.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_placement_curve

Reads the two tables the pack's reduction writes --
``campaign/04_binary_headon/placement_curve.dat`` and
``placement_scout_residual.dat`` (``results/merger/analysis/placement_curve.py``,
run at every pack) -- and writes ``figures/04_binary_headon/placement_curve``.

WHAT THE FIGURE HAS TO GET RIGHT

*The reference is not a result.*  The isolated-throat radius is where the curve
would go if the neighbour were not there, so it is a rule at the foot of the
panel, labelled in place, not a third curve competing for attention.

*Two different measurements, not two series of one.*  Left panel: the probes
are a calibration (ink, joined, because a curve is what they are for) and the
scout's mouths are the thing being calibrated (burgundy, unjoined, because they
are readings at whatever separation the scout happened to reach).

*Extrapolation is marked, not hidden.*  Past t = 13 the scout is closer than
the closest probe, so the curve is held at its last point and the residual
there is a lower bound.  That stretch is drawn in the recessive grey with open
markers and its own band, so it cannot be read as measured.

STYLE (2026-09-16, "PRD review style", the seed-branches grammar): figure*
width (7.05 x 2.7), style.prd frame, no titles -- (a)/(b) tags inside and the
semantics in the caption -- no boxed key: every series is named in place.
Monochrome ink plus the one accent: BURGUNDY is the scout (its readings in
panel a, its response in panel b); the calibration is ink; anything not
backed by a probe is open-faced grey.  The isolated-throat rule is the same
R_star dotted line, labelled the same way, as in the single-throat figures.
"""

from __future__ import annotations

import argparse
import pathlib
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "04_binary_headon"


def read_header(path: pathlib.Path, pattern: str) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            break
        m = re.search(pattern, line)
        if m:
            return m.group(1)
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    group = pack / "campaign" / GROUP
    curve_f, scout_f = group / "placement_curve.dat", group / "placement_scout_residual.dat"
    if not curve_f.exists():
        raise SystemExit(f"no {curve_f}\nRun results/merger/analysis/placement_curve.py first.")

    curve = np.loadtxt(curve_f, usecols=(0, 1, 2, 3))
    d, R_mouth = curve[:, 0], curve[:, 1]
    isolated = float(read_header(curve_f, r"radius:\s*([\d.]+)") or "nan")
    slope = float(read_header(curve_f, r"d\^(-?[\d.]+)") or "nan")

    scout = np.loadtxt(scout_f) if scout_f.exists() else np.empty((0, 6))
    if scout.ndim == 1 and scout.size:
        scout = scout.reshape(1, -1)
    inside = scout[:, 5] > 0.5 if len(scout) else np.zeros(0, bool)

    style.prd(base=10.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.05, 2.7), constrained_layout=True)

    # ---- (a) the calibration curve, and the scout laid against it --------
    # The isolated throat IS R_star of the single-throat figures: same rule,
    # same dotted idiom, same label, so the three figures read as one family.
    ax1.axhline(isolated, color=style.MUTED, lw=0.8, ls=(0, (1, 2.5)), zorder=2)
    ax1.plot(d, R_mouth, color=style.INK, lw=1.2, marker="o", ms=2.6, zorder=4)
    if len(scout):
        # Same in/out encoding as panel (b): burgundy where a probe backs the
        # comparison, open-faced where the scout has run in past the closest
        # probe (the reading is real; the calibration there is not).
        ax1.plot(scout[inside, 1], scout[inside, 2], ls="none", marker="s",
                 ms=3.2, color=style.BURGUNDY, zorder=5)
        ax1.plot(scout[~inside, 1], scout[~inside, 2], ls="none", marker="s",
                 ms=3.2, mfc=style.GROUND, mec=style.CONTEXT, mew=1.0, zorder=5)
    ax1.set_xscale("log")
    # Ticks chosen to span everything drawn -- the scout runs in below the
    # closest probe, and an axis whose labels stopped at the probes left a
    # third of the panel unlabelled.  Log minors off: with hand-set ticks
    # they crowd the short decade.
    lo = min(d.min(), scout[:, 1].min()) if len(scout) else d.min()
    ticks = [x for x in (3, 4, 6, 8, 12, 20, 32, 48) if lo * 0.95 <= x <= d.max() * 1.05]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([f"{x:g}" for x in ticks])
    ax1.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax1.set_xlabel(r"$d$")
    ax1.set_ylabel(r"$R_{\mathrm{mouth}}$")
    # Names written in place, no boxed key (the seed-branches rule): the
    # probes above their own tail, the scout under its cluster, the open
    # run-in above its markers, the rule at the right edge.
    ax1.text(d.max() * 0.96, isolated, r"$R_\star$", color=style.MUTED,
             fontsize=8, ha="right", va="bottom")
    ax1.text(14, 4.26, r"probes ($t=0$)", fontsize=8, ha="left", va="bottom")
    if len(scout):
        ax1.text(6.9, 4.415, "scout", fontsize=8, color=style.BURGUNDY,
                 ha="center", va="top")
        if (~inside).any():
            # Under the open run-in, not over it: the (a) tag owns the corner.
            ax1.text(3.8, 4.502, r"below probed $d$", fontsize=8,
                     color=style.MUTED, ha="center", va="top")
    ax1.text(0.03, 0.955, "(a)", transform=ax1.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) what is left once the ruler is subtracted --------------------
    if len(scout):
        t, resp = scout[:, 0], scout[:, 4]
        ax2.axhline(0, color=style.FAINT, lw=0.8, zorder=1)
        ax2.set_xlim(-1, t.max() + 1.5)
        # Headroom above zero so the held-band note has its own air.
        ax2.set_ylim(1.09 * resp.min(), -0.22 * resp.min())
        if (~inside).any():
            # Held-curve stretch: a lower bound, not a measurement.
            t_edge = t[inside].max() if inside.any() else t.min()
            ax2.axvspan(t_edge, ax2.get_xlim()[1], color=style.GRID, lw=0, zorder=0)
            y0, y1 = ax2.get_ylim()
            ax2.text(0.5 * (t_edge + ax2.get_xlim()[1]), y1 - 0.035 * (y1 - y0),
                     "curve held\n(lower bound)", fontsize=7.5, color=style.MUTED,
                     ha="center", va="top", linespacing=1.2)
            ax2.plot(t[~inside], resp[~inside], ls="none", marker="s", ms=3.2,
                     mfc=style.GROUND, mec=style.CONTEXT, mew=1.0, zorder=4)
        ax2.plot(t[inside], resp[inside], marker="s", ms=3.2, zorder=5,
                 color=style.BURGUNDY, linestyle=(0, ()), linewidth=1.2)
        ax2.set_xlabel(r"$t$")
        ax2.set_ylabel(r"$\delta R\,/\,R$  (\%)"
                       if matplotlib.rcParams["text.usetex"]
                       else "$\\delta R\\,/\\,R$  (%)")
        ax2.text(0.03, 0.955, "(b)", transform=ax2.transAxes, ha="left", va="top",
                 fontsize=9, color=style.INK)

    png = style.save(fig, pathlib.Path(args.out) if args.out
                     else figure_dir(GROUP, args.pack_root) / "placement_curve.png")
    print(f"[placement] wrote {png} (+pdf); {len(d)} probes, {len(scout)} scout rows, "
          f"{int(inside.sum())} of them inside the probed range")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
