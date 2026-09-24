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

WHAT THE PANELS SAY (record to t ~ 157, LIVE -- regenerate at landing):
(a) R_areal (the stream's min over the x-ray, min_radius 0.5): flat at 3.89,
    10 % off at t = 66, x2.62 by t = 144 and still rising.  Past t = 145 the
    stream is DROPPED: its argmin falls off the neck onto the first sample
    past the r = 0.5 cut, exactly the artifact the extractor's docstring
    warns about (the compactified far universe under-resolved: chi flat at
    ~3e-3 where it should fall like r^4, so R there is fiction and drifts
    down as the inner chi plateau rises ~1 %/u).  Verified on Plt15400/15700
    rays 2026-09-24: R(r) is monotone rising off the cut -- no interior
    minimum there -- and the TRUE neck sits at r ~ 20, still growing:
    10.321 (t = 154) -> 10.347 (t = 157).  The line continues through the
    open circles: the neck's own record (min R over r > 2), from the
    run's neck sidecar (small_data/areal_neck.dat, one point per rolling
    plotfile) plus the hand-measured seeds.  The L = 64 twin (pack) rides
    beneath to its t = 100 end, equal to 0.2 %.
(b) d ln R/dt: the valid stream to t = 144, then the neck measurements
    carry the curve on toward zero (~0.0009/u by t ~ 156): peak 0.032
    (t ~ 74), a decelerating coast, doubling 23 u -> 117 u and stretching;
    the halving law points at R leveling near ~10.5.
(c) min alpha: twin-identical to 4 digits; 1.9e-2 by t = 154, e-folding
    ~20 u -- drifting down, not plunging.
(d) the live arm's own L2 norms: the seam bump (9e-3, t = 100) falls back to
    the 7e-4 floor by t = 109 -- then a SECOND climb from t ~ 120 doubling
    ~10 u, 1.3e-2 at t = 154; on the L = 64 death clock (died at H ~ 0.33)
    that says watch t ~ 185-205.

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


