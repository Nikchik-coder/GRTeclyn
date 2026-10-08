#!/usr/bin/env python3
r"""The force law of two like-signed throats at rest: how the push falls with d.

Four like-signed pairs (sigma = +1, a = 2, m = 1) released from rest,
identical but for the gap d = 12/14/16/18 (article Sec. V B).  Each point is
how far the pair has pushed itself apart by the common time t = 11.5 -- the
growth of the separation, delta d, the same quantity the sign-rule panel
draws against time.  Against it: inverse-square in the coordinate separation,
scaled through the d = 12 rung (grey, dashed), and the offset law
A/(d + delta)^2 fitted on d = 12-16 alone (gold), whose value at d = 18 is a
prediction (drawn dotted past d = 16).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_force_law

WHY THIS PANEL (2026-09-25, a read of Sec. V B: "what are those
numbers, I don't get it -- there should be a figure").  The text quoted the
four displacements and the two predictions with nothing to look at; the
sign-rule panel shows only the d = 12 pairs.  This is the ladder itself.

SWITCHED TO THE MATCHED PAIRS 2026-09-30 (with plot_sign_rule).
Reads ``campaign/03_two_throats/matched_rest_displacement.dat`` (the mode-3
csm like pairs) at t = 11.5: 0.4791 / 0.3716 / 0.2963 / 0.2406, each within
2 % of the superposed ladder (``separation_ladder_2026-09-04.txt``, kept --
the ledger's clmDLadder* still quote it).  The 12-16 fit gives A = 104.0,
delta = 2.74, predicting 0.242 at d = 18 (inverse square: 0.213).
Standalone it writes ``figures/03_two_throats/force_law``; the article draws
it as panel (c) of the pair strip (plot_pair_row).

STYLE: the sign-rule grammar -- ink points, the one gold accent for the model
the data pick, the rejected law in context grey, names on the curves.
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
LADDER = "matched_rest_displacement.dat"
RUNGS = (12.0, 14.0, 16.0, 18.0)
T_LADDER = 11.5
FIT_RUNGS = (12.0, 14.0, 16.0)


def ladder(pack_root=PACK_ROOT) -> tuple[np.ndarray, np.ndarray]:
    """(d, delta d at t = 11.5): the matched like pairs' columns interpolated
    at T_LADDER -- the same arithmetic as the ledger's single_matched_dsep."""
    path = pathlib.Path(pack_root).expanduser() / "campaign" / GROUP / LADDER
    tab = np.loadtxt(path)   # time, like d12/14/16/18, flip d12
    d = np.array(RUNGS)
    dd = np.array([np.interp(T_LADDER, tab[:, 0], tab[:, 1 + i])
                   for i in range(len(RUNGS))])
    return d, dd


def offset_fit(d: np.ndarray, dd: np.ndarray) -> tuple[float, float]:
    """(A, delta) of A/(d + delta)^2, least squares on FIT_RUNGS -- the
    ledger's clmOffsetPrediction arithmetic."""
    from scipy.optimize import curve_fit
    m = np.isin(d, FIT_RUNGS)
    (amp, delta), _ = curve_fit(lambda s, A, dl: A / (s + dl) ** 2, d[m], dd[m],
                                p0=(100.0, 3.0))
    return float(amp), float(delta)


def figure_panel(ax, pack_root=PACK_ROOT, keys: bool = False) -> None:
    """The ladder drawn onto a SUPPLIED axis (style.prd already active; the
    caller owns the letter tag).  ``keys=True`` names the lines in a key above
    the frame (``style.legend_top``) instead of on the curves."""
    d, dd = ladder(pack_root)
    amp, delta = offset_fit(d, dd)
    s = np.linspace(11.6, 18.8, 200)
    inv = dd[d == 12.0][0] * (12.0 / s) ** 2
    (h_inv,) = ax.plot(s, inv, color=style.CONTEXT, linestyle=(0, (4, 2.2)),
                       linewidth=1.0, zorder=2)
    # Solid over the rungs it was fitted on, dotted where it predicts.
    fit = s <= max(FIT_RUNGS)
    (h_fit,) = ax.plot(s[fit], amp / (s[fit] + delta) ** 2, color=style.GOLD,
                       linewidth=1.2, zorder=3)
    ax.plot(s[~fit], amp / (s[~fit] + delta) ** 2, color=style.GOLD, linewidth=1.2,
            linestyle=(0, (1.2, 1.5)), zorder=3)
    (h_dd,) = ax.plot(d, dd, linestyle="none", marker="o", ms=3.4, color=style.INK,
                      zorder=4)
    ax.set_xlim(11, 19)
    ax.set_xticks([12, 14, 16, 18])
    ax.set_ylim(0.18, 0.53)
    ax.set_xlabel(r"$d$")
    ax.set_ylabel(r"$\delta d$ at $t=11.5$")
    if keys:
        style.legend_top(ax, [(h_dd, "measured"), (h_fit, r"$(d{+}\delta)^{-2}$"),
                              (h_inv, r"$d^{-2}$")], ncol=1, borderpad=0.35)
    else:
        # Names on the two laws, where they have parted: gold above the
        # points, the grey rule below them.
        ax.text(15.1, amp / (15.1 + delta) ** 2 + 0.03, r"$(d{+}\delta)^{-2}$",
                fontsize=7.5, color=style.GOLD, ha="left", va="bottom")
        ax.text(16.9, dd[d == 12.0][0] * (12.0 / 16.9) ** 2 - 0.025, r"$d^{-2}$",
                fontsize=7.5, color=style.CONTEXT, ha="right", va="top")
    print(f"[force law] delta d = {dict(zip(d, dd))}; offset fit on {FIT_RUNGS}: "
          f"A = {amp:.1f}, delta = {delta:.2f}, predicts {amp / (18 + delta) ** 2:.3f} "
          f"at d = 18 (inverse square {dd[d == 12.0][0] * (12 / 18) ** 2:.3f}, "
          f"measured {dd[d == 18.0][0]:.4f})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    style.prd(base=10.0)
    fig, ax = plt.subplots(figsize=(3.4, 2.6), constrained_layout=True)
    figure_panel(ax, pack_root=args.pack_root)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "force_law.png")
    style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[force law] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
