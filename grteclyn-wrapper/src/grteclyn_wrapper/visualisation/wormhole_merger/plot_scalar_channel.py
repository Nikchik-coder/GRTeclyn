#!/usr/bin/env python3
r"""The second radiation channel: what the ghost scalar carries, and its sign.

Every energy this campaign has quoted so far is a Psi4 number, and Psi4 is
blind to the scalar.  For a system whose entire novelty is negative-energy
matter that is the one channel that cannot be left unmeasured, and until
2026-09-19 it was: the paper carried the caveat ("the scalar channel radiates
its own energy, of the opposite sign, which Psi4 does not see") with no number
behind it.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_scalar_channel

This figure is that number.  Nothing new was run for it: the ``orbit-modes``
consumer profile has written ``scalar_modes.dat`` on the spiral and fly-by arms
since 2026-09-15, on the SAME two extraction spheres (R = 14, 30) as the Python
Psi4 stream, so the two channels can be compared sphere for sphere with no
cross-pipeline normalisation to argue about.

THE SIGN, WHICH IS THE WHOLE POINT

``scalar_modes.dat`` stores the *canonical* kinematic flux,

    flux_kin(R) = -R^2 \oint Pi \partial_r phi dOmega,

signed so that a canonical outgoing wave (Pi ~ -d_r phi) gives a positive
number -- energy leaving.  Gravity here couples to MINUS that stress tensor
(Sec. II.A of the article), so the physical energy flux of this matter is

    F_phi = -flux_kin,

and an outgoing scalar wave removes NEGATIVE energy: the bound system gains.
That is not a bug in the diagnostic, it is what a ghost does, and it is why
this channel cannot be folded into the gravitational-wave budget as a small
correction of known sign.

WHAT THE TWO ESTIMATORS ARE

(i) the kinematic flux above, integrated in time; and (ii) the wave-zone
estimator built from the stored mode amplitudes.  Writing phi = sum_lm
A_lm(t-r) Y_lm / r, the stream stores exactly A_lm = R phi_lm, so the outgoing
power is sum_lm |dA_lm/dt|^2 -- positive definite for a canonical field,
negative for this one.  The two disagree by at most a factor 1.7 here, which
is the honest precision of the statement.

WHERE IT STOPS BEING A MEASUREMENT

Two limits.  (1) THE FLY-BY'S TRUST WINDOW: the p = 0.45 boosted-solve arm's
constraint norms cross the 2.5e-2 criterion at t = 67.6 as its mouths inflate
(results/merger/trust_windows.tsv), and the pack's stated convention there is
that waves are quotable to the matching retarded time u = t - R <= 67.6
(U_GATE).  Every curve is drawn to its sphere's gate: R = 14 to t = 81.6,
R = 30 to t = 97.6 -- which, on this longer-lived solved run, is past the
whole dipole arch: the burst is complete inside the window, and the
full-record ratio is the article's headline number.  (2) A coordinate sphere
is only outside the source while the mouths are smaller than it, and the
solved runs carry no live horizon scan to read the mouths' size from.  The
fingerprint is in the record itself: the R = 14 flux climbs an order of
magnitude from t ~ 73 with no counterpart at R = 30 one light-crossing later
(1.4e-2 at t = 81 against 1.5e-4 at t = 95), so that climb is the inflating
mouths' near field, not radiation, and the inner sphere is quoted only to the
t = 60 mid-burst cut (the blue rule in panel (c)).

Reads ``scalar_modes.dat``, ``psi4_mode_l2_all.dat`` and ``horizon_scan.dat``
under ``campaign/`` and writes ``figures/08_waves/scalar_channel``.

STYLE: single-column PRD frame, three stacked panels on one clock, no boxed
key, every curve named in place.  GOLD is spent on the scalar channel --
the quantity the page exists to introduce -- and the gravitational channel,
already the subject of two figures, is drawn in INK.
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

FLYBY = ("06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm",
         r"fly-by, $p=0.45$", 60.0)
RADII = (14, 30)
T_MAX = 100.0
ELLS = (0, 1, 2)
# The fly-by's trust window (docstring, WHERE IT STOPS): the pack's stated
# convention for this run is retarded, u = t - R <= U_GATE on every sphere.
U_GATE = 67.6


def _cols(path: pathlib.Path):
    head = path.open().readline().split()[1:]
    return head, np.loadtxt(path, comments="#")


def _gw_flux(path: pathlib.Path, radius: int):
    """dE/dt = (1/16pi) sum_m |int r Psi4_lm dt'|^2 on one sphere, l = 2."""
    head, d = _cols(path)
    t = d[:, 0]
    tot = np.zeros_like(t)
    for m in (-2, -1, 0, 1, 2):
        i = head.index(f"Re_m{m}(R={radius})")
        psi = d[:, i] + 1j * d[:, i + 1]
        tot += np.abs(np.cumsum(psi * np.gradient(t))) ** 2
    return t, tot / (16.0 * np.pi)


