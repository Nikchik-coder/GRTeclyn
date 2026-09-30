#!/usr/bin/env python3
r"""The sign rule: like-oriented throats push apart, a flipped one pulls in.

Two far-side-matched d = 12 pairs released from rest, one sign apart: the
like pair (sigma = +1, a = 2) opens, the flipped pair (sigma = -1) closes.
The scalar charge sets the size as well as the sign: with
Q = |F_phi/F_grav| = (a^2+m^2)/m^2 = 5, pull and push are (Q+1) and (Q-1)
in the same units, so the ratio of the flipped pair's infall to the like
pair's escape is predicted 3/2, time by time -- and the systematic every
single-arm number carries (the coordinate under-read) cancels in that
ratio, because the two arms differ in exactly one parameter.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_sign_rule

Reads ``campaign/03_two_throats/matched_rest_displacement.dat`` (the mode-3
csm rest pairs, written by the sign_rule.py measurement from the chi_z
slice-cache centroids -- never from throat_track.dat, whose 0.03 quantum is
the whole early displacement) and writes ``figures/03_two_throats/sign_rule``.

SWITCHED TO THE MATCHED PAIRS 2026-09-30 (the user: "we have new csm data
... and the attraction changes").  Before, the superposed d = 12 trio of
``sign_rule_displacement.dat``, whose ratio was 1.518 +/- 0.021; matched,
1.462 +/- 0.022 over the same t = 3.5..10.5 window (the ledger's
clmMatchedSignRatio, extract_single.single_matched_sign_rule -- this module
recomputes the same numbers from the same 4-decimal columns).  The narrow
a = 1 arm left the panel with the switch: it has no matched twin, and the
width ladder lives in Sec. V B's text (clmALadder*).  The matched records
run to t = 15, past the window: there the displacements are no longer small
(the closing pair has eaten a tenth of its gap and accelerates), so the
ratio climbs off the fixed-potential prediction -- drawn open-faced, kept
out of the quoted mean.

STYLE (the seed-branches grammar): single-column PRD frame (style.prd), two
stacked panels on one clock, no boxed key -- every curve named in place,
(a)/(b) tags, monochrome ink with the one gold accent reserved for the
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
TABLE = "matched_rest_displacement.dat"   # time  like d12/14/16/18  flip d12
WINDOW = (3.5, 10.5)
PRED = 1.5   # (Q+1)/(Q-1) at Q = (a^2+m^2)/m^2 = 5


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(
        2, 1, figsize=(3.4, 3.4), sharex=True, constrained_layout=True,
        gridspec_kw=dict(height_ratios=[1.75, 1.0]))
    figure_panels(axA, axB, pack_root=args.pack_root, stacked=True)
    axA.text(0.03, 0.945, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    axB.text(0.03, 0.92, "(b)", transform=axB.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "sign_rule.png")
    png = style.save(fig, out)
    print(f"[sign-rule] wrote {png} (+pdf)")
    return 0


def figure_panels(axA, axB, pack_root=PACK_ROOT, stacked: bool = True) -> None:
    """The two sign-rule panels drawn onto SUPPLIED axes.

    ``stacked=True`` is `main`'s own single-column canvas (shared clock, so
    only the lower panel is labelled $t$); ``stacked=False`` is the side-by-
    side placement of the article's pair strip (plot_pair_row, 2026-09-18),
    where each panel needs its own $t$ label.  ``style.prd`` must already be
    active, and no letter tags are drawn: the caller owns the lettering.
    """
    pack = pathlib.Path(pack_root).expanduser()
    dat = pack / "campaign" / GROUP / TABLE
    if not dat.exists():
        raise SystemExit(f"no {dat}\nRun the matched close-out reduction first.")
    tab = np.loadtxt(dat)
    t, like, flip = tab[:, 0], tab[:, 1], tab[:, 5]
    win = (t >= WINDOW[0]) & (t <= WINDOW[1])
    ratio = np.full_like(t, np.nan)
    ratio[win] = -flip[win] / like[win]
    late = np.isfinite(flip) & (t > WINDOW[1])
    fin = np.isfinite(ratio)
    print(f"  ratio over t = {WINDOW[0]} .. {WINDOW[1]}: "
          f"{ratio[fin].mean():.3f} +/- {ratio[fin].std(ddof=1):.3f} "
          f"(n = {fin.sum()}, predicted {PRED}); past the window it climbs to "
          f"{(-flip[late] / like[late])[-1]:.3f} at t = {t[late][-1]:g}")
    # A little air past the last sample, enough for the end names; the wide
    # 1.35 margin of the superposed trio held the a = 1 arm's name, which
    # left with the arm (no matched twin).
    xhi = t[np.isfinite(like)][-1] * 1.08

    # ---- (a) the separations themselves -----------------------------------
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    # Dash = direction; all ink (the seed-branches rule).
    arms = (
        (like, dict(color=style.INK, linewidth=1.6, linestyle=(0, (4, 2.5))),
         r"$\sigma=+1$", "above"),
        (flip, dict(color=style.INK, linewidth=1.6, linestyle=(0, ())),
         r"$\sigma=-1$", "below"),
    )
    for y, kw, lab, where in arms:
        ok = np.isfinite(y)
        axA.plot(t[ok], y[ok], zorder=3, **kw)
        x_end, y_end = t[ok][-1], y[ok][-1]
        axA.text(x_end - 0.015 * xhi, y_end + (0.05 if where == "above" else -0.05),
                 lab, fontsize=8, ha="right",
                 va="bottom" if where == "above" else "top")
    axA.set_xlim(0, xhi)
    axA.margins(y=0.16)   # the end names sit outside the curves' own span
    axA.set_ylabel(r"$\delta d$")
    if not stacked:
        axA.set_xlabel(r"$t$")

    # ---- (b) the ratio against the scalar-charge prediction ---------------
    axB.axvspan(0, WINDOW[0], color=style.GRID, lw=0, zorder=0)
    axB.plot(t[fin], ratio[fin], ls="none", marker="o", ms=2.8,
             color=style.INK, zorder=4)
    # Past the window the displacements are no longer small -- the closing
    # pair has eaten ~10 % of its gap and accelerates -- so the ratio climbs
    # off the fixed-potential prediction.  Open-faced: real readings, outside
    # the quoted mean (the caption says why).
    axB.plot(t[late], -flip[late] / like[late], ls="none", marker="o", ms=2.8,
             mfc=style.GROUND, mec=style.CONTEXT, mew=0.9, zorder=3)
    axB.axhline(PRED, color=style.GOLD, linewidth=1.0, zorder=3)
    lo, hi = 1.40, 1.63
    axB.set_ylim(lo, hi)
    axB.set_yticks([1.4, 1.5, 1.6])
    # Centre of the band, under the prediction line, clear of the (b) tag.
    axB.text(0.5 * WINDOW[0], lo + 0.30 * (hi - lo), "gauge\nsettling",
             fontsize=7, color=style.MUTED, ha="center", va="top",
             linespacing=1.2)
    if stacked:
        axB.text(0.985 * xhi, PRED - 0.02 * (hi - lo), r"$(Q{+}1)/(Q{-}1)$",
                 fontsize=7.5, color=style.GOLD, ha="right", va="top")
    else:
        # A quarter-page panel has no room for the algebra beside the points:
        # the rule is named by its value, over the settling band where no
        # measurement lives, and the caption carries (Q+1)/(Q-1).
        axB.text(0.15, PRED + 0.03 * (hi - lo), r"$3/2$", fontsize=7.5,
                 color=style.GOLD, ha="left", va="bottom")
    # Side by side the two panels are not on a shared axis the way the
    # stacked pair is, and two different clocks under one figure would be a
    # lie: (b) takes (a)'s limits explicitly.
    axB.set_xlim(0, xhi)
    axB.set_xlabel(r"$t$")
    axB.set_ylabel(r"$|\delta d_-|\,/\,\delta d_+$")


if __name__ == "__main__":
    raise SystemExit(main())
