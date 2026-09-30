#!/usr/bin/env python3
r"""The head-on merger's collapse: the pair makes a black hole, and the hole settles.

The paper's head-on figure (sec:headon), and the spiral collapse page's
counterpart with the opposite verdict: here the scans FIND the horizon.  A
common MOTS encloses both mouths from t = 22 -- neither mouth ever has its
own -- and the remnant's horizon sheds the phantom scalar that held the
throats open and settles onto the Schwarzschild size of the pair's ADM mass.

SINCE 2026-09-30 THE FIGURE DRAWS THE MODE-3 PRODUCTION CHAIN (the user:
"the head-on now is the composition of the legs, like the spiral page"), the
far-side-matched (mode-3) data replacing the superposed runs.  One evolution
in three legs (d = 8, p = 0, flipped, L = 128, N = 256, M_ADM = 2.3573),
composed the way the spiral collapse page composes its history:

* leg 1 ``merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm`` --
  max_level 5 from t = 0.  Used to t = 35; it ran on to a NaN in h11 at
  t = 38.845, AT THE MERGED CORE, INSIDE THE MOTS (the same censored wall the
  spiral chain hits), drawn faint with the death cross so the composition's
  reason is on the page.
* leg 2 ``..._lvl6from35_scalar_chk_t100_csm_r03500`` -- max_level 6 from
  leg 1's t = 35 checkpoint, THROUGH the wall, stopped by hand at t = 50.80.
* leg 3 ``..._lvl4from50_scalar_t100_csm_r05000`` -- max_level 4 from leg 2's
  t = 50 checkpoint, to t = 100, exit 0, no NaN (the merged core no longer
  needs the fine levels once the wall is crossed).

The seams carry nothing: in-code Psi4 identical on both overlaps, level-0
norms continuous to 1.4 % / 0.1 %, the common MOTS continuous across t = 50
(R 4.266 -> 4.247; leg 3's VALIDATION.md).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_headon_collapse

WHAT THE FIGURE HAS TO GET RIGHT

*The horizon record is the round common scan, one row per unit* (centre C of
each leg's ``horizon_scan.dat``): first MOTS at t = 22 (R = 5.02,
M_MS = 2.69), found t = 22-25, LOST t = 26-35 -- the round scan cannot hold
the deformed merging surface, an aperture gap, not a horizon loss -- then
found every unit t = 36-100.  Data are joined by solid lines only within a
contiguous run of scan rows; the gap is left open, never bridged.

*The last word is the oriented scan* (``ah_oriented_scan_t098/099/100.dat``,
level 3, half 4.0, corrected orientation): at t = 100 the outermost MOTS is
R = 4.688, M_MS = 2.373 -- 0.99 of the Schwarzschild radius of the pair's
ADM mass (2 M_ADM = 4.715) and 1.007 of it in mass (M_ADM = 2.357, the
volume identity of leg 1's constraint solve).  Filled gold diamonds.

*The scan's R is a lower bound and it wobbles; the wobble is shape.*  The
round scan reports the outermost fully trapped COORDINATE sphere, inscribed
in the ringing MOTS, so R (and the M_MS read on it) oscillates by ~1 % about
its settle; the t = 45-51 dip (R 4.25, M_MS 2.29) is that systematic, not
mass loss and regain.  Where the round scan and the oriented one see the
surface at once (t = 100) they agree to 0.5 %.

*The reference lines are the initial data, not fits*: one isolated throat
R_star = 3.8895 (closed form, clmRstar), the two throats' summed area as one
sphere sqrt2 R_star = 5.50, and the Schwarzschild radius of the pair's ADM
mass 2 M_ADM = 4.715; on (b), M_ADM = 2.357 itself.  The superposed page's
exponential-settle and linear fits are not redrawn here: this chain's late
track is the round scan's shape wobble about a level line, and a fit through
it would state a precision the instrument does not have.

STYLE (grammar of 2026-09-24, "the plot is junk, why is there no solid
line"): a top-of-page strip, 7.05 x 4.3 in, set at 0.80\textwidth under [t].
The remnant's horizon is the figure -- areal radius (a) and Misner-Sharp
mass (b) on the left half, data joined, the initial data ruled -- and the
right half keeps the three panels the text leans on: the approach (c), the
composition's own record max|K| (d), and the field that is swallowed (e).
The era rules at t = 35 and 50.8 mark the seams in every panel, with the
levels named in (c), the composition panel -- the spiral collapse page's
grammar for a history drawn across legs.  style.prd frame, letter tags
above the frames, every series named in place, no boxed key.  GOLD is the
horizon instrument -- open circles the live round scan, filled diamonds the
oriented scan -- and nothing else.
"""

