#!/usr/bin/env python3
"""Generate the figures for the Bondi-dipole article (PRD style).

Everything is derived from the packed campaign in
results/bondi-dipole-runaway/campaign/ -- the revision's runs on the fixed
code (fourth-order time integration, c12664fd, and the fixed initial data;
research/bondi_dipole/STATUS.md), filed by question in campaign/NN_group/.
Text is rendered by pdflatex through matplotlib's pgf backend, so figure
fonts are the same Computer Modern as the article body.

Outputs (results/bondi-dipole-runaway/figures/<group>/, PDF + PNG, one folder per
campaign group; the article reads them from there; FIGURES.md is the index):
  00_overview/schematic        Bondi's sign rules (drawn, no data)
  04_runaway/chase_frames      activity and chi-1 stills of the headline N=256
                               cell with the tracked cores overlaid
  04_runaway/trajectories      worldlines / drift+fit to t=400 / signal vs nulls
  05_separation/forcelaw       both axes of a = M/d^2: the separation scan at
                               fixed mass, and the equal-mass ladder at fixed
                               separation
  03_same_sign/samesign        the same-sign controls merge on one clock; their
                               centroids stay pinned
  06_mass/massscale            the gap opens/closes according to which star is
                               heavier; zero crossing at mass ratio ~1
  04_runaway/wavezone          l=2 Weyl amplitude on four shells: near-zone
                               falloff, no radiative tail (the null with a number)
The constraint record of the appendix is plot_convergence's two figures,
09_convergence/convergence_pair and convergence_lone; print_convergence
prints the resolution numbers the text quotes.

Run it from anywhere; it prints every number quoted in the article text.
"""

import os
import csv
import glob
import re
import json

import numpy as np
from PIL import Image

import matplotlib

matplotlib.use("pgf")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from grteclyn_wrapper.visualisation.wormhole_merger import style

# .../GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/bondi_dipole
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *[os.pardir] * 5))
PACK = os.path.join(REPO, "results", "bondi-dipole-runaway")
CAMP = os.path.join(PACK, "campaign")
OUT = os.path.join(PACK, "figures")

# The article's look; plot_convergence draws the appendix figures with it too
RC = {
    "pgf.texsystem": "pdflatex",
    "pgf.rcfonts": False,
    "font.family": "serif",
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "axes.titlesize": 8.5,
    "legend.fontsize": 7.3,
    "xtick.labelsize": 7.8,
    "ytick.labelsize": 7.8,
    "axes.linewidth": 0.5,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.minor.size": 1.6,
    "ytick.minor.size": 1.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "lines.linewidth": 1.1,
    "legend.frameon": False,
    "legend.handlelength": 1.7,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
}
plt.rcParams.update(RC)

SINGLE = 3.375  # PRD column width, inches
DOUBLE = 7.0

# One accent colour for every fitted or predicted curve, so that a fit is never
# told from the data by dash pattern alone (Okabe--Ito vermillion: colour-blind
# safe, and still a mid grey if the page is printed in black and white).
FIT = "#D55E00"
GREY = "0.45"     # every second-tier curve: one accent, the rest ink or grey
# the resolution ladder, coarsest to finest, in every figure that shows it,
# and the convergence orders it is measured against: order 2 in the fit
# accent, order 4 in grey, each with its own dash (2026-10-26: no blue)
LADDER = {128: (0, (1, 1.5)), 192: (0, (4, 1.6)), 256: "-"}
ORDER_COLOUR = {2: FIT, 4: GREY}
ORDER_LS = {2: (0, (3.4, 1.5)), 4: (0, (3.4, 1.2, 1.0, 1.2))}

# The frame stills carry locked colour scales (measured off their own colour
# bars, identical on every frame kept): activity 0 -> 4.0e-2 in viridis, and
# chi - 1 symmetric at +-8.7e-3 in RdBu, blue positive (2026-10-26, PM10 N 256
# on the fixed code; the v1 stills were at +-9.4e-3).
A_MAX = 0.040
CHI_MAX = 0.0087

# ---------------------------------------------------------------- cell names
# The Table I label, the box and the cells (2026-10-23); one run per label
# unless a resolution set is named.
HEAD = {n: f"PM10_L64_N{n}" for n in (128, 192, 256)}
SCAN = {8: "PM8_L64_N128",
        10: "PM10_L64_N128",
        12: "PM12_L64_N128",
        16: "PM16_L64_N128",
        20: "PM20_L64_N128"}
MIRROR = "MP10_L64_N128"
LONGRUN = "PM10_L64_N128_t400"
WAVEZONE = "PM10_L128_N256"
LONE_P = "P_L64_N128"
# M at its finest grid: N 192 and 256 agree on its drift to 0.4 %, while the
# N 128 core tracker takes a +2e-3 excursion over t 128-135
LONE_M = "M_L64_N256"
LONE_M_SET = {n: f"M_L64_N{n}" for n in (128, 192, 256)}
PP = "PP10_L64_N128"
MM = "MM10_L64_N128"
MASS = {"heavy": "R1.33_L64_N128",
        "matched": "PM10_L64_N128",
        "w0804": "R0.80_L64_N128",
        "w088": "R0.60_L64_N128"}

# dressed ADM masses of the working stars as the reruns' solver gives them
# (campaign/06_mass/mass_law.csv, row PM20_L64_N128; the August star table
# had 0.014349964 / 0.014294692)
M_P = 0.0143503759   # canonical, omega = 0.75
M_M = 0.0142931076   # |phantom|, omega = 0.7603 (matched to 0.40%)
MBAR = 0.5 * (M_P + M_M)   # what the midpoint acceleration measures

# dressed masses at the mass-ladder frequencies (stars/star_family_massratio.csv)
M_LADDER = {0.75: 0.014349964, 0.7603: 0.014294692, 0.804: 0.011472499,
            0.81: 0.010720519, 0.88: 0.008573106}


# a key above its frame, spread over the frame's width (the panels' standing
# rule: every line named above the frame, nothing but tags inside it)
def key_above(ax, x0=0.0, **kw):
    opts = dict(loc="lower left", bbox_to_anchor=(x0, 1.02, 1.0 - x0, 0.1),
                mode="expand", borderaxespad=0.0, handlelength=1.5,
                columnspacing=0.8, handletextpad=0.4, labelspacing=0.25)
    opts.update(kw)
    return ax.legend(**opts)


# ------------------------------------------------------------------- output
def save(fig, stem):
    """figures/<group>/<name>.pdf and its PNG, one folder per campaign group as
    the merger pack's figures/ (2026-10-26); unchanged pixels are not rewritten.
    Every text a line crosses, or that sits on another text or a key, is
    printed (style.label_audit)."""
    # a margin round every text, so a label resting on a curve is caught too
    if style.label_audit(fig, pad=0.02):  # it prints what it finds
        print(f"  ^ in {stem}")
    style.save(fig, os.path.join(OUT, stem))
    plt.close(fig)


# ------------------------------------------------------------------ loaders
def cell_dir(cell):
    """campaign/<NN_group>/<cell>: the pack files each run under the question
    it answers (2026-10-23), so a cell is found by its name alone."""
    hits = sorted(glob.glob(os.path.join(CAMP, "[0-9][0-9]_*", cell)))
    return hits[0] if hits else os.path.join(CAMP, cell)


def cell_file(cell, name):
    return os.path.join(cell_dir(cell), name)


def load(cell, name, skiprows=0):
    return np.loadtxt(cell_file(cell, name), skiprows=skiprows)


def bary(cell):
    """t, barycentre x of each sector, sector totals and rms radii."""
    d = load(cell, "sector_barycenters.dat")
    return dict(t=d[:, 0], xc=d[:, 2], xp=d[:, 7], totc=d[:, 1],
                totp=d[:, 6], rmsc=d[:, 5], rmsp=d[:, 10])


def dyn(cell):
    """t, sub-cell core positions, peaks, coordinate and proper gap,
    sector momenta, and the shift evaluated at each core."""
    d = load(cell, "sector_dynamics.dat")
    return dict(t=d[:, 0], xc=d[:, 1], xp=d[:, 5], pkc=d[:, 4], pkp=d[:, 8],
                sep=d[:, 9], psep=d[:, 10], pxc=d[:, 11], pxp=d[:, 12],
                pxt=d[:, 13], bxc=d[:, 14], bxp=d[:, 15])


def midpoint(cell):
    """t and the pair midpoint (mean of the two sector barycentres) --
    the article's drift variable."""
    b = bary(cell)
    return b["t"], 0.5 * (b["xc"] + b["xp"])


