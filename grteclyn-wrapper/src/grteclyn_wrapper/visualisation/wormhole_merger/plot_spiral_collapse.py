#!/usr/bin/env python3
r"""The spiral merger's collapse, on one page: gauge, matter, wall and throat.

The paper's p = 0.12 collapse figure.  It draws the level-5 window of the
production spiral -- restart at t = 36 from the level-3 leg, death by NaN at
t = 60.445 -- from the profiled arm's own streams, with the inspiral that led
there as a context strip on top.  Every curve is UNFROZEN physics: the freeze
arm exists to carry the burst to the spheres and contributes nothing here.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_collapse

Reads, all under ``campaign/05_binary_spiral/p012_paper/``:

* ``v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600/`` -- ``collapse_diagnostics.dat``
  (columns min_lapse, min_chi, max_abs_K, ..., NO header on a restart),
  ``constraint_norms.dat``, ``core_radial_profile.dat.gz`` (time + 128 shells x
  {chi_min, absK_max, lapse_min, n, dx}, dr = 0.03125), and the two oriented
  marginal-surface scans ``horizon_oriented_scan_t55-57.txt`` / ``_t58-60.txt``.
* ``v2_spiral_d12_p012_L128_SERIES/binary_throat_diagnostics.dat`` -- the glued
  three-leg record, for the separation strip only (t = 0 to the death).
* ``v2_spiral_d12_p012_L128_lvl3_t050/constraint_norms.dat`` -- the level-3
  leg's constraints, overlaid on (e) over the shared window t = 36-50 (its 22
  regrid spikes all sit before t = 36, so the overlap needs no filtering).

WHAT THE FIGURE HAS TO GET RIGHT

*The horizon columns of the in-code stream are not drawn.*  Its theta_common
goes negative at t = 30.77 with the naive +r orientation -- near a wormhole
throat +r is not the outgoing direction -- and that very signal was once quoted
as a common horizon and withdrawn (GPU_PLAN, 2026-09-15).  The only horizon
instrument in this figure is the ORIENTATION-CORRECTED offline scan, and its
verdict is a gold set of throat measurements and the words "no MOTS".

*The restart-settle rows are masked, not smoothed.*  For its first steps a
restart reduces over an incomplete hierarchy and reports coarse-grid extrema:
five rows of the glued separation stream spike to 7.5 just after t = 36, and
the first collapse-diagnostics rows do the same.  Both streams are clipped a
tenth of a unit past their restart.

*The peak-radius track starts where the peak is real.*  Before t = 49.09 the
radial |K| profile is flat (at t = 45 the "peak" is 0.078 against a 0.066
background) and an argmax there is noise, not a feature.  The track is drawn
from the first time the peak stands 2x above the background.

STYLE (2026-09-18, "PRD review style", the seed-branches grammar): full page
(7.05 x 6.4), a wide context strip over a 3 x 3 grid; style.prd frame, no
titles, letter tags above the frames, semantics in the caption; no boxed key,
every series named in place.  Monochrome ink plus the one accent: GOLD is
the oriented scan -- the horizon instrument -- and nothing else.  Ordered time
families (the radial snapshots) are a grey ramp, light = early.
"""

from __future__ import annotations

import argparse
import gzip
import pathlib
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "05_binary_spiral"
ARM = "p012_paper/v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600"
SERIES = "p012_paper/v2_spiral_d12_p012_L128_SERIES"

# BinaryWormholeLevel's writer, in order -- no header on a restart.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

CHI_FLOOR = 1e-8       # the evolution's clamp on chi
EDGE_K = 0.2           # |K| defining the disturbance's outer edge
SETTLE = 0.1           # time clipped after a restart (incomplete hierarchy)


def _sorted(path: pathlib.Path) -> np.ndarray:
    d = np.loadtxt(path)
    return d[np.argsort(d[:, 0])]


