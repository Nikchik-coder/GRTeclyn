#!/usr/bin/env python3
"""Generate the figures for the Bondi-dipole article (PRD style).

Everything is derived from the packed campaign in
results/bondi-dipole-runaway/campaign/ -- the corrected-code-path runs
(matched solve/evolution grids, maximal slicing in both sectors, t = 200).
Text is rendered by pdflatex through matplotlib's pgf backend, so figure
fonts are the same Computer Modern as the article body.

Outputs (research/bondi_dipole/figures/):
  fig_schematic.pdf      Bondi's sign rules (drawn, no data)
  fig_family.pdf         dressed-star families M(omega), both signs, with the
                         working pair and the light-star floors
  fig_chase_frames.pdf   activity and chi-1 stills of the headline N=256 cell
                         with the tracked cores overlaid
  fig_trajectories.pdf   worldlines / drift+fit to t=400 / signal vs nulls
  fig_forcelaw.pdf       both axes of a = M/d^2: the separation scan at fixed
                         mass, and the equal-mass ladder at fixed separation
  fig_convergence.pdf    resolution ladder + deep-solve/AMR twins; the two
                         error sources with opposite grid behaviour
  fig_samesign.pdf       the same-sign controls merge on one clock; their
                         centroids stay pinned
  fig_massscale.pdf      the gap opens/closes according to which star is
                         heavier; zero crossing at mass ratio ~1
  fig_wavezone.pdf       l=2 Weyl amplitude on four shells: near-zone falloff,
                         no radiative tail (the null with a number)
  fig_constraints.pdf    evolution-time constraint norms (appendix)

Run it from anywhere; it prints every number quoted in the article text.
"""

import os
import csv
import re
import json

import numpy as np
from PIL import Image

import matplotlib