def fit_a(t, x, t0=5.0, t1=None):
    """Twice the quadratic coefficient of x(t) over [t0, t1]: the fitted
    constant acceleration.  The article's convention is t0 = 5 (gauge
    settling) to the end of the run."""
    if t1 is None:
        t1 = t[-1]
    m = (t >= t0) & (t <= t1)
    return 2.0 * np.polyfit(t[m], x[m], 2)[0]


def norms(cell):
    """t, L2 Ham, L2 Mom on the evolution grid (constraint_norms.dat)."""
    d = load(cell, "constraint_norms.dat")
    return d[:, 0], d[:, 1], d[:, 2]


def interior_norm(cell, constraint=0, r_max=24):
    """t and the L2 norm of a constraint (0 Ham, 1 Mom) over r < r_max about
    the box centre, combined by volume from the unit shells of
    constraint_shells.dat (as plot_convergence.zone does); r_max 24 keeps the
    absorbing layer out, whose dissipation is not part of the field
    equations."""
    d = load(cell, "constraint_shells.dat")
    r = np.arange(r_max)
    w = (r + 1.0) ** 3 - r ** 3
    sh = d[:, 1 + constraint * 33 + r]
    return d[:, 0], np.sqrt((sh ** 2 * w).sum(axis=1) / w.sum())


def l2_amplitude(cell, radii):
    """t and A_l2(R) = sqrt(sum_m |r psi4^{2m}|^2) at each shell, from
    psi4_mode_l2_all.dat (columns: t, then (Re,Im) x 5 modes per shell)."""
    d = load(cell, "psi4_mode_l2_all.dat")
    t = d[:, 0]
    A = {}
    for ri, R in enumerate(radii):
        base = 1 + ri * 10
        A[R] = np.sqrt(sum(d[:, base + 2 * m] ** 2 +
                           d[:, base + 2 * m + 1] ** 2 for m in range(5)))
    return t, A


# ------------------------------------------------------------------ stills
def crop_axes_area(png_path):
    """Cut the plot interior out of a packed frame still.

    The stills come in two layouts: a light interior between thin dark
    spines (the slices) and a dark interior whose own pixels form the block
    (the mip projections).  Both carry a colour bar to the right, and on the
    dark-interior stills the bar's own pixels merge with the axes into one
    column block -- so only the top, bottom and left edges are detected and
    the right edge follows from squareness (equal aspect, square domain).
    The result spans the full simulation domain [0, L]^2; overlaying the
    tracked cores on it was checked against the tracker at t = 0, 120, 200.
    """
    im = np.asarray(Image.open(png_path).convert("RGB"))
    dark = im.mean(axis=2) < 128
    h, w = dark.shape

    def line_groups(counts, thresh):
        idx = np.where(counts > thresh)[0]
        groups, start = [], None
        for a, b in zip(idx, np.append(idx[1:], -99)):
            if start is None:
                start = a
            if b != a + 1:
                groups.append((start, a))
                start = None
        return groups

    vgroups = line_groups(dark.sum(axis=0), 0.55 * h)
    hgroups = line_groups(dark.sum(axis=1), 0.45 * w)
    if not vgroups or not hgroups:
        raise RuntimeError(f"spine detection failed for {png_path}")

    if hgroups[0][1] - hgroups[0][0] > 50:        # dark interior: one block
        top, bottom = hgroups[0][0] + 1, hgroups[0][1] - 1
    elif len(hgroups) > 1:                        # thin spines
        top, bottom = hgroups[0][1] + 1, hgroups[1][0] - 1
    else:
        raise RuntimeError(f"spine detection failed for {png_path}")
    if vgroups[0][1] - vgroups[0][0] > 50:
        left = vgroups[0][0] + 1
    else:
        left = vgroups[0][1] + 1

    side = bottom - top + 1
    return im[top:top + side, left:left + side]


# ------------------------------------------------------------ fig: schematic
def fig_schematic():
    """Bondi's sign rules: the three pairings of active mass."""
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(SINGLE, 2.62))
    ax.set_aspect("equal")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.75)
    ax.axis("off")

    R = 0.50
    XL, XR = 2.15, 4.85
    Y = {"a": 5.55, "b": 3.55, "c": 1.35}

    ax.text(5.0, 7.45, r"each body is accelerated by the \emph{other's} "
            r"active mass;", ha="center", va="center", fontsize=6.6,
            color="0.15")
    ax.text(5.0, 6.95, r"inertia is $|M|$ and positive in every case",
            ha="center", va="center", fontsize=6.6, color="0.15")

    def body(x, y, sector):
        if sector == "+":
            fc, ec, lab, ls = "0.88", "k", "$+M$", "-"
        else:
            fc, ec, lab, ls = "white", "0.25", "$-M$", (0, (2.6, 1.4))
        ax.add_patch(mpatches.Circle((x, y), R, facecolor=fc, edgecolor=ec,
                                     lw=0.9, linestyle=ls, zorder=3))
        ax.text(x, y, lab, ha="center", va="center", fontsize=6.8, color="k",
                zorder=4)

    def force(x0, x1, y):
        ax.annotate("", xy=(x1, y), xytext=(x0, y), zorder=5,
                    arrowprops=dict(arrowstyle="-|>", color="k", lw=0.9,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))

    def verdict(y, text, sub, bold=False, size=7.3):
        ax.text(6.05, y + 0.28, text, ha="left", va="center", fontsize=size,
                fontweight="bold" if bold else "normal")
        ax.text(6.05, y - 0.34, sub, ha="left", va="center", fontsize=5.9,
                color="0.35")

    def letter(y, s):
        ax.text(0.18, y + 0.72, s, ha="left", va="center", fontsize=7.5)

    def caption(y, s, x=3.5):
        ax.text(x, y + 0.72, s, ha="center", va="center", fontsize=6.0,
                color="0.3")

    y = Y["a"]
    letter(y, "(a)")
    body(XL, y, "+"); body(XR, y, "+")
    force(XL + R + 0.12, XL + R + 0.80, y)
    force(XR - R - 0.12, XR - R - 0.80, y)
    caption(y, "both attracted")
    verdict(y, "attract", "barycentre fixed")

    y = Y["b"]
    letter(y, "(b)")
    body(XL, y, "-"); body(XR, y, "-")
    force(XL - R - 0.12, XL - R - 0.80, y)
    force(XR + R + 0.12, XR + R + 0.80, y)
    caption(y, "both repelled")
    verdict(y, "repel", "barycentre fixed")

    y = Y["c"]
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.02, y - 0.98), 9.96, 2.12,
        boxstyle="round,pad=0,rounding_size=0.12",
        facecolor="0.95", edgecolor="0.75", lw=0.5, zorder=0))
    letter(y, "(c)")
    body(XL, y, "-"); body(XR, y, "+")
    force(XL + R + 0.12, XL + R + 0.80, y)
    force(XR + R + 0.12, XR + R + 0.80, y)
    caption(y, "attracted", x=XL + R + 0.46)
    caption(y, "repelled", x=XR + R + 0.46)
    # the longest verdict a size down, inside the box
    verdict(y, "accelerate together", "barycentre accelerates", bold=True,
            size=6.4)

    ax.annotate("", xy=(XR + R + 0.95, y - 1.28), xytext=(XL - R, y - 1.28),
                arrowprops=dict(arrowstyle="-|>", color="0.45", lw=0.6,
                                shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.text(XR + R + 1.10, y - 1.28, "$x$", ha="left", va="center",
            fontsize=7.0, color="0.45")

    save(fig, "00_overview/schematic")


# --------------------------------------------------------- fig: chase frames
def fig_chase_frames():
    """Stills of the headline cell (d = 10, N = 256, frames every dt = 10),
    activity projection and chi - 1 slice, with the tracked cores overlaid."""
    cell = HEAD[256]
    D = dyn(cell)
    times = [(0, "$t=0$"), (12000, "$t=60$"), (24000, "$t=120$"),
             (40000, "$t=200$")]  # step = t / dt, dt = 0.005 at N = 256

    fig = plt.figure(figsize=(DOUBLE, 3.05))
    gs = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 1, 0.05],
                          wspace=0.08, hspace=0.10,
                          left=0.052, right=0.885, bottom=0.125, top=0.925)
    axes = np.empty((2, 4), dtype=object)
    for r in range(2):
        for c in range(4):
            first = axes[0, 0] if (r or c) else None
            axes[r, c] = fig.add_subplot(gs[r, c], sharex=first, sharey=first)
            axes[r, c].tick_params(labelbottom=(r == 1), labelleft=(c == 0))
    caxes = [fig.add_subplot(gs[r, 4]) for r in range(2)]
    for col, (step, title) in enumerate(times):
        t_here = step * 0.005
        xc = float(np.interp(t_here, D["t"], D["xc"]))
        xp = float(np.interp(t_here, D["t"], D["xp"]))

        for row, view in enumerate(("scalar_activity_proj_z",
                                    "chi_minus_1_z")):
            ax = axes[row, col]
            stem = "frame_proj_z" if "proj" in view else "frame_z"
            png = cell_file(cell, f"frames/{view}/{stem}_{step:04d}.png")
            ax.imshow(crop_axes_area(png), extent=(0, 64, 0, 64),
                      origin="upper", interpolation="bilinear",
                      rasterized=True)
            ink = "white" if row == 0 else "0.25"
            for x, mk in ((xc, "o"), (xp, "s")):
                ax.plot(x, 32, mk, ms=3.6, markerfacecolor="white",
                        markeredgecolor="k", markeredgewidth=0.7)
            # release positions and displacement arrows.  The canonical tick
            # rides at x = 37, where both rows carry a label -- the sector
            # names on top, the hill/well names below -- so it sits at a
            # different height in each row to stay clear of them.
            y_can = 41.6 if row == 0 else 38.6
            for x0, x1, yy in ((37.0, xc, y_can), (27.0, xp, 22.4)):
                ax.plot([x0, x0], [yy - 1.6, yy + 1.6], color=ink, lw=0.5,
                        ls=(0, (2, 2)))
                if x1 - x0 > 0.5:
                    ax.annotate("", xy=(x1, yy), xytext=(x0, yy),
                                arrowprops=dict(arrowstyle="-|>",
                                                mutation_scale=5, lw=0.7,
                                                color=ink, shrinkA=0,
                                                shrinkB=0))
            ax.annotate("", xy=(xp, 27.6), xytext=(xc, 27.6),
                        arrowprops=dict(arrowstyle="<->", mutation_scale=5,
                                        lw=0.6, color=ink,
                                        shrinkA=0, shrinkB=0))
            ax.text((xc + xp) / 2, 26.6, f"${xc - xp:.2f}$", ha="center",
                    va="top", fontsize=6.8, color=ink)
            ax.set_xlim(17, 51)
            ax.set_ylim(19, 45)

        axes[0, col].set_title(title)
        axes[1, col].set_xticks([20, 30, 40, 50])
        axes[1, col].set_xlabel("$x$")

    for row in (0, 1):
        axes[row, 0].set_yticks([20, 30, 40])
        axes[row, 0].set_ylabel("$y$")

    axes[0, 0].text(0.04, 0.05, r"$\mathcal{A}$",
                    transform=axes[0, 0].transAxes,
                    ha="left", va="bottom", fontsize=8.5, color="white")
    axes[1, 0].text(0.04, 0.05, r"$\chi-1$",
                    transform=axes[1, 0].transAxes,
                    ha="left", va="bottom", fontsize=8.5, color="0.2")
    axes[0, 0].text(27, 37.2, r"$\Phi_-$", ha="center", fontsize=7.5,
                    color="white")
    axes[0, 0].text(37, 37.2, r"$\Phi_+$", ha="center", fontsize=7.5,
                    color="white")
    # name the two curvature signs on the panel that first shows them, so the
    # hill and the well are read off the figure and not out of the caption
    axes[1, 0].text(27, 43.9, r"$\chi>1$", ha="center", va="top", fontsize=6.4,
                    color="0.15")
    axes[1, 0].text(37, 43.9, r"$\chi<1$", ha="center", va="top", fontsize=6.4,
                    color="0.15")

    # the two locked colour scales of the stills, so the sign divide of the
    # bottom row is explicit: blue above zero is a hill, red below it a well
    cb = fig.colorbar(matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(0.0, A_MAX), cmap="viridis"),
        cax=caxes[0])
    cb.set_ticks([0.0, 0.02, 0.04])
    cb.set_ticklabels(["$0$", "$0.02$", "$0.04$"])
    cb.ax.tick_params(labelsize=6.2, width=0.4, length=1.8)
    cb.outline.set_linewidth(0.4)

    cb = fig.colorbar(matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(-CHI_MAX, CHI_MAX), cmap="RdBu"),
        cax=caxes[1])
    cb.set_ticks([-CHI_MAX, 0.0, CHI_MAX])
    cb.set_ticklabels([f"$-{CHI_MAX:.4f}$", "$0$", f"$+{CHI_MAX:.4f}$"])
    cb.ax.tick_params(labelsize=6.2, width=0.4, length=1.8)
    cb.outline.set_linewidth(0.4)
    save(fig, "04_runaway/chase_frames")


