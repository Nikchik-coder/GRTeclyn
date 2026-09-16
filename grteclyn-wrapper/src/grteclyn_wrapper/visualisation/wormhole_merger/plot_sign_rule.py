#!/usr/bin/env python3
r"""The sign rule: like-oriented throats push apart, a flipped one pulls in.

Three d = 12 pairs released from rest, one knob apart: the like pair
(sigma = +1, a = 2) opens, the flipped pair (sigma = -1) closes, and the
narrow like pair (a = 1, a quarter of the scalar charge) opens far more
slowly.  The scalar charge sets the size as well as the sign: with
Q = |F_phi/F_grav| = (a^2+m^2)/m^2 = 5, pull and push are (Q+1) and (Q-1)
in the same units, so the ratio of the flipped pair's infall to the like
pair's escape is predicted 3/2, time by time -- and the systematic every
single-arm number carries (the coordinate under-read) cancels in that
ratio, because the two arms differ in exactly one parameter.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_sign_rule

Reads ``campaign/03_two_throats/sign_rule_displacement.dat`` (written by
``results/merger/analysis/sign_rule.py`` from the chi_z slice-cache
centroids -- never from throat_track.dat, whose 0.03 quantum is the whole
early displacement) and writes ``figures/03_two_throats/sign_rule``.

STYLE (the seed-branches grammar): single-column PRD frame (style.prd), two
stacked panels on one clock, no boxed key -- every curve named in place,
(a)/(b) tags, monochrome ink with the one burgundy accent reserved for the
prediction line.  Dash = direction (dashed apart, solid together), weight =
charge (a = 1 is the light arm).  The gauge-settling stretch t < 3.5 is a
grey band in the ratio panel: the ratio there is 0/0, not a measurement.
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

GROUP = "03_two_throats"
WINDOW = (3.5, 10.5)
PRED = 1.5   # (Q+1)/(Q-1) at Q = (a^2+m^2)/m^2 = 5


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    pack = pathlib.Path(args.pack_root).expanduser()
    dat = pack / "campaign" / GROUP / "sign_rule_displacement.dat"
    if not dat.exists():
        raise SystemExit(f"no {dat}\nRun results/merger/analysis/sign_rule.py first.")
    tab = np.loadtxt(dat)
    t, like, a1, flip, ratio = (tab[:, i] for i in range(5))
    fin = np.isfinite(ratio)
    print(f"  ratio over t = {WINDOW[0]} .. {WINDOW[1]}: "
          f"{ratio[fin].mean():.3f} +/- {ratio[fin].std(ddof=1):.3f} "
          f"(n = {fin.sum()}, predicted {PRED})")

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(
        2, 1, figsize=(3.4, 3.4), sharex=True, constrained_layout=True,
        gridspec_kw=dict(height_ratios=[1.75, 1.0]))
    xhi = t[-1] * 1.05

    # ---- (a) the separations themselves -----------------------------------
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    # Dash = direction, weight = charge; all ink (the seed-branches rule).
    arms = (
        (like, dict(color=style.INK, linewidth=1.6, linestyle=(0, (4, 2.5))),
         r"$\sigma=+1$", "bottom"),
        (a1, dict(color=style.INK, linewidth=1.0, linestyle=(0, (4, 2.5))),
         r"$a=1$", "bottom"),
        (flip, dict(color=style.INK, linewidth=1.6, linestyle=(0, ())),
         r"$\sigma=-1$", "top"),
    )
    for y, kw, lab, va in arms:
        ok = np.isfinite(y)
        axA.plot(t[ok], y[ok], zorder=3, **kw)
        # Named at its own end, offset off the curve on the empty side.
        off = 0.03 if va == "bottom" else -0.03
        axA.text(t[ok][-1] - 0.015 * xhi, y[ok][-1] + off, lab,
                 fontsize=8, ha="right", va=va)
    axA.set_xlim(0, xhi)
    axA.margins(y=0.16)   # the end names sit outside the curves' own span
    axA.set_ylabel(r"$\delta d$")
    axA.text(0.03, 0.945, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) the ratio against the scalar-charge prediction ---------------
    fin = np.isfinite(ratio)
    axB.axvspan(0, WINDOW[0], color=style.GRID, lw=0, zorder=0)
    axB.plot(t[fin], ratio[fin], ls="none", marker="o", ms=2.8,
             color=style.INK, zorder=4)
    axB.axhline(PRED, color=style.BURGUNDY, linewidth=1.0, zorder=3)
    lo, hi = 1.40, 1.63
    axB.set_ylim(lo, hi)
    axB.set_yticks([1.4, 1.5, 1.6])
    # Centre of the band, under the prediction line, clear of the (b) tag.
    axB.text(0.5 * WINDOW[0], lo + 0.30 * (hi - lo), "gauge\nsettling",
             fontsize=7, color=style.MUTED, ha="center", va="top",
             linespacing=1.2)
    axB.text(0.985 * xhi, PRED - 0.02 * (hi - lo), r"$(Q{+}1)/(Q{-}1)$",
             fontsize=7.5, color=style.BURGUNDY, ha="right", va="top")
    axB.set_xlabel(r"$t$")
    axB.set_ylabel(r"$|\delta d_-|\,/\,\delta d_+$")
    axB.text(0.03, 0.92, "(b)", transform=axB.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "sign_rule.png")
    png = style.save(fig, out)
    print(f"[sign-rule] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
