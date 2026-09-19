#!/usr/bin/env python3
r"""The mouths inflate on the same clock whether the binary merges or misses.

The campaign's lifetime claim rests on one number -- the e-fold time of the
throat's unstable radial mode, tau ~ 4 units -- and until 2026-09-19 that
number came only from arms that do NOT merge: the isolated throats and the
p = 0.45 fly-by.  Every p = 0.12 arm, the ones that actually plunge, ran
before the per-mouth instruments existed, so nobody had watched a merging
binary's throats.  `v2_spiral_d12_p012_L128_lvl3_t050_mouths` is stage 1 of
that arm re-run with the oriented scan on, and this figure is the comparison
it was launched to make.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_mouth_growth

The verdict: the merging arm's mouths grow from the same initial areal radius
(4.2385, the two arms share their throat) on an e-fold time of 3.7 units
against the fly-by's 4.4, over the same fitted window t = 8-25 -- while one
binary closes from 11.9 to contact and the other misses at 4.8.  The clock
belongs to the throat, not to the encounter.

BOTH ARMS START AT d = 12, and the only thing that differs is the tangential
momentum: p = 0.12 is about a quarter of the circular value for the actual
central pull and plunges, p = 0.45 is 90 % of it and swings past.  So this is
not a comparison of a close pair with a distant one -- it is the same initial
separation, the same throats, two orbits.

WHERE EACH CURVE STOPS BEING A MEASUREMENT

The oriented scan centres a sphere on each tracked puncture and looks for the
minimal surface along its rays.  Two such spheres are separate readings only
while they are disjoint, i.e. while 2 r_min < d.  Past that the sphere around
A reaches across the other mouth and what it returns is a property of the
pair, not of one throat.  That crossing is drawn as the vertical rule, and
each arm's per-mouth curve goes dashed after it: t = 28 for the merger (the
mouths are in contact), t = 36 for the fly-by (closest approach).  After it,
the honest instrument is the common-centre scan -- one sphere on the box
centre enclosing both -- which is panel (a)'s grey curve.

Reads ``horizon_scan.dat`` from both arms under ``campaign/`` and writes
``figures/05_binary_spiral/p012_paper/mouth_growth``.

STYLE (the seed-branches grammar): single-column PRD frame, three stacked
panels on one clock, no boxed key, every curve named in place, letter tags
above the frames.  BURGUNDY is this package's horizon instrument and there is
no horizon in either arm -- that is itself a result -- so the accent is spent
on the fitted exponential instead, the one quantity the figure exists to
compare, and the absence of a MOTS is written on panel (a) in words.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

MERGER = ("05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl3_t050_mouths",
          r"merger, $p=0.12$")
FLYBY = ("06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100",
         r"fly-by, $p=0.45$")
FIT = (8.0, 25.0)        # shared window: both arms' scans are still disjoint
T_MAX = 50.0             # the merger's record; the fly-by's own page runs to 100
RULE_TOP = 9.0           # the rules stop below panel (a)'s label band


def _scan(path: pathlib.Path):
    """t, R_A, R_B, r_scan, separation, and the common-centre reading."""
    h = np.genfromtxt(path, dtype=None, encoding=None, names=True)
    A, B = h[h["centre"] == "A"], h[h["centre"] == "B"]
    n = min(len(A), len(B))
    sep = np.hypot(A["cx"][:n] - B["cx"][:n], A["cy"][:n] - B["cy"][:n])
    C = h[h["centre"] == "C"]
    mots = int(np.nansum(h["n_mots"]) + np.nansum(h["n_trapped"]))
    return dict(t=A["time"][:n], RA=A["R_min"][:n], RB=B["R_min"][:n],
                r=A["r_at_R_min"][:n], sep=sep, tC=C["time"], RC=C["R_min"],
                mots=mots)


def _split(s):
    """The index where the two scan spheres stop being disjoint."""
    bad = s["r"] > s["sep"] / 2.0
    return int(np.argmax(bad)) if bad.any() else len(s["t"])


def _tau(s, lo=FIT[0], hi=FIT[1]):
    ex = s["RA"] / s["RA"][0] - 1.0
    m = (s["t"] >= lo) & (s["t"] <= hi) & (ex > 0)
    p = np.polyfit(s["t"][m], np.log(ex[m]), 1)
    return 1.0 / p[0], float(np.exp(p[1])), ex


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser() / "campaign"

    m = _scan(pack / MERGER[0] / "horizon_scan.dat")
    f = _scan(pack / FLYBY[0] / "horizon_scan.dat")
    im, jf = _split(m), _split(f)
    tau_m, seed_m, ex_m = _tau(m)
    tau_f, seed_f, ex_f = _tau(f)

    style.prd(base=10.0)
    fig, (axA, axB, axC) = plt.subplots(
        3, 1, figsize=(3.4, 5.2), sharex=True, constrained_layout=True,
        gridspec_kw=dict(height_ratios=[1.15, 0.85, 1.0]))

    # ---- (a) each mouth's areal radius, solid while it is a measurement ----
    # Three dash languages, because three different things are drawn: solid is
    # a per-mouth measurement, DOTTED is the same scan after its sphere has
    # swallowed the other mouth, and the long dash is the common-centre scan,
    # which is a different instrument rather than the same one degraded.
    for s, i, col, lw in ((m, im, style.INK, 1.4), (f, jf, style.CONTEXT, 1.4)):
        k = (s["t"] <= T_MAX)
        axA.plot(s["t"][:i], s["RA"][:i], color=col, linewidth=lw, zorder=3)
        tail = slice(max(i - 1, 0), int(k.sum()))
        axA.plot(s["t"][tail], s["RA"][tail], color=col, linewidth=1.0,
                 linestyle=(0, (1.2, 1.8)), zorder=3)
        # The rules stop below the label band: a full-height axvline runs
        # through the two notes that explain what the rules are for.
        axA.vlines(s["t"][i] if i < len(s["t"]) else T_MAX, 3.6, RULE_TOP,
                   color=style.FAINT, linewidth=0.7, zorder=1)
    kC = m["tC"] <= T_MAX
    axA.plot(m["tC"][kC], m["RC"][kC], color=style.MUTED, linewidth=1.0,
             linestyle=(0, (6.5, 2.4)), zorder=2)
    axA.set_ylabel(r"$R_{\rm areal}$ per mouth")
    # The ceiling is above the highest curve (the common-centre scan starts at
    # 10.23) so that the two labels the data has no room for -- the rules' note
    # and the fly-by's name -- get a band of their own instead of being wedged
    # between curves.
    axA.set_ylim(3.6, 12.0)
    axA.text(2.0, 7.0, "common-centre scan", fontsize=7, color=style.MUTED)
    axA.text(2.0, 6.1, "no MOTS, no trapped surface", fontsize=6.5,
             color=style.MUTED)
    axA.text(3.0, 4.55, MERGER[1], fontsize=7.5, color=style.INK)
    axA.text(48.6, 9.9, FLYBY[1], fontsize=7.5, color=style.CONTEXT,
             ha="right", va="top")
    # Clear of the top spine AND of its inward ticks, which at 11.85 struck
    # through the first line.
    axA.text(26.0, 11.4, "past each rule the two\nscan spheres overlap",
             fontsize=6.5, color=style.MUTED, ha="center", va="top")

    # ---- (b) and meanwhile, what the orbit did ----------------------------
    for s, col in ((m, style.INK), (f, style.CONTEXT)):
        k = s["t"] <= T_MAX
        axB.plot(s["t"][k], s["sep"][k], color=col, linewidth=1.4, zorder=3)
    axB.set_ylabel(r"separation $d$")
    axB.set_ylim(0.0, 12.9)
    # Named so the panel reads without panel (a): each label says which arm
    # and what its orbit did, rather than a bare verdict.  The shared start is
    # stated because it is the point -- BOTH arms begin at d = 12 and the only
    # difference between them is the tangential momentum, so this panel is not
    # "near pair against far pair".
    axB.text(1.5, 0.9, r"both from $d=12$; only $p$ differs", fontsize=6.5,
             color=style.MUTED)
    axB.text(33.5, 2.45, "merger: to contact", fontsize=7, color=style.INK)
    axB.text(33.5, 6.3, f"fly-by: misses at {f['sep'].min():.1f}", fontsize=7,
             color=style.CONTEXT)

    # ---- (c) the clock itself ---------------------------------------------
    for s, ex, col, tau in ((m, ex_m, style.INK, tau_m),
                            (f, ex_f, style.CONTEXT, tau_f)):
        k = (s["t"] <= T_MAX) & (ex > 0)
        axC.plot(s["t"][k], ex[k], color=col, linewidth=1.4, zorder=3)
    tt = np.array(FIT)
    for seed, tau in ((seed_m, tau_m), (seed_f, tau_f)):
        axC.plot(tt, seed * np.exp(tt / tau), color=style.BURGUNDY,
                 linewidth=0.9, zorder=4)
    axC.set_yscale("log")
    axC.set_ylim(3e-5, 2.0)
    axC.set_xlim(0, T_MAX)
    axC.set_ylabel(r"$R_{\rm areal}/R_0 - 1$")
    axC.set_xlabel(r"$t$")
    # The two fits are within a factor 1.2 of each other, so their labels
    # cannot sit on the lines; they go together in the empty lower right.
    # Each label wears ITS ARM'S colour, not the accent: both fitted lines are
    # burgundy (that is what burgundy means here, "this is the fit"), so a
    # burgundy label would say which quantity it is and not which arm.
    axC.text(30.0, 4.5e-3, rf"$\tau={tau_f:.1f}$   fly-by", fontsize=7.5,
             color=style.CONTEXT, ha="left", va="top")
    axC.text(30.0, 1.3e-3, rf"$\tau={tau_m:.1f}$   merger", fontsize=7.5,
             color=style.INK, ha="left", va="top")
    axC.text(0.03, 0.95, rf"burgundy: fitted $t={FIT[0]:g}$--${FIT[1]:g}$",
             transform=axC.transAxes, fontsize=6.5, color=style.MUTED,
             va="top")

    # Panel (c)'s decade ticks are far wider than (a)'s and (b)'s integers, so
    # each y label would otherwise sit at its own indent and the stack would
    # read as three figures rather than one page.
    fig.align_ylabels((axA, axB, axC))

    for k, ax in enumerate((axA, axB, axC)):
        ax.text(0.0, 1.03, f"({'abc'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    print(f"[mouth-growth] merger: R {m['RA'][0]:.4f} -> {m['RA'][im - 1]:.4f} "
          f"(+{100 * (m['RA'][im - 1] / m['RA'][0] - 1):.1f} %) by t = {m['t'][im - 1]:.0f}, "
          f"d {m['sep'][0]:.2f} -> {m['sep'][im - 1]:.2f}; tau = {tau_m:.2f}, seed {seed_m:.2e}; "
          f"MOTS/trapped rows {m['mots']}")
    print(f"[mouth-growth] fly-by: R {f['RA'][0]:.4f} -> {f['RA'][jf - 1]:.4f} "
          f"(+{100 * (f['RA'][jf - 1] / f['RA'][0] - 1):.1f} %) by t = {f['t'][jf - 1]:.0f}, "
          f"d {f['sep'][0]:.2f} -> {f['sep'][jf - 1]:.2f}; tau = {tau_f:.2f}, seed {seed_f:.2e}; "
          f"MOTS/trapped rows {f['mots']}")
    print(f"[mouth-growth] A-B asymmetry: merger {np.abs(m['RA'] - m['RB']).max():.2e}, "
          f"fly-by {np.abs(f['RA'] - f['RB']).max():.2e}")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir("05_binary_spiral", args.pack_root) / "p012_paper" / "mouth_growth.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[mouth-growth] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
