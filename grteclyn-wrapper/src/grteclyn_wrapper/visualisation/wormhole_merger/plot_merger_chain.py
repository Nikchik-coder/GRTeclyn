#!/usr/bin/env python3
r"""The d = 6 orbital merger: the chain that carries a wormhole pair through
its merger wall to a settled black hole.

The paper's orbital-merger figure (sec:spiral:inspiral), replacing the
superposed production spiral's collapse page: on boosted, solved (mode-3)
data the d = 12 arms never merge (the race, sec:spiral:race), and THE orbital
merger is the d = 6, tangential p = 0.10 chain (2026-10-02/03).

One evolution, composed across its legs the way the head-on page is
(plot_headon_collapse):

* leg 1 ``spiral_d6_p010_L128_lvl5from0_t060_lbf_csm`` -- level 5 from t = 0,
  common MOTS from t = 13, stopped by hand at t = 26.26 as the merged core's
  K runaway turned exponential (trust 25.5); the chain restarts from its
  t = 25 checkpoint.
* the wall arms, all from that same Chk02500 (drawn as diagnostics in (d)):
  ``..._lvl6from25_...`` dies t = 29.407 (single-cell h11 NaN at the core
  centre, globals clean); ``..._lvl7from25_...`` dies t = 27.53 -- TWO UNITS
  EARLIER with max|K| still climbing: the core instability is continuum, not
  under-resolution; ``..._lvl5from25_sig10_...`` (Kreiss-Oliger sigma 1.0)
  clears the K wall and dies at the same cell at t = 30.53 -- sigma delays,
  it does not cure.
* the crossing leg ``..._lvl5from30_sig10_chi1e4_...`` -- min_chi 1e-8 ->
  1e-4 from sig10's t = 30 checkpoint: the chi floor caps the 1/chi
  steepness runaway and the leg sails through the death point to t = 36.62.
* the settle leg ``..._lvl4from35_t100_...`` -- pre-wall numerics restored
  (min_chi 1e-8, sigma 0.1), level 4, t = 35 -> 100, no NaN: the cured core
  never re-fails.

WHAT THE FIGURE HAS TO GET RIGHT

*The horizon record is the 3D spectral finder's history* (``mots_spectral.dat``
of the USED legs -- leg 1, sigma, chi, settle -- joined in time, later leg
winning a duplicate; the lvl6/lvl7 diagnostic arms are not part of the used
history): born t = 13 with R = 5.600 (M_MS = 2.800, deform 0.115), shrinking
monotonically (<= 0.05 % per-row rise over 87 rows) to R = 4.883,
M_MS = 2.441, deform 0.016 at t = 100 -- within 2.2 % of the head-on
remnant's R = 4.7787, drawn as a reference rule.  GOLD.

*The wall is panel (d)*: max|K| of every arm.  The used legs in ink; the
lvl6 / lvl7 arms grey with death crosses -- finer dies EARLIER (29.4 -> 27.5)
-- and sigma's delayed death at 30.53.  The chi-floor crossing leg and the
settle leg carry the history through where every other arm died.

*Reference lines are initial data and the head-on*: one isolated throat
R_star = 3.8895, sqrt2 R_star = 5.50 (both throats' area), and the head-on
chain's settled remnant R = 4.7787 (M_MS = 2.3894 on (b)).

STYLE: the head-on page's grammar -- 7.05 x 4.3 in strip, style.prd, GOLD is
the horizon instrument, era rules at the restarts, levels named per era,
label audit clean.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_merger_chain
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

GROUP = "05_binary_spiral"
CHAIN = "merger_d6"
LEG1 = "spiral_d6_p010_L128_lvl5from0_t060_lbf_csm"                     # level 5 from 0
LVL6 = "spiral_d6_p010_L128_lvl6from25_t060_lbf_csm_r02500"             # wall arm
LVL7 = "spiral_d6_p010_L128_lvl7from25_t060_lbf_csm_r02500"             # wall arm
SIG = "spiral_d6_p010_L128_lvl5from25_sig10_t060_lbf_csm_r02500"        # sigma 1.0
CHI = "spiral_d6_p010_L128_lvl5from30_sig10_chi1e4_t060_lbf_csm_r03000" # chi floor
SETTLE = "spiral_d6_p010_L128_lvl4from35_t100_lbf_csm_r03500"           # level 4

COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

SETTLE_CLIP = 0.15     # time clipped after a restart (incomplete hierarchy)

T_MOTS = 13.0          # horizon birth: the finder's first converged row
T_SEAM1 = 25.0         # leg 1's restart checkpoint (the wall era opens)
T_SEAM2 = 30.0         # sigma leg -> chi-floor crossing leg
T_SEAM3 = 35.0         # crossing leg -> level-4 settle leg
T_LEG1_STOP = 26.26    # leg 1 stopped by hand (pre-NaN)

R_STAR = 3.8895        # one isolated throat (clmRstar)
R_HEADON = 4.7787      # the head-on chain's settled remnant (clmHeadonCsmEndRadius)
M_HEADON = 2.3894      # its settled M_MS (clmHeadonCsmEndMass)


def _sorted(path: pathlib.Path) -> np.ndarray:
    d = np.loadtxt(path)
    return d[np.argsort(d[:, 0])]


def _spectral(path: pathlib.Path) -> dict[str, np.ndarray]:
    names, rows = None, []
    for ln in (path / "mots_spectral.dat").read_text().splitlines():
        if ln.startswith("#"):
            toks = ln.lstrip("#").split()
            if toks and toks[0] == "time":
                names = toks
            continue
        p = [float(x) for x in ln.split()]
        if names and len(p) >= len(names) and not np.isnan(p[1]):
            rows.append(p[:len(names)])
    arr = np.array(rows)
    arr = arr[np.argsort(arr[:, 0])]
    return {c: arr[:, i] for i, c in enumerate(names)}


def _join(paths: list[pathlib.Path]) -> dict[str, np.ndarray]:
    cols, rows = None, {}
    for path in paths:
        s = _spectral(path)
        if cols is None:
            cols = list(s)
        for i in range(len(s["time"])):
            rows[round(float(s["time"][i]), 3)] = {c: s[c][i] for c in cols}
    ts = sorted(rows)
    return {c: np.array([rows[t][c] for t in ts]) for c in cols}


def _era(d: np.ndarray, lo: float, hi: float, settle: float = 0.0) -> np.ndarray:
    return d[(d[:, 0] > lo + settle + 1e-9) & (d[:, 0] <= hi + 1e-9)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    leg1, lvl6, lvl7, sig, chi, settle = (pack / "campaign" / GROUP / CHAIN / p
                                          for p in (LEG1, LVL6, LVL7, SIG, CHI, SETTLE))

    # ---- the used composition: leg 1 -> sigma -> chi floor -> settle ---------
    used = [(leg1, -1.0, T_SEAM1), (sig, T_SEAM1, T_SEAM2),
            (chi, T_SEAM2, T_SEAM3), (settle, T_SEAM3, 1e9)]
    d_used, b_used = [], []
    for path, lo, hi in used:
        d = _sorted(path / "collapse_diagnostics.dat")
        b = _sorted(path / "binary_throat_diagnostics.dat")
        s = 0.0 if lo < 0 else SETTLE_CLIP
        d_used.append(_era(d, lo, hi, s))
        b_used.append(_era(b, lo, hi, s))
    d1_full = _sorted(leg1 / "collapse_diagnostics.dat")
    d1_over = d1_full[d1_full[:, 0] > T_SEAM1 - 1e-9]        # leg 1 runs on to 26.26
    b1_full = _sorted(leg1 / "binary_throat_diagnostics.dat")
    b1_over = b1_full[b1_full[:, 0] > T_SEAM1 - 1e-9]
    d_lvl6 = _sorted(lvl6 / "collapse_diagnostics.dat")
    d_lvl7 = _sorted(lvl7 / "collapse_diagnostics.dat")
    d_sig_over = _era(_sorted(sig / "collapse_diagnostics.dat"), T_SEAM2, 1e9)

    def col(d, name):
        return d[:, COLS.index(name) + 1]

    # ---- the horizon record --------------------------------------------------
    sp = _join([leg1, sig, chi, settle])
    ts, Rs, Ms = sp["time"], sp["R"], sp["M_MS"]
    t_end = float(d_used[-1][-1, 0])

    print(f"[merger chain] d = 6, p = 0.10 tangential, used legs: lvl5 to "
          f"{T_SEAM1:g} (stopped {T_LEG1_STOP}), sigma to {T_SEAM2:g}, chi floor "
          f"to {T_SEAM3:g}, lvl4 to {t_end:.0f}")
    print(f"  finder: born t = {ts[0]:.0f}, R = {Rs[0]:.3f}, M_MS = {Ms[0]:.3f}, "
          f"deform {sp['deform'][0]:.3f}; settle R = {Rs[-1]:.3f}, "
          f"M_MS = {Ms[-1]:.4f}, deform {sp['deform'][-1]:.4f} at t = {ts[-1]:.0f} "
          f"({100 * (Rs[-1] / R_HEADON - 1):+.1f}% of the head-on remnant)")
    print(f"  wall arms: lvl6 dies {d_lvl6[-1, 0]:.3f} (max|K| "
          f"{col(d_lvl6, 'max_abs_K').max():.2f}), lvl7 dies {d_lvl7[-1, 0]:.2f} "
          f"({col(d_lvl7, 'max_abs_K').max():.1f}, still climbing), sigma dies "
          f"{d_sig_over[-1, 0]:.2f}")

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
        for seam in (T_SEAM1, T_SEAM2, T_SEAM3):
            ax.axvline(seam, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)

    # (a) areal radius, (b) Misner-Sharp mass ----------------------------------
    for ax, ys in ((axA, Rs), (axB, Ms)):
        ax.plot(ts, ys, color=style.GOLD, lw=1.3, zorder=5)
        rules(ax)

    ref = dict(color=style.MUTED, lw=0.8, zorder=1)
    axA.axhline(R_STAR, ls=(0, (1, 1.6)), **ref)
    axA.axhline(np.sqrt(2) * R_STAR, ls=(0, (1, 1.6)), **ref)
    axA.axhline(R_HEADON, ls=(0, (5, 1.6, 1, 1.6)), **ref)
    axB.axhline(M_HEADON, ls=(0, (5, 1.6, 1, 1.6)), **ref)

    axA.set_xlim(10.0, 100.0)
    axA.set_ylim(3.66, 5.98)
    axA.set_ylabel(r"horizon areal radius $R$")
    axA.tick_params(labelbottom=False)
    axB.set_ylim(2.10, 3.05)
    axB.set_ylabel(r"horizon mass $M_{\rm MS}$")
    axB.set_xlabel(r"$t$")

    fs = 7.5
    axA.text(55.0, 5.08, "3D finder", fontsize=fs, ha="center", va="bottom",
             color=style.GOLD)
    axA.annotate(r"one throat, $R_\star$", (68.0, R_STAR), xytext=(0, -2),
                 textcoords="offset points", ha="center", va="top", fontsize=fs,
                 color=style.MUTED)
    axA.annotate(r"$\sqrt{2}\,R_\star$: both throats' area",
                 (t_end, np.sqrt(2) * R_STAR), xytext=(0, 2),
                 textcoords="offset points", ha="right", va="bottom",
                 fontsize=fs, color=style.MUTED)
    axA.annotate("head-on remnant", (76.0, R_HEADON), xytext=(0, -3),
                 textcoords="offset points", ha="center", va="top", fontsize=fs,
                 color=style.MUTED)
    axB.annotate("head-on remnant", (76.0, M_HEADON), xytext=(0, -3),
                 textcoords="offset points", ha="center", va="top", fontsize=fs,
                 color=style.MUTED)
    # The composition's levels, named per era in every panel that draws
    # across the legs (the user, 2026-10-05: "why there is no level text
    # still"): the full ladder -- level 5, the sigma leg, the chi-floor leg,
    # level 4 -- where the panel is wide, (a) and (e); digits in (c), (d).
    def ladder(ax, y, first="level 5", x1=19.0, last="level 4", x4=55.0):
        for x, name in ((x1, first), (27.5, r"$\sigma$"), (32.5, r"$\chi$"),
                        (x4, last)):
            ax.text(x, y, name, fontsize=7, ha="center", va="top",
                    color=style.MUTED)
    ladder(axA, 5.90)   # tops below the 3.4 pt ticks

    # (c) the approach, drawn across the legs ----------------------------------
    for b in b_used:
        axC.plot(b[:, 0], b[:, 1], color=style.INK, lw=1.2)
    axC.plot(b1_over[:, 0], b1_over[:, 1], color=style.CONTEXT, lw=0.9)
    axC.set_ylim(-0.4, 7.0)
    axC.set_ylabel(r"$\chi$-pit separation")
    axC.text(68.0, 0.45, "merged pit", fontsize=fs, ha="center", va="bottom",
             color=style.INK)
    for x, name in ((6.0, "5"), (68.0, "4")):
        axC.text(x, 6.9, name, fontsize=fs, ha="center", va="top",
                 color=style.MUTED)

    # (d) the wall: every arm's max|K|; the cures carry the history ------------
    for d in d_used:
        axD.semilogy(d[:, 0], col(d, "max_abs_K"), color=style.INK, lw=1.1)
    for d, x in ((d1_over, None), (d_sig_over, "X")):
        axD.semilogy(d[:, 0], col(d, "max_abs_K"), color=style.CONTEXT, lw=0.9)
        if x:
            axD.plot(d[-1, 0], col(d, "max_abs_K")[-1], "X", color=style.CONTEXT,
                     markersize=5, markeredgecolor="white", markeredgewidth=0.8,
                     zorder=4)
    for d in (d_lvl6, d_lvl7):
        axD.semilogy(d[:, 0], col(d, "max_abs_K"), color=style.CONTEXT, lw=0.9,
                     ls=(0, (3, 1.6)))
        axD.plot(d[-1, 0], col(d, "max_abs_K")[-1], "X", color=style.CONTEXT,
                 markersize=5, markeredgecolor="white", markeredgewidth=0.8,
                 zorder=4)
    axD.set_ylim(2e-2, 90)
    axD.set_ylabel(r"$\max|K|$")
    axD.text(6.0, 55.0, "5", fontsize=fs, ha="center", va="top", color=style.MUTED)
    axD.text(68.0, 55.0, "4", fontsize=fs, ha="center", va="top", color=style.MUTED)
    axD.text(68.0, 6.0, "6, 7: dashed\n$\\sigma$: solid", fontsize=6.3,
             ha="center", va="top", color=style.CONTEXT, linespacing=1.2)

    # (e) the field that held the throats open, swallowed ----------------------
    for d in d_used:
        phi = np.maximum(abs(col(d, "min_phi")), abs(col(d, "max_phi")))
        pi = np.maximum(abs(col(d, "min_Pi")), abs(col(d, "max_Pi")))
        axE.semilogy(d[:, 0], phi, color=style.INK, lw=1.1)
        tt = d[:, 0]
        axE.semilogy(tt[tt > 0.2], pi[tt > 0.2], color=style.MUTED, lw=0.9,
                     ls=(0, (4, 2.5)))
    axE.set_ylim(1.5e-3, 2.5)
    axE.set_ylabel(r"$\max|\phi|,\ \max|\Pi|$")
    axE.set_xlabel(r"$t$")
    axE.text(6.0, 1.15, r"$|\phi|$", fontsize=8, ha="left", va="bottom",
             color=style.INK)
    axE.text(63.0, 0.0075, r"$|\Pi|$", fontsize=8, ha="center", va="top",
             color=style.MUTED)
    ladder(axE, 1.95, first="5", x4=67.0)   # 13-25 is too narrow for "level 5" here

    for ax in (axC, axD, axE):
        rules(ax)
        ax.set_xlim(0.0, 100.0)
    axC.tick_params(labelbottom=False)
    axD.tick_params(labelbottom=False)

    for ax, letter in zip((axA, axB, axC, axD, axE), "abcde"):
        tag(ax, letter)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir(GROUP, args.pack_root) / "d6_merger_chain.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[merger chain] wrote {png} (+pdf); 5 panels, {len(ts)} finder rows; "
          f"label audit: {len(hits)} crossing(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