# ------------------------------------------------------------ fig: trajectories
def fig_trajectories():
    fig, (ax, bx, cx, px) = plt.subplots(1, 4, figsize=(DOUBLE, 2.42))

    # (a) core worldlines of the headline cell: both accelerate, gap holds
    D = dyn(HEAD[256])
    t, xc, xp = D["t"], D["xc"], D["xp"]
    ax.fill_between(t, xp, xc, color="0.93", lw=0)
    ax.plot(t, xc, color="k", ls="-", lw=1.0, label="positive mass")
    ax.plot(t, xp, color="k", ls="--", lw=1.0, label="negative mass")
    for tt in (12.0, 100.0, 188.0):
        a = float(np.interp(tt, t, xc))
        b = float(np.interp(tt, t, xp))
        ax.annotate("", xy=(tt, b), xytext=(tt, a),
                    arrowprops=dict(arrowstyle="<->", lw=0.6, color="0.35",
                                    shrinkA=0, shrinkB=0))
        if tt == 100.0:
            continue          # middle arrow unlabelled: no room at this width
        ax.annotate(f"${a - b:.2f}$", xy=(tt, (a + b) / 2),
                    xytext=(tt + (5 if tt < 150 else -5), (a + b) / 2),
                    fontsize=6.6, color="0.35", va="center",
                    ha="left" if tt < 150 else "right")
    ax.set_xlim(0, 205)
    ax.set_ylim(24, 42)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$x$")

    # (b) midpoint drift with the constant-acceleration fit, to t = 400
    tL, mL = midpoint(LONGRUN)
    dL = mL - mL[0]
    aL = fit_a(tL, mL)
    m = tL >= 5
    fit = np.polyfit(tL[m], dL[m], 2)
    bx.plot(tL, dL, color="k", ls="-", lw=1.0, zorder=4,
            label=r"PM10-t400")
    bx.plot(tL, np.polyval(fit, tL), color=FIT, ls=(0, (3.4, 1.5)), lw=1.5,
            zorder=6,
            label=rf"fit, ${aL * 1e4:.2f}{{\times}}10^{{-4}}$")
    t3, m3 = midpoint(HEAD[256])
    bx.plot(t3, m3 - m3[0], color="0.3", ls="--", lw=0.9, zorder=3,
            label=r"PM10, $N{=}256$")
    bx.set_xlim(0, 410)
    bx.set_ylim(-0.3, 1.25 * dL.max())
    bx.set_xlabel("$t$")
    bx.set_ylabel(r"$\Delta X$")

    # (c) the signal against every null, log scale.  The lone stars are
    # tracked by their cores: the whole-domain barycentre of an off-centre
    # star picks up domain noise in the sector weight (see the text).  On the
    # fixed code the star at the centre and the two same-sign pairs keep their
    # mirror symmetry, so they sit at round-off; M, 5 units off centre, drifts.
    cx.plot(t3, np.abs(m3 - m3[0]), color="k", ls="-", lw=1.1, zorder=5,
            label="mixed pair")
    dP = dyn(LONE_P)
    cx.plot(dP["t"], np.abs(dP["xc"] - dP["xc"][0]), color="0.5",
            ls=(0, (3, 1.2)), lw=0.8, label="P")
    dM = dyn(LONE_M)
    cx.plot(dM["t"], np.abs(dM["xp"] - dM["xp"][0]), color="0.5",
            ls="-.", lw=0.8, label="M")
    bpp = bary(PP)
    cx.plot(bpp["t"], np.abs(bpp["xc"] - bpp["xc"][0]), color="0.35",
            ls=(0, (1, 1.5)), lw=0.8, label="PP10")
    bmm = bary(MM)
    cx.plot(bmm["t"], np.abs(bmm["xp"] - bmm["xp"][0]), color="0.35",
            ls=(0, (5, 1.5)), lw=0.8, label="MM10")
    # the separation bar: both tips land on the curves they measure --
    # the signal above, the highest of the four nulls below
    t_bar = 103.0
    sig = float(np.interp(t_bar, t3, np.abs(m3 - m3[0])))
    floor = max(float(np.interp(t_bar, tt, np.abs(xx - xx[0])))
                for tt, xx in ((dP["t"], dP["xc"]), (dM["t"], dM["xp"]),
                               (bpp["t"], bpp["xc"]), (bmm["t"], bmm["xp"])))
    cx.annotate("", xy=(t_bar, floor), xytext=(t_bar, sig),
                arrowprops=dict(arrowstyle="<->", lw=0.6, color="0.45",
                                shrinkA=0, shrinkB=0))
    cx.set_yscale("log")
    cx.set_xlim(0, 205)
    cx.set_ylim(3e-16, 3e3)          # headroom: the label sits above its curve
    cx.set_yticks([1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1])
    cx.minorticks_off()
    cx.set_xlabel("$t$")
    cx.set_ylabel(r"$|\Delta X|$", labelpad=1)

    # (d) the Bondi signature itself: each sector's volume-integrated matter
    # momentum grows like M|v| while the *signed* sum of Eq. (4) stays at
    # zero.  Plotted for the base and finest rungs; the signed sum is
    # magnified x10 to be visible on the same axis as its own terms; the base
    # rung's residual is the larger of the two, so the cancellation improves
    # with resolution rather than sitting at a diagnostic floor.
    for n, (lw, al) in ((128, (0.8, 0.45)), (256, (1.1, 1.0))):
        Dn = dyn(HEAD[n])
        px.plot(Dn["t"], Dn["pxc"] * 1e4, color="k", ls="-", lw=lw, alpha=al)
        px.plot(Dn["t"], np.abs(Dn["pxp"]) * 1e4, color="0.45", ls="--",
                lw=lw, alpha=al)
        px.plot(Dn["t"], Dn["pxt"] * 1e4 * 10, color=FIT, ls="-", lw=lw,
                alpha=al)
    px.axhline(0, color="0.75", lw=0.5, zorder=0)
    D2 = dyn(HEAD[256])
    p_top = D2["pxc"].max() * 1e4
    # the key: the three quantities in the finest rung's ink, then the two
    # rungs by weight (light N 128, dark N 256)
    px.legend(handles=[
        Line2D([], [], color="k", ls="-", lw=1.1, label=r"$P^{(+)}$"),
        Line2D([], [], color="0.45", ls="--", lw=1.1, label=r"$|P^{(-)}|$"),
        Line2D([], [], color=FIT, ls="-", lw=1.1, label=r"$10\,P$"),
        Line2D([], [], color="k", lw=0.8, alpha=0.45, label=r"$N{=}128$"),
        Line2D([], [], color="k", lw=1.1, label=r"$N{=}256$")],
        loc="lower left", bbox_to_anchor=(0.0, 1.02, 1.0, 0.1),
        borderaxespad=0.0, ncol=2, fontsize=5.8,
        handlelength=1.3, columnspacing=0.8, handletextpad=0.35,
        labelspacing=0.25)
    px.set_xlim(0, 205)
    px.set_ylim(-0.16 * p_top, 1.2 * p_top)
    px.set_xlabel("$t$")
    px.set_ylabel(r"matter momentum $[10^{-4}]$")

    small = dict(fontsize=5.8, handlelength=1.3, columnspacing=0.5,
                 handletextpad=0.35)
    key_above(ax, ncol=1, **small)
    key_above(bx, ncol=1, **small)
    key_above(cx, ncol=2, mode=None, **small)   # natural width: "mixed pair" is long
    # the panel letters inside the frames, top left: the keys hold the top
    for a, s in zip((ax, bx, cx, px), "abcd"):
        a.text(0.04, 0.96, f"({s})", transform=a.transAxes, ha="left",
               va="top")

    for a in (ax, cx, px):
        a.set_xticks([0, 100, 200])
    bx.set_xticks([0, 200, 400])
    fig.subplots_adjust(wspace=0.56)
    save(fig, "04_runaway/trajectories")


