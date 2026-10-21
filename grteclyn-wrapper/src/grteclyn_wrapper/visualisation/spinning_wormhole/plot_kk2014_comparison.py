#!/usr/bin/env python3
r"""Our symmetric family against Kleihaus & Kunz 2014, Fig. 1 -- the paper figure.

Same axes and normalisation as KK 2014 Fig. 1 (M0 = R, J0 = R^2/2,
Omega0 = 1/R at fixed equatorial throat radius R), drawn from numbers only:

- solid lines: this work, the eta0 = 1, gamma = 0 members of the packed
  solver table (v_e 0.02-0.991) and the exact static member at v_e = 0,
  joined by monotone cubic interpolation.  Our Omega J/(Omega0 J0) equals
  M/M0 to the packed Smarr gate (<= 1e-10), so one line carries both;
- open symbols: KK 2014's wormhole curves, digitized from their Fig. 1
  (``kk2014.py``; reading error <= 1e-3, measured on their printed Kerr
  curves), thinned for legibility;
- dashed lines: Kerr at fixed horizon radius from closed forms, the
  extremal values as dots at v_e = 1.

Colours (``--palette``): ``rgb``, the default, colours each quantity the way
KK do (red M/M0 and R_p/R, green J/J0 and R_A/R, blue Omega J/(Omega0 J0))
with black extremal dots; ``house`` is ink / deep blue with gold Kerr curves.
``--colors C1,C2,C3`` replaces the three quantity colours of either, so the
figure redraws in another scheme without touching the code.

The agreement (rms and max of digitized minus ours, per curve) is printed
and is at the level of the reading error.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_comparison
    ... plot_kk2014_comparison --palette house --out <path>
    ... plot_kk2014_comparison --colors "#c00000,#007a00,#0000c0"

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
KK = "KK 2014"
SOLID, DASHED, DOTTED = "-", (0, (6.5, 2.2)), (0, (1.3, 1.7))

# colours: the three quantities (M or R_p, J or R_A, Omega J); kerr: one
# colour for every Kerr curve, or None for the quantity's own.
PALETTES = {
    "rgb": dict(colours=("#d62728", "#2ca02c", "#1f77b4"), kerr=None, extremal="black",
                ours_dash=(SOLID, SOLID), kerr_dash=(DASHED, DASHED, DASHED)),
    "house": dict(colours=(style.INK, style.DEEP_BLUE, style.INK), kerr=style.GOLD,
                  extremal=style.GOLD, ours_dash=(SOLID, DASHED),
                  kerr_dash=(SOLID, DASHED, DOTTED)),
}


def look(palette: str, colours: tuple[str, str, str] | None = None) -> dict[str, dict]:
    """Plot kwargs for every element of the figure under one palette."""
    p = PALETTES[palette]
    c = colours or p["colours"]
    kerr = [p["kerr"] or c[i] for i in range(3)]
    open_ = dict(ls="none", mfc="none", mew=0.8)
    return {
        "ours1": dict(color=c[0], ls=p["ours_dash"][0], lw=1.4),
        "ours2": dict(color=c[1], ls=p["ours_dash"][1], lw=1.4),
        "kk1": dict(open_, marker="o", ms=3.8, mec=c[0]),
        "kk2": dict(open_, marker="s", ms=3.2, mec=c[1]),
        "kk3": dict(ls="none", marker="+", ms=4.2, mec=c[2], mew=0.8),
        "kerr1": dict(color=kerr[0], ls=p["kerr_dash"][0], lw=1.1),
        "kerr2": dict(color=kerr[1], ls=p["kerr_dash"][1], lw=1.1),
        "kerr3": dict(color=kerr[2], ls=p["kerr_dash"][2], lw=1.1 if p["kerr"] is None else 1.6),
        "extremal": dict(ls="none", marker="o", ms=5.0, mfc=p["extremal"], mec=p["extremal"],
                         mew=0.6, zorder=6, clip_on=False),
    }


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


def draw(fam, kk, sep: float, lk: dict[str, dict]):
    style.prd(8.0)
    # one column, the panels stacked, keys reading one quantity per row
    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(3.4, 3.6), layout="constrained", sharex=True)
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

    def key(fmt, label):
        return (Line2D([], [], **{k: v for k, v in fmt.items() if k != "clip_on"}), label)

    # (a) mass, angular momentum and the Smarr side.
    spans = (XLIM[1] - XLIM[0], YLIM_A[1] - YLIM_A[0])
    ax_a.plot(v_kerr, kerr["M"], **lk["kerr1"])
    ax_a.plot(v_kerr, kerr["J"], **lk["kerr2"])
    ax_a.plot(v_kerr, kerr["OmJ"], **lk["kerr3"])
    ax_a.plot(v_ours, ours("M"), **lk["ours1"])
    ax_a.plot(v_ours, ours("J"), **lk["ours2"])
    points(ax_a, "M_over_M0", spans, lk["kk1"])
    points(ax_a, "OmJ_over_OmJ0", spans, lk["kk3"])
    points(ax_a, "J_over_J0", spans, lk["kk2"])
    ax_a.plot([1.0], ext["M"], **lk["extremal"])
    ax_a.set(xlim=XLIM, ylim=YLIM_A)
    style.legend_top(ax_a, [
        key(lk["ours1"], r"$M/M_0$ this work"),
        key(lk["kk1"], rf"$M/M_0$ {KK}"),
        key(lk["kerr1"], r"$M/M_0$ Kerr"),
        key(lk["ours2"], r"$J/J_0$ this work"),
        key(lk["kk2"], rf"$J/J_0$ {KK}"),
        key(lk["kerr2"], r"$J/J_0$ Kerr"),
        key(lk["extremal"], "extremal Kerr"),
        key(lk["kk3"], rf"$\Omega J/\Omega_0 J_0$ {KK}"),
        key(lk["kerr3"], r"$\Omega J/\Omega_0 J_0$ Kerr"),
    ], ncol=3, borderpad=0.6)

    # (b) the throat's polar and areal radii.
    spans = (XLIM[1] - XLIM[0], YLIM_B[1] - YLIM_B[0])
    ax_b.plot(v_kerr, kerr["Rp"], **lk["kerr1"])
    ax_b.plot(v_kerr, kerr["RA"], **lk["kerr2"])
    ax_b.plot(v_ours, ours("Rp"), **lk["ours1"])
    ax_b.plot(v_ours, ours("RA"), **lk["ours2"])
    points(ax_b, "Rp_over_R", spans, lk["kk1"])
    points(ax_b, "RA_over_R", spans, lk["kk2"])
    ax_b.plot([1.0, 1.0], [ext["Rp"][0], ext["RA"][0]], **lk["extremal"])
    ax_b.set(xlim=XLIM, ylim=YLIM_B, xlabel=r"$v_e$")
    ax_b.set_yticks([0.6, 0.7, 0.8, 0.9])  # no label on the top edge, where the tag sits
    style.legend_top(ax_b, [
        key(lk["ours1"], r"$R_p/R$ this work"),
        key(lk["kk1"], rf"$R_p/R$ {KK}"),
        key(lk["kerr1"], r"$R_p/R$ Kerr"),
        key(lk["ours2"], r"$R_A/R$ this work"),
        key(lk["kk2"], rf"$R_A/R$ {KK}"),
        key(lk["kerr2"], r"$R_A/R$ Kerr"),
        key(lk["extremal"], "extremal Kerr"),
    ], ncol=3, borderpad=0.6)

    style.tag_keys(fig, [ax_a, ax_b], ["(a)", "(b)"], row="last")
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--digitized", type=pathlib.Path, default=kk2014.DIGITIZED)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--palette", choices=sorted(PALETTES), default="rgb",
                    help="colour scheme (default rgb, the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing the palette's quantity colours")
    ap.add_argument("--sep", type=float, default=0.03,
                    help="symbol spacing along each KK curve, in frame fractions (0: all)")
    args = ap.parse_args(argv)
    colours = None
    if args.colors:
        colours = tuple(c.strip() for c in args.colors.split(","))
        if len(colours) != 3:
            ap.error("--colors takes exactly three colours")

    fam = kk2014.symmetric_family(solutions.load(args.table), static_end=True)
    kk = kk2014.load(args.digitized)
    fig = draw(fam, kk, args.sep, look(args.palette, colours))
    problems = style.label_audit(fig)
    png = style.save(fig, args.out)
    print(f"this work: {len(fam['v']) - 1} solutions + the static member, "
          f"v_e up to {fam['v'][-1]:.4f}; Smarr gate max {fam['smarr_rel'].max():.1e}")
    for name, (rms, mx, n) in agreement(fam, kk).items():
        print(f"  KK {name:14s} - ours: rms {rms:.1e}  max {mx:.1e}  ({n} points)")
    print(f"palette {args.palette}{' with ' + ', '.join(colours) if colours else ''}; "
          f"label audit: {'clean' if not problems else f'{len(problems)} problem(s)'}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