def _scalar(path: pathlib.Path, radius: int):
    """Ghost-signed kinematic flux, and the wave-zone power per multipole."""
    head, d = _cols(path)
    t = d[:, 0]
    kin = -d[:, head.index(f"R{radius}_scalar_flux_kin")]
    per_l = {}
    for l in ELLS:
        s = np.zeros_like(t)
        for m in range(-l, l + 1):
            i = head.index(f"R{radius}_phi_l{l}_m{m}_re")
            s += np.abs(np.gradient(d[:, i] + 1j * d[:, i + 1], t)) ** 2
        per_l[l] = s
    return t, kin, per_l


def _cum(t, f):
    return np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(t))])


def _at(t, y, t0):
    return float(np.interp(t0, t, y))


def _mouth_crossing(path: pathlib.Path, radius: float) -> float | None:
    """When the per-mouth areal radius first passes a sphere's own radius."""
    h = np.genfromtxt(path, dtype=None, encoding=None, names=True)
    a = h[h["centre"] == "A"]
    over = a["R_min"] >= radius
    if not over.any():
        return None
    k = int(np.argmax(over))
    return float(a["time"][k]) if k == 0 else float(
        np.interp(radius, a["R_min"][k - 1:k + 1], a["time"][k - 1:k + 1]))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser() / "campaign"

    arms = {}
    for key, (rel, label, t_cut) in (("flyby", FLYBY),):
        run = pack / rel
        a = dict(label=label, t_cut=t_cut, gw={}, kin={}, per_l={}, run=run)
        for R in RADII:
            tg, fg = _gw_flux(run / "psi4_mode_l2_all.dat", R)
            ts, kin, per_l = _scalar(run / "scalar_modes.dat", R)
            a["gw"][R] = (tg, _cum(tg, fg))
            a["kin"][R] = (ts, _cum(ts, kin), kin)
            a["per_l"][R] = (ts, per_l)
        arms[key] = a

    # ---- the numbers, printed for the caption and the article ---------------
    ratio = {}
    for key, a in arms.items():
        for R in RADII:
            tg, Eg = a["gw"][R]
            ts, Ep, _ = a["kin"][R]
            g, p = _at(tg, Eg, a["t_cut"]), _at(ts, Ep, a["t_cut"])
            ratio[(key, R)] = (g, p, abs(p) / g)
            tl, per_l = a["per_l"][R]
            k = tl <= a["t_cut"]
            E = {l: np.trapezoid(per_l[l][k], tl[k]) for l in ELLS}
            print(f"[scalar-channel] {key:6s} R={R:2d} to t={a['t_cut']:.0f}: "
                  f"E_GW = {g:+.4e}, E_phi = {p:+.4e}, |E_phi|/E_GW = {abs(p) / g:.2f}; "
                  f"wave-zone sum|dA/dt|^2 = {sum(E.values()):.4e} "
                  f"(l=1 share {100 * E[1] / sum(E.values()):.4f} %, "
                  f"l1/l0 = {E[1] / E[0]:.1e}, l1/l2 = {E[1] / E[2]:.1e})")

    style.prd(base=10.0)
    # Full-page width (figure* at 0.80\textwidth): three panels ACROSS on one
    # clock.  Every arm's record ends by t = 60, so in (a) and (b) the right
    # third of the frame is free and every label lives there, clear of a curve.
    fig, (axA, axB, axC) = plt.subplots(
        1, 3, figsize=(7.05, 2.55), sharex=True, constrained_layout=True)

    # ---- (a) the fly-by's two channels through R = 30 ------------------------
    # One arm only.  The spiral's scalar record (level 3) ends at t = 50,
    # before its burst reaches R = 30, so its "ratio" divides by a pre-burst
    # E_GW and is not a measurement (dropped 2026-09-23).  The ratio is
    # cut-dependent -- the gravitational burst peaks at R = 30 near t = 65, so
    # a t = 60 cut still misses most of it -- and the panel shows that: both
    # curves run to t = 80, where the fly-by's trust window closes on this
    # sphere (u = t - R = 50; past it both integrals grow without bound as
    # the mouths inflate), with the ratio printed at each cut the article
    # quotes.
    a = arms["flyby"]
    tg, Eg = a["gw"][30]
    ts, Ep, _ = a["kin"][30]
    T_A = U_GATE + 30  # the R = 30 gate: the whole dipole arch is inside it
    norm = _at(tg, Eg, T_A)
    k = tg <= T_A
    axA.plot(tg[k], Eg[k] / norm, color=style.INK, linewidth=1.4, zorder=3)
    k = ts <= T_A
    axA.plot(ts[k], Ep[k] / norm, color=style.GOLD, linewidth=1.4, zorder=3)
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    pE = _at(ts, Ep, T_A) / norm
    lo = min(-1.2, pE - 0.35)
    axA.set_ylim(lo, 1.62)
    for tc in (60.0, 70.0, 80.0, T_A):
        g, pp = _at(tg, Eg, tc), _at(ts, Ep, tc)
        r = abs(pp) / g
        print(f"[scalar-channel] flyby R=30 cut t={tc:.0f}: |E_phi|/E_GW = {r:.2f}")
        # a short tick at the cut, the ratio hung on top of it
        axA.vlines(tc, 1.24, 1.34, color=style.MUTED, linewidth=0.7, zorder=1)
        axA.text(min(tc, 95.0), 1.38, f"{r:.1f}", fontsize=6.5,
                 color=style.GOLD, ha="center", va="bottom")
    axA.text(45.5, 1.45, r"$|E_\phi|/E_{\rm GW}$ at $t=$", fontsize=6.3,
             color=style.MUTED, ha="right", va="center")
    axA.set_ylabel(r"$E(<t)\,/\,E_{\rm GW}(t{=}97.6)$")
    axA.set_xlabel(r"$t$")
    # Each name sits just left of its own curve's end: above the rising ink,
    # below the falling gold, clear of the frame.
    axA.text(T_A - 1.0, 1.04, "gravitational", fontsize=7, color=style.INK,
             ha="right", va="bottom")
    axA.text(T_A - 1.0, pE - 0.10, "scalar, ghost sign", fontsize=7,
             color=style.GOLD, ha="right", va="top")
    axA.text(3.0, 0.72, "fly-by, $R=30$", fontsize=6.5, color=style.MUTED,
             ha="left", va="center")

    # ---- (b) which multipole carries it ------------------------------------
    # Two opposite scalar charges have a dipole moment and a black-hole binary
    # does not: l = 1 is the channel general relativity has no analogue for,
    # and it is six orders of magnitude above everything else here.
    a = arms["flyby"]
    tl, per_l = a["per_l"][30]
    for l, col, lw in ((1, style.GOLD, 1.4), (0, style.MUTED, 1.0),
                       (2, style.CONTEXT, 1.0)):
        k = (tl <= U_GATE + 30) & (per_l[l] > 0)
        axB.plot(tl[k], per_l[l][k], color=col, linewidth=lw, zorder=3)
    axB.set_yscale("log")
    axB.set_ylim(1e-13, 1e-1)
    axB.set_ylabel(r"$\sum_m|\dot A_{\ell m}|^2$")
    axB.set_xlabel(r"$t$")
    axB.text(30.0, 2.5e-2, r"$\ell=1$, dipole", fontsize=7,
             color=style.GOLD, va="center")
    # l = 0 and l = 2 are on top of each other at this scale, so they take one
    # label: the panel's statement is the gap, not which of the two is which.
    axB.text(50.0, 1.2e-7, "$\\ell=0$ and $\\ell=2$,\n$10^{6}\\times$ down",
             fontsize=6.5, color=style.MUTED, ha="center", va="bottom")
    axB.text(97.0, 4e-13, "fly-by, $R=30$", fontsize=6.5, color=style.MUTED,
             va="center", ha="right")

    # ---- (c) where a coordinate sphere stops being outside the source -------
    # Each sphere to its retarded gate, t - R <= U_GATE (t = 81.6 at R = 14,
    # 97.6 at R = 30).  The solved runs carry no live horizon scan, so the
    # near-zone limit is read off the record itself (docstring, WHERE IT
    # STOPS): the R = 14 flux climbs an order of magnitude from t ~ 73 with no
    # counterpart at R = 30 one light-crossing later -- the inflating mouths'
    # near field -- so R = 14 is solid only to the t = 60 mid-burst cut (the
    # blue rule) and dashed, carrying no claim, from there to its gate.
    ts, _, kin = arms["flyby"]["kin"][30]
    k = ts <= U_GATE + 30 + 1e-9
    axC.plot(ts[k], np.abs(kin[k]), color=style.GOLD, linewidth=1.4, zorder=3)
    ts, _, kin = arms["flyby"]["kin"][14]
    k = ts <= arms["flyby"]["t_cut"] + 1e-9
    axC.plot(ts[k], np.abs(kin[k]), color=style.CONTEXT, linewidth=1.0, zorder=3)
    k = (ts >= arms["flyby"]["t_cut"] - 1e-9) & (ts <= U_GATE + 14 + 1e-9)
    axC.plot(ts[k], np.abs(kin[k]), color=style.CONTEXT, linewidth=0.9,
             ls=(0, (2.0, 1.8)), alpha=0.75, zorder=2)
    print(f"[scalar-channel] flyby (c): R=30 drawn to t = {U_GATE + 30:.1f}, "
          f"R=14 solid to t = {arms['flyby']['t_cut']:.0f}, dashed to "
          f"t = {U_GATE + 14:.1f} (near zone: mouths inflating)")
    axC.vlines(arms["flyby"]["t_cut"], 1e-8, 1.2e-2, color=style.DEEP_BLUE,
               linewidth=0.7, linestyle=(0, (2.5, 2.0)), zorder=2)
    axC.set_yscale("log")
    axC.set_ylim(1e-8, 3e0)   # the data stay below 1e-2; the top holds the note
    axC.set_xlim(0.0, T_MAX)
    axC.set_ylabel(r"$|F_\phi|$")
    axC.set_xlabel(r"$t$")
    axC.text(2.5, 1.6e0, "left of the blue rule the inner sphere\nis still clear of the inflating mouths",
             fontsize=6, color=style.MUTED, va="top")
    axC.text(20.0, 1.0e-6, r"$R=30$", fontsize=7, color=style.GOLD,
             ha="center", va="top")
    axC.text(30.0, 2.0e-2, r"$R=14$", fontsize=7, color=style.CONTEXT,
             ha="right", va="center")
    axC.text(98.0, 1.8e-2, "$R=14$, near zone:\nmouths inflating",
             fontsize=6, color=style.MUTED, ha="right", va="bottom")

    for k, ax in enumerate((axA, axB, axC)):
        ax.text(0.0, 1.03, f"({'abc'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    style.label_audit(fig)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir("08_waves", args.pack_root) / "scalar_channel.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[label audit] {'clean' if not hits else hits}")
    print(f"[scalar-channel] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
