#!/usr/bin/env python3
"""A schematic of the Bondi dipole: the bend, and the band it sweeps.

Drawn, not measured -- the shapes are softened point-mass potentials, so the
caption must call this a schematic.  Fonts come from pdflatex through
matplotlib's pgf backend, so it matches the article's typography.

  (a) one spatial slice as a rubber sheet.  The phantom star is a hill and
      the canonical star a well -- blue up, red down, the sign convention of
      the article's chi - 1 panels.  Each body is accelerated by the
      *other's* active mass, so both arrows point the same way.

  (b) the same pair in spacetime.  Both worldlines lean and curve; the width
      of the band between them does not change.

Writes research/bondi_dipole/figures/fig_spacetime_bend.pdf.
"""

import argparse
import os

import numpy as np

import matplotlib

matplotlib.use("pgf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402
from mpl_toolkits.mplot3d import proj3d  # noqa: E402

# .../GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/bondi_dipole
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *[os.pardir] * 5))
OUT = os.path.join(REPO, "research", "bondi_dipole", "figures")

plt.rcParams.update(
    {
        "pgf.texsystem": "pdflatex",
        "pgf.rcfonts": False,
        "font.family": "serif",
        "font.size": 8.5,
        "axes.labelsize": 8.5,
        "axes.titlesize": 8.5,
        "axes.linewidth": 0.5,
        "lines.linewidth": 1.0,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    }
)

DOUBLE = 7.0

D0 = 5.0        # half-separation of the pair
SOFT = 3.0      # core softening: these stars are extended, not points
DRIFT = 11.0    # how far the pair travels over the drawn time span


def sheet(x, y):
    """Softened dipole potential: hill on the left, well on the right."""
    rp = np.sqrt((x + D0) ** 2 + y ** 2 + SOFT ** 2)     # phantom, M < 0
    rc = np.sqrt((x - D0) ** 2 + y ** 2 + SOFT ** 2)     # canonical, M > 0
    return SOFT * (1.0 / rp - 1.0 / rc)


def profile(x):
    return sheet(x, 0.0)


def proj(ax, p):
    """A 3D point in the axes' projected 2D frame."""
    return proj3d.proj_transform(*p, ax.get_proj())[:2]


def flat_arrow(ax, p0, p1, color="k", lw=0.9, head=6.0, zorder=8):
    """A 2D arrow between two 3D points, drawn in the projected frame.

    mplot3d's own quiver puts the head in the data volume, where it
    foreshortens into a smudge; projecting first keeps every head the same
    size on the page.
    """
    ax.annotate("", xy=proj(ax, p1), xytext=proj(ax, p0), xycoords="data",
                textcoords="data", zorder=zorder,
                arrowprops=dict(arrowstyle="-|>", mutation_scale=head,
                                lw=lw, color=color, shrinkA=0, shrinkB=0))


def callout(ax, p, text, xy_axes, ha, va):
    """Label a 3D point from a fixed corner of the panel.

    Anchoring the text in axes fractions and running a leader to the point
    is the only placement that cannot drift onto the surface when the view
    or the panel size changes.
    """
    ax.annotate(text, xy=proj(ax, p), xycoords="data", xytext=xy_axes,
                textcoords="axes fraction", ha=ha, va=va, ma="left",
                fontsize=7.2, color="0.1", zorder=9,
                arrowprops=dict(arrowstyle="-", lw=0.55, color="0.45",
                                shrinkA=1, shrinkB=3))


def panel_bend(ax):
    x = np.linspace(-14, 14, 161)
    y = np.linspace(-9, 9, 101)
    X, Y = np.meshgrid(x, y)
    Z = sheet(X, Y)
    lim = float(np.abs(Z).max())

    norm = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
    ax.plot_surface(X, Y, Z, cmap="RdBu", norm=norm, rstride=2, cstride=2,
                    linewidth=0, antialiased=True, shade=False, alpha=0.95,
                    rasterized=True, zorder=2)
    ax.plot_wireframe(X, Y, Z, rstride=6, cstride=8, color="0.30",
                      linewidth=0.25, alpha=0.55, zorder=3)

    ax.set_axis_off()
    ax.set_box_aspect((2.0, 1.15, 0.66), zoom=1.15)
    ax.set_zlim(-1.05 * lim, 1.05 * lim)
    ax.view_init(elev=32, azim=-60)

    zh, zw = float(profile(-D0)), float(profile(D0))
    for xs, zs, mk in ((-D0, zh, "s"), (D0, zw, "o")):
        ax.plot([xs], [0], [zs], marker=mk, ms=4.2, markerfacecolor="white",
                markeredgecolor="k", markeredgewidth=0.75, zorder=6)

    # both accelerations point the same way -- that is the whole effect
    for xs, zs, lab in ((-D0, zh, "$a_-$"), (D0, zw, "$a_+$")):
        flat_arrow(ax, (xs + 1.2, 0, zs), (xs + 6.0, 0, zs))
        ax.annotate(lab, xy=proj(ax, (xs + 3.6, 0, zs)), xycoords="data",
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7.4, color="0.1",
                    zorder=9)

    callout(ax, (-D0, 0, zh), "phantom, $M_-<0$:\na \\emph{hill}",
            (0.015, 0.96), "left", "top")
    callout(ax, (D0, 0, zw), "canonical, $M_+>0$:\na \\emph{well}",
            (0.985, 0.04), "right", "bottom")
    ax.set_title("(a)", loc="left", pad=-2)


