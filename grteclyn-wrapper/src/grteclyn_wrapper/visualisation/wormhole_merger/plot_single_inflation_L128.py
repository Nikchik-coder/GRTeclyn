"""The unkicked L = 128 throat's long inflation record -- the LIVE t500 arm.

A separate page from ``single_throat_inflation`` (untouched on the user's word,
2026-09-24: the L2 norms are domain norms and the 8x bigger box dilutes them
x1.4-3.2 against the L = 64 twin, so the records cannot be spliced): this
figure carries the new run's own data, with the L = 64 twin drawn as a halo
beneath wherever the two agree.

THE ARM AND ITS NAME.  ``single_pureq_q1e2_L128_ml4_scalar_t500`` was launched
as "the pure-quadrupole inflation arm" but the launcher's default binary
(boost_2026-09-08 pin) predates the l2 seed and silently drops
``wormhole_seed_l2_amplitude_A`` -- the 2026-09-24 audit's trap, confirmed on
the live process (exe hash == the pin, zero l2 strings).  What is evolving is
THE UNKICKED L = 128, max_level 4 throat, and that is what this page shows:
the throat's own truncation-seeded inflation, decelerating.

WHAT THE PANELS SAY (record to t ~ 110, LIVE -- regenerate at landing):
(a) R_areal: flat at 3.89, 10 % off the flat at t = 66, x2.37 by t = 110 and
    climbing ever slower.  The L = 64 twin (pack) rides beneath to its t = 100
    end, equal to 0.2 % -- the inflation clock does not care about the box.
(b) d ln R/dt: the growth rate peaks at 0.031 (t ~ 78) and has fallen to
    0.006 by t ~ 108 -- doubling time 23 u -> 117 u, a decelerating coast.
(c) min alpha: identical to the twin to 4 digits over the shared window.
(d) the live arm's own L2 norms: the seam-mode bump (the refinement square's
    corners, the L = 64 box's killer) peaks at 9e-3 at t = 100 and falls BACK
    to its floor by t ~ 109 -- this box contains what killed the small one.

SOURCES (the run tree, NOT the pack -- the run is in flight):
``runs/wormhole_merger/single_pureq_q1e2_L128_ml4_scalar_t500/``
  ``small_data/areal_radius.dat``, ``data/collapse_diagnostics.dat``,
  ``data/constraint_norms.dat``
and the pack's ``01_single_throat/hold/single_hold_ml4_t100/`` for the twin.

STYLE: house (style.prd); INK = the live arm, CONTEXT = the L = 64 twin drawn
as a wider halo UNDER the ink line (the curves coincide, so side-by-side
styles would lie); letter tags above the frames; every label sits in a gap
measured off the drawn curves.
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
RUN = "runs/wormhole_merger/single_pureq_q1e2_L128_ml4_scalar_t500"
TWIN = "hold/single_hold_ml4_t100"


def _dedup(a: np.ndarray) -> np.ndarray:
    """First row per time (the streams re-log a step on consumer restarts)."""
    _, idx = np.unique(a[:, 0], return_index=True)
    return a[idx]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--run", default=RUN,
                    help="the live run dir (switch to the pack path at landing)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run = pathlib.Path(args.run).expanduser()
    if not run.is_absolute():
        run = pathlib.Path(args.pack_root).expanduser().parents[1] / run
    twin_dir = pathlib.Path(args.pack_root).expanduser() / "campaign" / GROUP / TWIN

    ar = _dedup(np.loadtxt(run / "small_data" / "areal_radius.dat"))
    cd = _dedup(np.loadtxt(run / "data" / "collapse_diagnostics.dat"))
    cn = _dedup(np.loadtxt(run / "data" / "constraint_norms.dat"))
    tw_ar = _dedup(np.loadtxt(twin_dir / "areal_radius.dat"))
    tw_cd = _dedup(np.loadtxt(twin_dir / "collapse_diagnostics.dat"))

    t_end = ar[-1, 0]
    xmax = 5.0 * np.ceil(t_end / 5.0)

    # Growth rate: d ln R / dt on the unit-cadence stream, boxcar-5 smoothed.
    rate = np.gradient(np.log(ar[:, 1]), ar[:, 0])
    rate = np.convolve(rate, np.ones(5) / 5.0, mode="same")
    i_pk = int(np.argmax(rate))
    # 10 % departure from the flat start.
    i_dep = int(np.argmax(ar[:, 1] > 1.1 * ar[0, 1]))
    t_dep = ar[i_dep, 0]

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 4.1), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1, i]) for i in range(3)]

    # ---- (a) the throat, with the twin as a halo beneath -------------------
    m = tw_ar[:, 0] <= 100.0
    axT.plot(tw_ar[m, 0], tw_ar[m, 1], color=style.CONTEXT, linewidth=2.6,
             zorder=2, solid_capstyle="butt")
    axT.plot(ar[:, 0], ar[:, 1], color=style.INK, linewidth=1.2, zorder=3)
    axT.axvline(100.0, color=style.FAINT, linewidth=0.7, zorder=1)
    axT.axvline(t_dep, color=style.FAINT, linewidth=0.7, zorder=1)
    # Label geometry, measured: the curve is flat at 3.89 until t = 66 and
    # ends at 9.23 (t = 110); the whole band above the flat stretch left of
    # t = 60 is empty, and the top-right corner above the end of the curve is
    # not.  So the departure note hangs from the top at its own vline, the
    # twin names itself below the flat line, the record-end note tops its
    # vline, and the end label tucks UNDER the curve's tail (0.62 below, clear of the ink).
    axT.text(2.0, 4.18, "the $L=64$ twin rides beneath to $t=100$, equal to $0.2\\,\\%$",
             fontsize=7, color=style.CONTEXT, ha="left", va="bottom")
    axT.text(t_dep - 1.5, 9.9, f"$10\\,\\%$ off the flat at $t={t_dep:.0f}$",
             fontsize=7, color=style.MUTED, ha="right", va="top")
    axT.text(99.0, 9.9, "the $L=64$ record ends", fontsize=7,
             color=style.MUTED, ha="right", va="top")
    axT.text(101.5, 9.55,
             f"$\\times{ar[-1, 1] / ar[0, 1]:.2f}$ by $t={t_end:.0f}$",
             fontsize=7, color=style.INK, ha="left", va="bottom")
    # Between the two vlines, under the rising curve: the t = 100 vline runs
    # full height and crossed this label in the lower-right corner.
    axT.text(0.85, 0.03, "unkicked, $L=128$, level 4 (live)",
             transform=axT.transAxes, fontsize=7.5, color=style.INK,
             ha="right", va="bottom")
    axT.set_xlim(0, xmax)
    axT.set_ylim(3.3, 10.2)
    axT.set_ylabel(r"$R_{\rm areal}$")
    axT.set_xlabel(r"$t$")
    axT.text(0.012, 0.93, "(a)", transform=axT.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) the growth rate: a decelerating coast --------------------------
    axs[0].plot(ar[:, 0], rate, color=style.INK, linewidth=1.1, zorder=3)
    axs[0].axvline(t_dep, color=style.FAINT, linewidth=0.7, zorder=1)
    # Two right-aligned lines ending at t = 62, left of the t = 66 vline: the
    # audit showed a left-anchored block at t = 4 still reaches t ~ 78 at 7 pt
    # and the rising limb (0.016 -> 0.032 over t = 66-74) cuts through it.
    axs[0].text(62.0, 0.0345, f"${rate[i_pk]:.3f}$ at $t={ar[i_pk, 0]:.0f}$",
                fontsize=7, color=style.MUTED, ha="right", va="top")
    axs[0].text(62.0, 0.0300, "doubling $23\\,$u$\\;\\to\\;117\\,$u",
                fontsize=7, color=style.MUTED, ha="right", va="top")
    axs[0].set_xlim(0, xmax)
    axs[0].set_ylim(-0.002, 0.037)
    axs[0].set_ylabel(r"$d\ln R/dt$")

    # ---- (c) min lapse, the twin beneath ------------------------------------
    mt = tw_cd[:, 0] <= 100.0
    axs[1].plot(tw_cd[mt, 0], tw_cd[mt, 1], color=style.CONTEXT, linewidth=2.4,
                zorder=2, solid_capstyle="butt")
    axs[1].plot(cd[:, 0], cd[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    axs[1].set_yscale("log")
    axs[1].set_xlim(0, xmax)
    axs[1].set_ylabel(r"$\min\alpha$")
    axs[1].text(0.05, 0.10, "twin beneath,\nequal to $4$ digits",
                transform=axs[1].transAxes, fontsize=7, color=style.CONTEXT,
                ha="left", va="bottom")

    # ---- (d) the live arm's own constraints ---------------------------------
    axs[2].plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    mm = cn[:, 2] > 0
    axs[2].plot(cn[mm, 0], cn[mm, 2], color=style.MUTED, linewidth=1.1,
                linestyle=(0, (4, 2.5)), zorder=3)
    axs[2].set_yscale("log")
    axs[2].set_xlim(0, xmax)
    axs[2].set_ylim(1e-7, 4e-2)
    axs[2].set_ylabel(r"$L_2$ norms")
    # H sits near 8e-4 through t = 60 and M crosses 1e-5 at t ~ 50; each label
    # rides just above its own curve where the frame is empty.
    axs[2].text(25.0, 1.8e-3, r"$\mathcal{H}$", fontsize=7.5,
                color=style.INK, ha="center", va="bottom")
    axs[2].text(55.0, 3.5e-6, r"$\mathcal{M}$", fontsize=7.5,
                color=style.MUTED, ha="center", va="top")
    axs[2].text(0.05, 0.97, "the seam bump falls back\nto its floor by $t=109$",
                transform=axs[2].transAxes, fontsize=7, color=style.MUTED,
                ha="left", va="top")

    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({'bcd'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
        ax.set_xlabel(r"$t$")

    print(f"[single-inflation-L128] live to t = {t_end:.1f}: "
          f"R {ar[0, 1]:.3f} -> {ar[-1, 1]:.3f} (x{ar[-1, 1] / ar[0, 1]:.2f}), "
          f"rate peak {rate[i_pk]:.4f} at t = {ar[i_pk, 0]:.0f}, "
          f"end rate {rate[-3]:.4f}; Ham end {cn[-1, 1]:.2e}")

    style.label_audit(fig)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation_L128.png")
    png = style.save(fig, out)
    print(f"[single-inflation-L128] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
