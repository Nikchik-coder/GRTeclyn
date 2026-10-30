"""Exotic matter against spin for the classical families and the CMA-ES finds.

Panel (e) of the spinning-wormhole solver figure, with the screened CMA-ES
points overlaid.  Classical curves reuse ``plot_spin_trends.family``; the
finds are the STATUS X values (2026-10-30), never the optimisation package.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_exotic_spin
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends import (
    FAMILIES,
    RGB,
    TIGHT,
    family,
)
from grteclyn_wrapper.visualisation.spinning_wormhole.solutions import load as load_solutions
from grteclyn_wrapper.visualisation.wormhole_merger import style

REPO = pathlib.Path(__file__).resolve().parents[5]
OUT = REPO / "results" / "optimisation" / "figures"
ACCENT = RGB[2]  # spinning-paper blue #1f77b4

# X = |VIQ|/R_e from STATUS.  v_e is the packed member (symmetric) or the
# packed spinning header (drainhole D21, D30, D51, D90) or the r1 JSON (D80);
# D0 and the symmetric static are J = 0 (search-best).
FOUND = (
    ("drainhole", "D0", 0.0, 1.83872766),
    ("drainhole", "D21", 0.2100172006151723, 1.8287958015),
    ("drainhole", "D30", 0.3044712262324205, 1.88040565),
    ("drainhole", "D51", 0.5127052512125934, 1.6061738698),
    ("drainhole", "D80", 0.7908256780231234, 1.10469483),
    ("drainhole", "D90", 0.8997849046244889, 0.787086131),
    ("symmetric", "S0", 0.0, 1.62676341),
    ("symmetric", "S27", 0.2747870070282676, 1.63372),
    ("symmetric", "S50", 0.5037707249409871, 1.49461),
    ("symmetric", "S85", 0.8474413551909138, 1.09759),
)

# Per-model tag offsets (points) and anchors, each tag against its own marker.
TAG_SIDES = {
    "D0": (4.0, -3.0, "left", "top"),
    "D21": (0.0, -4.5, "center", "top"),
    "D30": (4.0, 2.0, "left", "bottom"),
    "D51": (-4.0, -3.0, "right", "top"),
    "D80": (-4.0, -2.5, "right", "top"),
    "D90": (-4.0, -2.5, "right", "top"),
    "S0": (4.0, 2.5, "left", "bottom"),
    "S27": (0.0, 4.5, "center", "bottom"),
    "S50": (4.0, 2.5, "left", "bottom"),
    "S85": (4.0, -2.5, "left", "top"),
}

# Found-point markers follow the family: filled square on drainhole (solid),
# open square on symmetric (dashed).
MARK = {
    "drainhole": dict(marker="s", ms=4.2, mfc=ACCENT, mec=ACCENT, mew=0.6),
    "symmetric": dict(marker="s", ms=4.2, mfc="white", mec=ACCENT, mew=0.9),
}


def _curve(ax, fam, ls):
    v = np.concatenate(([0.0], fam["v"]))
    y = np.concatenate(([fam["static"]["Xrel"]], fam["Xrel"]))
    ok = np.isfinite(y)
    return ax.plot(v[ok], y[ok], color=style.INK, ls=ls, lw=1.3, zorder=1)[0]


def plot(out=OUT) -> None:
    rows = load_solutions()
    fams = [family(rows, eta0, gamma) for eta0, gamma, *_ in FAMILIES]
    x0 = {name: fam["static"]["X"] for fam, (*_, name, _) in zip(fams, FAMILIES)}
    fig, ax = plt.subplots(figsize=(3.4, 2.55), dpi=300, layout="constrained")
    rule = dict(color=style.FAINT, lw=0.6, zorder=0)
    ax.axhline(1.0, **rule)
    for fam, (*_, name, ls) in zip(fams, FAMILIES):
        _curve(ax, fam, ls)
        pts = sorted((ve, X / x0[name], lbl) for n, lbl, ve, X in FOUND if n == name)
        xv, yv, lbls = zip(*pts)
        ax.plot(xv, yv, color=ACCENT, ls=ls, lw=1.1, zorder=3)
        ax.plot(xv, yv, ls="none", zorder=4, clip_on=False, **MARK[name])
        for ve, y, lbl in pts:
            dx, dy, ha, va = TAG_SIDES[lbl]
            ax.annotate(lbl, (ve, y), textcoords="offset points",
                        xytext=(dx, dy), fontsize=6.2, ha=ha, va=va,
                        color=style.INK, zorder=5)
    handles = [
        (Line2D([], [], color=style.INK, ls=FAMILIES[0][3], lw=1.3),
         r"drainhole ($\mathcal{V}=0$)"),
        (Line2D([], [], color=ACCENT, ls=FAMILIES[0][3], lw=1.1,
                **{**MARK["drainhole"], "ms": 3.4}),
         "drainhole (CMA-ES)"),
        (Line2D([], [], color=style.INK, ls=FAMILIES[1][3], lw=1.3),
         r"symmetric ($\mathcal{V}=0$)"),
        (Line2D([], [], color=ACCENT, ls=FAMILIES[1][3], lw=1.1,
                **{**MARK["symmetric"], "ms": 3.4}),
         "symmetric (CMA-ES)"),
    ]
    ax.set(xlabel=r"$v_e$", ylabel=r"$X/X_{\rm static}$",
           xlim=(-0.04, 1.0), ylim=(0.0, 1.15))
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                  ["", "0.2", "0.4", "0.6", "0.8", "1.0"])
    style.legend_top(ax, handles, ncol=2, borderpad=0.4, labelspacing=0.45, **TIGHT)
    hits = style.label_audit(fig)
    if hits:
        print("\n".join(hits), file=sys.stderr)
        raise SystemExit("label audit failed")
    path = style.save(fig, out / "exotic_spin.png")
    plt.close(fig)
    print(path.relative_to(REPO))
    for name, lbl, ve, X in FOUND:
        print(f"  {lbl:4s} ({name:9s})  v_e {ve:.3f}  X {X:.4f}  X/X_static {X / x0[name]:.3f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    args = ap.parse_args(argv)
    style.prd(8.0)
    plot(out=args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
