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

Both mouths inflate, and a coordinate sphere is only outside the source while
the mouths are smaller than it.  The rule in panel (c) is where the fly-by's
per-mouth areal radius passes the sphere's own radius; past it the inner sphere
is reading the throat, not the wave.  The numbers quoted in the article are
taken at the rule in panel (a) (t = 60 for the fly-by, the end of the record
for the spiral), and their spread over the two spheres is their error bar --
the same convention the Psi4 energies of Sec. VIII use.

Reads ``scalar_modes.dat``, ``psi4_mode_l2_all.dat`` and ``horizon_scan.dat``
under ``campaign/`` and writes ``figures/08_waves/scalar_channel``.

STYLE: single-column PRD frame, three stacked panels on one clock, no boxed
key, every curve named in place.  BURGUNDY is spent on the scalar channel --
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

FLYBY = ("06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100",
         r"fly-by, $p=0.45$", 60.0)
SPIRAL = ("05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl3_t050",
          r"spiral, $p=0.12$", 50.0)
RADII = (14, 30)
T_MAX = 100.0
ELLS = (0, 1, 2)


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
    for key, (rel, label, t_cut) in (("flyby", FLYBY), ("spiral", SPIRAL)):
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

    # ---- (a) the two channels' energies, each arm in units of its own E_GW --
    # Normalising by E_GW at the rule puts two arms of very different loudness
    # on one axis and makes the number the figure exists to report -- how many
    # times the gravitational energy the scalar channel carries, and with which
    # sign -- readable straight off the y axis.
    for key, dash in (("flyby", None), ("spiral", (0, (5.0, 2.0)))):
        a = arms[key]
        tg, Eg = a["gw"][30]
        ts, Ep, _ = a["kin"][30]
        norm = _at(tg, Eg, a["t_cut"])
        kw = dict(linewidth=1.4, zorder=3) if dash is None else dict(
            linewidth=1.1, linestyle=dash, zorder=3)
        k = tg <= a["t_cut"]
        axA.plot(tg[k], Eg[k] / norm, color=style.INK, **kw)
        k = ts <= a["t_cut"]
        axA.plot(ts[k], Ep[k] / norm, color=style.BURGUNDY, **kw)
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    axA.set_ylabel(r"$E(<t)\,/\,E_{\rm GW}$")
    axA.set_ylim(-3.2, 1.7)
    axA.set_xlabel(r"$t$")
    # Every label sits to the right of t = 60, where no curve goes, and at the
    # height of the curve it names -- so nothing needs a leader line and
    # nothing is struck through.
    axA.text(64.0, 1.0, "gravitational", fontsize=7, color=style.INK,
             va="center")
    axA.text(64.0, -2.37, "scalar,\nghost sign", fontsize=7,
             color=style.BURGUNDY, va="center")
    axA.text(97.0, -0.55, "solid fly-by\ndashed spiral", fontsize=6.5,
             color=style.MUTED, va="center", ha="right")
    # The two arms land within 3 % of each other, so they take one label
    # between them rather than two that would overprint.
    axA.text(97.0, 1.45,
             rf"ends at $-{ratio[('flyby', 30)][2]:.1f}$ and "
             rf"$-{ratio[('spiral', 30)][2]:.1f}$",
             fontsize=6.5, color=style.BURGUNDY, va="center", ha="right")

    # ---- (b) which multipole carries it ------------------------------------
    # Two opposite scalar charges have a dipole moment and a black-hole binary
    # does not: l = 1 is the channel general relativity has no analogue for,
    # and it is six orders of magnitude above everything else here.
    a = arms["flyby"]
    tl, per_l = a["per_l"][30]
    for l, col, lw in ((1, style.BURGUNDY, 1.4), (0, style.MUTED, 1.0),
                       (2, style.CONTEXT, 1.0)):
        k = (tl <= a["t_cut"]) & (per_l[l] > 0)
        axB.plot(tl[k], per_l[l][k], color=col, linewidth=lw, zorder=3)
    axB.set_yscale("log")
    axB.set_ylim(1e-13, 1e-1)
    axB.set_ylabel(r"$\sum_m|\dot A_{\ell m}|^2$")
    axB.set_xlabel(r"$t$")
    axB.text(64.0, 3e-3, r"$\ell=1$, dipole", fontsize=7,
             color=style.BURGUNDY, va="center")
    # l = 0 and l = 2 are on top of each other at this scale, so they take one
    # label: the panel's statement is the gap, not which of the two is which.
    axB.text(64.0, 1.5e-9, "$\\ell=0$ and $\\ell=2$,\n$10^{-7}$ of it",
             fontsize=6.5, color=style.MUTED, va="center")
    axB.text(97.0, 4e-13, "fly-by, $R=30$", fontsize=6.5, color=style.MUTED,
             va="center", ha="right")

    # ---- (c) where a coordinate sphere stops being outside the source -------
    for R, col, lw in ((14, style.CONTEXT, 1.0), (30, style.BURGUNDY, 1.4)):
        ts, _, kin = arms["flyby"]["kin"][R]
        k = ts <= T_MAX
        axC.plot(ts[k], np.abs(kin[k]), color=col, linewidth=lw, zorder=3)
        t_x = _mouth_crossing(arms["flyby"]["run"] / "horizon_scan.dat", R)
        if t_x is not None and t_x <= T_MAX:
            # The rule stops below the note's band; rotated text runs UPWARD
            # from its anchor, so it is hung off the bottom of the frame where
            # both curves are already far above it.
            axC.vlines(t_x, 1e-8, 4e0, color=style.FAINT, linewidth=0.7,
                       zorder=1)
            # R = 14's rule stands two units from the blue one, so its label
            # goes on the far side of it rather than into that gap.
            side = 1.8 if R == 14 else -1.8
            axC.text(t_x + side, 1.6e-8, rf"$R={R}$ engulfed", fontsize=6,
                     color=style.MUTED, rotation=90,
                     ha="left" if side > 0 else "right", va="bottom")
    # Clipped below the note's band, like the grey rules: a full-height
    # axvline ran straight through the second line of the note that explains
    # what the rule is for.
    axC.vlines(arms["flyby"]["t_cut"], 1e-8, 4e1, color=style.DEEP_BLUE,
               linewidth=0.7, linestyle=(0, (2.5, 2.0)), zorder=2)
    axC.set_yscale("log")
    axC.set_ylim(1e-8, 3e3)
    axC.set_xlim(0.0, T_MAX)
    axC.set_ylabel(r"$|F_\phi|$")
    axC.set_xlabel(r"$t$")
    # Not "the spheres agree to a factor 3" -- they do not, and an earlier
    # draft said so wrongly.  What agrees is the ratio the figure reports, to
    # 30 %; that belongs on (a) with the ratio itself, and this panel says only
    # where the spheres are still outside the source.  Two lines, so the note
    # ends well short of the R = 14 curve's late climb into the same band.
    axC.text(2.5, 1.6e3, "left of the blue rule\nboth spheres lie outside the mouths",
             fontsize=6, color=style.MUTED, va="top")
    # Under its own curve, not on it: at y = 1.5e-4 the burgundy line ran
    # straight through the label.
    axC.text(44.0, 2.0e-5, r"$R=30$", fontsize=7, color=style.BURGUNDY,
             ha="center", va="top")
    axC.text(30.0, 2.0e-2, r"$R=14$", fontsize=7, color=style.CONTEXT,
             ha="right", va="center")

    for k, ax in enumerate((axA, axB, axC)):
        ax.text(0.0, 1.03, f"({'abc'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir("08_waves", args.pack_root) / "scalar_channel.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    png = style.save(fig, out)
    print(f"[scalar-channel] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
