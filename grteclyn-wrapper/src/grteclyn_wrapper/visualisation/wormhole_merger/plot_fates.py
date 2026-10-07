#!/usr/bin/env python3
r"""The fates of foam-born throats as one fork, read left to right.

A schematic, not a measurement: no number is drawn.  Each fork is a selection
rule the paper measures, and each leaf is a fate it evolves.

    birth separation   born apart -> a lone throat; born close -> a pair
    perturbation       a lone throat pushed out (eps > 0) collapses, squeezed
                       (eps < 0) inflates (Sec. IV C)
    relative sign      like signs repel and the pair recedes; opposite signs
                       attract (Sec. V A)
    the race           an attracting pair merges into one black hole where its
                       common horizon wins the race against the inflation the
                       companion starts -- short d, small p; otherwise both
                       throats inflate, at contact or after a fly-by (Sec. VII B)

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_fates

STYLE: the full 7.05 in width, no frame, Hubble's tuning fork: each fork splits
into level prongs, and every label sits flat above or below its prong.  Throats
are ink rings with their scalar sign; gold is the horizon, so it rings the two
fates that end in a black hole and nothing else; grey carries the context (the
growing necks' earlier shells).

WHY: 2026-10-07, the user: a population fork for the fates, like Hubble's
tuning fork for the shapes of galaxies; the attracting pair branches too, into
the merger (by d and p) and both throats inflating.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

TAG = "[fates]"

W, H = 14.1, 5.0            # canvas in half-inches: 1 unit = 0.5 in at 7.05 x 2.5 in
EDGE = dict(color=style.INK, lw=1.1, solid_capstyle="round", solid_joinstyle="round", zorder=1)
LABEL = dict(fontsize=8.0, color=style.INK)
RULE = dict(fontsize=7.5, color=style.MUTED, style="italic")

# leaves, top to bottom: (fate, pictogram centre y)
LEAVES = (("collapse", 4.5), ("inflation", 3.5), ("scattering", 2.5), ("merger", 1.45),
          ("pair inflation", 0.45))
Y = dict(LEAVES)
FOAM = (0.95, 2.95)
ROOT = (2.0, 2.95)                              # birth separation
LONE = (4.3, 0.5 * (Y["collapse"] + Y["inflation"]))      # the perturbation's sign
RACE = (7.6, 0.5 * (Y["merger"] + Y["pair inflation"]))   # contact against inflation
PAIR = (4.3, 0.5 * (Y["scattering"] + RACE[1]))           # the relative sign
KNEE = 0.55                 # how far a prong runs on the slant before it levels
LEAF_X = 10.55
REACH = {"collapse": 0.5, "inflation": 0.58, "scattering": 0.76, "merger": 0.5,
         "pair inflation": 0.74}
TEXT_X = LEAF_X + 0.78


def throat(ax, x, y, r, sign="", lw=1.1, fill=style.GRID, fs=7.5, z=3):
    """One mouth: an ink ring on a pale fill, its scalar sign inside."""
    ax.add_patch(Circle((x, y), r, facecolor=fill, edgecolor=style.INK, lw=lw, zorder=z))
    if sign:
        ax.text(x, y - 0.012, sign, ha="center", va="center", fontsize=fs,
                color=style.INK, zorder=z + 1)


def arrow(ax, a, b, color=style.INK, lw=0.9, ms=6.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=2))


def prong(ax, a, b):
    """From a to b: a short slant, then level -- the tuning fork's prong."""
    if abs(a[1] - b[1]) < 1e-9:
        xs, ys = [a[0], b[0]], [a[1], b[1]]
    else:
        xs, ys = [a[0], a[0] + KNEE, b[0]], [a[1], b[1], b[1]]
    ax.plot(xs, ys, **EDGE)
    return a[0] + KNEE, b[0]


def over(ax, x0, x1, y, text, *, below=False, **kw):
    """A flat label centred on the level run x0..x1 at height y."""
    ax.text(0.5 * (x0 + x1), y + (-0.13 if below else 0.13), text, ha="center",
            va="top" if below else "bottom", **{**LABEL, **kw})


def foam(ax, cx, cy):
    """Throats of both signs, born together out of the foam."""
    for dx, dy, s in ((-0.55, 0.42, "+"), (0.05, 0.62, "−"), (0.5, 0.22, "+"),
                      (-0.32, -0.12, "−"), (0.22, -0.38, "+"), (-0.62, -0.55, "+"),
                      (0.62, -0.62, "−")):
        throat(ax, cx + dx, cy + dy, 0.17, s, lw=0.9, fs=7.0)


def growing(ax, x, y, r, shells, reach, ms=5.0):
    """A throat that inflates: its earlier shells in grey, arrows outward."""
    for rs, a in zip(shells, (0.55, 0.8)):
        ax.add_patch(Circle((x, y), rs, facecolor="none", edgecolor=style.CONTEXT, lw=0.8,
                            linestyle=(0, (2.0, 1.6)), alpha=a, zorder=2))
    throat(ax, x, y, r)
    for t in np.deg2rad((45, 135, 225, 315)):
        u = np.array([np.cos(t), np.sin(t)])
        arrow(ax, (x, y) + (r + 0.02) * u, (x, y) + reach * u, lw=0.8, ms=ms)


def collapse(ax, x, y):
    ax.add_patch(Circle((x, y), 0.36, facecolor="none", edgecolor=style.GOLD, lw=2.0, zorder=3))
    ax.add_patch(Circle((x, y), 0.25, facecolor=style.INK, edgecolor=style.INK, lw=0.8, zorder=3))


def inflation(ax, x, y):
    growing(ax, x, y, 0.21, (0.42, 0.32), 0.47)