# ------------------------------------------------------------ fig: force law
def mass_ladder():
    """The equal-mass ladder at fixed d = 20, as the pack's mass_law.csv holds it.

    Four mass-matched pairs spanning a factor 2.46 in mass.  Matching the two
    stars is what makes the absolute constant quotable: an unequal pair deforms
    over the run (Sec. V F), and a quadratic fit to a moving separation is not
    a measurement of anything.  A matched pair stays rigid, so a alone answers
    a = M/d^2.

    Each row carries the acceleration on the halo-free CORE tracker (the
    reported one), its window spread, and the whole-domain barycentre as the
    cross-check -- the two part company only on the lightest, most diffuse
    pair, whose shed halo drags the barycentre fit off.  The file is
    written by grteclyn_wrapper.analysis.bondi_dipole.fit_mass_law, which
    recomputes the masses from the frequencies the elliptic solver itself
    recorded.
    """
    with open(os.path.join(CAMP, "06_mass", "mass_law.csv")) as fh:
        text = fh.read()
    slope = re.search(r"^# slope p = ([-\d.]+) \+/- ([\d.]+)", text, re.M)
    if slope is None:
        raise SystemExit("mass_law.csv carries no fitted slope header")
    rows = sorted(
        csv.DictReader(ln for ln in text.splitlines() if not ln.startswith("#")),
        key=lambda r: float(r["m_mean"]),
    )
    return (
        dict(m=np.array([float(r["m_mean"]) for r in rows]),
             a=np.array([float(r["a"]) for r in rows]),
             aerr=np.array([float(r["a_err"]) for r in rows]),
             abar=np.array([float(r["a_bary"]) for r in rows]),
             d=float(rows[0]["d"])),
        float(slope.group(1)), float(slope.group(2)),
    )


