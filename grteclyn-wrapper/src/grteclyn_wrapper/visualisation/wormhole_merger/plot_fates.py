#!/usr/bin/env python3
r"""The fates of foam-born throats as one fork, read left to right.

A schematic, not a measurement: no number is drawn.  Each fork is a selection
rule the paper measures, and each leaf is a fate it evolves.

    birth separation   born apart -> a lone throat; born close -> a pair
    perturbation       a lone throat pushed out (eps > 0) collapses, squeezed
                       (eps < 0) inflates (Sec. IV C)
    relative sign      like signs repel: the pair recedes and both throats
                       inflate (Sec. V C); opposite signs attract (Sec. V A)
    the race           an attracting pair merges into one black hole where its
                       common horizon wins the race against the inflation the
                       companion starts -- short d, small p; otherwise both
                       throats inflate, at contact or after a fly-by (Sec. VII B)

    gravitational waves  a sketch of r Psi4 beside each fate it is known for
                       (shapes after Fig. gw_gallery, not data): the collapse
                       rings down at the new hole's frequency; the merger is one
                       burst with no chirp before it (Secs. VIII B, VIII D); the
                       lone inflating throat is spherical, so no gravitational
                       wave, a flat line; the inflating pair is not silent, its
                       encounter radiates one burst (the fly-by's is the loudest);
                       the receding pair radiates no burst: its l = 2 field only
                       drifts, smoothly, as its throats inflate (SCATTER-fate).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_fates

STYLE: the full 7.05 in width at 1.95 in, no frame, Hubble's tuning fork: each
fork splits into level prongs, and every label sits flat above or below its
prong.  Throats are ink rings with their scalar sign; gold is the horizon, so it
rings the two fates that end in a black hole and nothing else; grey carries the
context (the growing necks' earlier shells, the waves' zero lines).

WHY: 2026-10-07: a population fork for the fates, like Hubble's
tuning fork for the shapes of galaxies; the attracting pair branches too, into
the merger (by d and p) and both throats inflating; a sketched GW signal per
fate; then squeezed in height for Fig. 1 of the paper.
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

W, H = 14.1, 3.9            # canvas in half-inches: 1 unit = 0.5 in at 7.05 x 1.95 in
EDGE = dict(color=style.INK, lw=1.0, solid_capstyle="round", solid_joinstyle="round", zorder=1)
LABEL = dict(fontsize=8.0, color=style.INK)
RULE = dict(fontsize=7.5, color=style.MUTED, style="italic")

# leaves, top to bottom: (fate, pictogram centre y); 0.7 apart within a fork, 0.85
# between the lone throat's fork and the pair's, where two prong labels face each other
LEAVES = (("collapse", 3.4), ("inflation", 2.7), ("scattering", 1.85), ("merger", 1.15),
          ("pair inflation", 0.45))
Y = dict(LEAVES)
LONE = (5.0, 0.5 * (Y["collapse"] + Y["inflation"]))      # the perturbation's sign
RACE = (6.4, 0.5 * (Y["merger"] + Y["pair inflation"]))   # contact against inflation
PAIR = (3.85, 0.5 * (Y["scattering"] + RACE[1]))          # the relative sign
ROOT = (2.0, 0.5 * (LONE[1] + PAIR[1]))                   # birth separation
FOAM = (0.95, ROOT[1] + 0.25)
KNEE = 0.5                  # how far a prong runs on the slant before it levels
LEAF_X = 8.45
REACH = {"collapse": 0.42, "inflation": 0.46, "scattering": 0.58, "merger": 0.42,
         "pair inflation": 0.58}
TEXT_X = LEAF_X + 0.62
WAVE_X = (11.75, 13.0)      # the GW sketches' span, right of the leaf texts
# the lone inflating throat is spherical, and gravitational waves start at l = 2; the
# pair that inflates is not silent -- its encounter radiates (the fly-by is the loudest burst)
# the receding pair's l = 2 field drifts smoothly as its throats inflate, with
# no burst (SCATTER-fate, 2026-10-08)
GW = {"collapse": "Schwarzschild ringdown", "inflation": "none", "scattering": "no burst",
      "merger": "one burst, no chirp", "pair inflation": "one burst at the encounter"}


def throat(ax, x, y, r, sign="", lw=1.0, fill=style.GRID, fs=6.5, z=3):
    """One mouth: an ink ring on a pale fill, its scalar sign inside."""
    ax.add_patch(Circle((x, y), r, facecolor=fill, edgecolor=style.INK, lw=lw, zorder=z))
    if sign:
        ax.text(x, y - 0.01, sign, ha="center", va="center", fontsize=fs,
                color=style.INK, zorder=z + 1)


def arrow(ax, a, b, color=style.INK, lw=0.8, ms=4.5):
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


def over(ax, x0, x1, y, text, *, below=False, dx=0.0, **kw):
    """A flat label centred on the level run x0..x1 at height y (moved by dx)."""
    ax.text(0.5 * (x0 + x1) + dx, y + (-0.1 if below else 0.1), text, ha="center",
            va="top" if below else "bottom", **{**LABEL, **kw})


def foam(ax, cx, cy):
    """Throats of both signs, born together out of the foam."""
    for dx, dy, s in ((-0.46, 0.34, "+"), (0.04, 0.5, "−"), (0.42, 0.18, "+"),
                      (-0.27, -0.1, "−"), (0.18, -0.31, "+"), (-0.52, -0.46, "+"),
                      (0.52, -0.5, "−")):
        throat(ax, cx + dx, cy + dy, 0.14, s, lw=0.8, fs=6.0)


def growing(ax, x, y, r, shells, reach, ms=4.0, sign=""):
    """A throat that inflates: its earlier shells in grey, arrows outward."""
    for rs, a in zip(shells, (0.55, 0.8)):
        ax.add_patch(Circle((x, y), rs, facecolor="none", edgecolor=style.CONTEXT, lw=0.7,
                            linestyle=(0, (2.0, 1.6)), alpha=a, zorder=2))
    throat(ax, x, y, r, sign, fs=5.0)
    for t in np.deg2rad((45, 135, 225, 315)):
        u = np.array([np.cos(t), np.sin(t)])
        arrow(ax, (x, y) + (r + 0.02) * u, (x, y) + reach * u, lw=0.7, ms=ms)


def collapse(ax, x, y):
    ax.add_patch(Circle((x, y), 0.29, facecolor="none", edgecolor=style.GOLD, lw=1.8, zorder=3))
    ax.add_patch(Circle((x, y), 0.2, facecolor=style.INK, edgecolor=style.INK, lw=0.8, zorder=3))


def inflation(ax, x, y):
    growing(ax, x, y, 0.16, (0.33, 0.25), 0.37)


def pair_inflation(ax, x, y):
    for sx, sign in ((-1, "+"), (+1, "−")):
        growing(ax, x + sx * 0.3, y, 0.1, (0.22, 0.16), 0.24, ms=3.5, sign=sign)


def scattering(ax, x, y):
    """Like signs recede, and both throats inflate: the race's losing pair's
    pictogram, signed."""
    for sx in (-1, +1):
        growing(ax, x + sx * 0.3, y, 0.1, (0.22, 0.16), 0.24, ms=3.5, sign="+")


def merger(ax, x, y):
    ax.add_patch(Circle((x, y), 0.3, facecolor="#f4f2ec", edgecolor=style.GOLD, lw=1.8, zorder=3))
    throat(ax, x - 0.12, y, 0.1, "+", fs=5.5, z=4)
    throat(ax, x + 0.12, y, 0.1, "−", fs=5.5, z=4)


DRAW = {"collapse": collapse, "inflation": inflation, "scattering": scattering,
        "merger": merger, "pair inflation": pair_inflation}
TEXT = {
    "collapse": ("collapse", "a black hole"),
    "inflation": ("inflation", "open, anti-trapped, growing"),
    "scattering": ("scattering", "recede, both throats inflate"),
    "merger": ("merger", "one black hole, both inside"),
    "pair inflation": ("inflation", "both throats inflate"),
}


def wave(ax, x0, x1, y, kind, amp=0.13):
    """A sketched r Psi4: silent, then the burst -- no chirp ahead of any.

    The collapse rings at one frequency as its new hole settles; the merger's
    burst is broader and its frequency drifts down into the remnant's ringdown;
    the pass is one arch with no remnant to ring; the spherical inflation is a
    flat line.
    """
    t = np.linspace(0.0, 1.0, 600)
    ax.plot([x0, x1], [y, y], color=style.FAINT, lw=0.6, zorder=1)
    if kind in ("inflation", "scattering"):
        ax.plot([x0, x1], [y, y], color=style.INK, lw=0.9, zorder=2)
        return
    if kind == "pair inflation":
        h = np.exp(-((t - 0.55) / 0.14) ** 2) * np.sin(2.0 * np.pi * 2.3 * (t - 0.55) + 0.9)
    else:
        if kind == "collapse":
            t0, rise, fall = 0.4, 0.03, 0.2
            phase = 2.0 * np.pi * 5.5 * (t - t0)
        else:
            t0, rise, fall = 0.36, 0.05, 0.2
            phase = 2.0 * np.pi * (3.4 * (t - t0) - 1.0 * (t - t0) ** 2)
        env = 0.5 * (1.0 + np.tanh((t - t0) / rise)) * np.exp(-np.clip(t - t0 - 0.06, 0.0, None) / fall)
        h = env * np.sin(phase)
    ax.plot(x0 + (x1 - x0) * t, y + amp * h / np.abs(h).max(), color=style.INK, lw=0.9, zorder=2)


def draw(ax) -> None:
    # the foam and the first fork: birth separation
    foam(ax, *FOAM)
    ax.text(FOAM[0], FOAM[1] - 0.72, "foam-born throats\nat $t=0$", ha="center", va="top",
            fontsize=8.0, color=style.INK, linespacing=1.1)
    prong(ax, (FOAM[0] + 0.72, ROOT[1]), ROOT)
    x0, x1 = prong(ax, ROOT, (LONE[0] - 0.25, LONE[1]))
    over(ax, x0, x1, LONE[1], "born apart")
    x0, x1 = prong(ax, ROOT, (PAIR[0] - 0.4, PAIR[1]))
    over(ax, x0, x1, PAIR[1], "born close", below=True)
    ax.text(ROOT[0] + 1.15, ROOT[1], "birth\nseparation", ha="center", va="center",
            linespacing=1.05, **RULE)

    # the lone throat, kicked either way
    throat(ax, *LONE, 0.2)
    arrow(ax, (LONE[0] + 0.045, LONE[1] + 0.23), (LONE[0] + 0.045, LONE[1] + 0.4), lw=0.7, ms=4.0)
    arrow(ax, (LONE[0] - 0.045, LONE[1] + 0.4), (LONE[0] - 0.045, LONE[1] + 0.23), lw=0.7, ms=4.0)
    ax.text(LONE[0], LONE[1] - 0.27, "perturbation", ha="center", va="top", **RULE)
    end = {k: (LEAF_X - REACH[k], y) for k, y in LEAVES}
    lone_out = (LONE[0] + 0.25, LONE[1])
    x0, x1 = prong(ax, lone_out, end["collapse"])
    over(ax, x0, x1, Y["collapse"], r"pushed out, $\varepsilon>0$")
    x0, x1 = prong(ax, lone_out, end["inflation"])
    over(ax, x0, x1, Y["inflation"], r"squeezed, $\varepsilon<0$", below=True, dx=-0.35)

    # the pair, of either relative sign
    throat(ax, PAIR[0] - 0.2, PAIR[1], 0.15, "±", fs=6.5)
    throat(ax, PAIR[0] + 0.2, PAIR[1], 0.15, "±", fs=6.5)
    ax.text(PAIR[0], PAIR[1] + 0.24, "relative sign", ha="center", va="bottom", **RULE)
    pair_out = (PAIR[0] + 0.4, PAIR[1])
    x0, x1 = prong(ax, pair_out, end["scattering"])
    over(ax, x0, x1, Y["scattering"], "like signs: repel", dx=0.35)
    x0, x1 = prong(ax, pair_out, (RACE[0] - 0.36, RACE[1]))
    over(ax, x0, x1, RACE[1], "opposite signs: attract", below=True, dx=-0.4)

    # the attracting pair: its horizon against the inflation its companion starts
    throat(ax, RACE[0] - 0.15, RACE[1], 0.15, "+", fs=6.5)
    throat(ax, RACE[0] + 0.15, RACE[1], 0.15, "−", fs=6.5)
    ax.text(RACE[0], RACE[1] + 0.23, "the race", ha="center", va="bottom", **RULE)
    race_out = (RACE[0] + 0.31, RACE[1])
    x0, x1 = prong(ax, race_out, end["merger"])
    over(ax, x0, x1, Y["merger"], r"short $d$, small $p$", dx=-0.3)
    x0, x1 = prong(ax, race_out, end["pair inflation"])
    over(ax, x0, x1, Y["pair inflation"], "otherwise", below=True, dx=-0.2)

    for k, y in LEAVES:
        DRAW[k](ax, LEAF_X, y)
        name, what = TEXT[k]
        ax.text(TEXT_X, y + 0.02, name, ha="left", va="bottom", fontsize=9.0,
                color=style.INK, weight="bold")
        ax.text(TEXT_X, y - 0.02, what, ha="left", va="top", fontsize=7.5, color=style.MUTED)
        if k in GW:
            wave(ax, *WAVE_X, y + 0.08, k)
            ax.text(WAVE_X[0], y - 0.1, f"GW: {GW[k]}", ha="left", va="top", fontsize=6.5,
                    color=style.MUTED)


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
    # the audit cannot see a label that runs off the canvas
    frame = fig.bbox
    for txt in ax.texts:
        b = txt.get_window_extent()
        if b.x0 < frame.x0 or b.x1 > frame.x1 or b.y0 < frame.y0 or b.y1 > frame.y1:
            problems.append(f"'{txt.get_text()[:32]}' runs off the canvas")
            print(f"{TAG} '{txt.get_text()[:32]}' runs off the canvas")
    print(f"{TAG} label audit: {len(problems)} problem(s) {problems[:3]}")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("00_overview", args.pack_root) / "fates.png")
    png = style.save(fig, out)
    print(f"{TAG} wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
