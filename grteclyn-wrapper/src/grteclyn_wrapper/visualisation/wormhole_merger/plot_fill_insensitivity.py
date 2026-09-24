#!/usr/bin/env python3
r"""The fill is not in the physics: move the window, the waveform stays.

The p = 0.12 freeze arm holds the merged core still inside radius_full from
t = 57 (`CoreFreezeFill.hpp`), and the module demands two validations before
its waveform is quotable: the M6 overlap against the unfrozen twin on the
shared t = 57-60.44 window (passed 2026-09-16), and radius insensitivity --
a second arm with ONLY the fill window moved, 1.40/1.90 -> 1.25/1.75, from
the same t = 57 checkpoint and the same binary (md5 32e12cc4).  That twin
ran 2026-09-18/19 (`v2_spiral_d12_p012_L128_lvl5_t100_freeze2_r05700`, the
second machine's card) and this figure is the verdict: over the whole
shared record t = 57-100 the (2,2) waveform moves by at most 0.385 % of its
peak at the nearest sphere and 0.013 % at the farthest, overlap 0.999999+.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_fill_insensitivity

Reads both arms' in-code ``Weyl4_mode_22.dat`` (dt = 0.01, spheres
20/28/36/44) from ``campaign/05_binary_spiral/p012_paper/`` and writes
``figures/05_binary_spiral/p012_paper/fill_insensitivity``.

STYLE (the seed-branches grammar): single-column PRD frame, two stacked
panels on one clock, no boxed key, every curve named in place.  Panel (a)
overlays the two arms at R = 20 -- ink solid under gold dots, so
agreement reads as one bicolour curve.  Panel (b) is the per-sphere
difference against the few-percent gate, on a log axis, grey ramp inner to
outer.  The caveat that travels with the arm travels with the figure: this
certifies the fill's inertness, not a remnant ringdown -- the late record
stays a transported burst.
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

GROUP = "05_binary_spiral"
ARM_A = "p012_paper/v2_spiral_d12_p012_L128_lvl5_t100_freeze_r05700"
ARM_B = "p012_paper/v2_spiral_d12_p012_L128_lvl5_t100_freeze2_r05700"
RADII = (20.0, 28.0, 36.0, 44.0)
T_ENGAGE = 57.0
SKIN = 1.90          # core_fill_radius_start of ARM_A: the fill's outer edge
GATE = 1e-2          # "a few %" -- the module's own acceptance wording
RAMP = (style.INK, style.MUTED, style.CONTEXT, style.FAINT)


def _modes(path: pathlib.Path):
    d = np.loadtxt(path)
    t = d[:, 0]
    ys = {R: d[:, 1 + 2 * i] + 1j * d[:, 2 + 2 * i] for i, R in enumerate(RADII)}
    return t, ys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP

    ta, ya = _modes(pack / ARM_A / "Weyl4_mode_22.dat")
    tb, yb = _modes(pack / ARM_B / "Weyl4_mode_22.dat")
    n = min(len(ta), len(tb))
    if not np.allclose(ta[:n], tb[:n]):
        raise SystemExit("the two arms' clocks disagree -- wrong files?")
    keep = ta[:n] >= T_ENGAGE
    t = ta[:n][keep]

    style.prd(base=10.0)
    fig, (axA, axB) = plt.subplots(
        2, 1, figsize=(3.4, 3.6), sharex=True, constrained_layout=True,
        gridspec_kw=dict(height_ratios=[1.35, 1.0]))

    # ---- (a) the two arms at the nearest sphere, one on top of the other --
    # The in-code Weyl4 stream already holds r*Psi4 (its peaks are 0.0293 /
    # 0.0288 / 0.0283 / 0.0281 at R = 20 / 28 / 36 / 44); until 2026-09-24
    # this panel multiplied by R again and drew 20 r*Psi4 under an r*Psi4 label.
    R0 = RADII[0]
    wa = np.real(ya[R0][:n][keep])
    wb = np.real(yb[R0][:n][keep])
    axA.axhline(0.0, color=style.FAINT, linewidth=0.7, zorder=1)
    axA.plot(t, wa, color=style.INK, linewidth=1.4, linestyle=(0, ()), zorder=3)
    axA.plot(t, wb, color=style.GOLD, linewidth=1.7,
             linestyle=(0, (1.3, 1.7)), zorder=4)
    pk = np.abs(wa).max()
    axA.set_ylim(-1.25 * pk, 1.45 * pk)
    axA.set_ylabel(rf"$r\,\mathrm{{Re}}\,\Psi_4^{{2,2}}$  ($R={R0:g}$)")
    # Named in place: the ink arm above its first crest, the dotted twin below.
    axA.text(0.03, 0.955, "(a)", transform=axA.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)
    axA.text(0.35, 0.945, r"fill $1.40/1.90$", transform=axA.transAxes,
             ha="left", va="top", fontsize=7.5, color=style.INK)
    axA.text(0.35, 0.845, r"fill $1.25/1.75$ (twin)", transform=axA.transAxes,
             ha="left", va="top", fontsize=7.5, color=style.GOLD)

    # ---- (b) what moving the window moved, sphere by sphere ---------------
    # The raw |delta| of two oscillating signals combs down the log axis at
    # every near-zero crossing; the ENVELOPE (rolling max over 2 units) is
    # the quantity the gate is about, and it draws as one clean front per
    # sphere arriving on the causal clock t = 57 + (R - 1.9).
    w = max(1, int(round(2.0 / np.median(np.diff(t)))))
    fronts = {}
    for k, R in enumerate(RADII):
        da = np.abs(ya[R][:n][keep] - yb[R][:n][keep])
        ref = np.abs(ya[R][:n][keep]).max()
        frac = np.maximum(da / ref, 1e-12)
        env = np.array([frac[max(0, i - w):i + 1].max() for i in range(len(frac))])
        axB.plot(t, env, color=RAMP[k], linewidth=1.1, zorder=3)
        fronts[R] = t[np.argmax(env > 1e-7)]
        # The fill's causal clock at this sphere, t = 57 + (R - skin), as a
        # short tick under the top frame (2026-09-24: the caption claims the
        # fronts arrive on it; the ticks let the reader check that they do at
        # R = 20 and run ahead of it, below 2e-5 of peak, farther out).
        clock = T_ENGAGE + (R - SKIN)
        axB.plot([clock, clock], [0.09, 0.3], color=RAMP[k], linewidth=1.1, zorder=3)
        print(f"[fill-insensitivity] R = {R:g}: max |dPsi4|/peak = "
              f"{frac.max() * 100:.3f} %;  1e-7 front at t = {fronts[R]:.2f}, "
              f"clock {clock:.1f} ({fronts[R] - clock:+.2f})")
    axB.axhline(GATE, color=style.FAINT, linewidth=0.8,
                linestyle=(0, (4, 2.5)), zorder=2)
    axB.text(t[0] + 0.5, GATE * 1.25, "the few-% gate", ha="left", va="bottom",
             fontsize=7, color=style.MUTED)
    # Each end of the ramp named at the foot of its own front (to its left:
    # rightward the front itself runs low through the text).
    axB.text(fronts[20.0] - 0.4, 1.6e-7, r"$R=20$", fontsize=7, color=RAMP[0],
             ha="right", va="bottom")
    axB.text(fronts[44.0] - 0.4, 1.6e-7, r"$R=44$", fontsize=7, color=RAMP[3],
             ha="right", va="bottom")
    axB.set_yscale("log")
    axB.set_ylim(1e-7, 3e-1)
    axB.set_ylabel(r"$|\Delta\Psi_4^{2,2}|\,/\,\mathrm{peak}$")
    axB.set_xlabel(r"$t$")
    axB.text(0.03, 0.94, "(b)", transform=axB.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "p012_paper" / "fill_insensitivity.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    hits = style.label_audit(fig)
    png = style.save(fig, out)
    print(f"[fill-insensitivity] wrote {png} (+pdf); label audit: "
          + ("clean" if not hits else f"{len(hits)} hit(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