def pair_inflation(ax, x, y):
    for sx in (-1, +1):
        growing(ax, x + sx * 0.36, y, 0.13, (0.27, 0.2), 0.3, ms=4.0)


def scattering(ax, x, y):
    for sx in (-1, +1):
        throat(ax, x + sx * 0.2, y, 0.15, "+", fs=7.0)
        arrow(ax, (x + sx * 0.37, y), (x + sx * 0.62, y), lw=0.9, ms=5.5)


def merger(ax, x, y):
    ax.add_patch(Circle((x, y), 0.38, facecolor="#f4f2ec", edgecolor=style.GOLD, lw=2.0, zorder=3))
    throat(ax, x - 0.15, y, 0.12, "+", fs=6.5, z=4)
    throat(ax, x + 0.15, y, 0.12, "−", fs=6.5, z=4)


DRAW = {"collapse": collapse, "inflation": inflation, "scattering": scattering,
        "merger": merger, "pair inflation": pair_inflation}
TEXT = {
    "collapse": ("collapse", "a black hole that\nswallows its field"),
    "inflation": ("inflation", "the throat stays open\nand grows, anti-trapped"),
    "scattering": ("scattering", "the pair recedes"),
    "merger": ("merger", "one black hole,\nboth throats inside"),
    "pair inflation": ("inflation", "both throats inflate, at\ncontact or after a fly-by"),
}


def draw(ax) -> None:
    # the foam and the first fork: birth separation
    foam(ax, *FOAM)
    ax.text(FOAM[0], FOAM[1] - 1.2, "foam-born throats\nat $t=0$", ha="center", va="top",
            fontsize=8.5, color=style.INK, linespacing=1.15)
    prong(ax, (FOAM[0] + 0.8, ROOT[1]), ROOT)
    x0, x1 = prong(ax, ROOT, (LONE[0] - 0.3, LONE[1]))
    over(ax, x0, x1, LONE[1], "born apart")
    x0, x1 = prong(ax, ROOT, (PAIR[0] - 0.47, PAIR[1]))
    over(ax, x0, x1, PAIR[1], "born close", below=True)
    ax.text(ROOT[0] + 1.2, ROOT[1], "birth\nseparation", ha="center", va="center",
            linespacing=1.1, **RULE)

    # the lone throat, kicked either way
    throat(ax, *LONE, 0.24)
    arrow(ax, (LONE[0] + 0.05, LONE[1] + 0.27), (LONE[0] + 0.05, LONE[1] + 0.47), lw=0.8, ms=4.5)
    arrow(ax, (LONE[0] - 0.05, LONE[1] + 0.47), (LONE[0] - 0.05, LONE[1] + 0.27), lw=0.8, ms=4.5)
    ax.text(LONE[0], LONE[1] - 0.34, "perturbation", ha="center", va="top", **RULE)
    end = {k: (LEAF_X - REACH[k], y) for k, y in LEAVES}
    lone_out = (LONE[0] + 0.3, LONE[1])
    x0, x1 = prong(ax, lone_out, end["collapse"])
    over(ax, x0, x1, Y["collapse"], r"pushed out, $\varepsilon>0$")
    x0, x1 = prong(ax, lone_out, end["inflation"])
    over(ax, x0, x1, Y["inflation"], r"squeezed, $\varepsilon<0$", below=True)

    # the pair, of either relative sign
    throat(ax, PAIR[0] - 0.24, PAIR[1], 0.17, "±", fs=7.0)
    throat(ax, PAIR[0] + 0.24, PAIR[1], 0.17, "±", fs=7.0)
    ax.text(PAIR[0], PAIR[1] + 0.3, "relative sign", ha="center", va="bottom", **RULE)
    pair_out = (PAIR[0] + 0.47, PAIR[1])
    x0, x1 = prong(ax, pair_out, end["scattering"])
    over(ax, x0, x1, Y["scattering"], "like signs: repel")
    x0, x1 = prong(ax, pair_out, (RACE[0] - 0.42, RACE[1]))
    over(ax, x0, x1, RACE[1], "opposite signs: attract", below=True)

    # the attracting pair: its horizon against the inflation its companion starts
    throat(ax, RACE[0] - 0.18, RACE[1], 0.17, "+", fs=7.0)
    throat(ax, RACE[0] + 0.18, RACE[1], 0.17, "−", fs=7.0)
    ax.text(RACE[0], RACE[1] + 0.3, "the race", ha="center", va="bottom", **RULE)
    race_out = (RACE[0] + 0.37, RACE[1])
    x0, x1 = prong(ax, race_out, end["merger"])
    over(ax, x0, x1, Y["merger"], r"short $d$, small $p$")
    x0, x1 = prong(ax, race_out, end["pair inflation"])
    over(ax, x0, x1, Y["pair inflation"], "otherwise", below=True)

    for k, y in LEAVES:
        DRAW[k](ax, LEAF_X, y)
        name, what = TEXT[k]
        ax.text(TEXT_X, y + 0.05, name, ha="left", va="bottom", fontsize=9.5,
                color=style.INK, weight="bold")
        ax.text(TEXT_X, y, what, ha="left", va="top", fontsize=8.0,
                color=style.MUTED, linespacing=1.1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.typography(base=10.0)
    fig = plt.figure(figsize=(W / 2.0, H / 2.0))
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_xlim(0.0, W)
    ax.set_ylim(0.0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    draw(ax)
    problems = style.label_audit(fig)
    print(f"{TAG} label audit: {len(problems)} problem(s) {problems[:3]}")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("00_overview", args.pack_root) / "fates.png")
    png = style.save(fig, out)
    print(f"{TAG} wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