def _read_profile(path: pathlib.Path):
    with gzip.open(path, "rt") as fh:
        names = fh.readline().split()[1:]     # drop the leading '#'
        prof = np.loadtxt(fh)
    nsh = (len(names) - 1) // 5               # blocks: chi, |K|, lapse, n, dx
    rr = np.array([float(n.rsplit("_r", 1)[1]) for n in names[1:1 + nsh]])
    t = prof[:, 0]
    blk = {}
    for i, name in enumerate(("chi", "K", "lapse")):
        y = prof[:, 1 + i * nsh:1 + (i + 1) * nsh].copy()
        y[np.abs(y) > 1e29] = np.nan          # shells the fine mask never covered
        blk[name] = y
    return t, rr, blk


def _read_scans(paths) -> list[tuple[float, int, float, float]]:
    """(t, level, throat coordinate r, throat areal R) per scan block.

    A block can report several 'areal-radius minimum (throat)' lines -- grid
    noise at small r fakes minima with R in the hundreds -- so the genuine
    throat is the minimum with the SMALLEST areal radius.
    """
    head = re.compile(r"BinaryWormholePlt\d+\s+t=([\d.]+)\s+.*level=(\d)")
    line = re.compile(r"areal-radius minimum \(throat\) at r = ([\d.]+): R = ([\d.]+)")
    out, cur = [], None
    for path in paths:
        for ln in pathlib.Path(path).read_text().splitlines():
            m = head.search(ln)
            if m:
                if cur and cur[2] is not None:
                    out.append(cur)
                cur = [float(m.group(1)), int(m.group(2)), None, None]
                continue
            m = line.search(ln)
            if m and cur is not None:
                r, R = float(m.group(1)), float(m.group(2))
                if cur[3] is None or R < cur[3]:
                    cur[2], cur[3] = r, R
        if cur and cur[2] is not None:
            out.append(cur)
            cur = None
    return [tuple(c) for c in out]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    arm = pack / "campaign" / GROUP / ARM

    d = _sorted(arm / "collapse_diagnostics.dat")
    d = d[d[:, 0] >= d[0, 0] + SETTLE]
    t = d[:, 0]
    col = {n: d[:, i + 1] for i, n in enumerate(COLS)}
    cn = _sorted(arm / "constraint_norms.dat")
    cn = cn[cn[:, 0] >= t[0]]

    b = _sorted(pack / "campaign" / GROUP / SERIES / "binary_throat_diagnostics.dat")
    b = b[(b[:, 0] <= t[-1]) & ~((b[:, 0] > 36.0) & (b[:, 0] < 36.0 + 4 * SETTLE))]
    ts, sep = b[:, 0], b[:, 1]

    pt, rr, blk = _read_profile(arm / "core_radial_profile.dat.gz")
    dr = float(rr[1] - rr[0])
    scans = _read_scans([arm / "horizon_oriented_scan_t55-57.txt",
                         arm / "horizon_oriented_scan_t58-60.txt"])

    # ---- derived events, printed for the caption --------------------------
    i_fl = int(np.argmax(np.nanmin(blk["chi"], axis=1) <= CHI_FLOOR * 1.01))
    t_floor = float(pt[i_fl])
    i_tr = int(np.argmax(cn[:, 2]))
    t_trans = float(cn[i_tr, 0])
    t_end = float(t[-1])

    K = blk["K"]
    pk = np.nanargmax(np.where(np.isnan(K), -np.inf, K), axis=1)
    vpk = K[np.arange(len(pt)), pk]
    bg = K[:, int(0.4 / dr)]
    real = vpk > 2.0 * bg
    t_spike = float(pt[np.argmax(real & (pt > 45.0))])
    edge = np.array([rr[np.where(K[k] > EDGE_K)[0].max()]
                     if (K[k] > EDGE_K).any() else np.nan for k in range(len(pt))])
    i_wide = int(np.nanargmax(edge))

    def logc(a, v):
        a, v = np.log10(np.maximum(a, 1e-300)), np.log10(np.maximum(v, 1e-300))
        return float(np.corrcoef(a, v)[0, 1])

    m40 = t >= 40.0
    hh = np.interp(t, cn[:, 0], cn[:, 1])
    mm = np.interp(t, cn[:, 0], cn[:, 2])
    corr_h, corr_m = logc(col["max_abs_K"][m40], hh[m40]), logc(col["max_abs_K"][m40], mm[m40])

    print(f"[spiral collapse] window t = {t[0]:.2f}-{t_end:.2f}; "
          f"transient peak t = {t_trans:.2f} (H {cn[:,1].max():.2e}, M {cn[:,2].max():.2e}); "
          f"chi on {CHI_FLOOR:g} floor from t = {t_floor:.2f}; "
          f"min lapse {col['min_lapse'].min():.2e}; max|K| peak {col['max_abs_K'].max():.2f}")
    print(f"  spike real from t = {t_spike:.2f}; edge widest {np.nanmax(edge):.3f} "
          f"at t = {pt[i_wide]:.2f}; corr after t=40: K-H {corr_h:+.2f}, K-M {corr_m:+.2f}")
    for tv, lv, r0, R0 in scans:
        print(f"  scan t = {tv:.0f} level {lv}: throat r = {r0:.3f}, R = {R0:.3f}, no MOTS")

    # ---- the page ----------------------------------------------------------
    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 6.4), constrained_layout=True)
    gs = fig.add_gridspec(4, 3, height_ratios=[0.72, 1, 1, 1])
    axA = fig.add_subplot(gs[0, :])
    axes = [fig.add_subplot(gs[1 + i // 3, i % 3]) for i in range(9)]
    (axB, axC, axD, axE, axF, axG, axH, axI, axJ) = axes

    def tag(ax, letter):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    def rules(ax):
        ax.axvline(t_trans, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
        ax.axvline(t_floor, color=style.FAINT, lw=0.7, ls=(0, (1, 2)), zorder=1)

    # (a) the inspiral that leads to everything below ------------------------
    merged = ts >= t_trans
    axA.plot(ts[~merged], sep[~merged], color=style.INK, lw=1.2)
    axA.plot(ts[merged], sep[merged], color=style.CONTEXT, lw=1.0)
    axA.axvline(36.0, color=style.FAINT, lw=0.7, zorder=1)
    rules(axA)
    axA.set_xlim(-1, t_end + 0.8)
    axA.set_ylim(-0.6, 13.4)
    axA.set_ylabel(r"$d$")
    axA.set_xlabel(r"$t$")
    axA.text(3.0, 9.3, "separation of the $\\chi$ pits", fontsize=8,
             ha="left", va="top", color=style.INK)
    axA.text(35.4, 12.6, "level $3\\to 5$", fontsize=7.5, ha="right", va="top",
             color=style.MUTED)
    axA.text(t_trans + 0.5, 6.2, "constraint\ntransient", fontsize=7.5,
             ha="left", va="center", color=style.MUTED, linespacing=1.2)
    axA.text(t_floor - 0.5, 6.2, "$\\chi$ on floor", fontsize=7.5, ha="right",
             va="center", color=style.MUTED)
    axA.text(48.0, 2.1, "one merged pit", fontsize=7.5, ha="center",
             va="bottom", color=style.CONTEXT)
    axA.text(59.55, 1.05, "NaN", fontsize=7.5, ha="center", va="bottom",
             color=style.MUTED)
    tag(axA, "a")

    # (b)-(d) the core's clocks ----------------------------------------------
    axB.semilogy(t, col["min_lapse"], color=style.INK, lw=1.1)
    axB.set_ylabel(r"$\min\alpha$")

    axC.semilogy(t, col["min_chi"], color=style.INK, lw=1.1)
    axC.axhline(CHI_FLOOR, color=style.MUTED, lw=0.7, ls=(0, (1, 2)))
    axC.set_ylabel(r"$\min\chi$")
    axC.set_ylim(3e-9, 3e-5)
    axC.text(37.0, CHI_FLOOR * 1.35, "floor", fontsize=7.5, ha="left",
             va="bottom", color=style.MUTED)

    axD.plot(t, col["max_Pi"], color=style.INK, lw=1.1)
    axD.plot(t, col["min_Pi"], color=style.INK, lw=1.1)
    axD.plot(t, col["max_phi"], color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    axD.plot(t, col["min_phi"], color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    axD.set_ylabel(r"$\phi,\ \Pi$")
    axD.set_ylim(-4.9, 4.9)
    axD.text(52.5, 2.6, r"$\pm\Pi$", fontsize=8, ha="right", va="bottom",
             color=style.INK)
    axD.text(44.0, 1.15, r"$\pm\phi$", fontsize=8, ha="center", va="bottom",
             color=style.MUTED)

    # (e) do core and constraints grow together?  No. ------------------------
    def unit_tf(ref):
        v = np.log10(np.maximum(np.asarray(ref, float), 1e-300))
        lo, sp = v.min(), max(float(np.ptp(v)), 1e-30)
        return lambda y: (np.log10(np.maximum(np.asarray(y, float), 1e-300)) - lo) / sp

    uK, uH, uM = unit_tf(col["max_abs_K"]), unit_tf(hh), unit_tf(mm)
    # The level-3 leg through the SAME transforms, so where the grids agree
    # the curves coincide rather than being re-normalised into fake agreement.
    c3 = _sorted(pack / "campaign" / GROUP /
                 "p012_paper/v2_spiral_d12_p012_L128_lvl3_t050/constraint_norms.dat")
    c3 = c3[(c3[:, 0] >= t[0]) & (c3[:, 0] <= t[-1])]
    H5i, M5i = np.interp(c3[:, 0], t, hh), np.interp(c3[:, 0], t, mm)
    print(f"  level-3 overlap t = {c3[0, 0]:.1f}-{c3[-1, 0]:.1f}: median "
          f"|dH|/H = {np.median(abs(c3[:, 1] - H5i) / H5i) * 100:.1f}%, "
          f"|dM|/M = {np.median(abs(c3[:, 2] - M5i) / M5i) * 100:.1f}%")
    axE.plot(c3[:, 0], uH(c3[:, 1]), color=style.CONTEXT, lw=0.9,
             ls=(0, (4, 2.5)), zorder=2)
    axE.plot(c3[:, 0], uM(c3[:, 2]), color=style.CONTEXT, lw=0.9,
             ls=(0, (1, 1.8)), zorder=2)
    axE.plot(t, uK(col["max_abs_K"]), color=style.INK, lw=1.3, zorder=4)
    axE.plot(t, uH(hh), color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)), zorder=3)
    axE.plot(t, uM(mm), color=style.MUTED, lw=0.9, ls=(0, (1, 1.8)), zorder=3)
    axE.set_ylabel(r"normalised $\log_{10}$")
    axE.set_ylim(-0.06, 1.42)
    axE.text(50.2, 0.02, "level 3", fontsize=7.5, ha="left", va="bottom",
             color=style.CONTEXT)
    axE.text(55.2, 0.86, r"$\max|K|$", fontsize=7.5, ha="right", va="center",
             color=style.INK)
    def sci(v):
        e = int(np.floor(np.log10(v)))
        return rf"{v / 10**e:.1f}\times10^{{{e}}}"

    axE.text(42.6, 1.02,
             rf"$\|\mathcal{{H}}\|$ peak ${sci(cn[:, 1].max())}$" + "\n" +
             rf"$\|\mathcal{{M}}\|$ peak ${sci(cn[:, 2].max())}$",
             fontsize=6.5, ha="left", va="bottom", color=style.MUTED,
             linespacing=1.45)

    for ax in (axB, axC, axD, axE):
        rules(ax)
        ax.set_xlim(t[0] - 0.6, t_end + 0.6)
    axE.set_xlabel(r"$t$")   # (b)-(d) share the range; the title once is enough

    # (f) the wall rides the throat ------------------------------------------
    ok = real & (pt >= t_spike)
    axF.plot(pt[ok], rr[pk[ok]], color=style.INK, lw=1.1)
    axF.plot(pt, edge, color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    r_scan = {}
    for tv, lv, r0, R0 in scans:          # level 5 wins where both scanned
        if tv not in r_scan or lv > r_scan[tv][0]:
            r_scan[tv] = (lv, r0, R0)
    t_sc = sorted(r_scan)
    axF.plot(t_sc, [r_scan[tv][1] for tv in t_sc], ls="none", marker="o",
             ms=3.6, mfc=style.GROUND, mec=style.GOLD, mew=1.1, zorder=5)
    axF.axvline(t_floor, color=style.FAINT, lw=0.7, ls=(0, (1, 2)), zorder=1)
    axF.set_xlim(48.4, t_end + 0.7)
    axF.set_ylim(0.55, 1.52)
    axF.set_xlabel(r"$t$")
    axF.set_ylabel(r"$r$")
    axF.text(49.0, 1.40, "edge, $|K|>0.2$", fontsize=7.5, ha="left",
             va="bottom", color=style.MUTED)
    axF.text(50.0, 1.05, r"peak of $|K|$", fontsize=7.5, ha="left",
             va="top", color=style.INK)
    axF.text(53.9, 0.86, "throat (scan)", fontsize=7.5, ha="right",
             va="center", color=style.GOLD)

    # (g) the throat's areal radius; no horizon ever --------------------------
    for lv, mfc in ((3, style.GROUND), (5, style.GOLD)):
        pts = [(tv, R0) for tv, l, r0, R0 in scans if l == lv]
        if pts:
            xs, ys = zip(*pts)
            axG.plot(xs, ys, ls="none", marker="o", ms=3.6, mfc=mfc,
                     mec=style.GOLD, mew=1.1, zorder=5)
    axG.text(56.25, 4.077, "level 3", fontsize=7.5, ha="left", va="bottom",
             color=style.GOLD)
    axG.text(58.6, 3.99, "level 5", fontsize=7.5, ha="left", va="bottom",
             color=style.GOLD)
    axG.axvline(t_floor, color=style.FAINT, lw=0.7, ls=(0, (1, 2)), zorder=1)
    axG.set_xlim(54.4, 61.0)
    axG.set_ylim(3.82, 4.17)
    axG.set_xlabel(r"$t$")
    axG.set_ylabel(r"$R_{\mathrm{throat}}$")
    axG.text(55.0, 3.845, "no MOTS\nat any scan", fontsize=7.5, ha="left",
             va="bottom", color=style.INK, linespacing=1.25)

    # (h)-(j) the radial anatomy, six snapshots -------------------------------
    times = np.linspace(pt[0], pt[-1], 6)
    greys = [plt.cm.Greys(0.35 + 0.6 * i / 5) for i in range(6)]
    for ax, which in ((axH, "K"), (axI, "chi"), (axJ, "lapse")):
        y = blk[which]
        for i, tv in enumerate(times):
            k = int(np.argmin(abs(pt - tv)))
            ax.semilogy(rr, y[k], lw=1.2, color=greys[i], zorder=2 + i)
        ax.set_xlim(0, 2.0)
        ax.set_xlabel(r"$r$")
    axH.axhline(EDGE_K, color=style.MUTED, lw=0.7, ls=(0, (1, 2)))
    axH.set_ylabel(r"$\max|K|$")
    axH.set_ylim(6e-3, 12)
    axH.text(1.97, EDGE_K * 1.25, "edge", fontsize=7.5, ha="right", va="bottom",
             color=style.MUTED)
    axH.text(0.58, 8.5, f"$t={times[-1]:.1f}$", fontsize=7.5, ha="right",
             va="top", color=style.INK)
    axH.text(1.30, 0.026, f"$t={times[0]:.1f}$", fontsize=7.5, ha="center",
             va="top", color=style.CONTEXT)
    axI.axhline(CHI_FLOOR, color=style.MUTED, lw=0.7, ls=(0, (1, 2)))
    axI.set_ylabel(r"$\min\chi$")
    axI.set_ylim(2e-9, 1.5)
    axI.text(1.97, CHI_FLOOR * 2.6, "floor", fontsize=7.5, ha="right",
             va="bottom", color=style.MUTED)
    axJ.set_ylabel(r"$\min\alpha$")
    axJ.set_ylim(1.2e-3, 0.9)

    for ax, letter in zip(axes, "bcdefghij"):
        tag(ax, letter)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "p012_paper" / "p012_collapse_diagnostics.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[spiral collapse] wrote {png} (+pdf); 10 panels, {len(scans)} scan rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