matplotlib.use("pgf")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# .../GRTeclyn/grteclyn-wrapper/src/grteclyn_wrapper/visualisation/bondi_dipole
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *[os.pardir] * 5))
PACK = os.path.join(REPO, "results", "bondi-dipole-runaway")
CAMP = os.path.join(PACK, "campaign")
OUT = os.path.join(REPO, "research", "bondi_dipole", "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update(
    {
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
)

SINGLE = 3.375  # PRD column width, inches
DOUBLE = 7.0

# One accent colour for every fitted or predicted curve, so that a fit is never
# told from the data by dash pattern alone (Okabe--Ito vermillion: colour-blind
# safe, and still a mid grey if the page is printed in black and white).
FIT = "#D55E00"
SUM = "#0072B2"   # signed-momentum accent (Okabe-Ito blue)

# The frame stills carry locked colour scales (measured off their own colour
# bars, identical on every frame kept): activity 0 -> 4.0e-2 in viridis, and
# chi - 1 symmetric at +-0.0094 in RdBu, blue positive.
A_MAX = 0.040
CHI_MAX = 0.0094

# ---------------------------------------------------------------- cell names
HEAD = {128: "runaway_pair_d10_L64_N128_lev0",
        192: "runaway_pair_d10_L64_N192_lev0",
        256: "runaway_pair_d10_L64_N256_lev0"}
SCAN = {8: "runaway_pair_d08_L64_N128_lev0",
        10: "runaway_pair_d10_L64_N128_lev0",
        12: "runaway_pair_d12_L64_N128_lev0",
        16: "runaway_pair_d16_L64_N128_lev0",
        20: "runaway_pair_d20_L64_N128_lev0"}
MIRROR = "control_mirror_mp_d10_L64_N128_lev0"
DEEPSOLVE = "deepsolve_pair_d10_L64_N128_lev0"
AMRCHECK = "amrcheck_pair_d10_L64_N128_lev1"
LONGRUN = "longrun_pair_d10_t400_L64_N128_lev0"
WAVEZONE = "wavezone_pair_d10_L128_N256_lev0"
LONE_P = "control_lone_canonical_L64_N128_lev0"
LONE_M = "control_lone_phantom_L64_N128_lev0"
PP = {128: "control_pair_pp_d10_L64_N128_lev0",
      192: "control_pair_pp_d10_L64_N192_lev0",
      256: "control_pair_pp_d10_L64_N256_lev0"}
MM = {128: "control_pair_mm_d10_L64_N128_lev0",
      192: "control_pair_mm_d10_L64_N192_lev0",
      "frames": "control_pair_mm_d10_L64_N128_lev0_frames"}
MASS = {"heavy": "massratio_heavyphantom_d10_L64_N128_lev0",
        "matched": "runaway_pair_d10_L64_N128_lev0",
        "w0804": "massscale_pair_d10_w0804_L64_N128_lev0",
        "w088": "massratio_w088_r060_d10_L64_N128_lev0"}

# dressed ADM masses of the working stars (stars/*.dat headers)
M_P = 0.014349964   # canonical, omega = 0.75
M_M = 0.014294692   # |phantom|, omega = 0.7603 (matched to 0.39%)
MBAR = 0.5 * (M_P + M_M)   # what the midpoint acceleration measures

# dressed masses at the mass-ladder frequencies (stars/star_family_massratio.csv)
M_LADDER = {0.75: 0.014349964, 0.7603: 0.014294692, 0.804: 0.011472499,
            0.81: 0.010720519, 0.88: 0.008573106}


# ------------------------------------------------------------------ loaders
def cell_file(cell, name):
    return os.path.join(CAMP, cell, name)


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

    def verdict(y, text, sub, bold=False):
        ax.text(6.05, y + 0.28, text, ha="left", va="center", fontsize=7.3,
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
    verdict(y, "fall together", "barycentre fixed")

    y = Y["b"]
    letter(y, "(b)")
    body(XL, y, "-"); body(XR, y, "-")
    force(XL - R - 0.12, XL - R - 0.80, y)
    force(XR + R + 0.12, XR + R + 0.80, y)
    caption(y, "both repelled")
    verdict(y, "push apart", "barycentre fixed")

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
    verdict(y, "run away", "barycentre accelerates", bold=True)

    ax.annotate("", xy=(XR + R + 0.95, y - 1.28), xytext=(XL - R, y - 1.28),
                arrowprops=dict(arrowstyle="-|>", color="0.45", lw=0.6,
                                shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.text(XR + R + 1.10, y - 1.28, "$x$", ha="left", va="center",
            fontsize=7.0, color="0.45")

    fig.savefig(os.path.join(OUT, "fig_schematic.pdf"))
    plt.close(fig)


# ------------------------------------------------------------------ fig: family
def fig_family():
    """Both dressed-star branches over the full solved range, from the two
    scans (stars/star_family.csv, omega 0.53-0.80, and
    stars/star_family_massratio.csv, omega 0.75-0.98; same couplings)."""
    fam = {"canonical": {}, "phantom": {}}
    for fn in ("star_family.csv", "star_family_massratio.csv"):
        with open(os.path.join(PACK, "stars", fn)) as f:
            for r in csv.DictReader(f):
                if r["status"] == "ok":
                    fam[r["sector"]][round(float(r["omega_requested"]), 5)] \
                        = float(r["adm_mass"])

    fig, ax = plt.subplots(figsize=(SINGLE, 2.30))
    for sector, ls, lab, ly, va in [
            ("canonical", "-", "canonical", 0.047, "bottom"),
            ("phantom", (0, (4, 1.6)), "phantom", -0.054, "top")]:
        om = np.array(sorted(fam[sector]))
        m = np.array([fam[sector][o] for o in om])
        ax.plot(om, m, color="k", ls=ls, lw=1.05)
        ax.text(0.607, ly, lab, fontsize=7.3, color="0.1", ha="left", va=va)

    ax.axhline(0, color="0.5", lw=0.5)
    ax.axvspan(0.500, 0.5265, color="0.92", zorder=0, lw=0)
    ax.text(0.5133, -0.014, "no dressed star", rotation=90, ha="center",
            va="center", fontsize=6.2, color="0.45", zorder=4)

    # the working pair (mass-matched to 0.4%; the caption carries the
    # numbers).  The two stars sit at different frequencies on purpose: the
    # phantom is retuned until the mass magnitudes match, which is why the
    # stars are not vertically opposite each other.
    ax.plot([0.75], [M_P], marker="*", ms=8.5, color="k", ls="none", zorder=5)
    ax.plot([0.7603], [-M_M], marker="*", ms=8.5, color="k",
            markerfacecolor="white", markeredgewidth=0.8, ls="none", zorder=5)

    ax.set_xlim(0.50, 1.005)
    ax.set_ylim(-0.105, 0.085)
    ax.set_xlabel(r"$\omega$")
    ax.set_ylabel(r"$M_{\rm ADM}$")
    fig.savefig(os.path.join(OUT, "fig_family.pdf"))
    plt.close(fig)


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
    axes[1, 0].text(27, 43.9, "hill", ha="center", va="top", fontsize=6.4,
                    color="0.15")
    axes[1, 0].text(37, 43.9, "well", ha="center", va="top", fontsize=6.4,
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
    cb.set_ticklabels([f"$-{CHI_MAX:.3f}$", "$0$", f"$+{CHI_MAX:.3f}$"])
    cb.ax.tick_params(labelsize=6.2, width=0.4, length=1.8)
    cb.outline.set_linewidth(0.4)
    fig.savefig(os.path.join(OUT, "fig_chase_frames.pdf"), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------ fig: trajectories
def fig_trajectories():
    fig, (ax, bx, cx, px) = plt.subplots(1, 4, figsize=(DOUBLE, 2.42))

    # (a) core worldlines of the headline cell: both accelerate, gap holds
    D = dyn(HEAD[256])
    t, xc, xp = D["t"], D["xc"], D["xp"]
    ax.fill_between(t, xp, xc, color="0.93", lw=0)
    ax.plot(t, xc, color="k", ls="-", lw=1.0)
    ax.plot(t, xp, color="k", ls="--", lw=1.0)
    ax.text(6, 41.4, r"canonical, $M_+>0$", color="k", fontsize=6.4,
            ha="left", va="top")
    ax.text(6, 25.0, r"phantom, $M_-<0$", color="k", fontsize=6.4,
            ha="left", va="bottom")
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
    ax.set_title("(a)", loc="left")

    # (b) midpoint drift with the constant-acceleration fit, to t = 400
    tL, mL = midpoint(LONGRUN)
    dL = mL - mL[0]
    aL = fit_a(tL, mL)
    m = tL >= 5
    fit = np.polyfit(tL[m], dL[m], 2)
    bx.plot(tL, dL, color="k", ls="-", lw=1.0, zorder=4,
            label=r"$N{=}128$, $t{\le}400$")
    bx.plot(tL, np.polyval(fit, tL), color=FIT, ls=(0, (3.4, 1.5)), lw=1.5,
            zorder=6,
            label=rf"fit, ${aL * 1e4:.2f}{{\times}}10^{{-4}}$")
    t3, m3 = midpoint(HEAD[256])
    bx.plot(t3, m3 - m3[0], color="0.3", ls="--", lw=0.9, zorder=3)
    bx.legend(loc="upper left", borderaxespad=0.2, fontsize=5.8,
              handlelength=1.15, handletextpad=0.42, labelspacing=0.2,
              borderpad=0.16, framealpha=0.0)
    bx.set_xlim(0, 410)
    bx.set_ylim(-0.4, 12.4)
    bx.set_xlabel("$t$")
    bx.set_ylabel(r"$\Delta X$")
    bx.set_title("(b)", loc="left")

    # (c) the signal against every null, log scale.  The lone stars are
    # tracked by their cores: the whole-domain barycentre of an off-centre
    # star picks up domain noise in the sector weight (see the text).
    cx.plot(t3, np.abs(m3 - m3[0]), color="k", ls="-", lw=1.1, zorder=5)
    dP = dyn(LONE_P)
    cx.plot(dP["t"], np.abs(dP["xc"] - dP["xc"][0]), color="0.5",
            ls=(0, (3, 1.2)), lw=0.8)
    dM = dyn(LONE_M)
    cx.plot(dM["t"], np.abs(dM["xp"] - dM["xp"][0]), color="0.5",
            ls="-.", lw=0.8)
    bpp = bary(PP[256])
    cx.plot(bpp["t"], np.abs(bpp["xc"] - bpp["xc"][0]), color="0.35",
            ls=(0, (1, 1.5)), lw=0.8)
    bmm = bary(MM[128])
    cx.plot(bmm["t"], np.abs(bmm["xp"] - bmm["xp"][0]), color="0.35",
            ls=(0, (5, 1.5)), lw=0.8)
    cx.text(200, 5.6, "mixed pair", fontsize=6.6, ha="right", va="center")
    # the four nulls all live in one decade; label the band, not the lines
    cx.text(200, 1.05e-5, "nulls", fontsize=6.4,
            ha="right", va="bottom", color="0.3",
            bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
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
    cx.set_ylim(6.5e-6, 16)
    cx.set_xlabel("$t$")
    cx.set_ylabel(r"$|\Delta X|$")
    cx.set_title("(c)", loc="left")

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
        px.plot(Dn["t"], Dn["pxt"] * 1e4 * 10, color=SUM, ls="-", lw=lw,
                alpha=al)
    px.axhline(0, color="0.75", lw=0.5, zorder=0)
    D2 = dyn(HEAD[256])
    px.text(158, D2["pxc"][-1] * 1e4 - 0.55, r"$P_+,\ |P_-|$", fontsize=6.6,
            ha="right", va="top", color="k")
    px.text(7, 6.55, r"$(P_++P_-)\times10$", fontsize=6.3,
            ha="left", va="top", color="k")
    _lab = dict(fontsize=5.9, ha="right", va="center", color="k",
                bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    px.text(203, 4.02, r"$N{=}128$", **_lab)
    px.text(203, 0.78, r"$N{=}256$", **_lab)
    px.set_xlim(0, 205)
    px.set_ylim(-0.55, 6.9)
    px.set_xlabel("$t$")
    px.set_ylabel(r"sector momentum $[10^{-4}]$")
    px.set_title("(d)", loc="left")

    fig.subplots_adjust(wspace=0.50)
    fig.savefig(os.path.join(OUT, "fig_trajectories.pdf"))
    plt.close(fig)


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
    pair, whose shed halo drags the barycentre fit 18% off.  The file is
    written by research/bondi_dipole/fit_mass_law.py, which recomputes the
    masses from the frequencies the elliptic solver itself recorded.
    """
    with open(os.path.join(CAMP, "mass_law.csv")) as fh:
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
    ax.plot(ds, accs, ls="none", marker="o", ms=4, color="k",
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    dd = np.linspace(7.2, 22, 100)
    ax.plot(dd, MBAR / dd ** 2, color="0.5", ls="-", lw=0.8,
            label=r"$\bar M/d^2$ (point mass)")
    ax.plot(dd, np.exp(off) * dd ** slope, color=FIT, ls=(0, (3.4, 1.5)),
            lw=1.4, label=rf"fit $d^{{{slope:.2f}}}$")
    ax.legend(loc="upper right", borderaxespad=0.4, fontsize=6.3,
              handlelength=1.6, labelspacing=0.35, borderpad=0.2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([8, 10, 12, 16, 20])
    ax.set_xticklabels(["$8$", "$10$", "$12$", "$16$", "$20$"])
    ax.minorticks_off()
    ax.set_xlim(7.2, 22)
    ax.set_ylim(2.4e-5, 7.5e-4)      # headroom so the legend clears the data
    ax.set_xlabel("$d$")
    ax.set_ylabel(r"$a$")
    ax.set_title(r"(a)\quad vary $d$, mass fixed", loc="left", fontsize=7.5)

    # (b) a d^2 over the pair mass: the excess fades with separation
    ratio = accs * ds ** 2 / MBAR
    bx.axhspan(0.99, 1.01, color="0.93", zorder=0, lw=0)
    bx.axhline(1.0, color="0.5", lw=0.6)
    bx.plot(ds, ratio, marker="o", ms=4, color="k", ls="-", lw=0.8,
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    # the converged (N = 256) point at d = 10, for the grid calibration
    a256 = fit_a(*midpoint(HEAD[256]))
    bx.plot([10], [a256 * 100 / MBAR], marker="D", ms=4, color="k",
            ls="none", markerfacecolor="0.75", markeredgewidth=0.8, zorder=6)
    bx.text(7.3, 1.0043, r"$\pm1\%$", fontsize=6.4, color="0.45",
            va="center", ha="left")
    bx.set_xlim(7, 21)
    bx.set_ylim(0.985, 1.095)
    bx.set_xlabel("$d$")
    bx.set_ylabel(r"$a\,d^2/\bar M$")
    bx.set_title("(b)", loc="left", fontsize=7.5)

    # (c) a(M) at fixed separation -- the other axis of a = M/d^2
    mmline = np.linspace(0.80, 2.45, 100)
    cx.plot(mmline, mmline * 1e-2 / dm ** 2, color="0.5", ls="-", lw=0.8,
            label=rf"$\bar M/d^2$, $d={dm:.0f}$")
    cx.plot(mmline, np.exp(poff) * (mmline * 1e-2) ** pslope, color=FIT,
            ls=(0, (3.4, 1.5)), lw=1.4,
            label=rf"fit $M^{{{pslope:.2f}}}$")
    cx.errorbar(m2, am, yerr=aerr, ls="none", marker="o", ms=4, color="k",
                markerfacecolor="white", markeredgewidth=0.9, elinewidth=0.7,
                capsize=1.6, zorder=5)
    cx.legend(loc="upper left", borderaxespad=0.4, fontsize=6.3,
              handlelength=1.6, labelspacing=0.35, borderpad=0.2)
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
    cx.set_title(r"(c)\quad vary mass, $d$ fixed", loc="left", fontsize=7.5)

    # (d) the same ladder compensated: a d^2 / M, rung by rung
    dx.axhspan(0.99, 1.01, color="0.93", zorder=0, lw=0)
    dx.axhline(1.0, color="0.5", lw=0.6)
    dx.errorbar(m2, ratio_m, yerr=aerr * dm ** 2 / mm, marker="o", ms=4,
                color="k", ls="-", lw=0.8, markerfacecolor="white",
                markeredgewidth=0.9, elinewidth=0.7, capsize=1.6, zorder=5)
    dx.text(2.44, 1.0055, r"$\pm1\%$", fontsize=6.4, color="0.45",
            va="center", ha="right")
    dx.set_xticks([0.9, 1.2, 1.6, 2.0, 2.4])
    dx.set_xticklabels(["$0.9$", "$1.2$", "$1.6$", "$2.0$", "$2.4$"])
    dx.set_xlim(0.80, 2.45)
    dx.set_ylim(0.935, 1.098)
    dx.set_xlabel(r"$\bar M\ [10^{-2}]$")
    dx.set_ylabel(r"$a\,d^2/\bar M$")
    dx.set_title("(d)", loc="left", fontsize=7.5)

    fig.subplots_adjust(hspace=0.58, wspace=0.55)
    fig.savefig(os.path.join(OUT, "fig_forcelaw.pdf"))
    plt.close(fig)

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


# ---------------------------------------------------------- fig: convergence
def fig_convergence():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(DOUBLE, 2.6))

    styles = {128: (0, (1, 1.5)), 192: (0, (4, 1.6)), 256: "-"}
    for n in (128, 192, 256):
        t, m = midpoint(HEAD[n])
        ax.plot(t, m - m[0], color="k", ls=styles[n],
                lw=1.1 if n == 256 else 0.85, zorder=5)
    tD, mD = midpoint(DEEPSOLVE)
    ax.plot(tD[::20], (mD - mD[0])[::20], ls="none", marker="o", ms=2.6,
            markerfacecolor="white", markeredgewidth=0.7,
            markeredgecolor="0.3", zorder=6)
    tA, mA = midpoint(AMRCHECK)
    ax.plot(tA[::20], (mA - mA[0])[::20], ls="none", marker="x", ms=2.8,
            markeredgewidth=0.7, color="0.3", zorder=6)

    handles = [
        Line2D([], [], color="k", ls=styles[128], lw=0.85,
               label="$N=128$"),
        Line2D([], [], color="k", ls=styles[192], lw=0.85,
               label="$N=192$"),
        Line2D([], [], color="k", ls=styles[256], lw=1.1,
               label="$N=256$"),
        Line2D([], [], color="0.3", lw=0, marker="o", ms=2.6,
               markerfacecolor="white", markeredgewidth=0.7,
               label=r"solve $4.4\times$ deeper"),
        Line2D([], [], color="0.3", lw=0, marker="x", ms=2.8,
               markeredgewidth=0.7, label="mesh refinement on"),
    ]
    ax.legend(handles=handles, loc="upper left", borderaxespad=0.4,
              fontsize=6.8, handlelength=1.9, labelspacing=0.35,
              borderpad=0.2)
    ax.set_xlim(0, 205)
    ax.set_ylim(-0.1, 3.4)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$\Delta X$")
    ax.set_title("(a)", loc="left")

    # zoom on the endpoint: the fine pair coincide, the base rung sits 4% low
    ins = ax.inset_axes([0.605, 0.085, 0.375, 0.40])
    # child axes are drawn among the parent's artists, so it has to sit
    # above the marker overlays (zorder 6) or they show through it
    ins.set_zorder(9)
    ins.set_facecolor("white")
    ins.patch.set_alpha(1.0)
    for n in (128, 192, 256):
        t, m = midpoint(HEAD[n])
        ins.plot(t, m - m[0], color="k", ls=styles[n],
                 lw=1.0 if n == 256 else 0.7)
    ins.plot(tD[::10], (mD - mD[0])[::10], ls="none", marker="o", ms=2.2,
             markerfacecolor="white", markeredgewidth=0.6,
             markeredgecolor="0.3")
    ins.set_xlim(178, 201)
    ins.set_ylim(2.38, 3.16)
    ins.set_xticks([180, 200])
    ins.set_yticks([2.6, 3.0])
    ins.tick_params(labelsize=6.2)
    ins.minorticks_off()
    # the two fine rungs sit on top of each other; the base rung runs low
    ins.text(0.05, 0.93, r"$0.4\%$ apart", transform=ins.transAxes,
             fontsize=6.2, color="0.2", ha="left", va="top")
    ins.text(0.97, 0.06, r"$4\%$ low", transform=ins.transAxes,
             fontsize=6.2, color="0.35", ha="right", va="bottom")

    # (b) the two error sources with opposite grid behaviour
    dxs = np.array([0.5, 1 / 3, 0.25])
    h0, hl = [], []
    for n in (128, 192, 256):
        tn, ham, _ = norms(HEAD[n])
        h0.append(ham[0])                       # t = 0.01
        hl.append(ham[tn >= 150].mean())        # late-time mean
    bx.plot(dxs, h0, marker="o", ms=4, color="k", ls="-", lw=0.9,
            markerfacecolor="white", markeredgewidth=0.9,
            label=r"$t=0$ (initial data)")
    bx.plot(dxs, hl, marker="s", ms=4, color="0.35", ls="--", lw=0.9,
            markerfacecolor="white", markeredgewidth=0.9,
            label=r"$t\ge150$ (evolution)")
    dd = np.linspace(0.253, 0.53, 50)
    bx.plot(dd, h0[0] * (0.5 / dd) ** 2, color=FIT, ls=(0, (2.6, 1.4)),
            lw=1.2, zorder=3)
    bx.text(0.30, 7.4e-4, r"$\propto\Delta x^{-2}$", fontsize=6.8,
            color=FIT, ha="center", va="bottom")
    # the point of the panel: the two error sources move opposite ways
    bx.annotate("", xy=(0.237, 7.0e-4), xytext=(0.237, 3.1e-4),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=6, lw=0.7,
                                color="0.35", shrinkA=0, shrinkB=0))
    bx.text(0.237, 8.0e-4, "rises", fontsize=6.2, color="0.3", ha="center",
            va="bottom")
    bx.annotate("", xy=(0.237, 4.4e-6), xytext=(0.237, 8.6e-6),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=6, lw=0.7,
                                color="0.35", shrinkA=0, shrinkB=0))
    bx.text(0.237, 3.9e-6, "falls", fontsize=6.2, color="0.3", ha="center",
            va="top")
    bx.legend(loc="center left", borderaxespad=0.4, fontsize=6.8,
              handlelength=1.9, labelspacing=0.4, borderpad=0.2)
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_ylim(2.4e-6, 1.9e-3)  # room for the two trend arrows
    bx.set_xlim(0.56, 0.213)     # finer grids to the right
    bx.set_xticks([0.5, 1 / 3, 0.25])
    bx.set_xticklabels(["$0.50$", "$0.33$", "$0.25$"])
    bx.minorticks_off()
    bx.set_xlabel(r"$\Delta x$ \quad (grid refined $\rightarrow$)")
    bx.set_ylabel(r"$L_2(\mathcal{H})$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(wspace=0.30)
    fig.savefig(os.path.join(OUT, "fig_convergence.pdf"))
    plt.close(fig)

    print("fig_convergence stats:")
    for n in (128, 192, 256):
        t, m = midpoint(HEAD[n])
        d = dyn(HEAD[n])
        b = bary(HEAD[n])
        print(f"  N={n}: drift={m[-1] - m[0]:+.5f}  a5={fit_a(t, m):.4e}  "
              f"baryGap end {b['xc'][-1] - b['xp'][-1]:.3f}  "
              f"coreGap end {d['sep'][-1]:.3f}  px_end={d['pxt'][-1]:+.2e}")
    for cell, tag in ((DEEPSOLVE, "deepsolve"), (AMRCHECK, "amrcheck")):
        t, m = midpoint(cell)
        t0, m0 = midpoint(HEAD[128])
        print(f"  {tag}: drift={m[-1] - m[0]:+.5f} "
              f"(vs N128 {m0[-1] - m0[0]:+.5f}, "
              f"rel {abs((m[-1] - m[0]) / (m0[-1] - m0[0]) - 1) * 100:.4f}%)"
              f"  a5={fit_a(t, m):.4e}")
    t1, m1 = midpoint(HEAD[192]); t2, m2 = midpoint(HEAD[256])
    d1, d2 = m1[-1] - m1[0], m2[-1] - m2[0]
    a1, a2 = fit_a(t1, m1), fit_a(t2, m2)
    print(f"  fine pair: drift {d1:.4f}/{d2:.4f} "
          f"({abs(d1 / d2 - 1) * 100:.2f}%), "
          f"a {a1:.4e}/{a2:.4e} ({abs(a1 / a2 - 1) * 100:.2f}%)")
    for n, hh0, hhl in zip((128, 192, 256), h0, hl):
        print(f"  N={n}: L2Ham(t=0.01)={hh0:.2e}  late mean={hhl:.2e}")


# ------------------------------------------------------------ fig: same sign
def fig_samesign():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 3.62))

    # (a) the two same-sign pairs merge on the same clock
    for cell, ls, lab, tm, mfc in (
            (PP[256], "-", r"\texttt{PP} ($N{=}256$)", 33.6, "white"),
            (MM["frames"], "--", r"\texttt{MM} ($N{=}128$)", 32.8, "k")):
        W = load(cell, "well_tracking.dat")
        t, gap = W[:, 0], W[:, 3]
        live = gap > 0
        ax.plot(t[live], gap[live], color="k", ls=ls, lw=1.0, label=lab)
        ax.plot([tm], [0.35], marker="v", ms=4, color="k",
                markerfacecolor=mfc, markeredgewidth=0.8, ls="none")
    ax.annotate("merged:\n$t=33.6$ / $32.8$", xy=(33.6, 0.75),
                xytext=(44.0, 2.65), fontsize=6.8, color="0.2", ha="right",
                va="center", ma="left",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.45",
                                shrinkA=2, shrinkB=3))
    ax.text(1.5, 0.45, "gravity attracts \\texttt{PP}, repels \\texttt{MM};\n"
            "the shared-field force attracts both\n"
            r"($\sim\!35\times$ gravity at this gap)",
            fontsize=6.6, color="0.3", va="bottom")
    ax.legend(loc="upper right", borderaxespad=0.4, fontsize=6.8,
              handlelength=1.9, labelspacing=0.35, borderpad=0.2)
    ax.set_xlim(0, 45)
    ax.set_ylim(0, 9.4)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"gap of the $|\chi-1|$ extrema")
    ax.set_title("(a)", loc="left")

    # (b) and their centroids stay pinned through it
    t3, m3 = midpoint(HEAD[256])
    bx.plot(t3, np.abs(m3 - m3[0]), color="k", ls="-", lw=1.1, zorder=5)
    for grids, sect, ls in ((PP, "xc", (0, (1, 1.5))),
                            (MM, "xp", (0, (4, 1.6)))):
        for key, cell in grids.items():
            b = bary(cell)
            x = b[sect]
            bx.plot(b["t"], np.abs(x - x[0]), color="0.4", ls=ls, lw=0.7)
    bx.text(198, 6.5, "mixed pair", fontsize=6.8, ha="right", va="center")
    bx.text(198, 5.5e-3, r"\texttt{PP}/\texttt{MM} centroids, all grids",
            fontsize=6.8, ha="right", color="0.3")
    bx.axvline(33.6, color="0.7", lw=0.5, ls=(0, (2, 2)))
    bx.text(36.5, 6.5, "merger", fontsize=6.2, color="0.5", ha="left",
            va="top", rotation=90)
    bx.set_yscale("log")
    bx.set_xlim(0, 205)
    bx.set_ylim(2e-5, 16)
    bx.set_xlabel("$t$")
    bx.set_ylabel(r"$|\Delta X|$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(hspace=0.42)
    fig.savefig(os.path.join(OUT, "fig_samesign.pdf"))
    plt.close(fig)

    print("fig_samesign stats:")
    for cell in (PP[256], MM["frames"]):
        W = load(cell, "well_tracking.dat")
        t, gap = W[:, 0], W[:, 3]
        gaps = "  ".join(f"g({tt})={float(np.interp(tt, t, gap)):.2f}"
                         for tt in (0, 20, 30, 32))
        merged = t[gap == 0]
        print(f"  {cell}: {gaps}  merged from t={merged[0]:.1f}")
    for grids, sect in ((PP, "xc"), (MM, "xp")):
        for key, cell in grids.items():
            b = bary(cell)
            x = b[sect]
            print(f"  {cell}: centroid end {x[-1] - x[0]:+.5f} "
                  f"max|.| {np.max(np.abs(x - x[0])):.1e}")
    tff = (np.pi / 2) * np.sqrt(10.0 ** 3 / (2 * (M_P + M_P)))
    print(f"  Newtonian free-fall (2 x M+, d=10): t={tff:.0f}; "
          f"merger at 33.6 -> force ratio ~{(tff / 33.6) ** 2:.0f}")


# ------------------------------------------------------------ fig: mass scale
def fig_massscale():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 3.62))

    ratios = {"heavy": M_M / M_LADDER[0.81],          # |M-|/M+' = 1.333
              "matched": M_M / M_P,                    # 0.996
              "w0804": M_LADDER[0.804] / M_P,          # 0.800
              "w088": M_LADDER[0.88] / M_P}            # 0.597
    styles = {"heavy": ("-", "k", "$1.33$"),
              "matched": ((0, (1, 1.5)), "k", "$1.00$"),
              "w0804": ("--", "0.35", "$0.80$"),
              "w088": ("-.", "0.35", "$0.60$")}
    # label each curve where it ends: a legend box has nowhere to sit here
    for key in ("heavy", "matched", "w0804", "w088"):
        b = bary(MASS[key])
        gap = np.abs(b["xc"] - b["xp"])
        ls, c, lab = styles[key]
        ax.plot(b["t"], gap - gap[0], color=c, ls=ls, lw=1.0)
        ax.text(209, gap[-1] - gap[0], lab, fontsize=6.6, color=c,
                ha="left", va="center")
    # stop the zero line short of the label column
    ax.plot([0, 204], [0, 0], color="0.75", lw=0.5, zorder=0)
    ax.text(209, 1.02, r"$|M_-|/M_+$", fontsize=6.6, color="0.2",
            ha="left", va="top")
    ax.text(7, 1.02, "phantom heavier: the gap opens", fontsize=6.4,
            color="0.35", ha="left", va="top")
    ax.set_xlim(0, 256)
    ax.set_ylim(-1.55, 1.16)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$d(t)-d_0$")
    ax.set_title("(a)", loc="left")

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
    # the sign flip, read off the two cells that bracket it
    i = int(np.searchsorted(ys, 0.0))
    x0 = xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1]) / (ys[i] - ys[i - 1])
    bx.axvline(1.0, color="0.8", lw=0.5, ls=(0, (2, 2)), zorder=0)
    bx.annotate(f"sign flip at ${x0:.3f}$,\nagainst $1.000$ predicted",
                xy=(1.005, 0.02), xytext=(1.425, -0.72), fontsize=6.8,
                color="0.2", ha="right", va="center", ma="left",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.45",
                                shrinkA=2, shrinkB=3))
    bx.set_xlim(0.5, 1.45)
    bx.set_ylim(-1.65, 0.85)
    bx.set_xlabel(r"phantom-to-canonical mass ratio $|M_-|/M_+$")
    bx.set_ylabel(r"$d(200)-d_0$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(hspace=0.42)
    fig.savefig(os.path.join(OUT, "fig_massscale.pdf"))
    plt.close(fig)

    print("fig_massscale stats:")
    for key, x, y in zip(("w088", "w0804", "matched", "heavy"), xs, ys):
        print(f"  {key:8s} ratio={x:.4f}  gap change at 200 = {y:+.4f}")
    print(f"  sign flip (bracketing cells) at ratio {x0:.4f}")

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

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 3.62))

    styles = {16: "-", 24: "--", 32: "-.", 40: (0, (1, 1.5))}
    for R in radii:
        ax.plot(t, A[R], color="k" if R == 16 else "0.35", ls=styles[R],
                lw=0.9, label=f"$R={R}$")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01, 1.0, 0.12),
              mode="expand", ncol=4, borderaxespad=0.0, fontsize=6.8,
              handlelength=1.5, columnspacing=0.8, handletextpad=0.4)
    ax.set_yscale("log")
    ax.set_xlim(0, 205)
    ax.set_ylim(1e-7, 3e-3)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$A_{\ell=2}=|r\,\psi_4|_{\ell=2}$")
    ax.text(0.025, 0.94, "(a)", transform=ax.transAxes, ha="left", va="top")
    # what the panel is a measurement of, stated on the panel
    ax.text(105, 4.0e-4, "ordered by radius at all times:\n"
            "near-zone Coulombic curvature, no front", fontsize=6.4,
            color="0.3", ha="center", va="center", ma="center")

    # (b) the falloff: psi4 vs R against r^-1 (radiation) and the fit
    sel = (t >= 150) & (t <= 200)
    means = np.array([A[R][sel].mean() / R for R in radii])
    p = np.polyfit(np.log(radii), np.log(means), 1)
    bx.plot(radii, means, ls="none", marker="o", ms=4.5, color="k",
            markerfacecolor="white", markeredgewidth=0.9, zorder=5)
    rr = np.linspace(15, 42, 50)
    bx.plot(rr, np.exp(p[1]) * rr ** p[0], color=FIT, ls=(0, (3.4, 1.5)),
            lw=1.4, label=rf"fit $r^{{{p[0]:.1f}}}$ (near zone)")
    bx.plot(rr, means[0] * (radii[0] / rr), color="0.45", ls="--", lw=0.9,
            label=r"$r^{-1}$ (radiation)")
    bx.legend(loc="lower left", borderaxespad=0.5, fontsize=6.8,
              handlelength=1.9, labelspacing=0.4, borderpad=0.2)
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xticks(radii)
    bx.set_xticklabels([f"${R}$" for R in radii])
    bx.minorticks_off()
    bx.set_xlim(15, 42)
    bx.set_xlabel("$R$")
    bx.set_ylabel(r"$|\psi_4|_{\ell=2}$, mean $150\le t\le200$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(hspace=0.42)
    fig.savefig(os.path.join(OUT, "fig_wavezone.pdf"))
    plt.close(fig)

    print("fig_wavezone stats:")
    i = int(np.argmin(np.abs(t - 199)))
    for R in radii:
        print(f"  R={R}: A(t=199)={A[R][i]:.2e}  "
              f"mean(150-200) r*psi4={A[R][sel].mean():.2e}  "
              f"psi4={A[R][sel].mean() / R:.2e}")
    print(f"  psi4 ~ r^{p[0]:.2f} (mean 150-200); "
          f"r*psi4 falls x{A[16][sel].mean() / A[40][sel].mean():.0f} "
          "from R=16 to 40")
    tw, mw = midpoint(WAVEZONE)
    t1, m1 = midpoint(HEAD[128])
    print(f"  wavezone drift {mw[-1] - mw[0]:+.4f} vs L=64 "
          f"{m1[-1] - m1[0]:+.4f} "
          f"({(mw[-1] - mw[0]) / (m1[-1] - m1[0]) - 1:+.1%})")


# ------------------------------------------------------------ fig: constraints
def fig_constraints():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(SINGLE, 3.4), sharex=True)

    styles = {128: (0, (1, 1.5)), 192: (0, (4, 1.6)), 256: "-"}
    for n in (128, 192, 256):
        tn, ham, mom = norms(HEAD[n])
        ax.plot(tn, ham, color="k", ls=styles[n],
                lw=1.0 if n == 256 else 0.7)
        bx.plot(tn, mom, color="k", ls=styles[n],
                lw=1.0 if n == 256 else 0.7)
    tp, hamp, momp = norms(PP[256])
    ax.plot(tp, hamp, color="0.55", ls="-", lw=0.7)
    bx.plot(tp, momp, color="0.55", ls="-", lw=0.7)

    handles = [Line2D([], [], color="k", ls=styles[n],
                      lw=1.0 if n == 256 else 0.7, label=f"$N={n}$")
               for n in (128, 192, 256)]
    handles.append(Line2D([], [], color="0.55", ls="-", lw=0.7,
                          label=r"\texttt{PP} ($N{=}256$)"))
    ax.legend(handles=handles, loc="upper right", ncol=2, borderaxespad=0.4,
              fontsize=6.6, handlelength=1.9, columnspacing=1.0,
              labelspacing=0.3, borderpad=0.2)
    ax.set_yscale("log")
    ax.set_ylim(1.5e-6, 2.5e-3)
    ax.set_ylabel(r"$L_2(\mathcal{H})$")
    ax.set_title("(a)", loc="left")

    bx.set_yscale("log")
    bx.set_ylim(1e-7, 2e-4)
    bx.set_xlim(0, 205)
    bx.set_xlabel("$t$")
    bx.set_ylabel(r"$L_2(\mathcal{M})$")
    bx.set_title("(b)", loc="left")

    fig.subplots_adjust(hspace=0.16)
    fig.savefig(os.path.join(OUT, "fig_constraints.pdf"))
    plt.close(fig)


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

    for cell, cols in ((LONE_P, slice(1, 4)), (LONE_M, slice(5, 8))):
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

    Cpp = load(PP[256], "confinement.dat")
    print(f"PP N256: activity {Cpp[0, 1]:.2f} -> "
          f"x{Cpp[:, 1].max() / Cpp[0, 1]:.1f} at "
          f"t={Cpp[int(np.argmax(Cpp[:, 1])), 0]:.0f}; "
          f"min chi {Cpp[:, 17].min():.5f}")
    F = load(PP[256], "boundary_flux.dat", skiprows=1)
    early = F[:, 0] <= 50
    print(f"  net boundary flux |max| t<=50: "
          f"{np.abs(F[early, 1]).max():.1e}; outward peak "
          f"{F[:, 1].max():.1e} at t={F[int(np.argmax(F[:, 1])), 0]:.0f}")
    S = load(MM[128], "shell_profiles.dat")
    print(f"MM hills: chi max on R=8 shell {S[:, 3].max():.4f}")

    for w in ("075", "080", "085", "090"):
        Ks = load(f"stability_canonical_w{w}_L64_N128_lev0",
                  "collapse_diagnostics.dat")
        print(f"stability w=0.{w[1:]}: lapse {Ks[0, 1]:.5f} -> "
              f"{Ks[-1, 1]:.5f} (t={Ks[-1, 0]:.0f})")

    for cell in (HEAD[128], HEAD[192], HEAD[256], DEEPSOLVE, PP[256]):
        lines = [l.split() for l in
                 open(cell_file(cell,
                                "Ham_and_Mom_errors.txt")).readlines()[1:]
                 if l.strip()]
        print(f"solve {cell}: {len(lines)} NL iters, exit "
              f"Ham {float(lines[-1][1]):.2e}% "
              f"Mom {float(lines[-1][2]):.2e}%")

    total = 0.0
    per = {}
    for c in sorted(os.listdir(CAMP)):
        p = os.path.join(CAMP, c, "metadata.json")
        if os.path.isdir(os.path.join(CAMP, c)) and os.path.exists(p):
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
        drag = np.trapz(np.abs(sym), t)
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
        t10 = t[np.where((t > t[np.argmax(H[:20])]) & (H <= 0.1 * pk))[0][0]]
        t2 = t[np.where((t > t[np.argmax(H[:20])]) & (H <= 2 * late))[0][0]]
        print(f"constraint spike N={n}: peak {pk:.2e} -> 10% by t={t10:.1f}, "
              f"within 2x of the late plateau ({late:.2e}) by t={t2:.1f}")

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
    ratios = {"heavy": M_M / M_LADDER[0.81], "matched": M_M / M_P,
              "w0804": M_LADDER[0.804] / M_P, "w088": M_LADDER[0.88] / M_P}
    keys = ("w088", "w0804", "matched", "heavy")

    def cross(vals):
        xs = np.array([ratios[k] for k in keys])
        ys = np.array([vals[k] for k in keys])
        i = int(np.searchsorted(ys, 0.0))
        return xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1]) / (ys[i] - ys[i - 1])

    def gap_bary(k, tt=None, avg_from=None):
        b = bary(MASS[k])
        g = np.abs(b["xc"] - b["xp"])
        if avg_from is not None:
            return g[b["t"] >= avg_from].mean() - g[0]
        return (g[-1] if tt is None else float(np.interp(tt, b["t"], g))) - g[0]

    conv = {
        "barycentre gap at t=200 (paper)": {k: gap_bary(k) for k in keys},
        "core gap at t=200": {k: dyn(MASS[k])["sep"][-1] - dyn(MASS[k])["sep"][0]
                              for k in keys},
        "proper gap at t=200": {k: dyn(MASS[k])["psep"][-1] - dyn(MASS[k])["psep"][0]
                                for k in keys},
        "barycentre gap, mean over [190,200]": {k: gap_bary(k, avg_from=190)
                                                for k in keys},
    }
    xs = [cross(v) for v in conv.values()]
    for lab, v in conv.items():
        print(f"sign flip, {lab}: ratio {cross(v):.4f}")
    print(f"  end-of-run convention spread: {min(xs):.3f}--{max(xs):.3f} "
          f"-> quote 0.995 +- {max(max(xs) - 0.995, 0.995 - min(xs)):.2f}")


def main():
    fig_schematic()
    fig_family()
    fig_chase_frames()
    fig_trajectories()
    fig_forcelaw()
    fig_convergence()
    fig_samesign()
    fig_massscale()
    fig_wavezone()
    fig_constraints()
    print_numbers()
    print_gauge_and_invariants()
    print("wrote figures to", OUT)


if __name__ == "__main__":
    main()
