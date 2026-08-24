#!/usr/bin/env python3
"""A schematic of the Bondi dipole: the bend, and the worldlines it draws.

Drawn, not measured -- the shape is a pair of softened point-mass
potentials, so the caption must call this a schematic.  Line art in black
and white throughout, so the two panels read as one figure and the thing
survives a greyscale print.  Fonts come from pdflatex through matplotlib's
pgf backend, so it matches the article's typography.

  (a) one spatial slice as a rubber sheet.  The phantom star raises a hill,
      the canonical star sinks a well.  A body follows the slope the *other*
      one made, never its own -- and at a body's own centre its own dimple
      is flat, so the sheet's tangent there IS the partner's slope.  Both
      tangents run the same way, so the two arrows come out parallel.

  (b) the same pair in spacetime.  Both worldlines lean and curve; the width
      of the band between them never changes.

Writes research/bondi_dipole/figures/fig_spacetime_bend.pdf.
"""

import argparse
import os

import numpy as np

import matplotlib

matplotlib.use("pgf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402
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

SINGLE = 3.375  # PRD column width, inches

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


def callout(ax, p, text, offset, va, fontsize=6.9):
    """Label a 3D point with a short leader, offset in typographic points.

    Offsetting from the projected point rather than anchoring to a panel
    corner keeps the leader short and the bounding box tight, whatever the
    view angle does to the surface.
    """
    ax.annotate(text, xy=proj(ax, p), xycoords="data", xytext=offset,
                textcoords="offset points", ha="center", va=va, ma="center",
                fontsize=fontsize, color="0.1", zorder=9,
                arrowprops=dict(arrowstyle="-", lw=0.55, color="0.45",
                                shrinkA=1, shrinkB=3))


def panel_bend(ax):
    # the sample counts are 8n+1 and 6m+1 so that the strides below divide
    # them exactly -- otherwise plot_surface leaves a sliver row and a
    # sliver column at two edges, and the mesh looks unfinished there
    x = np.linspace(-14.5, 14.5, 8 * 22 + 1)
    y = np.linspace(-9.0, 9.0, 6 * 18 + 1)
    X, Y = np.meshgrid(x, y)
    Z = sheet(X, Y)
    lim = float(np.abs(Z).max())

    # An opaque white sheet whose own polygons carry the mesh: one call, so
    # the far side of the surface hides the lines behind it.  Line art beats
    # grey wash here -- the figure has to survive a greyscale print at one
    # column wide, and the mesh is what tells hill from well.
    ax.plot_surface(X, Y, Z, color="white", edgecolor="0.22", linewidth=0.3,
                    rstride=6, cstride=8, shade=False, antialiased=True,
                    zorder=2)
    # the sheet is exactly level along x = 0: hill on one side, well on the
    # other, and the divide is where the two contributions cancel
    ax.plot(np.zeros_like(y), y, np.zeros_like(y), color="k", lw=0.75,
            ls=(0, (2.5, 1.5)), zorder=4)

    ax.set_axis_off()
    # orthographic, so the two acceleration arrows -- equal vectors at
    # different depths -- project to exactly equal lengths, and the hill and
    # the well are drawn at the same scale
    ax.set_proj_type("ortho")
    ax.set_box_aspect((2.0, 1.12, 0.74), zoom=1.26)
    ax.set_zlim(-1.06 * lim, 1.06 * lim)
    ax.view_init(elev=32, azim=-70)

    zh, zw = float(profile(-D0)), float(profile(D0))
    for xs, zs, mk in ((-D0, zh, "s"), (D0, zw, "o")):
        ax.plot([xs], [0], [zs], marker=mk, ms=4.2, markerfacecolor="white",
                markeredgecolor="k", markeredgewidth=0.75, zorder=6)

    callout(ax, (-D0, 0, zh), "phantom, $M_-<0$:\na \\emph{hill}",
            (-4, 17), "bottom")
    callout(ax, (D0, 0, zw), "canonical, $M_+>0$:\na \\emph{well}",
            (4, -18), "top")


def panel_band(ax):
    t = np.linspace(0.0, 1.0, 240)
    drift = DRIFT * t ** 2
    xm, xp = -D0 + drift, D0 + drift

    ax.fill_betweenx(t, xm, xp, color="0.905", lw=0, zorder=1)
    ax.plot([0, 0], [0, 1], color="0.62", ls=(0, (1, 2)), lw=0.6,
            zorder=2)
    ax.plot(xm, t, color="k", ls=(0, (3, 1.6)), lw=1.1, zorder=4)
    ax.plot(xp, t, color="k", ls="-", lw=1.1, zorder=4)
    ax.plot(0.5 * (xm + xp), t, color="0.45", ls=(0, (1, 1.4)), lw=0.9,
            zorder=3)

    for xs, mk in ((-D0, "s"), (D0, "o")):
        for tt in (0.0, 1.0):
            ax.plot([xs + DRIFT * tt ** 2], [tt], marker=mk, ms=3.8,
                    markerfacecolor="white", markeredgecolor="k",
                    markeredgewidth=0.75, zorder=6, clip_on=False)

    # the separation never changes: a rigid pair, not a tidal stretch
    tb, xb = 0.46, DRIFT * 0.46 ** 2
    ax.annotate("", xy=(xb + D0, tb), xytext=(xb - D0, tb), zorder=5,
                arrowprops=dict(arrowstyle="<->", mutation_scale=6, lw=0.7,
                                color="0.35", shrinkA=0, shrinkB=0))
    ax.text(xb - D0 - 0.7, tb, "$d$ fixed", ha="right", va="center",
            fontsize=6.9, color="0.3")

    # the headline quantity: the midpoint itself moves
    ax.annotate("", xy=(DRIFT, 1.055), xytext=(0.0, 1.055),
                annotation_clip=False,
                arrowprops=dict(arrowstyle="-|>", mutation_scale=6, lw=0.8,
                                color="0.3", shrinkA=0, shrinkB=0))
    ax.text(0.5 * DRIFT, 1.085, r"midpoint drift $\Delta X$", ha="center",
            va="bottom", fontsize=6.9, color="0.3", clip_on=False)

    tl = 0.87
    ax.text(-D0 + DRIFT * tl ** 2 - 0.8, tl, "phantom", ha="right",
            va="center", fontsize=6.9, color="0.1")
    ax.text(D0 + DRIFT * tl ** 2 + 0.8, tl, "canonical", ha="left",
            va="center", fontsize=6.9, color="0.1")

    x0, x1 = -D0 - 5.5, D0 + DRIFT + 7.5
    y0, y1 = -0.03, 1.03
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)

    # a spacetime diagram wants axes that point, not a box
    for xy, xytext in (((x1, y0), (x0, y0)), ((x0, y1), (x0, y0))):
        ax.annotate("", xy=xy, xytext=xytext, annotation_clip=False,
                    zorder=7,
                    arrowprops=dict(arrowstyle="-|>", mutation_scale=7,
                                    lw=0.7, color="k", shrinkA=0, shrinkB=0))
    ax.text(x1, y0 - 0.05, "$x$", ha="right", va="top", fontsize=8.5,
            clip_on=False)
    ax.text(x0 - 0.9, y1, "time", ha="center", va="top", rotation=90,
            fontsize=8.5, clip_on=False)


def build(path=None):
    # mplot3d reports a square bounding box whatever the surface looks
    # like, so a tight save wastes half the column on white.  Oversize the
    # 3D axes instead, sit the spacetime panel under it, and save the
    # canvas verbatim at exactly one column.
    height = 3.80
    fig = plt.figure(figsize=(SINGLE, height))
    ax = fig.add_axes([-0.055, 0.3211, 1.11, 0.7526], projection="3d")
    panel_bend(ax)
    bx = fig.add_axes([0.135, 0.0813, 0.840, 0.2937])
    panel_band(bx)
    fig.text(0.012, 0.988, "(a)", ha="left", va="top", fontsize=8.5)
    fig.text(0.012, 0.4092, "(b)", ha="left", va="top", fontsize=8.5)

    path = path or os.path.join(OUT, "fig_spacetime_bend.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=400, pad_inches=0.0,
                bbox_inches=Bbox([[0.0, 0.0], [SINGLE, height]]))
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
