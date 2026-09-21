#!/usr/bin/env python3
r"""The head-on merger's collapse, on one page: the pair makes a black hole.

The paper's Phase-3 figure, and the spiral collapse page's counterpart with
the opposite verdict: here the orientation-corrected scans FIND the horizon.
A common MOTS encloses both mouths from t = 22 -- neither mouth ever has its
own -- the level-3 wall five units later is resolution (level 5 walks through
it with the constraints falling), and the remnant is a ringing black hole
whose Misner-Sharp mass DRIFTS DOWN as it swallows the phantom scalar that
held the throats open.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_headon_collapse

Reads, all under ``campaign/04_binary_headon/``:

* ``merge_headon_flip_d8_v1_t100/`` -- the level-3 scout (t = 0-26.91, dies at
  the wall): ``collapse_diagnostics.dat``, ``constraint_norms.dat``,
  ``binary_throat_diagnostics.dat``, the live oriented ``horizon_scan.dat``
  and the offline formation scan ``horizon_offline_scan.dat`` (level 3,
  dx 0.0625, t = 22-26 -- the record of the horizon's birth).
* ``merge_headon_flip_d8_v1_lvl5from0_scalar_t100/`` -- THE PAPER'S ARM since
  2026-09-21: max_level 5 FROM t = 0, no interior fill, no restart, no seam,
  t = 100 with no NaN, carrying the scalar-mode stream besides.  Same streams
  as the old arm plus ``scalar_modes.dat``; its live scan finds the common
  MOTS at t = 21.5 and reads R = 4.456, M = 2.736 at t = 36 -- on the seamed
  arm's own track to 0.1 %.
* ``merge_headon_flip_d8_v1_lvl5_t100_r02200/`` -- the SUPERSEDED seamed arm
  (level 5 from V1c's t = 22 checkpoint), kept on this page for two things:
  ``horizon_offline_scan_lvl5_t42.5_43.dat`` (its level-3-sampled corrected
  scan, the filled late anchors on (f)-(g)) and the seam-independence check
  itself -- its (2,0) agrees with the seamless arm's to 2.9-5.4 % of peak on
  all three spheres over the burst window t = 23-70, and its E_GW to 3-8 %.
* ``merge_headon_flip_d8_v1_lvl3down_t100_r03500/`` -- back to max_level 3 from
  the level-5 t = 35 checkpoint, no fill: the cross-resolution check on (e)
  and the late-time horizon track on (f)-(g).

WHAT THE FIGURE HAS TO GET RIGHT

*Every horizon point is the corrected orientation.*  The live consumer scan
(2026-09-09, one hour older than the scout) and the offline scans share the
validated shell mathematics; there is no naive-+r instrument on this page.

*The live scan's gaps are aperture, not horizon loss.*  The common scan's
shells reach 0.5 sep + 2.3, with sep read off the chi-pit tracker; once the
pits merge (sep -> 0.016 by t = 40) the shells stop at r = 2.3 while the MOTS
sits at r = 2.7-3.3.  Those scans report every shell trapped and no surface
inside range -- which is the trapped BALL, honestly seen through a keyhole --
and the track resumes whenever the aperture grazes the surface.  Where two
no-fill arms see the MOTS at the same time they agree: at t = 36 the level-5
arm reads R = 4.461, M = 2.736 and the down-step reads R = 4.441, M = 2.737.

*V1c's late-time scan rows are not drawn.*  From t ~ 29 its common scan sits
at r = 1.15, INSIDE its own frozen interior (r_full = 1.2): a surface of the
fill, not of the physics.  The freeze arm carried the waveform to t = 100 and
contributes nothing to this page.

*The restart-settle rows are masked, not smoothed.*  The level-5 arm's first
tenth of a unit reduces over an incomplete hierarchy; both restarted streams
are clipped SETTLE past their first row.

STYLE (2026-09-18, "PRD review style", the seed-branches grammar): full page
(7.05 x 6.4), a wide context strip over a 3 x 3 grid; style.prd frame, no
titles, letter tags above the frames, semantics in the caption; no boxed key,
every series named in place.  Monochrome ink plus the one accent: DEEP_GREEN is
the oriented horizon instrument -- filled diamonds for the offline fine scans,
open circles for the live scans -- and nothing else.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)

GROUP = "04_binary_headon"
SCOUT = "merge_headon_flip_d8_v1_t100"
ARM = "merge_headon_flip_d8_v1_lvl5from0_scalar_t100"
SEAMED = "merge_headon_flip_d8_v1_lvl5_t100_r02200"   # late offline anchors only
DOWN = "merge_headon_flip_d8_v1_lvl3down_t100_r03500"

# BinaryWormholeLevel's writer, in order -- no header on a restart.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

LAPSE_FLOOR = 1e-10    # the evolution's clamp on the lapse
CHI_FLOOR = 1e-20      # min_chi clamp of the head-on family (chi_rhs_floor 1e-8)
SETTLE = 0.1           # time clipped after a restart (incomplete hierarchy)

T_MOTS = 22.0          # first corrected-orientation common MOTS (offline scan)
T_WALL = 26.91         # the scout's death: the level-3 wall


def _sorted(path: pathlib.Path) -> np.ndarray:
    d = np.loadtxt(path)
    return d[np.argsort(d[:, 0])]


def _clipped(path: pathlib.Path) -> np.ndarray:
    d = _sorted(path)
    return d[d[:, 0] >= d[0, 0] + SETTLE]


def _live_scan(path: pathlib.Path, centre: str = "C") -> dict[str, np.ndarray]:
    """The oriented live scan's rows for one centre, as named arrays."""
    rows = [ln.split() for ln in path.read_text().splitlines()
            if ln and not ln.startswith("#")]
    rows = [p for p in rows if len(p) >= 19 and p[1] == centre]
    take = {"t": 0, "R_min": 5, "n_mots": 9, "r_mots": 10, "R_mots": 11,
            "M_MS": 12, "th_out": 14, "th_in": 15, "n_trapped": 16}
    return {k: np.array([float(p[i]) for p in rows]) for k, i in take.items()}


