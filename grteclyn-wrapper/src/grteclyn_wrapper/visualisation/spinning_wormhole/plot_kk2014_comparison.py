#!/usr/bin/env python3
r"""Our symmetric family against Kleihaus & Kunz 2014, Fig. 1 -- the paper figure.

Same axes and normalisation as KK 2014 Fig. 1 (M0 = R, J0 = R^2/2,
Omega0 = 1/R at fixed equatorial throat radius R), drawn from numbers only:

- lines: this work, the eta0 = 1, gamma = 0 members of the packed solver
  table (v_e 0.02-0.991) and the exact static member at v_e = 0, joined by
  monotone cubic interpolation.  Our Omega J/(Omega0 J0) equals M/M0 to the
  packed Smarr gate (<= 1e-10), so one line carries both;
- open symbols: KK 2014's wormhole curves, digitized from their Fig. 1
  (``kk2014.py``; reading error <= 1e-3, measured on their printed Kerr
  curves), thinned for legibility;
- gold: Kerr at fixed horizon radius from closed forms, the extremal values
  as dots at v_e = 1.

The agreement (rms and max of digitized minus ours, per curve) is printed
and is at the level of the reading error.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_comparison

Reads ``results/spinningwormhole/solver/solutions.tsv`` and
``results/spinningwormhole/solver/kk2014_fig1_digitized.tsv``; writes
``results/spinningwormhole/figures/solver/kk2014_comparison`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.interpolate import PchipInterpolator  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import kk2014, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

OUT = solutions.REPO / "results" / "spinningwormhole" / "figures" / "solver" / "kk2014_comparison"
XLIM = (0.0, 1.0)
YLIM_A = (0.0, 0.52)
YLIM_B = (0.595, 1.005)
KK = "KK 2014, digitized"

OURS_1 = dict(color=style.INK, ls="-", lw=1.3)
OURS_2 = dict(color=style.DEEP_BLUE, ls=(0, (6.5, 2.2)), lw=1.3)
KK_1 = dict(ls="none", marker="o", ms=3.8, mfc="none", mec=style.INK, mew=0.75)
KK_SMARR = dict(ls="none", marker="+", ms=4.2, mec=style.INK, mew=0.75)
KK_2 = dict(ls="none", marker="s", ms=3.2, mfc="none", mec=style.DEEP_BLUE, mew=0.75)
KERR_1 = dict(color=style.GOLD, ls="-", lw=1.3)
KERR_2 = dict(color=style.GOLD, ls=(0, (6.5, 2.2)), lw=1.3)
KERR_3 = dict(color=style.GOLD, ls=(0, (1.3, 1.7)), lw=1.6)
EXTREMAL = dict(ls="none", marker="o", ms=5.5, mfc=style.GOLD, mec=style.INK, mew=0.6,
                zorder=6, clip_on=False)
BLANK = (Line2D([], [], alpha=0.0), "")


def agreement(fam, kk) -> dict[str, tuple[float, float, int]]:
    """rms, max |KK - ours| per digitized curve, where ours exists."""
    ours = {q: PchipInterpolator(fam["v"], fam[q]) for q in ("M", "OmJ", "J", "Rp", "RA")}
    out = {}
    for name, (_, _, q) in kk2014.CURVES.items():
        pts = kk.get(name)
        if pts is None:
            continue
        pts = pts[pts[:, 0] <= fam["v"][-1]]
        d = pts[:, 1] - ours[q](pts[:, 0])
        out[name] = (float(np.sqrt(np.mean(d**2))), float(np.abs(d).max()), len(d))
    return out


def draw(fam, kk, sep: float):
    style.prd(9.0)
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.0, 3.4), layout="constrained")
    v_ours = np.linspace(0.0, fam["v"][-1], 600)
    v_kerr = np.linspace(0.0, 1.0, 401)
    kerr = kk2014.kerr(v_kerr)
    ext = kk2014.kerr(np.array([1.0]))

    def ours(q):
        return PchipInterpolator(fam["v"], fam[q])(v_ours)

    def points(ax, name, spans, fmt):
        p = kk[name]
        i = kk2014.thin(p[:, 0], [p[:, 1]], spans, sep)
        ax.plot(p[i, 0], p[i, 1], **fmt)

    # (a) mass, angular momentum and the Smarr side.
    spans = (XLIM[1] - XLIM[0], YLIM_A[1] - YLIM_A[0])
    ax_a.plot(v_kerr, kerr["M"], **KERR_1)
    ax_a.plot(v_kerr, kerr["J"], **KERR_2)
    ax_a.plot(v_kerr, kerr["OmJ"], **KERR_3)
    ax_a.plot(v_ours, ours("M"), **OURS_1)
    ax_a.plot(v_ours, ours("J"), **OURS_2)
    points(ax_a, "M_over_M0", spans, KK_1)
    points(ax_a, "OmJ_over_OmJ0", spans, KK_SMARR)
    points(ax_a, "J_over_J0", spans, KK_2)
    ax_a.plot([1.0], ext["M"], **EXTREMAL)
    ax_a.set(xlim=XLIM, ylim=YLIM_A, xlabel=r"$v_e$")
    style.legend_top(ax_a, [
        (Line2D([], [], **OURS_1), r"$M/M_0$ this work"),
        (Line2D([], [], **KK_1), rf"$M/M_0$ {KK}"),
        (Line2D([], [], **OURS_2), r"$J/J_0$ this work"),
        (Line2D([], [], **KK_2), rf"$J/J_0$ {KK}"),
        (Line2D([], [], **KERR_1), r"$M/M_0$ Kerr"),
        (Line2D([], [], **KK_SMARR), rf"$\Omega J/\Omega_0 J_0$ {KK}"),
        (Line2D([], [], **KERR_2), r"$J/J_0$ Kerr"),
        (Line2D([], [], **KERR_3), r"$\Omega J/\Omega_0 J_0$ Kerr"),
        BLANK,
        (Line2D([], [], **EXTREMAL), "extremal Kerr"),
    ], ncol=2)

    # (b) the throat's polar and areal radii.
    spans = (XLIM[1] - XLIM[0], YLIM_B[1] - YLIM_B[0])
    ax_b.plot(v_kerr, kerr["Rp"], **KERR_1)
    ax_b.plot(v_kerr, kerr["RA"], **KERR_2)
    ax_b.plot(v_ours, ours("Rp"), **OURS_1)
    ax_b.plot(v_ours, ours("RA"), **OURS_2)
    points(ax_b, "Rp_over_R", spans, KK_1)
    points(ax_b, "RA_over_R", spans, KK_2)
    ax_b.plot([1.0, 1.0], [ext["Rp"][0], ext["RA"][0]], **EXTREMAL)
    ax_b.set(xlim=XLIM, ylim=YLIM_B, xlabel=r"$v_e$")
    style.legend_top(ax_b, [
        (Line2D([], [], **OURS_1), r"$R_p/R$ this work"),
        (Line2D([], [], **KK_1), rf"$R_p/R$ {KK}"),
        (Line2D([], [], **OURS_2), r"$R_A/R$ this work"),
        (Line2D([], [], **KK_2), rf"$R_A/R$ {KK}"),
        (Line2D([], [], **KERR_1), r"$R_p/R$ Kerr"),
        (Line2D([], [], **KERR_2), r"$R_A/R$ Kerr"),
        BLANK,
        (Line2D([], [], **EXTREMAL), "extremal Kerr"),
    ], ncol=2)

    style.tag_keys(fig, [ax_a, ax_b], ["(a)", "(b)"], row="last")
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--digitized", type=pathlib.Path, default=kk2014.DIGITIZED)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--sep", type=float, default=0.03,
                    help="symbol spacing along each KK curve, in frame fractions (0: all)")
    args = ap.parse_args(argv)

    fam = kk2014.symmetric_family(solutions.load(args.table), static_end=True)
    kk = kk2014.load(args.digitized)
    fig = draw(fam, kk, args.sep)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    print(f"this work: {len(fam['v']) - 1} solutions + the static member, "
          f"v_e up to {fam['v'][-1]:.4f}; Smarr gate max {fam['smarr_rel'].max():.1e}")
    for name, (rms, mx, n) in agreement(fam, kk).items():
        print(f"  KK {name:14s} - ours: rms {rms:.1e}  max {mx:.1e}  ({n} points)")
    print(f"label audit: {'clean' if not problems else f'{len(problems)} problem(s)'}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
