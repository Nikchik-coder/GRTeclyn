#!/usr/bin/env python3
r"""The head-on merger's collapse: the pair makes a black hole, and the hole shrinks.

The paper's head-on figure (sec:headon), and the spiral collapse page's
counterpart with the opposite verdict: here the orientation-corrected scans
FIND the horizon.  A common MOTS encloses both mouths from t = 22 -- neither
mouth ever has its own -- the level-3 wall five units later is resolution
(level 5 walks through it with the constraints falling), and the remnant's
horizon then loses mass at every step as it swallows the phantom scalar that
held the throats open, settling toward the Schwarzschild size of the pair's
mass from above.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_headon_collapse

Reads, all under ``campaign/04_binary_headon/``:

* ``merge_headon_flip_d8_v1_t100/`` -- the level-3 scout (t = 0-26.91, dies at
  the wall): ``collapse_diagnostics.dat``, ``constraint_norms.dat``,
  ``binary_throat_diagnostics.dat`` and the offline formation scan
  ``horizon_offline_scan.dat`` (level 3, dx 0.0625, t = 22-26 -- the record of
  the horizon's birth).
* ``merge_headon_flip_d8_v1_lvl5from0_scalar_t100/`` -- THE PAPER'S ARM since
  2026-09-21: max_level 5 FROM t = 0, no interior fill, no restart, no seam,
  t = 100 with no NaN.  Its live scan finds the common MOTS at t = 21.5 and
  loses it behind the aperture after t = 37 (below).
* ``merge_headon_flip_d8_v1_lvl5_t100_r02200/`` -- the SUPERSEDED seamed arm,
  kept for ``horizon_offline_scan_lvl5_t42.5_43.dat``: its corrected offline
  scan at t = 42.5 / 43, the late filled anchors.
* ``merge_headon_flip_d8_v1_lvl3down_t100_r03500/`` -- back to max_level 3 from
  the level-5 t = 35 checkpoint, no fill: THE LATE HORIZON TRACK the text and
  the ledger quote (clmHeadonRemnantRadius, clmHeadonRadiusSlope, the M_MS
  fit).
* ``merge_headon_flip_d8_v1c_fillnarrow_t100_r02200/`` -- the fill twin (level
  3, fill 1.0/1.5 from t = 26.5, same t = 22 restart state as the down-step's
  parent).  Its live scan's aperture was never closed, so it tracks the
  horizon through the down-step's gaps; it agrees with the down-step to
  0.24 % in M_MS (clmHeadonDownStepMass) and ~0.2 % in R where both see the
  surface.  Drawn as the grey line under the gold, t >= 36 only; rows whose
  surface sits inside the fill's taper (r_mots <= 1.5) are the device's and
  are never drawn.

WHAT THE FIGURE HAS TO GET RIGHT

*Every horizon point is the corrected orientation*, live or offline.

*The live scan's gaps are aperture, not horizon loss.*  The common scan's
shells reach 0.5 sep + 2.3, with sep read off the chi-pit tracker; once the
pits merge the shells stop at r = 2.3 while the MOTS sits at r = 2.7-3.3, and
those scans report every shell trapped and no surface inside range.  Data
are therefore joined by solid lines only WITHIN a contiguous run of scan
rows; a gap is left open, never bridged -- a line drawn across t = 57-87
would print a constant slope the scan never measured.

*The scan's R is a lower bound and it wobbles; M_MS does not.*  The scan's
sphere is the outermost fully trapped COORDINATE sphere, so it sits inside
the MOTS; as the ringing surface changes shape the inscribed sphere moves in
and out, and R oscillates by ~1 % about its decline in anti-phase with the
shape excess 2 M_MS / R (detrended correlation -0.90 on the fill twin), while
M_MS falls at every one of the 24 / 51 down-step / fill-twin rows after t = 36
(scripts/analysis/merger_feedback/headon_remnant.py).

*The reference lines are the initial data, not fits*: one isolated throat
R_star = 3.8895 (closed form, clmRstar), the two throats' summed area as one
sphere sqrt2 R_star = 5.50, and the Schwarzschild radius of the pair's ADM
mass 2 M_ADM = 4 (clmHeadonADMMass); on (b), M_ADM = 2 itself.

*V1c's late-time scan rows are not drawn* (its common scan sits inside its
own frozen interior from t ~ 29), and the restart-settle rows of restarted
streams are masked, not smoothed.

STYLE (2026-09-24, feedback D1 -- "the plot is junk, why is there no solid
line; how the radius compares to the initial data"): a top-of-page strip,
7.05 x 4.3 in, set at 0.80\textwidth under [t].  The remnant's horizon is the
figure -- areal radius (a) and Misner-Sharp mass (b) on the left half, data
joined, the ledger's fits dashed, the initial data ruled -- and the right half
keeps the three panels the text leans on: the approach (c), max|K| through the
wall (d) and the field that is swallowed (e).  The Hamiltonian norms (scout,
level 5, down-step), once a panel here, are panel (e) of the appendix's
code-health figure (``plot_constraint_evolution``, 2026-09-26).  The (2,0)
wave left (Sec. VIII draws it), and so did min alpha, min chi and the null
expansions at the areal minimum (their numbers stay in the text).  style.prd
frame, letter tags above the frames, every series named in place, no boxed
key.  GOLD is the oriented horizon instrument -- filled diamonds offline,
open circles live -- and nothing else.
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
FILL = "merge_headon_flip_d8_v1c_fillnarrow_t100_r02200"   # dense late track, grey

# BinaryWormholeLevel's writer, in order -- no header on a restart.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

LAPSE_FLOOR = 1e-10    # the evolution's clamp on the lapse
CHI_FLOOR = 1e-20      # min_chi clamp of the head-on family (chi_rhs_floor 1e-8)
SETTLE = 0.1           # time clipped after a restart (incomplete hierarchy)

T_MOTS = 22.0          # first corrected-orientation common MOTS (offline scan)
T_WALL = 26.91         # the scout's death: the level-3 wall

R_STAR = 3.8895        # one isolated throat, closed form for a = 2, m = 1 (clmRstar)
M_ADM = 2.0            # the pair's ADM mass, 1 + 1 (clmHeadonADMMass)
T_LATE = 36.0          # the late track starts: the down-step's first MOTS row


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


def _param(run_dir: pathlib.Path, key: str) -> float:
    """One numeric key of a packed run's evolution_params.txt."""
    for ln in (run_dir / "evolution_params.txt").read_text().splitlines():
        p = ln.split("#")[0].split("=")
        if len(p) == 2 and p[0].strip() == key:
            return float(p[1].split()[0])
    raise KeyError(f"{key} not in {run_dir.name}/evolution_params.txt")