def _offline_formation(path: pathlib.Path) -> np.ndarray:
    """The scout's offline scan: t, r_mots, R_mots, M_MS (columns 0-3)."""
    return np.loadtxt(path)[:, :4]


def _offline_anchors(path: pathlib.Path) -> list[tuple[float, float, float, float]]:
    """(t, r_mots, R_mots, M_MS) from the t = 42.5/43 block-format scan."""
    import re
    head = re.compile(r"BinaryWormholePlt\d+\s+t=([\d.]+)")
    mots = re.compile(r"MOTS \(outermost, corrected orientation\): "
                      r"r = ([\d.]+), R = ([\d.]+), M_MS = ([\d.]+)")
    out, t = [], None
    for ln in path.read_text().splitlines():
        m = head.search(ln)
        if m:
            t = float(m.group(1))
        m = mots.search(ln)
        if m and t is not None:
            out.append((t, *(float(g) for g in m.groups())))
            t = None
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    scout, arm, down, seamed = (pack / "campaign" / GROUP / p
                            for p in (SCOUT, ARM, DOWN, SEAMED))

    ds = _sorted(scout / "collapse_diagnostics.dat")
    d5 = _sorted(arm / "collapse_diagnostics.dat")   # seamless: nothing to settle
    cs = _sorted(scout / "constraint_norms.dat")
    c5 = _sorted(arm / "constraint_norms.dat")
    c3 = _clipped(down / "constraint_norms.dat")
    col_s = {n: ds[:, i + 1] for i, n in enumerate(COLS)}
    col_5 = {n: d5[:, i + 1] for i, n in enumerate(COLS)}
    t_s, t_5 = ds[:, 0], d5[:, 0]
    t_end = float(t_5[-1])

    bs = _sorted(scout / "binary_throat_diagnostics.dat")
    b5 = _sorted(arm / "binary_throat_diagnostics.dat")

    scC = _live_scan(scout / "horizon_scan.dat")
    a5C = _live_scan(arm / "horizon_scan.dat")
    d3C = _live_scan(down / "horizon_scan.dat")
    form = _offline_formation(scout / "horizon_offline_scan.dat")
    late = _offline_anchors(seamed / "horizon_offline_scan_lvl5_t42.5_43.dat")

    wave = _sorted(arm / "Weyl4_mode_20.dat")     # t, (Re, Im) at R = 10/14/18

    # ---- derived numbers, printed for the caption --------------------------
    fl = (col_5["min_lapse"] <= LAPSE_FLOOR * 2.0)
    print(f"[headon collapse] scout t = 0-{t_s[-1]:.2f} (level 3, dies at the wall); "
          f"paper arm t = {t_5[0]:.2f}-{t_end:.2f} (level 5 FROM ZERO, no fill, no seam, no NaN)")
    print(f"  wall: scout max|K| {col_s['max_abs_K'][-1]:.1f}, H {cs[-1, 1]:.1f} at death; "
          f"level 5 max|K| peak {col_5['max_abs_K'].max():.2f} "
          f"(t = {t_5[np.argmax(col_5['max_abs_K'])]:.2f}), end {col_5['max_abs_K'][-1]:.2f}; "
          f"H falls {c5[:, 1].max():.2e} -> {c5[-1, 1]:.2e}")
    print(f"  clocks: level-5 lapse on the {LAPSE_FLOOR:g} clamp t = "
          f"{t_5[fl][0]:.2f}-{t_5[fl][-1]:.2f}, ends {col_5['min_lapse'][-1]:.2e}; "
          f"chi hits {CHI_FLOOR:g} at t = {t_5[np.argmin(col_5['min_chi'])]:.2f} "
          f"(scout: {t_s[np.argmin(col_s['min_chi'])]:.2f}), ends {col_5['min_chi'][-1]:.1e}")
    print(f"  field: max|phi| {col_5['max_phi'][0]:.2f} -> {col_5['max_phi'][-1]:.3f}; "
          f"|Pi| peak {max(col_5['max_Pi'].max(), -col_5['min_Pi'].min()):.3f} "
          f"at t = {t_5[np.argmax(np.maximum(col_5['max_Pi'], -col_5['min_Pi']))]:.2f}")
    for tv, r0, R0, M0 in form:
        print(f"  formation scan t = {tv:.0f}: MOTS r = {r0:.3f}, R = {R0:.3f}, M_MS = {M0:.3f}")
    for tv, r0, R0, M0 in late:
        print(f"  late scan t = {tv:.1f}: MOTS r = {r0:.3f}, R = {R0:.3f}, M_MS = {M0:.3f}")

    def mots(c):
        m = c["n_mots"] > 0
        return c["t"][m], c["R_mots"][m], c["M_MS"][m]

    tm5, Rm5, Mm5 = mots(a5C)
    tm3, Rm3, Mm3 = mots(d3C)
    tms, Rms, Mms = mots(scC)
    blind = int(((a5C["n_mots"] == 0) & (a5C["n_trapped"] >= 30)).sum())
    print(f"  live MOTS rows: scout {len(tms)}, level-5 arm {len(tm5)}, down-step {len(tm3)}; "
          f"{blind} level-5 scans blind (all shells trapped, MOTS outside aperture)")
    k36 = np.argmin(abs(tm5 - 36.0)), np.argmin(abs(tm3 - 36.0))
    print(f"  cross-arm at t = 36: level 5 R = {Rm5[k36[0]]:.3f}, M = {Mm5[k36[0]]:.3f}; "
          f"down-step R = {Rm3[k36[1]]:.3f}, M = {Mm3[k36[1]]:.3f}")
    if len(tm3) > 1:
        sl = np.polyfit(tm3, Mm3, 1)[0]
        print(f"  mass drift on the down-step track: dM/dt = {sl:+.4f} "
              f"({Mm3[0]:.3f} at t = {tm3[0]:.0f} -> {Mm3[-1]:.3f} at t = {tm3[-1]:.0f})")
    H5 = np.interp(c3[:, 0], c5[:, 0], c5[:, 1])
    M5 = np.interp(c3[:, 0], c5[:, 0], c5[:, 2])
    print(f"  down-step vs the SEAMLESS arm (its parent is the seamed chain; t = {c3[0, 0]:.1f}-{c3[-1, 0]:.1f}): median "
          f"|dH|/H = {np.median(abs(c3[:, 1] - H5) / H5) * 100:.2f}%, "
          f"|dM|/M = {np.median(abs(c3[:, 2] - M5) / M5) * 100:.2f}%")

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
        ax.axvline(T_MOTS, color=style.DEEP_GREEN, lw=0.7, ls=(0, (1, 2)), zorder=1)
        ax.axvline(T_WALL, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)

    # (a) the approach, and where each grid's story ends ----------------------
    # The seamless arm's own separation covers the WHOLE approach at level 5
    # now, so it carries the ink; the scout stays as the grey witness of the
    # level-3 wall.  Pre-merger the two curves lie on each other.
    axA.plot(bs[:, 0], bs[:, 1], color=style.CONTEXT, lw=1.0)
    axA.plot(b5[:, 0], b5[:, 1], color=style.INK, lw=1.2)
    rules(axA)
    axA.set_xlim(-1.5, t_end + 1.5)
    axA.set_ylim(-0.5, 9.4)
    axA.set_ylabel(r"$d$")
    axA.set_xlabel(r"$t$")
    # The black curve's name, in the corner its own descent encloses.  On one
    # line it is 23 t-units wide, which is wider than every clear stretch this
    # strip has: laid over the curve it was struck through by it, and pushed
    # into the band above the flat start it ran through the t = 22 rule and out
    # of the frame (2026-09-18).  Broken in two it fits under the descent, with
    # the curve 3.5 pt clear of the block's top right corner.  7.5 pt, like the
    # panel's other three names.
    axA.text(0.0, 3.9, "separation of the $\\chi$ pits\n(level 5, from $t=0$)", fontsize=7.5,
             ha="left", va="top", color=style.INK, linespacing=1.25)
    axA.text(29.5, 5.6, "common MOTS, $t=22$", fontsize=7.5, ha="left",
             va="bottom", color=style.DEEP_GREEN)
    axA.text(29.5, 3.4, "level-3 wall, $t=26.9$", fontsize=7.5, ha="left",
             va="bottom", color=style.MUTED)
    axA.text(44.0, 1.15, "one merged pit, to $t=100$ -- one grid, no seam",
             fontsize=7.5, ha="left", va="bottom", color=style.INK)
    tag(axA, "a")

    # (b)-(d) the clocks: level 5 walks through the level-3 wall --------------
    axB.semilogy(t_s, col_s["min_lapse"], color=style.CONTEXT, lw=0.9)
    axB.semilogy(t_5, col_5["min_lapse"], color=style.INK, lw=1.1)
    axB.axhline(LAPSE_FLOOR, color=style.MUTED, lw=0.7, ls=(0, (1, 2)))
    axB.set_ylabel(r"$\min\alpha$")
    axB.set_ylim(1e-11, 3)
    axB.text(97.0, 2.2e-10, "clamp", fontsize=7.5, ha="right", va="bottom",
             color=style.MUTED)
    # No grey label in this panel: the scout dies of a one-step overflow with
    # its lapse still at 1e-2, UNDER the ink -- there is no visible grey
    # stretch for a name to point at.  (c)-(e) carry the scout's names.

    axC.semilogy(t_s, col_s["min_chi"], color=style.CONTEXT, lw=0.9)
    axC.semilogy(t_5, col_5["min_chi"], color=style.INK, lw=1.1)
    axC.text(9.0, 1.35e-5, "level 3", fontsize=7.5, ha="center", va="bottom",
             color=style.CONTEXT)
    axC.set_ylabel(r"$\min\chi$")
    axC.set_ylim(1e-9, 4e-3)   # the clamp excursions leave the frame, honestly
    # Right-aligned: left-anchored the name ran to within half a point of the
    # right spine, which is closer than anything else on the page comes.
    axC.text(99.5, 2.6e-9, "onto the $10^{-20}$ clamp", fontsize=7.5, ha="right",
             va="bottom", color=style.MUTED)

    axD.semilogy(t_s, col_s["max_abs_K"], color=style.CONTEXT, lw=0.9)
    axD.semilogy(t_5, col_5["max_abs_K"], color=style.INK, lw=1.1)
    axD.set_ylabel(r"$\max|K|$")
    axD.set_ylim(2e-2, 90)
    axD.text(33.5, 16.0, "the wall\n(level 3)", fontsize=7.5, ha="left",
             va="top", color=style.CONTEXT, linespacing=1.25)
    axD.text(62.0, 0.32, "level 5", fontsize=7.5, ha="center", va="bottom",
             color=style.INK)

    # (e) the wall is resolution: the down-step lands on the level-5 curves ---
    axE.semilogy(cs[:, 0], cs[:, 1], color=style.CONTEXT, lw=0.9, ls=(0, (4, 2.5)))
    axE.semilogy(cs[:, 0], cs[:, 2], color=style.CONTEXT, lw=0.9, ls=(0, (1, 1.8)))
    axE.semilogy(c5[:, 0], c5[:, 1], color=style.INK, lw=1.1, ls=(0, (4, 2.5)))
    axE.semilogy(c5[:, 0], c5[:, 2], color=style.INK, lw=1.1, ls=(0, (1, 1.8)))
    axE.semilogy(c3[:, 0], c3[:, 1], color=style.MUTED, lw=0.8, ls=(0, (4, 2.5)))
    axE.semilogy(c3[:, 0], c3[:, 2], color=style.MUTED, lw=0.8, ls=(0, (1, 1.8)))
    axE.set_ylabel(r"$L^2$ constraints")
    # A decade of floor under the settled curves.  H bottoms at 6.1e-4, which
    # on the old 2.5e-4 floor left 9 pt between the curve and the frame -- less
    # than its own name, so the name printed through the spine and through both
    # H curves at once (2026-09-18).
    axE.set_ylim(5e-5, 6e1)
    axE.text(29.5, 6.0, "level 3", fontsize=7.5, ha="left", va="bottom",
             color=style.CONTEXT)
    # Each norm named off its OWN curve, at the t where the two are furthest
    # apart, with the clearance in points rather than in decades.
    axE.annotate(r"$\|\mathcal{M}\|$", (52.0, np.interp(52.0, c5[:, 0], c5[:, 2])),
                 xytext=(0, 5), textcoords="offset points", fontsize=7.5,
                 ha="center", va="bottom", color=style.INK)
    # |H| hangs off the LOWEST of the H curves (the down-step's, 0.2 dex under
    # the seamless arm's): pinned to the upper one it printed straight through
    # the lower (2026-09-21).
    axE.annotate(r"$\|\mathcal{H}\|$", (62.0, np.interp(62.0, c3[:, 0], c3[:, 1])),
                 xytext=(0, -5), textcoords="offset points", fontsize=7.5,
                 ha="center", va="top", color=style.INK)
    # "Coincides with level 5" was TRUE of the seamed chain this down-step
    # restarts from (median 0.08 %/1.5 %) and stays in the section text about
    # that pair; against the SEAMLESS arm drawn here its H sits a constant
    # ~0.2 dex below (different truncation history), M within 1.3 %.
    axE.text(66.0, 3.2e-2, "the down-step (level 3),\nfrom the seamed chain",
             fontsize=7.5, ha="center", va="bottom", color=style.MUTED,
             linespacing=1.25)

    for ax in (axB, axC, axD, axE):
        rules(ax)
        ax.set_xlim(-1.5, t_end + 1.5)
    axE.set_xlabel(r"$t$")   # (b)-(d) share the range; the title once is enough

    # (f)-(g) the horizon: found, tracked, and losing mass --------------------
    def scan_points(ax, ts_, ys, filled=False, small=False):
        ax.plot(ts_, ys, ls="none", marker="D" if filled else "o",
                ms=3.4 if filled else (2.6 if small else 3.2),
                mfc=style.DEEP_GREEN if filled else style.GROUND,
                mec=style.DEEP_GREEN, mew=1.0, zorder=5 if filled else 4)

    for ax, k in ((axF, 2), (axG, 3)):
        scan_points(ax, tms, [Rms, Mms][k - 2], small=True)
        scan_points(ax, tm5, [Rm5, Mm5][k - 2])
        scan_points(ax, tm3, [Rm3, Mm3][k - 2], small=True)
        scan_points(ax, form[:, 0], form[:, k], filled=True)
        scan_points(ax, [p[0] for p in late], [p[k] for p in late], filled=True)
        ax.axvline(T_WALL, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)
        ax.set_xlim(18.5, t_end + 1.5)
        ax.set_xlabel(r"$t$")
    # FITS through the long track (the down-step's 24 points, t = 36-99), so
    # the scatter reads as a trend and not as noise.  The two quantities do
    # NOT obey the same law, and that is the result: the radius is still
    # shrinking linearly at t = 100, while the mass has all but stopped.
    from scipy.optimize import curve_fit

    def _settle(x, a, b, tau):
        return a + b * np.exp(-(x - tm3[0]) / tau)

    t_fine = np.linspace(tm3[0], t_end, 200)
    slope = np.polyfit(tm3, Rm3, 1)
    axF.plot(t_fine, np.polyval(slope, t_fine), color=style.MUTED, lw=0.9,
             ls=(0, (4, 2.5)), zorder=2)
    pm, cm = curve_fit(_settle, tm3, Mm3, p0=(Mm3[-1], Mm3[0] - Mm3[-1], 25.0),
                       maxfev=40000)
    em = np.sqrt(np.diag(cm))
    axG.plot(t_fine, _settle(t_fine, *pm), color=style.MUTED, lw=0.9,
             ls=(0, (4, 2.5)), zorder=2)
    axG.axhline(pm[0], color=style.FAINT, lw=0.7, ls=(0, (1, 2)), zorder=1)
    rms_lin = np.sqrt(np.mean((Mm3 - np.polyval(np.polyfit(tm3, Mm3, 1), tm3)) ** 2))
    rms_exp = np.sqrt(np.mean((Mm3 - _settle(tm3, *pm)) ** 2))
    print(f"  FIT R_MOTS: linear, slope {slope[0]:+.5f} per unit "
          f"(rms {np.sqrt(np.mean((Rm3 - np.polyval(slope, tm3)) ** 2)):.4f}); "
          f"an exponential does not converge -- no asymptote is resolvable")
    print(f"  FIT M_MS: settles to {pm[0]:.3f} +- {em[0]:.3f} with "
          f"tau = {pm[2]:.1f} +- {em[2]:.1f} (rms {rms_exp:.4f}, "
          f"{rms_lin / rms_exp:.1f}x better than linear)")

    axF.set_ylabel(r"$R_{\mathrm{MOTS}}$")
    axF.set_ylim(3.9, 6.05)
    axF.text(28.5, 5.98, "offline scan,\n$\\mathrm{d}x=0.0625$", fontsize=7.5,
             ha="left", va="top", color=style.DEEP_GREEN, linespacing=1.25)
    axF.text(61.0, 4.62, "live scan\n(aperture gaps)", fontsize=7.5, ha="left",
             va="bottom", color=style.DEEP_GREEN, linespacing=1.25)
    axG.set_ylabel(r"$M_{\mathrm{MS}}$")
    axG.set_ylim(2.05, 3.42)
    # The asymptote is the news, so it is labelled on its own rule rather than
    # left for the caption.
    axG.text(96.0, 2.80, "settles to $M_\\infty=2.16$,\n$\\tau=19.4$", fontsize=7.5,
             ha="right", va="bottom", color=style.INK, linespacing=1.25)

    # (h) the surface that becomes the horizon --------------------------------
    w = scC["t"] >= 14.0
    axH.plot(scC["t"][w], scC["th_out"][w], color=style.INK, lw=1.1)
    axH.plot(scC["t"][w], scC["th_in"][w], color=style.MUTED, lw=0.9,
             ls=(0, (4, 2.5)))
    # Two clips: below t = 19.5 the areal-minimum shell hops between the two
    # mouths (a sawtooth of identity, not of geometry), and past the wall the
    # merged record belongs to (f)-(g).
    w5 = (a5C["t"] >= 19.5) & (a5C["t"] <= T_WALL)
    axH.plot(a5C["t"][w5], a5C["th_out"][w5], color=style.CONTEXT, lw=0.9)
    axH.axhline(0.0, color=style.FAINT, lw=0.7)
    axH.axvline(T_MOTS, color=style.DEEP_GREEN, lw=0.7, ls=(0, (1, 2)), zorder=1)
    axH.set_xlim(13.4, 28.6)
    axH.set_ylim(-0.62, 0.86)   # headroom for theta_+'s name over its flat start
    axH.set_xlabel(r"$t$")
    axH.set_ylabel(r"$\theta$ at areal min.")
    # Both names sit 4 pt ABOVE their own curve on the flat left stretch, where
    # the two are 0.36 apart: each is then unambiguously the curve beneath it.
    # Set at fixed y the upper name touched the frame and the lower one lay
    # along its own dashes (2026-09-18).
    axH.annotate(r"$\theta_+$", (15.4, scC["th_out"][w][0]), xytext=(0, 4),
                 textcoords="offset points", fontsize=8, ha="center",
                 va="bottom", color=style.INK)
    axH.annotate(r"$\theta_-$", (14.6, scC["th_in"][w][0]), xytext=(0, 4),
                 textcoords="offset points", fontsize=8, ha="center",
                 va="bottom", color=style.MUTED)
    axH.text(25.6, -0.45, "level 5", fontsize=7.5, ha="center", va="bottom",
             color=style.CONTEXT)

    # (i) the field that held the throats open is swallowed -------------------
    axI.plot(t_s, col_s["max_phi"], color=style.CONTEXT, lw=0.9)
    axI.plot(t_s, col_s["min_phi"], color=style.CONTEXT, lw=0.9)
    axI.plot(t_5, col_5["max_phi"], color=style.INK, lw=1.1)
    axI.plot(t_5, col_5["min_phi"], color=style.INK, lw=1.1)
    axI.plot(t_5, col_5["max_Pi"], color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    axI.plot(t_5, col_5["min_Pi"], color=style.MUTED, lw=0.9, ls=(0, (4, 2.5)))
    rules(axI)
    axI.set_xlim(-1.5, t_end + 1.5)
    axI.set_ylim(-1.05, 1.05)
    axI.set_xlabel(r"$t$")
    axI.set_ylabel(r"$\phi,\ \Pi$")
    axI.text(55.0, 0.44, r"$\pm\phi$", fontsize=8, ha="center", va="bottom",
             color=style.INK)
    axI.text(75.0, 0.10, r"$\pm\Pi$", fontsize=8, ha="center", va="bottom",
             color=style.MUTED)

    # (j) the remnant rings ----------------------------------------------------
    # NO r factor here.  `Weyl4_mode_20.dat` is already r*Psi4: the in-code
    # extraction multiplies by the sphere radius before integrating
    # (Source/ParticleInterpolator/WeylExtraction.hpp, "normalised by
    # multiplying by radius"), exactly as the Python consumer's
    # psi4_mode_l2m0.dat does, and the two agree to 0.1 % on this arm.  An
    # earlier draft multiplied by R = 10 a second time, which put this panel a
    # factor 10 above Fig. 8's same mode on the same sphere and sent +0.233
    # into the ledger for a peak that is +0.0233.
    axJ.plot(wave[:, 0], wave[:, 1], color=style.INK, lw=1.0)
    axJ.axhline(0.0, color=style.FAINT, lw=0.7)
    axJ.set_xlim(20.5, t_end + 1.5)
    axJ.set_ylim(-0.027, 0.030)
    axJ.set_xlabel(r"$t$")
    axJ.set_ylabel(r"$\mathrm{Re}\;r\psi_4^{(2,0)}$")
    # Inside the frame: this label carried an absolute y from the old, tenfold
    # ylim, and matplotlib does not clip text -- it floated out of (j) and
    # landed in panel (d).
    axJ.text(96.0, 0.020, "$(2,0)$ at $R=10$", fontsize=7.5, ha="right",
             va="bottom", color=style.INK)

    for ax, letter in zip(axes, "bcdefghij"):
        tag(ax, letter)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "headon_collapse_diagnostics.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[headon collapse] wrote {png} (+pdf); 10 panels, "
          f"{len(form) + len(late)} offline + {len(tms) + len(tm5) + len(tm3)} live MOTS points")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