from __future__ import annotations

import argparse
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

GROUP = "04_binary_headon"
CHAIN = "csm"
LEG1 = "merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm"      # level 5
LEG2 = "merge_headon_flip_d8_v1_L128_lvl6from35_scalar_chk_t100_csm_r03500"  # level 6
LEG3 = "merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000"      # level 4

# BinaryWormholeLevel's writer, in order -- no header on a restart.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")

SETTLE = 0.15          # time clipped after a restart (incomplete hierarchy)

T_MOTS = 22.0          # first common MOTS (round scan, one row per unit)
T_SEAM1 = 35.0         # leg 1 -> leg 2 (level 5 -> 6)
T_SEAM2 = 50.8         # leg 2 -> leg 3 (level 6 -> 4)
T_NAN = 38.845         # leg 1's death: NaN in h11 at the merged core

R_STAR = 3.8895        # one isolated throat, closed form for a = 2, m = 1 (clmRstar)
M_ADM = 2.3573         # the pair's ADM mass, mode-3 volume identity (leg 1's solve)


def _sorted(path: pathlib.Path) -> np.ndarray:
    d = np.loadtxt(path)
    return d[np.argsort(d[:, 0])]


def _live_scan(path: pathlib.Path, centre: str = "C") -> dict[str, np.ndarray]:
    """The round common scan's rows for one centre, as named arrays."""
    rows = [ln.split() for ln in path.read_text().splitlines()
            if ln and not ln.startswith("#")]
    rows = [p for p in rows if len(p) >= 19 and p[1] == centre]
    take = {"t": 0, "R_min": 5, "n_mots": 9, "r_mots": 10, "R_mots": 11,
            "M_MS": 12, "n_trapped": 16}
    return {k: np.array([float(p[i]) for p in rows]) for k, i in take.items()}


def _oriented_anchors(run: pathlib.Path) -> list[tuple[float, float, float, float]]:
    """(t, r_mots, R_mots, M_MS) from the block-format oriented scans."""
    head = re.compile(r"BinaryWormholePlt\d+\s+t=([\d.]+)")
    mots = re.compile(r"MOTS \(outermost, corrected orientation\): "
                      r"r = ([\d.]+), R = ([\d.]+), M_MS = ([\d.]+)")
    out = []
    for path in sorted(run.glob("ah_oriented_scan_t*.dat")):
        t = None
        for ln in path.read_text().splitlines():
            m = head.search(ln)
            if m:
                t = float(m.group(1))
            m = mots.search(ln)
            if m and t is not None:
                out.append((t, *(float(g) for g in m.groups())))
                t = None
    return out


def _mots(c: dict[str, np.ndarray], lo: float = -np.inf, hi: float = np.inf):
    """t, R, M of a scan's MOTS rows within (lo, hi]."""
    m = (c["n_mots"] > 0) & (c["t"] > lo + 1e-9) & (c["t"] <= hi + 1e-9)
    return c["t"][m], c["R_mots"][m], c["M_MS"][m]


def _runs(t: np.ndarray, gap: float) -> list[np.ndarray]:
    """Index blocks of consecutive rows no further apart than gap."""
    if not len(t):
        return []
    return np.split(np.arange(len(t)), np.where(np.diff(t) > gap)[0] + 1)