def _mots(c: dict[str, np.ndarray], t0: float = -np.inf, r_cut: float = 0.0):
    """t, R, M of a scan's MOTS rows from t0 on, surfaces inside r_cut dropped."""
    m = (c["n_mots"] > 0) & (c["t"] >= t0 - 1e-9) & (c["r_mots"] > r_cut)
    return c["t"][m], c["R_mots"][m], c["M_MS"][m]


def _runs(t: np.ndarray, gap: float) -> list[np.ndarray]:
    """Index blocks of consecutive rows no further apart than gap."""
    if not len(t):
        return []
    return np.split(np.arange(len(t)), np.where(np.diff(t) > gap)[0] + 1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    scout, arm, down, seamed, fill = (pack / "campaign" / GROUP / p
                                      for p in (SCOUT, ARM, DOWN, SEAMED, FILL))

    ds = _sorted(scout / "collapse_diagnostics.dat")
    d5 = _sorted(arm / "collapse_diagnostics.dat")   # seamless: nothing to settle
    c5 = _sorted(arm / "constraint_norms.dat")    # the console's H line only
    col_s = {n: ds[:, i + 1] for i, n in enumerate(COLS)}
    col_5 = {n: d5[:, i + 1] for i, n in enumerate(COLS)}
    t_s, t_5 = ds[:, 0], d5[:, 0]
    t_end = float(t_5[-1])

    bs = _sorted(scout / "binary_throat_diagnostics.dat")
    b5 = _sorted(arm / "binary_throat_diagnostics.dat")

    a5C = _live_scan(arm / "horizon_scan.dat")
    d3C = _live_scan(down / "horizon_scan.dat")
    fiC = _live_scan(fill / "horizon_scan.dat")
    form = _offline_formation(scout / "horizon_offline_scan.dat")
    late = np.array(_offline_anchors(seamed / "horizon_offline_scan_lvl5_t42.5_43.dat"))

    tm5, Rm5, Mm5 = _mots(a5C)
    tm3, Rm3, Mm3 = _mots(d3C)
    tmf, Rmf, Mmf = _mots(fiC, T_LATE, r_cut=_param(fill, "core_fill_radius_start"))

    # ---- derived numbers, printed for the caption and the ledger ------------
    print(f"[headon collapse] scout t = 0-{t_s[-1]:.2f} (level 3, dies at the wall); "
          f"paper arm t = {t_5[0]:.2f}-{t_end:.2f} (level 5 FROM ZERO, no fill, no seam, no NaN)")
    print(f"  wall: scout max|K| {col_s['max_abs_K'][-1]:.1f} at its last row; level 5 max|K| "
          f"peak {col_5['max_abs_K'].max():.2f} (t = {t_5[np.argmax(col_5['max_abs_K'])]:.2f}), "
          f"end {col_5['max_abs_K'][-1]:.2f}; level-5 H {c5[:, 1].max():.2e} -> {c5[-1, 1]:.2e}")
    for tv, r0, R0, M0 in form:
        print(f"  formation scan t = {tv:.0f}: MOTS r = {r0:.3f}, R = {R0:.3f}, M_MS = {M0:.3f}")
    for tv, r0, R0, M0 in late:
        print(f"  late scan t = {tv:.1f}: MOTS r = {r0:.3f}, R = {R0:.3f}, M_MS = {M0:.3f}")
    blind = int(((a5C["n_mots"] == 0) & (a5C["n_trapped"] >= 30)).sum())
    print(f"  live MOTS rows: level-5 arm {len(tm5)} (to t = {tm5[-1]:.1f}; {blind} scans blind "
          f"behind the aperture), down-step {len(tm3)}, fill twin {len(tmf)} from t = {T_LATE:g}")
    print(f"  M_MS rises after t = {T_LATE:g}: down-step {int((np.diff(Mm3[tm3 >= T_LATE]) > 0).sum())}, "
          f"fill twin {int((np.diff(Mmf) > 0).sum())}; R rises: down-step "
          f"{int((np.diff(Rm3[tm3 >= T_LATE]) > 0).sum())}, fill twin {int((np.diff(Rmf) > 0).sum())}")
    k = np.argmin(abs(tm3 - 97.0))
    print(f"  end of the track, t = {tm3[k]:.0f}: R = {Rm3[k]:.4f} = {Rm3[k] / R_STAR:.3f} R_star "
          f"= {Rm3[k] / (np.sqrt(2) * R_STAR):.3f} sqrt2 R_star = {Rm3[k] / (2 * M_ADM):.3f} (2 M_ADM); "
          f"M_MS = {Mm3[k]:.4f} = {Mm3[k] / M_ADM:.3f} M_ADM")
    print(f"  at formation: R = {form[0, 2]:.3f} = {form[0, 2] / (np.sqrt(2) * R_STAR):.3f} sqrt2 R_star, "
          f"M_MS = {form[0, 3]:.3f} = {form[0, 3] / M_ADM:.3f} M_ADM")

    # FITS through the down-step's 24 rows (t = 36-99), exactly the ledger's
    # (extract_mergers.mergers_headon_fit): a line through R, an exponential
    # settle through M_MS.  They describe the paper's track; they are not laws
    # -- the window moves M_inf by more than its statistical error.
    from scipy.optimize import curve_fit

    def _settle(x, a, b, tau):
        return a + b * np.exp(-(x - tm3[0]) / tau)

    slope = np.polyfit(tm3, Rm3, 1)
    pm, cm = curve_fit(_settle, tm3, Mm3, p0=(Mm3[-1], Mm3[0] - Mm3[-1], 25.0),
                       maxfev=40000)
    em = np.sqrt(np.diag(cm))
    rms_lin = np.sqrt(np.mean((Mm3 - np.polyval(np.polyfit(tm3, Mm3, 1), tm3)) ** 2))
    rms_exp = np.sqrt(np.mean((Mm3 - _settle(tm3, *pm)) ** 2))
    print(f"  FIT R_MOTS: linear, slope {slope[0]:+.5f} per unit "
          f"(rms {np.sqrt(np.mean((Rm3 - np.polyval(slope, tm3)) ** 2)):.4f}); "
          f"an exponential does not converge -- no asymptote is resolvable")
    print(f"  FIT M_MS: settles to {pm[0]:.3f} +- {em[0]:.3f} with "
          f"tau = {pm[2]:.1f} +- {em[2]:.1f} (rms {rms_exp:.4f}, "
          f"{rms_lin / rms_exp:.1f}x better than linear)")

    # ---- the strip ----------------------------------------------------------
    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 4.3), constrained_layout=True)
    gs = fig.add_gridspec(2, 4, width_ratios=[1.0, 1.0, 0.86, 0.86])
    axA = fig.add_subplot(gs[0, 0:2])
    axB = fig.add_subplot(gs[1, 0:2], sharex=axA)
    axC = fig.add_subplot(gs[0, 2])
    axD = fig.add_subplot(gs[0, 3])
    axE = fig.add_subplot(gs[1, 2:4])

    def tag(ax, letter):
        ax.text(0.0, 1.03, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    def rules(ax):
        ax.axvline(T_MOTS, color=style.GOLD, lw=0.7, ls=(0, (1, 2)), zorder=1)
        ax.axvline(T_WALL, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)

    def scan(ax, ts_, ys, *, filled, gap, ms=None):
        """One scan's rows: markers joined by a solid line within each run."""
        for idx in _runs(np.asarray(ts_), gap):
            ax.plot(np.asarray(ts_)[idx], np.asarray(ys)[idx], color=style.GOLD,
                    lw=1.0, ls="-", marker="D" if filled else "o",
                    ms=ms or (3.3 if filled else 2.9),
                    mfc=style.GOLD if filled else style.GROUND, mec=style.GOLD,
                    mew=0.9, zorder=5 if filled else 4)

    def twin(ax, ts_, ys):
        """The fill twin's dense track: grey, solid, gaps left open."""
        for idx in _runs(ts_, 1.5):
            ax.plot(ts_[idx], ys[idx], color=style.CONTEXT, lw=1.0, zorder=2)

    # (a) the remnant's areal radius against the initial data ------------------
    # (b) its Misner-Sharp mass against the pair's ADM mass --------------------
    for ax, j, yf, yd, yl in ((axA, 2, Rmf, Rm3, Rm5), (axB, 3, Mmf, Mm3, Mm5)):
        twin(ax, tmf, yf)
        scan(ax, tm5, yl, filled=False, gap=0.75)
        scan(ax, tm3, yd, filled=False, gap=1.5)
        scan(ax, form[:, 0], form[:, j], filled=True, gap=1.5)
        scan(ax, late[:, 0], late[:, j], filled=True, gap=1.5)
        rules(ax)
    t_fit = np.linspace(tm3[0], tm3[-1], 200)
    axA.plot(t_fit, np.polyval(slope, t_fit), color=style.MUTED, lw=0.9,
             ls=(0, (4, 2.5)), zorder=3)
    axB.plot(t_fit, _settle(t_fit, *pm), color=style.MUTED, lw=0.9,
             ls=(0, (4, 2.5)), zorder=3)

    ref = dict(color=style.MUTED, lw=0.8, zorder=1)
    axA.axhline(R_STAR, ls=(0, (1, 1.6)), **ref)
    axA.axhline(2 * M_ADM, ls=(0, (5, 1.6, 1, 1.6)), **ref)
    axA.axhline(np.sqrt(2) * R_STAR, ls=(0, (1, 1.6)), **ref)
    axB.axhline(M_ADM, ls=(0, (5, 1.6, 1, 1.6)), **ref)

    axA.set_xlim(18.5, t_end + 1.5)
    axA.set_ylim(3.66, 5.98)
    axA.set_ylabel(r"horizon areal radius $R$")
    axA.tick_params(labelbottom=False)
    axB.set_ylim(1.88, 3.30)
    axB.set_ylabel(r"horizon mass $M_{\rm MS}$")
    axB.set_xlabel(r"$t$")

    fs = 7.5
    # The initial data, named where the strip is empty: t = 27.5-34.5 carries
    # no scan row at any height (the level-5 arm is behind its aperture, the
    # fill twin's rows there are the device's).
    axA.annotate(r"one throat, $R_\star$", (28.0, R_STAR), xytext=(0, -2),
                 textcoords="offset points", ha="left", va="top", fontsize=fs,
                 color=style.MUTED)
    axA.annotate(r"$2M_{\rm ADM}$ (pair)", (28.0, 2 * M_ADM), xytext=(0, 2),
                 textcoords="offset points", ha="left", va="bottom", fontsize=fs,
                 color=style.MUTED)
    axA.annotate(r"$\sqrt{2}\,R_\star$: both throats' area", (t_end, np.sqrt(2) * R_STAR),
                 xytext=(0, 2), textcoords="offset points", ha="right", va="bottom",
                 fontsize=fs, color=style.MUTED)
    axA.text(29.0, 5.62, "offline scans", fontsize=fs, ha="left", va="center",
             color=style.GOLD)
    # Over the t = 47-56 run, above the grey line that shares it (the grey
    # sits at R <= 4.56 across the name's width).
    axA.text(53.5, 4.62, "live scans", fontsize=fs, ha="center", va="bottom",
             color=style.GOLD)
    # Over the grey's own t = 67-74 run (max 4.51), clear of the gold.
    axA.text(69.5, 4.555, "fill twin", fontsize=fs, ha="center", va="bottom",
             color=style.CONTEXT)
    # The fits are named, not quoted: their numbers reach the reader through
    # the caption's ledger macros (clmHeadonRadiusSlope, clmHeadonMass*).
    axA.annotate("linear fit", (72.0, np.polyval(slope, 72.0)), xytext=(0, -6),
                 textcoords="offset points", ha="center", va="top", fontsize=fs,
                 color=style.MUTED)

    axB.annotate(r"$M_{\rm ADM}$", (28.0, M_ADM), xytext=(0, 2),
                 textcoords="offset points", ha="left", va="bottom", fontsize=fs,
                 color=style.MUTED)
    axB.annotate("exponential fit", (70.0, _settle(70.0, *pm)),
                 xytext=(0, -6), textcoords="offset points", ha="center", va="top",
                 fontsize=fs, color=style.MUTED)

    # (c) the approach ----------------------------------------------------------
    axC.plot(bs[:, 0], bs[:, 1], color=style.CONTEXT, lw=1.0)
    axC.plot(b5[:, 0], b5[:, 1], color=style.INK, lw=1.2)
    axC.set_ylim(-0.5, 9.4)
    axC.set_ylabel(r"$\chi$-pit separation")
    # Over the merged pit's flat run, the ink's own stretch (the grey scout
    # lies under the ink until its wall and has no stretch of its own to name).
    axC.text(70.0, 0.55, "one pit, level 5", fontsize=fs, ha="center", va="bottom",
             color=style.INK)

    # (d) the wall: level 3 runs away, level 5 walks through --------------------
    axD.semilogy(t_s, col_s["max_abs_K"], color=style.CONTEXT, lw=0.9)
    axD.semilogy(t_5, col_5["max_abs_K"], color=style.INK, lw=1.1)
    axD.set_ylim(2e-2, 90)
    axD.set_ylabel(r"$\max|K|$")
    axD.text(31.0, 25.0, "level 3", fontsize=fs, ha="left", va="center",
             color=style.CONTEXT)
    axD.text(62.0, 0.30, "level 5", fontsize=fs, ha="center", va="bottom",
             color=style.INK)

    # (e) the field that held the throats open, swallowed ----------------------
    phi5 = np.maximum(abs(col_5["min_phi"]), abs(col_5["max_phi"]))
    pi5 = np.maximum(abs(col_5["min_Pi"]), abs(col_5["max_Pi"]))
    phis = np.maximum(abs(col_s["min_phi"]), abs(col_s["max_phi"]))
    axE.semilogy(t_s, phis, color=style.CONTEXT, lw=0.9)
    axE.semilogy(t_5, phi5, color=style.INK, lw=1.1)
    axE.semilogy(t_5[t_5 > 0.2], pi5[t_5 > 0.2], color=style.MUTED, lw=0.9,
                 ls=(0, (4, 2.5)))
    axE.set_ylim(1.5e-3, 2.5)
    axE.set_ylabel(r"$\max|\phi|,\ \max|\Pi|$")
    axE.set_xlabel(r"$t$")
    axE.text(6.0, 1.15, r"$|\phi|$", fontsize=8, ha="left", va="bottom", color=style.INK)
    # Under the dashed hump, right of both rules, where the ink is a decade up.
    axE.text(31.0, 0.036, r"$|\Pi|$", fontsize=8, ha="left", va="top", color=style.MUTED)

    for ax in (axC, axD, axE):
        rules(ax)
        ax.set_xlim(-1.5, t_end + 1.5)
    axC.tick_params(labelbottom=False)
    axD.tick_params(labelbottom=False)

    for ax, letter in zip((axA, axB, axC, axD, axE), "abcde"):
        tag(ax, letter)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "headon_collapse_diagnostics.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[headon collapse] wrote {png} (+pdf); 5 panels, 7.05 x 4.3 in, "
          f"{len(form) + len(late)} offline + {len(tm5) + len(tm3)} live MOTS points "
          f"+ {len(tmf)} fill-twin rows; label audit: {len(hits)} crossing(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
