#!/usr/bin/env python3
r"""One throat's wave is linear in its deformation -- across a decade.

Queue 2e's gate 3, closed 2026-09-19: the (2,0) wave from a single kicked
throat carrying an l = 2 seed scales with the seed.  Three amplitudes exist
(0.005 / 0.01 / 0.05, the first and last launched as the halved and the
five-fold arms), plus the arm that settles WHERE the wave comes from -- the
pure quadrupole, seed 0.01 with the radial kick set to zero, whose wave
equals the kicked arm's to 2-3 % at every sphere while its throat still
collapses (MOTS at t = 33, on the level whose own truncation seed inflates
the round throat).  The spherical control (kick without quadrupole) is the
floor all of them are read against.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_seed_linearity

Reads each arm's consumer ``psi4_mode_l2m0.dat`` (the SAME instrument on
every arm; the in-code Weyl4 streams exist only on the 2026-09-18 arms)
from ``campaign/01_single_throat/seed/`` and writes
``figures/01_single_throat/seed_linearity``.

STYLE (the seed-branches grammar): a two-column PRD strip, two panels side
by side (stacked in one column until 2026-09-26, when the article moved the
figure to its appendix and the user asked for the horizontal layout, "so they
take less space"), no boxed key, curves named in place.  Panel (a) divides each arm's
R = 14 waveform by its own seed: linearity is the collapse of four curves
onto one.  Panel (b) is amplitude against seed on log-log with the slope-1
line through the headline arm; the pure quadrupole sits as an open marker
on top of the kicked one, and the control floor is the grey rule below.

THE FLOOR AND THE DECADE (2026-09-24, first-author review: "why not 0.001?
where does 5 come from?").  The floor rule was the LEVEL-3 spherical control
`single_eps_p1e2_t100`, read against level-4 arms.  A level-4 control exists:
`single_eps_p1e2_q1e2_ml4_scalar_t100` ran on a binary that ignores the
quadrupole key (runs_index.tsv: seed NOT APPLIED), so it is the +0.01 kick at
level 4 with no quadrupole -- and runs are deterministic (identical input
gives bit-identical r Psi4, checked on the pairs that exist), so it is the
exact floor of these arms.  Its rms over the window is 6.75e-5 at R = 14,
against 6.79e-5 for the level-3 control: the rule does not move, but it now
belongs to the arms' own level.  Panel (b)'s axis spans the decade the
reviewer asked about, 1e-3 to 1e-1, with the slope-one line carried across it
as a reference (no arm exists at either end): it meets the floor at
eps2 ~ 2e-3, which is where 1e-3 would sit, raw, at half the floor.  The
numbers behind this, and the floor-subtracted linearity, are in
``grteclyn-wrapper/scripts/analysis/merger_feedback/waves_seed_ladder.py``.
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

GROUP = "01_single_throat"
SEED_DIR = "seed"
# arm -> (eps2, pack folder).  The 0.01 arm is leg 2 of the headline pair,
# level 4 from the t = 25 checkpoint, record t = 25-51; the window below
# sits inside every record.
ARMS = {
    0.005: "single_eps_p1e2_q5e3_ml4_t100",
    0.010: "single_eps_p1e2_q1e2_ml4_t100_r02500",
    0.050: "single_eps_p1e2_q5e2_ml4_t100",
}
PURE = "single_pureq_q1e2_ml4_t100"      # eps2 = 0.01, radial kick 0
# Kick without quadrupole, LEVEL 4 like the arms: the floor.  (The seed key
# is in its params but its binary did not read it -- see the docstring.)
# Until 2026-09-24 this was the level-3 `single_eps_p1e2_t100`.
CONTROL = "single_eps_p1e2_q1e2_ml4_scalar_t100"
WINDOW = (30.0, 50.0)
DECADE = (1e-3, 1e-1)                    # the span panel (b) draws
RADII = (10.0, 14.0, 18.0)               # the consumer's columns, every arm
R_SHOW = 14.0


def _l2m0(path: pathlib.Path):
    d = np.loadtxt(path)
    return d[:, 0], {R: d[:, 1 + 2 * i] for i, R in enumerate(RADII)}


def _rms(t, y, lo=WINDOW[0], hi=WINDOW[1]):
    m = (t >= lo) & (t <= hi)
    return float(np.sqrt(np.mean(y[m] ** 2)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    seed = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP / SEED_DIR

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.05, 2.45), constrained_layout=True)

    # ---- (a) each arm divided by its own seed: the collapse ---------------
    looks = {
        0.050: dict(color=style.CONTEXT, linewidth=1.0, linestyle=(0, ())),
        0.010: dict(color=style.INK, linewidth=1.4, linestyle=(0, ())),
        0.005: dict(color=style.DEEP_BLUE, linewidth=1.5, linestyle=(0, (6.5, 2.2))),
    }
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    amps: dict[float, dict[float, float]] = {}
    ends = []                                # (y at t = 50, name, colour)
    # Clipped at the rms window's top: past t = 50 the small arm's record is
    # the numerical floor amplified by 1/eps2, and its swings bury the labels.
    for eps, folder in ARMS.items():
        t, ys = _l2m0(seed / folder / "psi4_mode_l2m0.dat")
        keep = (t >= 20) & (t <= 50.0)
        axA.plot(t[keep], ys[R_SHOW][keep] / eps, zorder=3, **looks[eps])
        amps[eps] = {R: _rms(t, ys[R]) for R in RADII}
        ends.append((ys[R_SHOW][keep][-1] / eps, rf"${eps:g}$", looks[eps]["color"]))
    tp, yp = _l2m0(seed / PURE / "small_data/psi4_mode_l2m0.dat"
                   if (seed / PURE / "small_data").exists()
                   else seed / PURE / "psi4_mode_l2m0.dat")
    keep = (tp >= 20) & (tp <= 50.0)
    axA.plot(tp[keep], yp[R_SHOW][keep] / 0.01, color=style.GOLD,
             linewidth=1.7, linestyle=(0, (1.3, 1.7)), zorder=4)
    ends.append((yp[R_SHOW][keep][-1] / 0.01, "no kick", style.GOLD))
    amp_pure = {R: _rms(tp, yp[R]) for R in RADII}
    # The level-4 control carries the arms' own columns (R = 10 / 14 / 18).
    tc, yc = _l2m0(seed / CONTROL / "psi4_mode_l2m0.dat")
    floors = {R: _rms(tc, yc[R]) for R in RADII}
    floor = floors[R_SHOW]
    axA.set_xlim(20, 57.5)
    axA.set_ylim(-0.075, 0.098)
    # Each arm named at its own end (t = 50), nudged apart where two ends
    # crowd and off the zero rule -- a corner key named nothing it touched,
    # and the 0.005 arm's late swing ran through it (label audit 2026-09-24).
    gap, zero_band, placed = 0.0115, 0.0095, []
    for y, name, col in sorted(ends, reverse=True):        # top down
        if abs(y) < zero_band:
            y = np.copysign(zero_band, y)
        if placed and y > placed[-1][0] - gap:
            y = placed[-1][0] - gap
            if abs(y) < zero_band:
                y = -zero_band
        placed.append((y, name, col))
    for y, name, col in placed:
        axA.text(50.7, y, name, fontsize=7, color=col, ha="left", va="center")
    axA.set_ylabel(rf"$\mathrm{{Re}}\,\Psi_4^{{2,0}}(R{{=}}{R_SHOW:g})\,/\,\varepsilon_2$")
    axA.set_xlabel(r"$t$")
    axA.text(0.03, 0.955, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) amplitude against seed, and the slope-1 line -----------------
    marks = {10.0: "o", 14.0: "s", 18.0: "^"}
    for R in RADII:
        xs = sorted(amps)
        axB.plot(xs, [amps[e][R] for e in xs], marks[R], color=style.INK,
                 markersize=3.4, markerfacecolor="none" if R != R_SHOW else style.INK,
                 linestyle="none", zorder=4)
    e0 = 0.010
    ref = amps[e0][R_SHOW]
    # The slope-one reference across the whole decade: measured between
    # 0.005 and 0.05 only, a reference line beyond them.
    xs = np.array(DECADE)
    axB.plot(xs, ref * xs / e0, color=style.GOLD, linewidth=0.9, zorder=2)
    axB.text(2.6e-2, ref * 2.6e-2 / e0 * 0.60, "slope 1", fontsize=7,
             color=style.GOLD, ha="left", va="top")
    axB.plot([0.01], [amp_pure[R_SHOW]], "o", color=style.GOLD,
             markerfacecolor="none", markersize=6.0, zorder=5)
    axB.text(0.0112, amp_pure[R_SHOW] * 0.82, "no kick", fontsize=7,
             color=style.GOLD, ha="left", va="top")
    axB.axhline(floor, color=style.FAINT, linewidth=0.8,
                linestyle=(0, (4, 2.5)), zorder=1)
    # Named on its right half, where the slope-one line is far above it.
    axB.text(1.05e-2, floor * 1.25, "spherical control", fontsize=7,
             color=style.MUTED, va="bottom")
    e_cross = e0 * floor / ref              # where the line meets the floor
    axB.set_xscale("log"); axB.set_yscale("log")
    axB.set_xlim(0.8 * DECADE[0], 1.25 * DECADE[1])
    axB.set_ylim(0.45 * ref * DECADE[0] / e0, 2.2 * ref * DECADE[1] / e0)
    axB.set_xlabel(r"$\varepsilon_2$")
    axB.set_ylabel(rf"rms $\mathrm{{Re}}\,\Psi_4^{{2,0}}$, $t={WINDOW[0]:g}$--${WINDOW[1]:g}$")
    axB.text(0.03, 0.94, "(b)", transform=axB.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    axB.text(0.97, 0.06, r"$R=10\ (\circ)\quad 14\ (\blacksquare)\quad 18\ (\triangle)$",
             transform=axB.transAxes, ha="right", va="bottom", fontsize=6.5,
             color=style.MUTED)

    for eps in sorted(amps):
        r = {R: amps[eps][R] / (amps[e0][R] * eps / e0) for R in RADII}
        print(f"[seed-linearity] eps2 = {eps:5.3f}: amp/(linear pred) = "
              + "  ".join(f"{r[R]:.2f}" for R in RADII))
    print(f"[seed-linearity] pure/kicked at 0.01: "
          + "  ".join(f"{amp_pure[R]/amps[e0][R]:.3f}" for R in RADII)
          + "   level-4 control floor " + "  ".join(f"R{R:g} {floors[R]:.2e}" for R in RADII)
          + f";  slope-one line meets the R = {R_SHOW:g} floor at eps2 = {e_cross:.2e}")

    hits = style.label_audit(fig)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "seed_linearity.png")
    png = style.save(fig, out)
    print(f"[seed-linearity] wrote {png} (+pdf); label audit: "
          + ("clean" if not hits else f"{len(hits)} hit(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
