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

STYLE (the seed-branches grammar): single-column PRD frame, two stacked
panels, no boxed key, curves named in place.  Panel (a) divides each arm's
R = 14 waveform by its own seed: linearity is the collapse of four curves
onto one.  Panel (b) is amplitude against seed on log-log with the slope-1
line through the headline arm; the pure quadrupole sits as an open marker
on top of the kicked one, and the control floor is the grey rule below.
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
CONTROL = "single_eps_p1e2_t100"         # kick without quadrupole: the floor
WINDOW = (30.0, 50.0)
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
    fig, (axA, axB) = plt.subplots(
        2, 1, figsize=(3.4, 3.8), constrained_layout=True,
        gridspec_kw=dict(height_ratios=[1.2, 1.0]))

    # ---- (a) each arm divided by its own seed: the collapse ---------------
    looks = {
        0.050: dict(color=style.CONTEXT, linewidth=1.0, linestyle=(0, ())),
        0.010: dict(color=style.INK, linewidth=1.4, linestyle=(0, ())),
        0.005: dict(color=style.DEEP_BLUE, linewidth=1.5, linestyle=(0, (6.5, 2.2))),
    }
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    amps: dict[float, dict[float, float]] = {}
    # Clipped at the rms window's top: past t = 50 the small arm's record is
    # the numerical floor amplified by 1/eps2, and its swings bury the labels.
    for eps, folder in ARMS.items():
        t, ys = _l2m0(seed / folder / "psi4_mode_l2m0.dat")
        keep = (t >= 20) & (t <= 50.0)
        axA.plot(t[keep], ys[R_SHOW][keep] / eps, zorder=3, **looks[eps])
        amps[eps] = {R: _rms(t, ys[R]) for R in RADII}
    tp, yp = _l2m0(seed / PURE / "small_data/psi4_mode_l2m0.dat"
                   if (seed / PURE / "small_data").exists()
                   else seed / PURE / "psi4_mode_l2m0.dat")
    keep = (tp >= 20) & (tp <= 50.0)
    axA.plot(tp[keep], yp[R_SHOW][keep] / 0.01, color=style.DEEP_GREEN,
             linewidth=1.7, linestyle=(0, (1.3, 1.7)), zorder=4)
    amp_pure = {R: _rms(tp, yp[R]) for R in RADII}
    # The control's file has its own columns (R = 14 and 30, five in all),
    # so it is read directly rather than through _l2m0.
    dc = np.loadtxt(seed / CONTROL / "psi4_mode_l2m0.dat")
    floor = _rms(dc[:, 0], dc[:, 1])     # control's R = 14 column is col 1
    axA.set_xlim(20, 51)
    axA.set_ylim(-0.075, 0.098)
    axA.set_ylabel(rf"$\mathrm{{Re}}\,\Psi_4^{{2,0}}(R{{=}}{R_SHOW:g})\,/\,\varepsilon_2$")
    axA.set_xlabel(r"$t$")
    axA.text(0.03, 0.955, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    axA.text(0.98, 0.955, r"$\varepsilon_2 = 0.05$", transform=axA.transAxes,
             ha="right", va="top", fontsize=7, color=style.CONTEXT)
    axA.text(0.98, 0.875, r"$0.01$", transform=axA.transAxes,
             ha="right", va="top", fontsize=7, color=style.INK)
    axA.text(0.98, 0.795, r"$0.005$", transform=axA.transAxes,
             ha="right", va="top", fontsize=7, color=style.DEEP_BLUE)
    axA.text(0.98, 0.715, r"$0.01$, no kick", transform=axA.transAxes,
             ha="right", va="top", fontsize=7, color=style.DEEP_GREEN)

    # ---- (b) amplitude against seed, and the slope-1 line -----------------
    marks = {10.0: "o", 14.0: "s", 18.0: "^"}
    for R in RADII:
        xs = sorted(amps)
        axB.plot(xs, [amps[e][R] for e in xs], marks[R], color=style.INK,
                 markersize=3.4, markerfacecolor="none" if R != R_SHOW else style.INK,
                 linestyle="none", zorder=4)
    e0 = 0.010
    ref = amps[e0][R_SHOW]
    xs = np.array([3.2e-3, 7.5e-2])
    axB.plot(xs, ref * xs / e0, color=style.DEEP_GREEN, linewidth=0.9, zorder=2)
    axB.text(2.6e-2, ref * 2.6e-2 / e0 * 0.60, "slope 1", fontsize=7,
             color=style.DEEP_GREEN, ha="left", va="top")
    axB.plot([0.01], [amp_pure[R_SHOW]], "o", color=style.DEEP_GREEN,
             markerfacecolor="none", markersize=6.0, zorder=5)
    axB.text(0.0112, amp_pure[R_SHOW] * 0.82, "no kick", fontsize=7,
             color=style.DEEP_GREEN, ha="left", va="top")
    axB.axhline(floor, color=style.FAINT, linewidth=0.8,
                linestyle=(0, (4, 2.5)), zorder=1)
    axB.text(3.4e-3, floor * 1.25, "spherical control", fontsize=7,
             color=style.MUTED, va="bottom")
    axB.set_xscale("log"); axB.set_yscale("log")
    axB.set_xlim(3e-3, 9e-2)
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
          + f"   control floor (R=14) {floor:.2e}")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "seed_linearity.png")
    png = style.save(fig, out)
    print(f"[seed-linearity] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