def _era(d: np.ndarray, lo: float, hi: float, settle: float = 0.0) -> np.ndarray:
    """The composition rule: rows of one stream within (lo, hi], the first
    ``settle`` units after a restart dropped (incomplete hierarchy)."""
    return d[(d[:, 0] > lo + settle + 1e-9) & (d[:, 0] <= hi + 1e-9)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    leg1, leg2, leg3 = (pack / "campaign" / GROUP / CHAIN / p
                        for p in (LEG1, LEG2, LEG3))

    # ---- the composition: diagnostics era by era ----------------------------
    d1, d2, d3 = (_sorted(p / "collapse_diagnostics.dat") for p in (leg1, leg2, leg3))
    d1_used = _era(d1, -1.0, T_SEAM1)
    d1_over = d1[d1[:, 0] > T_SEAM1 - 1e-9]              # runs on to the NaN
    d2_used = _era(d2, T_SEAM1, T_SEAM2, SETTLE)
    d3_used = _era(d3, T_SEAM2, 1e9, SETTLE)
    b1, b2, b3 = (_sorted(p / "binary_throat_diagnostics.dat")
                  for p in (leg1, leg2, leg3))
    b1_used, b1_over = _era(b1, -1.0, T_SEAM1), b1[b1[:, 0] > T_SEAM1 - 1e-9]
    b2_used = _era(b2, T_SEAM1, T_SEAM2, SETTLE)
    b3_used = _era(b3, T_SEAM2, 1e9, SETTLE)

    def col(d, name):
        return d[:, COLS.index(name) + 1]

    # ---- the horizon record: round scan per era, oriented anchors -----------
    c1, c2, c3 = (_live_scan(p / "horizon_scan.dat") for p in (leg1, leg2, leg3))
    tm1, Rm1, Mm1 = _mots(c1, -1.0, T_SEAM1)             # t = 22-25
    tm2, Rm2, Mm2 = _mots(c2, T_SEAM1, T_SEAM2)          # t = 36-50
    tm3, Rm3, Mm3 = _mots(c3, T_SEAM2, np.inf)           # t = 51-100
    anchors = np.array(_oriented_anchors(leg3))
    t_end = float(d3_used[-1, 0])

    tm = np.concatenate([tm1, tm2, tm3])
    Rm = np.concatenate([Rm1, Rm2, Rm3])
    Mm = np.concatenate([Mm1, Mm2, Mm3])

    # ---- derived numbers, printed for the caption and the ledger ------------
    print(f"[headon collapse] mode-3 chain: leg 1 level 5 t = 0-{T_SEAM1:g} "
          f"(ran to NaN in h11 at t = {d1[-1, 0]:.3f}), leg 2 level 6 to {T_SEAM2:g}, "
          f"leg 3 level 4 to {t_end:.0f} (no NaN); M_ADM = {M_ADM:g}")
    print(f"  first common MOTS t = {tm[0]:.0f}: R = {Rm[0]:.3f} "
          f"= {Rm[0] / (np.sqrt(2) * R_STAR):.3f} sqrt2 R_star, M_MS = {Mm[0]:.3f} "
          f"= {Mm[0] / M_ADM:.3f} M_ADM; found t = 22-25, blind 26-35 "
          f"(round scan vs the deformed surface), found every unit 36-{tm[-1]:.0f}")
    print(f"  late track t = 36-{tm[-1]:.0f}: R {Rm[tm >= 36].min():.2f}-"
          f"{Rm[tm >= 36].max():.2f}, M_MS {Mm[tm >= 36].min():.2f}-"
          f"{Mm[tm >= 36].max():.2f} (round-scan shape wobble ~1 %)")
    for tv, r0, R0, M0 in anchors:
        print(f"  oriented scan t = {tv:.0f}: MOTS r = {r0:.3f}, R = {R0:.3f} "
              f"= {R0 / (2 * M_ADM):.3f} (2 M_ADM), M_MS = {M0:.3f} "
              f"= {M0 / M_ADM:.3f} M_ADM")
    print(f"  wall: leg-1 (level 5) max|K| peak {col(d1, 'max_abs_K').max():.2f}, "
          f"NaN at t = {d1[-1, 0]:.3f}; leg-2 (level 6) end {col(d2_used, 'max_abs_K')[-1]:.2f}; "
          f"leg-3 (level 4) end {col(d3_used, 'max_abs_K')[-1]:.3f}")
    print(f"  fields: max|phi| {max(col(d, 'max_phi').max() for d in (d1_used,)):.2f} "
          f"-> {max(abs(col(d3_used, 'min_phi')[-1]), col(d3_used, 'max_phi')[-1]):.3f}; "
          f"max|Pi| peak {np.maximum(abs(col(d2_used, 'min_Pi')), col(d2_used, 'max_Pi')).max():.3f}")

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
        for seam in (T_SEAM1, T_SEAM2):
            ax.axvline(seam, color=style.FAINT, lw=0.7, ls=(0, (4, 3)), zorder=1)

    def scan(ax, ts_, ys, *, filled, gap, ms=None):
        """One scan's rows: markers joined by a solid line within each run."""
        for idx in _runs(np.asarray(ts_), gap):
            ax.plot(np.asarray(ts_)[idx], np.asarray(ys)[idx], color=style.GOLD,
                    lw=1.0, ls="-", marker="D" if filled else "o",
                    ms=ms or (3.3 if filled else 2.9),
                    mfc=style.GOLD if filled else style.GROUND, mec=style.GOLD,
                    mew=0.9, zorder=5 if filled else 4)

    # (a) the remnant's areal radius against the initial data ------------------
    # (b) its Misner-Sharp mass against the pair's ADM mass --------------------
    for ax, ys, anc in ((axA, Rm, anchors[:, 2]), (axB, Mm, anchors[:, 3])):
        scan(ax, tm, ys, filled=False, gap=1.5)
        scan(ax, anchors[:, 0], anc, filled=True, gap=1.5)
        rules(ax)

    ref = dict(color=style.MUTED, lw=0.8, zorder=1)
    axA.axhline(R_STAR, ls=(0, (1, 1.6)), **ref)
    axA.axhline(2 * M_ADM, ls=(0, (5, 1.6, 1, 1.6)), **ref)
    axA.axhline(np.sqrt(2) * R_STAR, ls=(0, (1, 1.6)), **ref)
    axB.axhline(M_ADM, ls=(0, (5, 1.6, 1, 1.6)), **ref)

    axA.set_xlim(18.5, t_end + 1.5)
    axA.set_ylim(3.66, 5.98)
    axA.set_ylabel(r"horizon areal radius $R$")
    axA.tick_params(labelbottom=False)
    axB.set_ylim(2.10, 3.05)
    axB.set_ylabel(r"horizon mass $M_{\rm MS}$")
    axB.set_xlabel(r"$t$")

    fs = 7.5
    # Every name sits between the era rules (t = 35 and 50.8 are full-height
    # verticals, so a label that spans one is struck through): the reference
    # names in the blind window t = 26-35 or under their own rule past t = 52,
    # the instrument names over stretches their own rows leave clear.
    axA.annotate(r"one throat, $R_\star$", (68.0, R_STAR), xytext=(0, -2),
                 textcoords="offset points", ha="center", va="top", fontsize=fs,
                 color=style.MUTED)
    axA.annotate(r"$2M_{\rm ADM}$", (30.0, 2 * M_ADM), xytext=(0, 2),
                 textcoords="offset points", ha="center", va="bottom", fontsize=fs,
                 color=style.MUTED)
    axA.annotate(r"$\sqrt{2}\,R_\star$: both throats' area",
                 (t_end, np.sqrt(2) * R_STAR),
                 xytext=(0, 2), textcoords="offset points", ha="right", va="bottom",
                 fontsize=fs, color=style.MUTED)
    axA.text(43.0, 5.30, "round scan", fontsize=fs, ha="center", va="bottom",
             color=style.GOLD)
    # Left of the t = 98-100 diamonds, above the round scan's level stretch.
    axA.annotate("oriented scan", (96.5, float(anchors[0, 2])), xytext=(-4, 7),
                 textcoords="offset points", ha="right", va="bottom", fontsize=fs,
                 color=style.GOLD)
    axB.annotate(r"$M_{\rm ADM}$", (27.0, M_ADM), xytext=(0, 2),
                 textcoords="offset points", ha="left", va="bottom", fontsize=fs,
                 color=style.MUTED)

    # (c) the approach, drawn across the legs ----------------------------------
    axC.plot(b1_used[:, 0], b1_used[:, 1], color=style.INK, lw=1.2)
    axC.plot(b1_over[:, 0], b1_over[:, 1], color=style.CONTEXT, lw=0.9)
    for b in (b2_used, b3_used):
        axC.plot(b[:, 0], b[:, 1], color=style.INK, lw=1.2)
    axC.set_ylim(-0.6, 10.5)
    axC.set_ylabel(r"$\chi$-pit separation")
    # The composition named in ITS panel: one level per era, above the
    # curve's start (the separation opens at 8.0).
    # "level" and the digit stack in the first era (one line is wider than
    # the 22 units left of the t = 22 rule at this panel's width).
    for x, name in ((11.0, "level\n5"), (43.0, "6"), (76.0, "4")):
        axC.text(x, 10.35, name, fontsize=fs, ha="center", va="top",
                 color=style.INK, linespacing=1.1)
    axC.text(76.0, 0.55, "merged pit", fontsize=fs, ha="center", va="bottom",
             color=style.INK)

    # (d) the wall: level 5 dies at the core, level 6 walks through ------------
    axD.semilogy(d1_used[:, 0], col(d1_used, "max_abs_K"), color=style.INK, lw=1.1)
    axD.semilogy(d1_over[:, 0], col(d1_over, "max_abs_K"), color=style.CONTEXT, lw=0.9)
    axD.plot(d1_over[-1, 0], col(d1_over, "max_abs_K")[-1], "X", color=style.CONTEXT,
             markersize=5, markeredgecolor="white", markeredgewidth=0.8, zorder=4)
    axD.semilogy(d2_used[:, 0], col(d2_used, "max_abs_K"), color=style.INK, lw=1.1)
    axD.semilogy(d3_used[:, 0], col(d3_used, "max_abs_K"), color=style.INK, lw=1.1)
    axD.set_ylim(2e-2, 90)
    axD.set_ylabel(r"$\max|K|$")
    # Leg 1's overrun ends on the death cross; at this panel's width no name
    # fits between the era rules, so the NaN in h11 is the caption's to state.

    # (e) the field that held the throats open, swallowed ----------------------
    for d, faint in ((d1_used, False), (d1_over, True), (d2_used, False),
                     (d3_used, False)):
        phi = np.maximum(abs(col(d, "min_phi")), abs(col(d, "max_phi")))
        pi = np.maximum(abs(col(d, "min_Pi")), abs(col(d, "max_Pi")))
        axE.semilogy(d[:, 0], phi, color=style.CONTEXT if faint else style.INK,
                     lw=0.9 if faint else 1.1)
        tt = d[:, 0]
        axE.semilogy(tt[tt > 0.2], pi[tt > 0.2],
                     color=style.CONTEXT if faint else style.MUTED,
                     lw=0.9, ls=(0, (4, 2.5)))
    axE.set_ylim(1.5e-3, 2.5)
    axE.set_ylabel(r"$\max|\phi|,\ \max|\Pi|$")
    axE.set_xlabel(r"$t$")
    axE.text(6.0, 1.15, r"$|\phi|$", fontsize=8, ha="left", va="bottom", color=style.INK)
    # Under the two tails' close pass (t ~ 60-66, both >= 0.016), where the
    # panel is empty below 0.009.
    axE.text(63.0, 0.0085, r"$|\Pi|$", fontsize=8, ha="center", va="top",
             color=style.MUTED)

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
          f"{len(tm)} round-scan + {len(anchors)} oriented MOTS points; "
          f"label audit: {len(hits)} crossing(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
