#!/usr/bin/env python3
r"""The remnant horizon that shrinks, bottoms out, and grows back.

The single-throat collapse remnants' horizon history across the three arms
with a record past the floor (2026-09-19 finding; article Sec. IV C): the
undamped radial kick `single_eps_p1e2_t100` and the two scalar-damped level-4
arms `single_eps_p1e2_q5e3_ml4_t100` / `..._q5e2_ml4_t100`.  Each swallows its
own phantom support (areal radius and Misner-Sharp mass falling), bottoms out
near t = 43-48, and then regrows +9-17 % in radius and +11-13 % in mass as
the negative-energy exchange reverses -- the area-law's null-energy-condition
hypothesis failing in real time, both ways in one record.  The pure-quadrupole
arm of the collapse page reaches its own floor only at t = 92 and is drawn as
context.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_horizon_regrowth

Reads each arm's ``horizon_scan.dat`` (oriented scan, centre C rows with a
MOTS) under ``campaign/01_single_throat/seed/``.  Writes
``figures/01_single_throat/single_horizon_regrowth``.

STYLE: style.prd, no titles, letter tags above the frames, no boxed key,
every series named in place.  INK is the undamped arm (the headline numbers
of Sec. IV C), MUTED the two damped twins, CONTEXT grey the floorless
pure-quadrupole arm; the floor of each curve carries a small marker.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "01_single_throat"
ARMS = (
    ("seed/single_eps_p1e2_t100", "undamped", style.INK, "-", 1.3),
    ("seed/single_eps_p1e2_q5e3_ml4_t100", "damped, $\\varepsilon_2=0.005$", style.MUTED, (0, (4, 2.5)), 1.1),
    ("seed/single_eps_p1e2_q5e2_ml4_t100", "damped, $\\varepsilon_2=0.05$", style.MUTED, (0, (1.2, 1.6)), 1.1),
)
CONTEXT_ARM = ("seed/single_pureq_q1e2_ml4_t100", "pure quadrupole (floor only at $t=92$)")


def _mots_history(pack: pathlib.Path, arm: str):
    rows = []
    for ln in open(pack / GROUP / arm / "horizon_scan.dat"):
        if ln.startswith("#"):
            continue
        f = ln.split()
        if f[1] != "C" or int(f[9]) < 1:
            continue
        rows.append((float(f[0]), float(f[11]), float(f[12])))
    a = np.array(rows)
    return a[np.argsort(a[:, 0])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root) if args.pack_root else PACK_ROOT
    pack = pack / "campaign" if (pack / "campaign" / GROUP).is_dir() else pack

    style.prd()
    fig, axs = plt.subplots(1, 2, figsize=(7.05, 2.75), constrained_layout=True)

    hist = [_mots_history(pack, arm) for arm, *_ in ARMS]
    ctx = _mots_history(pack, CONTEXT_ARM[0])

    for ax, col in ((axs[0], 1), (axs[1], 2)):
        ax.plot(ctx[:, 0], ctx[:, col], color=style.CONTEXT, linewidth=0.9,
                alpha=0.75, zorder=1)
        for a, (arm, name, colr, ls, lw) in zip(hist, ARMS):
            ax.plot(a[:, 0], a[:, col], color=colr, linestyle=ls,
                    linewidth=lw, zorder=3)
            i = int(np.nanargmin(a[:, 1]))          # the RADIUS floor times both panels
            ax.plot(a[i, 0], a[i, col], marker="v", markersize=3.6,
                    color=colr, zorder=4, linestyle="none")
        ax.set_xlim(15, 102)
        ax.set_xlabel(r"$t$")

    # ---- (a) areal radius ---------------------------------------------------
    axs[0].set_ylabel(r"$R_{\rm MOTS}$")
    axs[0].text(100.5, 2.17, "+17.0%", ha="right", va="top", fontsize=7,
                color=style.INK)
    axs[0].set_ylim(1.86, 3.72)
    axs[0].text(66, 1.965, "past the floor, every arm sheds the phantom and regrows",
                ha="center", va="top", fontsize=6.8, color=style.MUTED)

    # ---- (b) Misner-Sharp mass ---------------------------------------------
    axs[1].set_ylabel(r"$M_{\rm MS}$")
    axs[1].text(100.5, 1.315, "+11–13%", ha="right", va="bottom",
                fontsize=7, color=style.INK)

    # One shared legend on top (the censorship figure's rule).
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], color=style.INK, linewidth=1.3, label="undamped kick"),
        Line2D([], [], color=style.MUTED, linewidth=1.1,
               linestyle=(0, (4, 2.5)), label="damped, $\\varepsilon_2=0.005$"),
        Line2D([], [], color=style.MUTED, linewidth=1.1,
               linestyle=(0, (1.2, 1.6)), label="damped, $\\varepsilon_2=0.05$"),
        Line2D([], [], color=style.CONTEXT, linewidth=0.9, alpha=0.75,
               label="pure quadrupole (floor $t=92$)"),
        Line2D([], [], color=style.INK, marker="v", markersize=3.6,
               linestyle="none", label="radius floor"),
    ]
    fig.legend(handles=handles, loc="outside upper center", ncol=5,
               frameon=False, fontsize=6.8, handlelength=1.9,
               columnspacing=1.1, handletextpad=0.5)

    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({'ab'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    for a, (arm, *_ ) in zip(hist, ARMS):
        i = int(np.nanargmin(a[:, 1]))
        print(f"[regrowth] {arm}: floor R={a[i,1]:.3f} at t={a[i,0]:.0f}, "
              f"end R={a[-1,1]:.3f} (+{(a[-1,1]/a[i,1]-1)*100:.1f}%), "
              f"M {a[i,2]:.3f} -> {a[-1,2]:.3f} (+{(a[-1,2]/a[i,2]-1)*100:.1f}%)")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_horizon_regrowth.png")
    png = style.save(fig, out)
    print(f"[regrowth] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