def fig_forcelaw():
    # --- left column: the separation axis, at fixed mass -------------------
    ds = np.array(sorted(SCAN))
    accs = np.array([fit_a(*midpoint(SCAN[d])) for d in ds])
    slope, off = np.polyfit(np.log(ds), np.log(accs), 1)
    res = np.log(accs) - (slope * np.log(ds) + off)
    dof = len(ds) - 2
    var = np.sum(res ** 2) / dof / np.sum(
        (np.log(ds) - np.mean(np.log(ds))) ** 2)
    slope_err = np.sqrt(var)

    # --- right column: the mass axis, at fixed separation ------------------
    ml, pslope, pslope_err = mass_ladder()
    mm, am, aerr, abar, dm = ml["m"], ml["a"], ml["aerr"], ml["abar"], ml["d"]
    m2 = mm * 100.0                      # plotted in units of 10^-2
    ratio_m = am * dm ** 2 / mm
    poff = np.mean(np.log(am) - pslope * np.log(mm))

    fig, ((ax, cx), (bx, dx)) = plt.subplots(2, 2, figsize=(SINGLE, 3.80))

    # (a) a(d) at fixed mass
    ax.plot(ds, accs * 1e4, ls="none", marker="o", ms=4, color="k",
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    dd = np.linspace(7.2, 22, 100)
    ax.plot(dd, MBAR / dd ** 2 * 1e4, color="0.5", ls="-", lw=0.8,
            label=r"$\bar M/d^2$")
    ax.plot(dd, np.exp(off) * dd ** slope * 1e4, color=FIT,
            ls=(0, (3.4, 1.5)), lw=1.4, label=rf"fit $d^{{{slope:.2f}}}$")
    key_above(ax, ncol=1, fontsize=6.0, handlelength=1.4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([8, 10, 12, 16, 20])
    ax.set_xticklabels(["$8$", "$10$", "$12$", "$16$", "$20$"])
    ax.set_yticks([0.3, 0.5, 1, 2])
    ax.set_yticklabels(["$0.3$", "$0.5$", "$1$", "$2$"])
    ax.minorticks_off()
    ax.set_xlim(7.2, 22)
    ax.set_ylim(0.2, 3.2)
    ax.set_xlabel("$d$")
    ax.set_ylabel(r"$a\ [10^{-4}]$")
    ax.set_title(r"(a)\quad vary $d$, mass fixed", loc="left", fontsize=7.5,
                 pad=22)   # above its key

    # (b) a d^2 over the pair mass, against separation
    ratio = accs * ds ** 2 / MBAR
    bx.axhspan(0.99, 1.01, color="0.93", zorder=0, lw=0)
    bx.axhline(1.0, color="0.5", lw=0.6)
    bx.plot(ds, ratio, marker="o", ms=4, color="k", ls="-", lw=0.8,
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    # the converged (N = 256) point at d = 10, for the grid calibration
    a256 = fit_a(*midpoint(HEAD[256]))
    bx.plot([10], [a256 * 100 / MBAR], marker="D", ms=4, color="k",
            ls="none", markerfacecolor="0.75", markeredgewidth=0.8, zorder=6)
    bx.text(20.7, 1.012, r"$\pm1\%$", fontsize=6.4, color="0.45",
            va="bottom", ha="right")
    bx.set_xlim(7, 21)
    bx.set_ylim(min(ratio.min(), 0.99) - 0.015,
                max(a256 * 100 / MBAR, 1.01) + 0.02)
    bx.set_xlabel("$d$")
    bx.set_ylabel(r"$a\,d^2/\bar M$")
    bx.set_title("(b)", loc="left", fontsize=7.5)

    # (c) a(M) at fixed separation -- the other axis of a = M/d^2
    mmline = np.linspace(0.80, 2.45, 100)
    cx.plot(mmline, mmline * 1e-2 / dm ** 2, color="0.5", ls="-", lw=0.8,
            label=r"$\bar M/d^2$")
    cx.plot(mmline, np.exp(poff) * (mmline * 1e-2) ** pslope, color=FIT,
            ls=(0, (3.4, 1.5)), lw=1.4,
            label=rf"fit $M^{{{pslope:.2f}}}$")
    cx.errorbar(m2, am, yerr=aerr, ls="none", marker="o", ms=4, color="k",
                markerfacecolor="white", markeredgewidth=0.9, elinewidth=0.7,
                capsize=1.6, zorder=5)
    key_above(cx, ncol=1, fontsize=6.0, handlelength=1.4)
    cx.set_xscale("log")
    cx.set_yscale("log")
    cx.set_xticks([0.9, 1.2, 1.6, 2.2])
    cx.set_xticklabels(["$0.9$", "$1.2$", "$1.6$", "$2.2$"])
    cx.minorticks_off()
    cx.set_yticks([2e-5, 3e-5, 4e-5, 6e-5])
    cx.set_yticklabels(["$2$", "$3$", "$4$", "$6$"])
    cx.set_xlim(0.80, 2.72)
    cx.set_ylim(1.9e-5, 7.6e-5)
    cx.set_xlabel(r"$\bar M\ [10^{-2}]$")
    cx.set_ylabel(r"$a\ [10^{-5}]$")
    cx.set_title(r"(c)\quad vary mass, $d$ fixed", loc="left", fontsize=7.5,
                 pad=22)

    # (d) the same ladder compensated: a d^2 / M, rung by rung
    dx.axhspan(0.99, 1.01, color="0.93", zorder=0, lw=0)
    dx.axhline(1.0, color="0.5", lw=0.6)
    dx.errorbar(m2, ratio_m, yerr=aerr * dm ** 2 / mm, marker="o", ms=4,
                color="k", ls="-", lw=0.8, markerfacecolor="white",
                markeredgewidth=0.9, elinewidth=0.7, capsize=1.6, zorder=5)
    dx.text(2.44, 1.012, r"$\pm1\%$", fontsize=6.4, color="0.45",
            va="bottom", ha="right")
    dx.set_xticks([0.9, 1.2, 1.6, 2.0, 2.4])
    dx.set_xticklabels(["$0.9$", "$1.2$", "$1.6$", "$2.0$", "$2.4$"])
    dx.set_xlim(0.80, 2.45)
    # room for the error bars: at N = 128 a falls by ~20 % over the run in
    # every rung (2026-10-26), so the window spread is ~10 %
    err_m = aerr * dm ** 2 / mm
    dx.set_ylim(min((ratio_m - err_m).min(), 0.99) - 0.02,
                max((ratio_m + err_m).max(), 1.01) + 0.02)
    dx.set_xlabel(r"$\bar M\ [10^{-2}]$")
    dx.set_ylabel(r"$a\,d^2/\bar M$")
    dx.set_title("(d)", loc="left", fontsize=7.5)

    fig.subplots_adjust(hspace=0.58, wspace=0.55)
    save(fig, "05_separation/forcelaw")

    print("fig_forcelaw stats:")
    for d, a in zip(ds, accs):
        D = dyn(SCAN[d])
        print(f"  d={d:2.0f}: a={a:.4e}  a*d2={a * d ** 2:.5f} "
              f" a*d2/Mbar={a * d ** 2 / MBAR:.4f}  "
              f"px_end={D['pxt'][-1]:+.1e}")
    print(f"  power law: d^({slope:.3f} +- {slope_err:.3f}); "
          f"4-pt (no d=20): "
          f"{np.polyfit(np.log(ds[:4]), np.log(accs[:4]), 1)[0]:.3f}")
    print(f"  N=256 d=10: a={a256:.4e}, a*d2/Mbar={a256 * 100 / MBAR:.4f}")
    print(f"  mass ladder at d={dm:.0f} (core tracker, barycentre in brackets):")
    for m, a, e, ab in zip(mm, am, aerr, abar):
        print(f"    M={m:.5e}: a={a:.4e} +- {e:.1e}  a*d2/M={a * dm ** 2 / m:.4f}"
              f"  [bary {ab * dm ** 2 / m:.4f}]")
    print(f"  power law: M^({pslope:.3f} +- {pslope_err:.3f}); "
          f"mass span x{mm.max() / mm.min():.2f}; "
          f"|a d^2/M - 1| max {np.max(np.abs(ratio_m - 1)) * 100:.2f}%")


# ------------------------------------------------------ numbers: convergence
def print_convergence():
    """The resolution numbers the text quotes (Sec. VII A): Delta X(200) and a
    at the three resolutions, and the order of the Hamiltonian norm inside
    r < 24 at t = 0 (the elliptic solve's second) and late in the run (the
    evolution's).  The main-text figure that drew them left the article on
    2026-10-26; the appendix sets (plot_convergence) show the same data."""
    h0, hl = [], []
    for n in (128, 192, 256):
        tn, ham = interior_norm(HEAD[n])
        h0.append(ham[0])                       # the first step, t = 0.02 dx
        hl.append(ham[tn >= 150].mean())        # late-time mean
    h0, hl = np.array(h0), np.array(hl)
    p0 = np.log(h0[0] / h0[-1]) / np.log(2.0)   # N 128 -> 256
    pl = np.log(hl[0] / hl[-1]) / np.log(2.0)

    print("convergence stats:")
    for n in (128, 192, 256):
        t, m = midpoint(HEAD[n])
        d = dyn(HEAD[n])
        b = bary(HEAD[n])
        print(f"  N={n}: drift={m[-1] - m[0]:+.5f}  a5={fit_a(t, m):.4e}  "
              f"baryGap end {b['xc'][-1] - b['xp'][-1]:.3f}  "
              f"coreGap end {d['sep'][-1]:.3f}  px_end={d['pxt'][-1]:+.2e}")
    t1, m1 = midpoint(HEAD[192]); t2, m2 = midpoint(HEAD[256])
    d1, d2 = m1[-1] - m1[0], m2[-1] - m2[0]
    a1, a2 = fit_a(t1, m1), fit_a(t2, m2)
    print(f"  fine pair: drift {d1:.4f}/{d2:.4f} "
          f"({abs(d1 / d2 - 1) * 100:.2f}%), "
          f"a {a1:.4e}/{a2:.4e} ({abs(a1 / a2 - 1) * 100:.2f}%)")
    for n, hh0, hhl in zip((128, 192, 256), h0, hl):
        print(f"  N={n}: L2Ham(r<24) t=0 {hh0:.2e}  late mean {hhl:.2e}")
    print(f"  orders N 128 -> 256: t=0 {p0:.2f}, late {pl:.2f}")


# ------------------------------------------------------------ fig: same sign
def merger_time(cell):
    """The first frame at which the |chi - 1| profile has one maximum left
    (well_tracking.dat, gap 0): the same-sign pair has merged."""
    W = load(cell, "well_tracking.dat")
    return float(W[W[:, 3] == 0, 0][0])


def fig_samesign():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 2.9))

    # (a) the two same-sign pairs merge on the same clock
    merged = {cell: merger_time(cell) for cell in (PP, MM)}
    for cell, ls, lab, mfc in ((PP, "-", r"PP10", "white"),
                               (MM, "--", r"MM10", "k")):
        W = load(cell, "well_tracking.dat")
        t, gap = W[:, 0], W[:, 3]
        live = gap > 0
        ax.plot(t[live], gap[live], color="k", ls=ls, lw=1.0, label=lab)
        ax.plot([merged[cell]], [0.35], marker="v", ms=4, color="k",
                markerfacecolor=mfc, markeredgewidth=0.8, ls="none")
    t_pp, t_mm = merged[PP], merged[MM]
    # the note just left of the two markers it names, under the curves
    ax.text(32.6, 1.3, f"merged:\n$t={t_pp:.1f}$ / ${t_mm:.1f}$",
            fontsize=6.8, color="0.2", ha="right", va="center", ma="left")
    key_above(ax, x0=0.09, ncol=2, fontsize=6.8, mode=None)
    ax.set_xlim(0, 45)
    ax.set_ylim(0, 9.4)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$d$ of the $|\chi-1|$ extrema")
    ax.text(0.0, 1.02, "(a)", transform=ax.transAxes, ha="left", va="bottom")

    # (b) and their centroids stay pinned through it: on the fixed code the
    # two pairs keep their mirror symmetry, so the centroid sits at round-off
    t3, m3 = midpoint(HEAD[256])
    bx.plot(t3, np.abs(m3 - m3[0]), color="k", ls="-", lw=1.1, zorder=5,
            label="mixed pair")
    for cell, sect, ls, lab in ((PP, "xc", (0, (1, 1.5)), "PP10"),
                                (MM, "xp", (0, (4, 1.6)), "MM10")):
        b = bary(cell)
        x = b[sect]
        bx.plot(b["t"], np.abs(x - x[0]), color="0.4", ls=ls, lw=0.7,
                label=lab)
    key_above(bx, x0=0.09, ncol=3, fontsize=6.8, mode=None)
    # the merger marked between the signal and the round-off band, where
    # its rule crosses nothing else
    bx.axvline(t_pp, color="0.7", lw=0.5, ls=(0, (2, 2)))
    bx.text(t_pp - 5.0, 1e-7, "merger", fontsize=6.2, color="0.5", ha="right",
            va="center", rotation=90)
    bx.set_yscale("log")
    bx.set_xlim(0, 205)
    bx.set_ylim(3e-16, 3e2)
    bx.set_yticks([1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1])
    bx.minorticks_off()
    bx.set_xlabel("$t$")
    bx.set_ylabel(r"$|\Delta X|$")
    bx.text(0.0, 1.02, "(b)", transform=bx.transAxes, ha="left", va="bottom")

    fig.subplots_adjust(hspace=0.55)
    save(fig, "03_same_sign/samesign")

    print("fig_samesign stats:")
    for cell in (PP, MM):
        W = load(cell, "well_tracking.dat")
        t, gap = W[:, 0], W[:, 3]
        gaps = "  ".join(f"g({tt})={float(np.interp(tt, t, gap)):.2f}"
                         for tt in (0, 20, 30, 32))
        print(f"  {cell}: {gaps}  merged from t={merged[cell]:.1f}")
    for cell, sect in ((PP, "xc"), (MM, "xp")):
        b = bary(cell)
        x = b[sect]
        print(f"  {cell}: centroid end {x[-1] - x[0]:+.2e} "
              f"max|.| {np.max(np.abs(x - x[0])):.1e}")
    tff = (np.pi / 2) * np.sqrt(10.0 ** 3 / (2 * (M_P + M_P)))
    print(f"  Newtonian free-fall (2 x M+, d=10): t={tff:.0f}; "
          f"merger at {t_pp:.1f} -> force ratio ~{(tff / t_pp) ** 2:.0f}")


# ------------------------------------------------------------ fig: mass scale
# --------------------------------------------------- the sign flip, shared
def sign_flip_spread():
    """Where the mass-ladder gap change crosses zero under four conventions
    (barycentres at t = 200, cores, proper distance, barycentres averaged over
    190-200): ({convention: ratio}, midpoint, half-range).  The massscale
    annotation and print_numbers quote the same midpoint +- half-range."""
    ratios = {"heavy": M_M / M_LADDER[0.81], "matched": M_M / M_P,
              "w0804": M_LADDER[0.804] / M_P, "w088": M_LADDER[0.88] / M_P}
    keys = ("w088", "w0804", "matched", "heavy")

    def cross(vals):
        xs = np.array([ratios[k] for k in keys])
        ys = np.array([vals[k] for k in keys])
        i = int(np.searchsorted(ys, 0.0))
        return xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1]) / (ys[i] - ys[i - 1])

    def gap_bary(k, avg_from=None):
        b = bary(MASS[k])
        g = np.abs(b["xc"] - b["xp"])
        if avg_from is not None:
            return g[b["t"] >= avg_from].mean() - g[0]
        return g[-1] - g[0]

    conv = {
        "barycentre gap at t=200 (paper)": {k: gap_bary(k) for k in keys},
        "core gap at t=200": {k: dyn(MASS[k])["sep"][-1] - dyn(MASS[k])["sep"][0]
                              for k in keys},
        "proper gap at t=200": {k: dyn(MASS[k])["psep"][-1] - dyn(MASS[k])["psep"][0]
                                for k in keys},
        "barycentre gap, mean over [190,200]": {k: gap_bary(k, avg_from=190)
                                                for k in keys},
    }
    out = {lab: float(cross(v)) for lab, v in conv.items()}
    lo, hi = min(out.values()), max(out.values())
    return out, 0.5 * (lo + hi), 0.5 * (hi - lo)


