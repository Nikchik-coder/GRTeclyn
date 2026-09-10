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

    style.paper(base=10.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 4.0), constrained_layout=True)

    # ---- left: the calibration curve ------------------------------------
    ax1.axhline(isolated, color=style.FAINT, ls=(0, (2, 2)), lw=0.8, zorder=1)
    ax1.annotate(f"isolated throat, {isolated:g}", (d.max(), isolated),
                 xytext=(0, 5), textcoords="offset points", ha="right",
                 fontsize=8.5, color=style.MUTED)
    ax1.plot(d, R_mouth, marker="o", ms=3.5, zorder=4,
             label="two throats placed at rest ($t=0$ probes)", **style.series(0))
    if len(scout):
        # Same in/out encoding as panel (b): filled where a probe backs the
        # reading, open where the scout has run in past the closest probe.
        ax1.plot(scout[inside, 1], scout[inside, 2], ls="none", marker="s", ms=4,
                 color=style.BURGUNDY, zorder=5,
                 label="the scout's mouths, at the separation it had reached")
        ax1.plot(scout[~inside, 1], scout[~inside, 2], ls="none", marker="s", ms=4,
                 mfc=style.GROUND, mec=style.CONTEXT, mew=1.2, zorder=5,
                 label="the same, closer than any probe")
    ax1.set_xscale("log")
    # Ticks chosen to span everything drawn -- the scout runs in below the
    # closest probe, and an axis whose labels stopped at the probes left a
    # third of the panel unlabelled.
    lo = min(d.min(), scout[:, 1].min()) if len(scout) else d.min()
    ticks = [x for x in (3, 4, 5, 6, 8, 10, 14, 20, 28, 40, 48) if lo * 0.95 <= x <= d.max() * 1.05]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([f"{x:g}" for x in ticks])
    ax1.minorticks_off()
    ax1.margins(y=0.14)   # headroom so the key clears the curve's first point
    # Axis labels are symbols. What the symbol MEANS goes in the title, once.
    ax1.set_xlabel(r"$d$")
    ax1.set_ylabel(r"$R_{\mathrm{mouth}}$")
    ax1.set_title(rf"(a) per-mouth areal radius vs separation (log):  "
                  rf"excess over isolated $\propto d^{{{slope:.2f}}}$", loc="left")
    style.legend(ax1)

    # ---- right: what is left once the ruler is subtracted ----------------
    if len(scout):
        t, resp = scout[:, 0], scout[:, 4]
        ax2.axhline(0, color=style.FAINT, lw=0.8, zorder=1)
        # Headroom for the band's caption, so it does not sit on the zero rule.
        ax2.set_ylim(1.06 * resp.min(), -0.30 * resp.min())
        if (~inside).any():
            # Held-curve stretch: a lower bound, not a measurement.
            t_edge = t[inside].max() if inside.any() else t.min()
            ax2.axvspan(t_edge, t.max(), color=style.GRID, lw=0, zorder=0)
            # Anchored to the frame, not centred on the band: centred, this
            # two-line caption is wider than the band and ran off the panel.
            style.note(ax2, "closer than the closest probe\n(curve held: a lower bound)",
                       loc="upper right")
            ax2.plot(t[~inside], resp[~inside], ls="none", marker="s", ms=4,
                     mfc=style.GROUND, mec=style.CONTEXT, mew=1.2, zorder=4)
        ax2.plot(t[inside], resp[inside], marker="s", ms=4, zorder=5,
                 color=style.BURGUNDY, linestyle=(0, ()), linewidth=1.5,
                 label="inside the probed range")
        ax2.set_xlabel(r"$t$")
        ax2.set_ylabel("$\\delta R\\,/\\,R$   (%)")
        ax2.set_title(r"(b) own response: $-$ squeezed, $+$ widened", loc="left")

    png = style.save(fig, pathlib.Path(args.out) if args.out
                     else figure_dir(GROUP, args.pack_root) / "placement_curve.png")
    print(f"[placement] wrote {png} (+pdf); {len(d)} probes, {len(scout)} scout rows, "
          f"{int(inside.sum())} of them inside the probed range")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