# The true neck, measured by hand off the rolling plotfiles' x-rays (r ~ 20,
# min of R over r > 2), 2026-09-24: the stream stops tracking it at t = 145
# when its argmin falls onto the r = 0.5 cut.  Extend at each regeneration
# while the artifact stands (plotfiles roll -- these points are irreplaceable).
NECK = np.array([
    [154.0, 10.3209],
    [157.0, 10.3468],
])


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

    # Valid branch vs the artifact branch: rows whose argmin sits on the
    # first sample past the r = 0.5 cut (r_at_min < 1) are the fiction.
    art = (ar[:, 2] < 1.0) & (ar[:, 0] > 10.0)
    arv = ar[~art]
    t_end = ar[-1, 0]
    xmax = 5.0 * np.ceil(max(t_end, NECK[-1, 0]) / 5.0)

    # Growth rate: d ln R / dt on the valid branch only, boxcar-5 smoothed.
    rate = np.gradient(np.log(arv[:, 1]), arv[:, 0])
    rate = np.convolve(rate, np.ones(5) / 5.0, mode="same")
    i_pk = int(np.argmax(rate))
    # 10 % departure from the flat start.
    i_dep = int(np.argmax(arv[:, 1] > 1.1 * arv[0, 1]))
    t_dep = arv[i_dep, 0]
    i_rpk = int(np.argmax(arv[:, 1]))
    t_rpk = arv[i_rpk, 0]
    sw = np.flatnonzero(art)
    t_sw = float(ar[sw[0], 0]) if sw.size else None

    style.prd(base=10.0)
    fig = plt.figure(figsize=(7.05, 4.1), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0])
    axT = fig.add_subplot(gs[0, :])
    axs = [fig.add_subplot(gs[1, i]) for i in range(3)]

    # ---- (a) the throat, with the twin as a halo beneath -------------------
    m = tw_ar[:, 0] <= 100.0
    axT.plot(tw_ar[m, 0], tw_ar[m, 1], color=style.CONTEXT, linewidth=2.6,
             zorder=2, solid_capstyle="butt")
    axT.plot(arv[:, 0], arv[:, 1], color=style.INK, linewidth=1.2, zorder=3)
    # The neck's continuation past the stream cut: the sidecar's log where
    # it has written, the hand-measured seeds otherwise; one INK line from
    # the stream's last valid point through the measured points (circles).
    neck = NECK
    nk_path = run / "small_data" / "areal_neck.dat"
    if nk_path.exists():
        try:
            d = np.atleast_2d(np.loadtxt(nk_path))
            if d.size:
                neck = _dedup(np.vstack([NECK, d[:, :2]]))
        except Exception:
            pass
    ext = np.vstack([arv[-1:, :2], neck[:, :2]])
    axT.plot(ext[:, 0], ext[:, 1], color=style.INK, linewidth=1.2, zorder=3)
    # Circles thinned to one per ~4 u (the sidecar logs every 0.5 u and a
    # bead chain reads badly); the line runs through every measured point.
    mk = [0]
    for i in range(1, len(neck)):
        if neck[i, 0] - neck[mk[-1], 0] >= 4.0:
            mk.append(i)
    if mk[-1] != len(neck) - 1:
        mk.append(len(neck) - 1)
    axT.plot(neck[mk, 0], neck[mk, 1], linestyle="none", marker="o",
             markersize=3.5, markerfacecolor="white",
             markeredgecolor=style.INK, markeredgewidth=1.0, zorder=4)
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
    # Above the curve but under the top spine, ending left of the t = 145
    # vline (the spine and the vline both clipped earlier placements).
    axT.text(t_rpk - 6.0, 10.35,
             f"stream $\\times{arv[i_rpk, 1] / arv[0, 1]:.2f}$ by $t={t_rpk:.0f}$;\n"
             "the neck (circles) grows on past it",
             fontsize=7, color=style.INK, ha="right", va="bottom",
             multialignment="right")
    if t_sw is not None:
        axT.axvline(t_sw, color=style.FAINT, linewidth=0.7, zorder=1)
        axT.text(t_sw - 2.0, 6.9,
                 f"stream dropped past $t={t_sw:.0f}$:\n"
                 "its argmin leaves the neck\n"
                 "for the $r=0.5$ cut",
                 fontsize=7, color=style.MUTED, ha="right", va="top")
    # Between the t = 100 and the surface-jump vlines, under the curve's arc
    # (both full-height vlines crossed earlier placements of this label).
    axT.text(0.5 * (100.0 + (t_sw if t_sw is not None else xmax)), 3.42,
             "unkicked, $L=128$, level 4 (live)", fontsize=7.5,
             color=style.INK, ha="center", va="bottom")
    axT.set_xlim(0, xmax)
    axT.set_ylim(3.3, 11.4)
    axT.set_ylabel(r"$R_{\rm areal}$")
    axT.set_xlabel(r"$t$")
    axT.text(0.012, 0.93, "(a)", transform=axT.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) the growth rate: a decelerating coast --------------------------
    # Boxcar 'same' zero-pads the ends and hooks the last samples toward
    # zero -- trim the two edge samples on each side.
    axs[0].plot(arv[2:-2, 0], rate[2:-2], color=style.INK, linewidth=1.1,
                zorder=3)
    # The neck measurements carry the rate past the stream cut (nonuniform
    # cadence: np.gradient handles it; the 145-154 hole averages across).
    if len(ext) > 2:
        rate_ext = np.gradient(np.log(ext[:, 1]), ext[:, 0])
        axs[0].plot(ext[:, 0], rate_ext, color=style.INK, linewidth=1.1,
                    zorder=3)
    axs[0].axvline(t_dep, color=style.FAINT, linewidth=0.7, zorder=1)
    axs[0].axhline(0.0, color=style.FAINT, linewidth=0.6, zorder=1)
    # Two right-aligned lines ending at t = 62, left of the t = 66 vline: the
    # audit showed a left-anchored block at t = 4 still reaches t ~ 78 at 7 pt
    # and the rising limb (0.016 -> 0.032 over t = 66-74) cuts through it.
    # Upper-right: the coast is low (< 0.008) past t ~ 95, and the left
    # margin is owned by the tick labels at this x-range.
    axs[0].text(0.96, 0.95, f"${rate[i_pk]:.3f}$ at $t={arv[i_pk, 0]:.0f}$",
                transform=axs[0].transAxes,
                fontsize=7, color=style.MUTED, ha="right", va="top")
    axs[0].text(0.99, 0.80, "doubling $23\\!\\to\\!117\\,$u",
                transform=axs[0].transAxes,
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
    axs[2].axvline(t_dep, color=style.FAINT, linewidth=0.7, zorder=1)
    axs[2].plot(cn[:, 0], cn[:, 1], color=style.INK, linewidth=1.1, zorder=3)
    mm = cn[:, 2] > 0
    axs[2].plot(cn[mm, 0], cn[mm, 2], color=style.MUTED, linewidth=1.1,
                linestyle=(0, (4, 2.5)), zorder=3)
    axs[2].set_yscale("log")
    axs[2].set_xlim(0, xmax)
    # The extra decade at the bottom is bought space: the M limb sweeps the
    # whole 1e-7..1e-2 middle, and below 1e-7 nothing is drawn past t = 18,
    # so the corner note lives there untouched.
    axs[2].set_ylim(1e-8, 4e-2)
    axs[2].set_ylabel(r"$L_2$ norms")
    # H sits near 8e-4 through t = 60 and M crosses 1e-5 at t ~ 50; each label
    # rides just above its own curve where the frame is empty.
    axs[2].text(25.0, 1.8e-3, r"$\mathcal{H}$", fontsize=7.5,
                color=style.INK, ha="center", va="bottom")
    axs[2].text(55.0, 3.5e-6, r"$\mathcal{M}$", fontsize=7.5,
                color=style.MUTED, ha="center", va="top")
    # The seam bump + second climb fill the upper band and the M limb (with
    # its ~1e-6 shelf at t ~ 40) sweeps the middle, so the note is two short
    # lines pinned to the bottom-right corner, wholly below 8e-7.
    # Short lines: the t = 66 vline runs full height at axes x = 0.41, so
    # every line of the note must start right of it.
    axs[2].text(0.97, 0.02,
                "seam bump\n"
                "back by $t=109$;\n"
                "then doubling $\\sim$$10\\,$u",
                transform=axs[2].transAxes, fontsize=7, color=style.MUTED,
                ha="right", va="bottom", multialignment="right")

    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({'bcd'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
        ax.set_xlabel(r"$t$")

    print(f"[single-inflation-L128] live to t = {t_end:.1f}: "
          f"stream valid to t = {arv[-1, 0]:.0f} "
          f"(R {arv[0, 1]:.3f} -> {arv[-1, 1]:.3f}, "
          f"x{arv[i_rpk, 1] / arv[0, 1]:.2f}), stream cut at t = {t_sw}, "
          f"neck {neck[-1, 1]:.3f} at t = {neck[-1, 0]:.0f} "
          f"({len(neck)} measured points), "
          f"rate peak {rate[i_pk]:.4f} at t = {arv[i_pk, 0]:.0f}; "
          f"Ham end {cn[-1, 1]:.2e}")

    style.label_audit(fig)

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "single_throat_inflation_L128.png")
    png = style.save(fig, out)
    print(f"[single-inflation-L128] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