def panel_band(ax):
    t = np.linspace(0.0, 1.0, 240)
    drift = DRIFT * t ** 2
    xm, xp = -D0 + drift, D0 + drift

    ax.fill_betweenx(t, xm, xp, color="0.905", lw=0, zorder=1)
    ax.plot([0, 0], [0, 1], color="0.62", ls=(0, (1, 2)), lw=0.6, zorder=2)
    ax.plot(xm, t, color="k", ls=(0, (3, 1.6)), lw=1.1, zorder=4)
    ax.plot(xp, t, color="k", ls="-", lw=1.1, zorder=4)
    ax.plot(0.5 * (xm + xp), t, color="0.45", ls=(0, (1, 1.4)), lw=0.9,
            zorder=3)

    for xs, mk in ((-D0, "s"), (D0, "o")):
        for tt in (0.0, 1.0):
            ax.plot([xs + DRIFT * tt ** 2], [tt], marker=mk, ms=4.0,
                    markerfacecolor="white", markeredgecolor="k",
                    markeredgewidth=0.75, zorder=6, clip_on=False)

    # the separation never changes: a rigid pair, not a tidal stretch
    tb, xb = 0.46, DRIFT * 0.46 ** 2
    ax.annotate("", xy=(xb + D0, tb), xytext=(xb - D0, tb), zorder=5,
                arrowprops=dict(arrowstyle="<->", mutation_scale=6, lw=0.7,
                                color="0.35", shrinkA=0, shrinkB=0))
    ax.text(xb - D0 - 0.7, tb, "$d$ fixed", ha="right", va="center",
            fontsize=7.2, color="0.3")

    # the headline quantity: the midpoint itself moves
    ax.annotate("", xy=(DRIFT, 1.055), xytext=(0.0, 1.055),
                annotation_clip=False,
                arrowprops=dict(arrowstyle="-|>", mutation_scale=6, lw=0.8,
                                color="0.3", shrinkA=0, shrinkB=0))
    ax.text(0.5 * DRIFT, 1.08, r"midpoint drift $\Delta X$", ha="center",
            va="bottom", fontsize=7.2, color="0.3", clip_on=False)

    tl = 0.88
    ax.text(-D0 + DRIFT * tl ** 2 - 0.7, tl, "phantom", ha="right",
            va="center", fontsize=7.2, color="0.1")
    ax.text(D0 + DRIFT * tl ** 2 + 0.7, tl, "canonical", ha="left",
            va="center", fontsize=7.2, color="0.1")

    ax.set_xlim(-D0 - 5.5, D0 + DRIFT + 7.5)
    ax.set_ylim(-0.012, 1.012)
    ax.set_xlabel("$x$", labelpad=1.5, loc="right")
    ax.set_ylabel("time", labelpad=3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("(b)", loc="left")


def build(path=None):
    fig = plt.figure(figsize=(DOUBLE, 2.85))
    gs = fig.add_gridspec(1, 2, width_ratios=(1.30, 1.0), wspace=0.08,
                          left=0.005, right=0.965, bottom=0.10, top=0.885)
    panel_bend(fig.add_subplot(gs[0, 0], projection="3d"))
    panel_band(fig.add_subplot(gs[0, 1]))
    path = path or os.path.join(OUT, "fig_spacetime_bend.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=400)
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--out", default=None,
                    help="output PDF (default: the article's figures/)")
    args = ap.parse_args(argv)
    print(f"wrote {build(args.out)}")


if __name__ == "__main__":
    main()
