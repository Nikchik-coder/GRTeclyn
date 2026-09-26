#!/usr/bin/env python3
r"""The mouths' growth in a binary that merges and in one that misses.

The campaign's lifetime claim rests on one number -- the e-fold time of the
throat's unstable radial mode, tau ~ 4 units -- and until 2026-09-19 that
number came only from arms that do NOT merge: the isolated throats and the
p = 0.45 fly-by.  Every p = 0.12 arm, the ones that actually plunge, ran
before the per-mouth instruments existed, so nobody had watched a merging
binary's throats.  `v2_spiral_d12_p012_L128_lvl3_t050_mouths` is stage 1 of
that arm re-run with the oriented scan on, and this figure is the comparison
it was launched to make.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_mouth_growth

As read, the merging arm's mouths grow from the same initial areal radius
(4.2385, the two arms share their throat) on an e-fold time of 3.64 units
against the fly-by's 4.33, over the same fitted window t = 8-25 -- while one
binary closes from 11.9 to contact and the other misses at 4.8.  But the
coordinate-sphere reading includes the companion's field (the placement
curve; results/merger/analysis/mouth_placement.py).  With it removed
(2026-09-26) the merging arm's mouths read BELOW a freshly placed pair at every
fitted time -- no growth of their own before contact -- and the fly-by's e-fold
time is 3.9: the old verdict "the clock belongs to the throat, not to the
encounter" does not survive.

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

THE FLY-BY STOPS AT ITS TRUST WINDOW, t = 70 (2026-09-26, referee;
results/merger/trust_windows.tsv): its constraint norms grow by orders of
magnitude as its mouths inflate, so nothing of it after t = 70 is read or
drawn (FLYBY_TRUST; the scan is cut on reading, before the split and the fit,
which both lie earlier).  The frame ends at T_MAX = 50, inside that window,
so the cut changes no pixel today; it keeps the figure honest if the frame is
ever widened.  The merger arm is unchanged.

Reads ``horizon_scan.dat`` from both arms under ``campaign/`` and writes
``figures/05_binary_spiral/mouth_growth``.

STYLE: a two-column PRD strip, three panels side by side on one clock
(stacked in one column until 2026-09-26, when the article moved the figure to
its appendix and the user asked for the horizontal layout, "so they take less
space").  Since 2026-09-26 (the user's standing rule, "add legend on top
saying what each line is ... so we dont pollute the figures with the text")
a key ABOVE every panel names each of its lines (``style.legend_top``), the
letter tags sit at the keys' left (``style.tag_keys``) and no text is left
inside a frame: the fit rates are in (c)'s key, and the absence of a MOTS,
the shared start at d = 12 and what the rules mark are the caption's.  GOLD is
this package's horizon instrument and there is no horizon in either arm --
that is itself a result -- so the accent is spent on the fitted exponential
instead, the one quantity the figure exists to compare.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

MERGER = ("05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl3_t050_mouths",
          r"merger, $p=0.12$")
FLYBY = ("06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100",
         r"fly-by, $p=0.45$")
FIT = (8.0, 25.0)        # shared window: both arms' scans are still disjoint
T_MAX = 50.0             # the merger's record; the frame ends here
FLYBY_TRUST = 70.0       # the fly-by's trust window (results/merger/trust_windows.tsv)
R_FLOOR = 3.8            # panel (a)'s floor, under the shared t = 0 radius 4.24
DOTS = (0, (1.2, 1.8))   # a per-mouth scan once its sphere holds both mouths
LONG = (0, (6.5, 2.4))   # the common-centre scan, a different instrument


def _scan(path: pathlib.Path, t_max: float | None = None):
    """t, R_A, R_B, r_scan, separation, and the common-centre reading; with
    t_max, only the rows at t <= t_max (a trust window) are read."""
    h = np.genfromtxt(path, dtype=None, encoding=None, names=True)
    if t_max is not None:
        h = h[h["time"] <= t_max + 1e-9]
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
    # the scan's times are stored as e.g. 7.99999999999987 and 25.0000000000011:
    # without the tolerance the window silently lost both end rows (2026-09-26)
    m = (s["t"] >= lo - 1e-6) & (s["t"] <= hi + 1e-6) & (ex > 0)
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
    # The fly-by only to its trust window: cut on reading, so nothing after
    # t = 70 reaches a panel (its split, t = 35, and the fit lie earlier).
    f = _scan(pack / FLYBY[0] / "horizon_scan.dat", t_max=FLYBY_TRUST)
    im, jf = _split(m), _split(f)
    tau_m, seed_m, ex_m = _tau(m)
    tau_f, seed_f, ex_f = _tau(f)

    style.prd(base=10.0)
    fig, (axA, axB, axC) = plt.subplots(
        1, 3, figsize=(7.05, 2.8), sharex=True, constrained_layout=True)
    # each arm to the frame's end -- and the fly-by to its trust window
    arms = ((m, im, ex_m, style.INK, T_MAX), (f, jf, ex_f, style.CONTEXT, min(T_MAX, FLYBY_TRUST)))

    # ---- (a) each mouth's areal radius, solid while it is a measurement ----
    # Three dash languages, because three different things are drawn: solid is
    # a per-mouth measurement, DOTTED is the same scan after its sphere has
    # swallowed the other mouth, and the long dash is the common-centre scan,
    # which is a different instrument rather than the same one degraded.  The
    # faint rule marks each arm's first overlapping row.
    keyA = []
    for (s, i, _, col, t_end), name in zip(arms, (MERGER[1], FLYBY[1])):
        n = int((s["t"] <= t_end + 1e-9).sum())
        keyA.append((axA.plot(s["t"][:min(i, n)], s["RA"][:min(i, n)], color=col,
                              linewidth=1.4, zorder=3)[0], name))
        axA.plot(s["t"][max(i - 1, 0):n], s["RA"][max(i - 1, 0):n], color=col,
                 linewidth=1.0, linestyle=DOTS, zorder=3)
        axA.axvline(s["t"][i] if i < n else t_end, color=style.FAINT, linewidth=0.7,
                    zorder=1)
    kC = m["tC"] <= T_MAX
    keyA.append((axA.plot(m["tC"][kC], m["RC"][kC], color=style.MUTED, linewidth=1.0,
                          linestyle=LONG, zorder=2)[0], "common-centre scan"))
    keyA.append((Line2D([], [], color=style.MUTED, linewidth=1.0, linestyle=DOTS),
                 "spheres overlap"))
    # a plain segment: a marker-only handle overhangs the key's edge
    keyA.append((Line2D([], [], color=style.FAINT, linewidth=0.9), "rule: first overlap"))
    axA.set_ylabel(r"$R_{\rm areal}$ per mouth")
    axA.set_ylim(R_FLOOR, 10.9)
    style.legend_top(axA, keyA, ncol=2, handlelength=1.8)

    # ---- (b) and meanwhile, what the orbit did ----------------------------
    keyB = []
    for (s, _, _, col, t_end), name in zip(arms, ("merger: to contact",
                                               f"fly-by: misses at {f['sep'].min():.1f}")):
        k = s["t"] <= t_end + 1e-9
        keyB.append((axB.plot(s["t"][k], s["sep"][k], color=col, linewidth=1.4,
                              zorder=3)[0], name))
    axB.set_ylabel(r"separation $d$")
    axB.set_ylim(0.0, 12.9)
    style.legend_top(axB, keyB, ncol=1)

    # ---- (c) the clock itself ---------------------------------------------
    # Each arm's key entry carries its fitted rate; both fits are gold (that is
    # what gold means here, "this is the fit"), keyed once.
    keyC = []
    for (s, _, ex, col, t_end), name, tau in zip(arms, ("merger", "fly-by"), (tau_m, tau_f)):
        k = (s["t"] <= t_end + 1e-9) & (ex > 0)
        keyC.append((axC.plot(s["t"][k], ex[k], color=col, linewidth=1.4, zorder=3)[0],
                     rf"{name}, $\tau={tau:.1f}$"))
    tt = np.array(FIT)
    for seed, tau in ((seed_m, tau_m), (seed_f, tau_f)):
        # Weight 1.9, the same as the seed panel's fits: at 0.9 the fit read
        # as a hairline beside the arm rather than as a measurement on it.
        fit = axC.plot(tt, seed * np.exp(tt / tau), color=style.GOLD,
                       linewidth=1.9, zorder=4)[0]
    keyC.append((fit, rf"fits, $t={FIT[0]:g}$–${FIT[1]:g}$"))
    axC.set_yscale("log")
    axC.set_ylim(3e-5, 2.0)
    axC.set_xlim(0, T_MAX)
    axC.set_ylabel(r"$R_{\rm areal}/R_0 - 1$")
    style.legend_top(axC, keyC, ncol=1)
    for ax in (axA, axB, axC):
        ax.set_xlabel(r"$t$")

    style.tag_keys(fig, (axA, axB, axC), ("(a)", "(b)", "(c)"), row="last")

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
        figure_dir("05_binary_spiral", args.pack_root) / "mouth_growth.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[mouth-growth] wrote {png} (+pdf); label audit: "
          + ("clean" if not hits else f"{len(hits)} hit(s): " + "; ".join(hits)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