def fig_massscale():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 2.75))

    ratios = {"heavy": M_M / M_LADDER[0.81],          # |M-|/M+' = 1.333
              "matched": M_M / M_P,                    # 0.996
              "w0804": M_LADDER[0.804] / M_P,          # 0.800
              "w088": M_LADDER[0.88] / M_P}            # 0.597
    styles = {"heavy": ("-", "k", "$1.33$"),
              "matched": ((0, (1, 1.5)), "k", "$1.00$"),
              "w0804": ("--", "0.35", "$0.80$"),
              "w088": ("-.", "0.35", "$0.60$")}
    for key in ("heavy", "matched", "w0804", "w088"):
        b = bary(MASS[key])
        gap = np.abs(b["xc"] - b["xp"])
        ls, c, lab = styles[key]
        ax.plot(b["t"], gap - gap[0], color=c, ls=ls, lw=1.0,
                label=rf"$|M_-|/M_+={lab[1:-1]}$" if key == "heavy" else lab)
    ax.axhline(0, color="0.75", lw=0.5, zorder=0)
    key_above(ax, x0=0.09, ncol=4, fontsize=6.6, columnspacing=0.6)
    ax.text(0.0, 1.02, "(a)", transform=ax.transAxes, ha="left",
            va="bottom")
    ax.set_xlim(0, 200)
    ax.set_ylim(-1.55, 1.16)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$d(t)-d_0$")

    # (b) the end-of-run gap change against the mass ratio
    xs, ys = [], []
    for key in ("w088", "w0804", "matched", "heavy"):
        b = bary(MASS[key])
        gap = np.abs(b["xc"] - b["xp"])
        xs.append(ratios[key])
        ys.append(gap[-1] - gap[0])
    xs, ys = np.array(xs), np.array(ys)
    bx.plot(xs, ys, color="0.72", ls="-", lw=0.8, zorder=2)
    bx.plot(xs, ys, ls="none", marker="o", ms=4.5, color="k",
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    bx.axhline(0, color="0.75", lw=0.5, zorder=0)
    # the sign flip, read off the two cells that bracket it, under the four
    # gap conventions: midpoint +- half-range, as the text quotes it
    i = int(np.searchsorted(ys, 0.0))
    x0 = xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1]) / (ys[i] - ys[i - 1])
    _, xmid, xhalf = sign_flip_spread()
    bx.axvline(1.0, color="0.8", lw=0.5, ls=(0, (2, 2)), zorder=0)
    bx.text(1.03, -0.3, rf"zero at ${xmid:.2f}\pm{xhalf:.2f}$,"
            "\npredicted $1$", fontsize=6.8,
            color="0.2", ha="left", va="top", ma="left")
    bx.set_xlim(0.5, 1.45)
    bx.set_ylim(-1.65, 0.85)
    bx.set_xlabel(r"mass ratio $|M_-|/M_+$")
    bx.set_ylabel(r"$d(200)-d_0$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(hspace=0.42)
    save(fig, "06_mass/massscale")

    print("fig_massscale stats:")
    for key, x, y in zip(("w088", "w0804", "matched", "heavy"), xs, ys):
        print(f"  {key:8s} ratio={x:.4f}  gap change at 200 = {y:+.4f}")
    print(f"  sign flip (bracketing cells) at ratio {x0:.4f}; "
          f"over the four conventions {xmid:.4f} +- {xhalf:.4f}")

    # separation-corrected pull fits: C in xdd = +-C/d(t)^2 per star,
    # from the core tracker, t >= 5.  Quote ratios to the matched cell only.
    def pull(cell):
        D = dyn(cell)
        t, gap = D["t"], np.abs(D["sep"])
        inv = 1.0 / gap ** 2
        I1 = np.concatenate([[0], np.cumsum(
            0.5 * (inv[1:] + inv[:-1]) * np.diff(t))])
        I2 = np.concatenate([[0], np.cumsum(
            0.5 * (I1[1:] + I1[:-1]) * np.diff(t))])
        out = {}
        for name, x in (("canon", D["xc"]), ("phant", D["xp"])):
            msk = t >= 5
            A = np.vstack([np.ones(msk.sum()), t[msk], I2[msk]]).T
            coef, *_ = np.linalg.lstsq(A, x[msk], rcond=None)
            out[name] = coef[2]
        return out

    base = pull(MASS["matched"])
    print(f"  matched-cell fit constants (nominal {M_M:.4f}/{M_P:.4f}): "
          f"canon {base['canon']:.4f}, phant {base['phant']:.4f} -- "
          "ratios only, never the constants")
    pred = {"w0804": M_LADDER[0.804] / M_M, "w088": M_LADDER[0.88] / M_M,
            "heavy": M_LADDER[0.81] / M_P}
    for key in ("w0804", "w088", "heavy"):
        f = pull(MASS[key])
        changed = "canon" if key != "heavy" else "phant"
        r = f[changed] / base[changed]
        other = "phant" if changed == "canon" else "canon"
        ru = f[other] / base[other]
        print(f"  {key:8s}: changed-partner pull ratio {r:.3f} "
              f"(predicted {pred[key]:.4f}, "
              f"dev {abs(r / pred[key] - 1) * 100:.1f}%); "
              f"unchanged-partner control {ru:.3f}")


# ------------------------------------------------------------ fig: wave zone
def fig_wavezone():
    radii = (16, 24, 32, 40)
    t, A = l2_amplitude(WAVEZONE, radii)

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 2.75))

    styles = {16: "-", 24: "--", 32: "-.", 40: (0, (1, 1.5))}
    for R in radii:
        ax.plot(t, A[R], color="k" if R == 16 else "0.35", ls=styles[R],
                lw=0.9, label=f"$R={R}$")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01, 1.0, 0.12),
              mode="expand", ncol=4, borderaxespad=0.0, fontsize=6.8,
              handlelength=1.5, columnspacing=0.8, handletextpad=0.4)
    ax.set_yscale("log")
    ax.set_xlim(0, 205)
    top = max(A[R].max() for R in radii)
    ax.set_ylim(0.5 * min(A[R][t >= 1].min() for R in radii), 3 * top)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$|R\,\Psi_4|_{\ell=2}$")
    ax.text(0.025, 0.94, "(a)", transform=ax.transAxes, ha="left", va="top")
    # once the start-up pulse has crossed the spheres outward, the amplitude
    # falls with radius at every time (a near zone); printed below, not drawn
    # (no notes inside the frame, 2026-10-26)
    stack = np.array([A[R] for R in radii])
    ordered = np.all(stack[:-1] > stack[1:], axis=0)
    t_ord = t[np.where(~ordered)[0][-1] + 1] if not ordered.all() else t[0]

    # (b) the falloff: psi4 vs R against r^-1 (radiation) and the fit
    sel = (t >= 150) & (t <= 200)
    means = np.array([A[R][sel].mean() / R for R in radii])
    p = np.polyfit(np.log(radii), np.log(means), 1)
    bx.plot(radii, means, ls="none", marker="o", ms=4.5, color="k",
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    rr = np.linspace(15, 42, 50)
    bx.plot(rr, np.exp(p[1]) * rr ** p[0], color=FIT, ls=(0, (3.4, 1.5)),
            lw=1.4, label=rf"fit $R^{{{p[0]:.1f}}}$ (near zone)")
    bx.plot(rr, means[0] * (radii[0] / rr), color="0.45", ls="--", lw=0.9,
            label=r"$R^{-1}$ (radiation)")
    key_above(bx, x0=0.09, ncol=2, fontsize=6.6, mode=None)
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xticks(radii)
    bx.set_xticklabels([f"${R}$" for R in radii])
    bx.minorticks_off()
    bx.set_xlim(15, 42)
    bx.set_xlabel("$R$")
    bx.set_ylabel(r"$|\Psi_4|_{\ell=2}$, mean $150\le t\le200$")
    bx.text(0.0, 1.02, "(b)", transform=bx.transAxes, ha="left", va="bottom")

    fig.subplots_adjust(hspace=0.55)
    save(fig, "04_runaway/wavezone")

    print("fig_wavezone stats:")
    i = int(np.argmin(np.abs(t - 199)))
    for R in radii:
        print(f"  R={R}: A(t=199)={A[R][i]:.2e}  "
              f"mean(150-200) r*psi4={A[R][sel].mean():.2e}  "
              f"psi4={A[R][sel].mean() / R:.2e}")
    print(f"  psi4 ~ r^{p[0]:.2f} (mean 150-200); "
          f"r*psi4 falls x{A[16][sel].mean() / A[40][sel].mean():.0f} "
          f"from R=16 to 40; ordered by radius from t={t_ord:.1f}")
    tw, mw = midpoint(WAVEZONE)
    t1, m1 = midpoint(HEAD[128])
    print(f"  wavezone drift {mw[-1] - mw[0]:+.4f} vs L=64 "
          f"{m1[-1] - m1[0]:+.4f} "
          f"({(mw[-1] - mw[0]) / (m1[-1] - m1[0]) - 1:+.1%})")


# ------------------------------------------------------------------ numbers
def print_numbers():
    """Every number quoted in the article text, in order of appearance."""
    print("=" * 72)
    print("QUOTED NUMBERS")
    print("=" * 72)

    print(f"masses: M+={M_P:.6f} M-={-M_M:.6f} "
          f"(matched to {(M_P - M_M) / M_P * 100:.2f}%), Mbar={MBAR:.6f}; "
          f"point-mass a at d=10: {MBAR / 100:.4e}")

    for n in (128, 192, 256):
        t, m = midpoint(HEAD[n])
        D = dyn(HEAD[n])
        print(f"headline N={n}: drift(200)={m[-1] - m[0]:+.5f} "
              f"a={fit_a(t, m):.4e} px_total(200)={D['pxt'][-1]:+.2e}")
    D = dyn(HEAD[256])
    for tt in (100, 200):
        i = int(np.argmin(np.abs(D["t"] - tt)))
        print(f"  sector momenta t={tt}: p+={D['pxc'][i]:+.3e} "
              f"p-={D['pxp'][i]:+.3e} signed total={D['pxt'][i]:+.2e} "
              f"({abs(D['pxt'][i] / D['pxc'][i]) * 100:.1f}% of either)")
    b = bary(HEAD[256])
    print(f"  bary gap 10.000 -> {b['xc'][-1] - b['xp'][-1]:.3f}; "
          f"core gap -> {D['sep'][-1]:.3f}")

    t0, m0 = midpoint(HEAD[128])
    tm, mm_ = midpoint(MIRROR)
    print(f"mirror: drift ratio "
          f"{(mm_[-1] - mm_[0]) / (m0[-1] - m0[0]):+.6f}, "
          f"a ratio {fit_a(tm, mm_) / fit_a(t0, m0):+.6f}")

    for cell, cols in ((LONE_P, slice(1, 4)),
                       *((m, slice(5, 8)) for m in LONE_M_SET.values())):
        d = load(cell, "sector_dynamics.dat")
        db = load(cell, "sector_barycenters.dat")
        bcols = slice(2, 5) if cell == LONE_P else slice(7, 10)
        print(f"{cell}: max any-axis core drift "
              f"{np.max(np.abs(d[:, cols] - d[0, cols])):.1e} "
              f"(whole-domain barycentre: "
              f"{np.max(np.abs(db[:, bcols] - db[0, bcols])):.1e})")
    Dl = dyn(LONE_P)
    print(f"  lone canonical peak {Dl['pkc'][0]:.4f}->{Dl['pkc'][-1]:.4f} "
          f"({(Dl['pkc'][-1] / Dl['pkc'][0] - 1) * 100:+.2f}%)")

    C = load(HEAD[256], "confinement.dat")
    print(f"matter: peak {C[0, 2]:.4f}->{C[-1, 2]:.4f} "
          f"({(C[-1, 2] / C[0, 2] - 1) * 100:+.2f}%), min chi over run "
          f"{C[:, 17].min():.5f}")
    K = load(HEAD[256], "collapse_diagnostics.dat")
    print(f"  min lapse {K[:, 1].min():.5f}, max|K| {K[:, 3].max():.1e}")
    bb = bary(HEAD[256])
    print(f"  sector rms: canon {bb['rmsc'][0]:.2f}->{bb['rmsc'][-1]:.2f}, "
          f"phant {bb['rmsp'][0]:.2f}->{bb['rmsp'][-1]:.2f}")

    tL, mL = midpoint(LONGRUN)
    bL = bary(LONGRUN)
    gapL = bL["xc"] - bL["xp"]
    print(f"longrun: drift(400)={mL[-1] - mL[0]:+.4f}; "
          f"a[5,400]={fit_a(tL, mL):.4e} "
          f"a[133,266]={fit_a(tL, mL, 133, 266):.4e} "
          f"a[300,400]={fit_a(tL, mL, 300, 400):.4e} "
          f"a[350,400]={fit_a(tL, mL, 350, 400):.4e}")
    v = (mL[-1] - float(np.interp(tL[-1] - 20, tL, mL))) / 20
    print(f"  gap {gapL[0]:.3f} -> {float(np.interp(200, tL, gapL)):.3f} "
          f"(t=200) -> {gapL[-1]:.3f} (t=400); final speed ~{v:.3f}")

    Cpp = load(PP, "confinement.dat")
    print(f"PP10: activity {Cpp[0, 1]:.2f} -> "
          f"x{Cpp[:, 1].max() / Cpp[0, 1]:.1f} at "
          f"t={Cpp[int(np.argmax(Cpp[:, 1])), 0]:.0f}; "
          f"min chi {Cpp[:, 17].min():.5f}")
    F = load(PP, "boundary_flux.dat", skiprows=1)
    early = F[:, 0] <= 50
    print(f"  net boundary flux |max| t<=50: "
          f"{np.abs(F[early, 1]).max():.1e}; outward peak "
          f"{F[:, 1].max():.1e} at t={F[int(np.argmax(F[:, 1])), 0]:.0f}")
    S = load(MM, "shell_profiles.dat")
    print(f"MM hills: chi max on R=8 shell {S[:, 3].max():.4f}")

    # every cell whose pack carries the elliptic solve's log (the PM10 set
    # and M at N 256 carry none)
    for d in sorted(glob.glob(os.path.join(CAMP, "[0-9][0-9]_*", "*",
                                           "Ham_and_Mom_errors.txt"))):
        lines = [l.split() for l in open(d).readlines()[1:] if l.strip()]
        print(f"solve {os.path.basename(os.path.dirname(d))}: "
              f"{len(lines)} NL iters, exit "
              f"Ham {float(lines[-1][1]):.2e}% "
              f"Mom {float(lines[-1][2]):.2e}%")

    total = 0.0
    per = {}
    for d in sorted(glob.glob(os.path.join(CAMP, "[0-9][0-9]_*", "*")),
                    key=os.path.basename):
        c = os.path.basename(d)
        p = os.path.join(d, "metadata.json")
        if os.path.isdir(d) and os.path.exists(p):
            m = json.load(open(p))
            s = m.get("simulation_elapsed_seconds", 0.0)
            total += s
            per[c] = s / 3600
    print(f"total evolution wall time, all packed cells: {total / 3600:.1f} h"
          f" over {len(per)} cells")
    for c, h in sorted(per.items(), key=lambda kv: -kv[1])[:6]:
        print(f"  {c}: {h:.1f} h")


# ------------------------------------------- gauge, invariants, energy budget
def print_gauge_and_invariants():
    """The numbers that answer the coordinate-dependence, energy-condition and
    radiation-budget questions.  All of them are post-processing on the packed
    streams; none needs a new run."""
    print("=" * 72)
    print("GAUGE, INVARIANTS, RADIATION BUDGET")
    print("=" * 72)

    # --- is the drift coordinate dragging?  Decompose the shift at the two
    # cores into the part that can translate the pair (the mean) and the part
    # that can only change its separation (the difference).
    for n in (128, 256):
        D = dyn(HEAD[n])
        t, bc, bp = D["t"], D["bxc"], D["bxp"]
        sym = 0.5 * (bc + bp)          # translational
        anti = 0.5 * (bp - bc)         # separation-changing
        xmid = 0.5 * (D["xc"] + D["xp"])
        v = np.gradient(xmid, t)[-1]
        drag = np.trapezoid(np.abs(sym), t)
        print(f"shift at cores, N={n}: max|beta_x| = {np.abs(np.r_[bc, bp]).max():.2e}; "
              f"antisymmetric part at t=200 = {anti[-1]:.2e}")
        print(f"  translational (mean) part: max = {np.abs(sym).max():.2e}, "
              f"vs core velocity {v:.3e} -- ratio {v / np.abs(sym).max():.0f}x")
        print(f"  integral |mean shift| dt = {drag:.2e} = "
              f"{drag / (xmid[-1] - xmid[0]) * 100:.3f}% of the measured drift "
              f"{xmid[-1] - xmid[0]:+.4f}")

    # --- coordinate vs proper separation between the cores
    for n in (128, 256):
        D = dyn(HEAD[n])
        c, pr = D["sep"], D["psep"]
        print(f"separation N={n}: coordinate {c[0]:.4f} -> {c[-1]:.4f} "
              f"({(c[-1] / c[0] - 1) * 100:+.2f}%); "
              f"proper {pr[0]:.4f} -> {pr[-1]:.4f} "
              f"({(pr[-1] / pr[0] - 1) * 100:+.2f}%)")
    D = dyn(LONGRUN)
    print(f"  longrun t=400: coordinate {D['sep'][-1]:.3f}, "
          f"proper {D['psep'][-1]:.3f} -- the late opening is not gauge")

    # --- energy conditions: violation localised to the phantom, and flat
    for lab, cell in (("mixed pair N=256", HEAD[256]),
                      ("lone canonical", LONE_P), ("lone phantom", LONE_M)):
        e = load(cell, "energy_conditions.dat")
        print(f"NEC {lab}: min over run {e[:, 1].min():+.3e} "
              f"(t=0 {e[0, 1]:+.3e}, end {e[-1, 1]:+.3e}); "
              f"min WEC {e[:, 2].min():+.3e}")

    # --- constraint spike relaxation: it is gone before the fit window opens
    for n in (128, 192, 256):
        d = load(HEAD[n], "constraint_norms.dat")
        t, H = d[:, 0], d[:, 1]
        pk = H[:20].max()
        late = H[t >= 150].mean()
        after = t > t[np.argmax(H[:20])]

        def first(mask):
            # the fixed initial data (2026-10-23) left no t = 0 spike to decay
            return t[after & mask][0] if np.any(after & mask) else float("nan")

        t10, t2 = first(H <= 0.1 * pk), first(H <= 2 * late)
        print(f"constraint spike N={n}: early peak {pk:.2e}, late plateau "
              f"{late:.2e}; 10% of the peak by t={t10:.1f}, within 2x of the "
              f"plateau by t={t2:.1f} (nan: never)")

    # --- the signed mass quadrupole and the radiated energy it implies
    D = dyn(HEAD[256])
    t = D["t"]
    xc, xp = D["xc"] - 32.0, D["xp"] - 32.0
    Q = M_P * xc ** 2 - M_M * xp ** 2          # signed: sum_s eps_s M_s x_s^2
    m = (t >= 20) & (t <= 190)
    pol = np.poly1d(np.polyfit(t[m], Q[m], 4))
    Qdd, Qddd = np.polyder(pol, 2)(t[m]), np.polyder(pol, 3)(t[m])
    a256 = fit_a(*midpoint(HEAD[256]))
    lum = np.mean(Qddd ** 2) / 45.0
    print(f"signed quadrupole: Qdd = {Qdd.mean():.3e} "
          f"(analytic 2*Mbar*a*d = {2 * MBAR * a256 * 10:.3e}), "
          f"constant to {(Qdd.max() - Qdd.min()) / 2 / Qdd.mean() * 100:.0f}%")
    print(f"  |Qddd| <= {np.abs(Qddd).max():.1e}; quadrupole luminosity "
          f"~(1/45)<Qddd^2> = {lum:.1e}")
    print(f"  energy radiated over t=200 ~ {lum * 200:.1e}, against the pair's "
          f"total mass {M_P - M_M:.2e} -- {np.log10((M_P - M_M) / (lum * 200)):.0f} "
          f"orders below")

    # --- the mass-ladder sign flip: where it lands under other conventions
    conv, xmid, xhalf = sign_flip_spread()
    xs = list(conv.values())
    for lab, x in conv.items():
        print(f"sign flip, {lab}: ratio {x:.4f}")
    print(f"  end-of-run convention spread: {min(xs):.3f}--{max(xs):.3f} "
          f"-> quote {xmid:.3f} +- {xhalf:.3f}")


def main():
    fig_schematic()
    fig_chase_frames()
    fig_trajectories()
    fig_forcelaw()
    print_convergence()
    fig_samesign()
    fig_massscale()
    fig_wavezone()
    print_numbers()
    print_gauge_and_invariants()
    print("wrote figures to", OUT)


if __name__ == "__main__":
    main()
