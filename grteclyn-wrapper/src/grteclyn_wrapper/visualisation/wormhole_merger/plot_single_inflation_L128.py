"""The unkicked L = 128 throat's long inflation record -- the t500 arm.

A separate page from ``single_throat_inflation`` (untouched on the user's word,
2026-09-24: the L2 norms are domain norms and the 8x bigger box dilutes them
x1.4-3.2 against the L = 64 twin, so the records cannot be spliced): this
figure carries the new run's own data, with the L = 64 twin drawn as a halo
beneath wherever the two agree.

THE ARM AND ITS NAME.  ``single_pureq_q1e2_L128_ml4_scalar_t500`` was launched
as "the pure-quadrupole inflation arm" but the launcher's default binary
(boost_2026-09-08 pin) predates the l2 seed and silently drops
``wormhole_seed_l2_amplitude_A`` -- the 2026-09-24 audit's trap, confirmed on
the live process (exe hash == the pin, zero l2 strings).  What evolved is
THE UNKICKED L = 128, max_level 4 throat, and that is what this page shows:
the throat's own truncation-seeded inflation, decelerating.  STOPPED BY HAND
at t = 195.14 on the user's word (2026-09-24 16:12): not quotable past
t ~ 100 -- box reflections, the refinement-box crossing, H ~ 0.13.

WHAT THE PANELS SAY (the whole record, t = 0-195.14):
(a) R_areal (the stream's min over the x-ray, min_radius 0.5): flat at 3.89,
    10 % off at t = 66, x2.62 by t = 144 and still rising.  Past t = 145 the
    stream is DROPPED: its argmin falls off the neck onto the first sample
    past the r = 0.5 cut, exactly the artifact the extractor's docstring
    warns about (the compactified far universe under-resolved: chi flat at
    ~3e-3 where it should fall like r^4, so R there is fiction and drifts
    down as the inner chi plateau rises ~1 %/u).  Verified on Plt15400/15700
    rays 2026-09-24: R(r) is monotone rising off the cut -- no interior
    minimum there -- and the TRUE neck sits at r ~ 20-28.  The line
    continues through the open circles: the neck's own record (min R over
    r > 2), from the run's neck sidecar (small_data/areal_neck.dat, one
    point per rolling plotfile; pack_results.sh carries small_data/*.dat)
    plus the hand-measured seeds.  That record says: the neck PEAKS at
    x2.67 (R = 10.37, t = 161) and falls to 9.68 by t = 195 -- ON THE GRID
    AXIS ONLY.  The neck is not isotropic past t ~ 155, where the axis neck
    leaves the level-1 box (half-width 20) for dx = 0.5 (the second vline):
    the directional sidecar (small_data/areal_neck_dirs.dat, t = 190-195)
    has the face- and body-diagonal necks 6 % apart, the face one RISING,
    and H climbs past 1e-1 (t = 190.24) beneath the fall.  NOT a measured
    turnover.  Past t = 130 the drawn line is a 3-knot ln-R fit crossfaded
    in from the raw stream (see the code): the ~0.1 % shell jitter of the
    neck points is not drawn.  The L = 64 twin (pack) rides beneath to its
    t = 100 end, equal to 0.2 %.
(b) d ln R/dt as ONE line: the raw gradient crossfaded (t = 110-130)
    into the ln-R fit's analytic derivative (3-knot least-squares
    spline, smooth by construction): peak 0.032 (t ~ 74), a
    decelerating coast, zero at t ~ 160, and a gentle turn.
(c) min alpha: twin-identical to 4 digits; 1.9e-2 by t = 154, e-folding
    ~20 u -- drifting down, not plunging.
(d) the arm's own L2 norms: the seam bump (9e-3, t = 100) falls back to
    the 7e-4 floor by t = 109 -- then a SECOND climb from t = 112 doubling
    ~10 u: 1.3e-2 at t = 154, 0.1 at t = 190.24, 0.13 at the stop.

SOURCES (the pack; ``--run`` takes the run tree instead, either layout):
``campaign/01_single_throat/seed/single_pureq_q1e2_L128_ml4_scalar_t500/``
  ``areal_radius.dat``, ``areal_neck.dat``, ``areal_neck_dirs.dat``,
  ``collapse_diagnostics.dat``, ``constraint_norms.dat``
and ``campaign/01_single_throat/hold/single_hold_ml4_t100/`` for the twin.

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
RUN = "seed/single_pureq_q1e2_L128_ml4_scalar_t500"
TWIN = "hold/single_hold_ml4_t100"


def _dedup(a: np.ndarray) -> np.ndarray:
    """First row per time (the streams re-log a step on consumer restarts)."""
    _, idx = np.unique(a[:, 0], return_index=True)
    return a[idx]


def _src(run: pathlib.Path, name: str) -> pathlib.Path:
    """A stream in either layout: the pack's flat folder or the run tree's
    small_data/ and data/ (the latter for --run on the run directory)."""
    for sub in ("", "small_data", "data"):
        p = run / sub / name
        if p.exists():
            return p
    return run / name


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
    ap.add_argument("--run", default=None,
                    help="the run's folder (default: the pack's); a relative "
                         "path resolves against the repo root")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()
    if args.run is None:
        run = pack / "campaign" / GROUP / RUN
    else:
        run = pathlib.Path(args.run).expanduser()
        if not run.is_absolute():
            run = pack.parents[1] / run
    twin_dir = pack / "campaign" / GROUP / TWIN

    ar = _dedup(np.loadtxt(_src(run, "areal_radius.dat")))
    cd = _dedup(np.loadtxt(_src(run, "collapse_diagnostics.dat")))
    cn = _dedup(np.loadtxt(_src(run, "constraint_norms.dat")))
    tw_ar = _dedup(np.loadtxt(twin_dir / "areal_radius.dat"))
    tw_cd = _dedup(np.loadtxt(twin_dir / "collapse_diagnostics.dat"))

    # Valid branch vs the artifact branch: rows whose argmin sits on the
    # first sample past the r = 0.5 cut (r_at_min < 1) are the fiction.
    art = (ar[:, 2] < 1.0) & (ar[:, 0] > 10.0)
    arv = ar[~art]
    t_end = ar[-1, 0]

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
    # Raw stream to t = 130 only: past that the drawn line is the blend
    # into the fit (below), so the ~0.03 fit-vs-raw offset at the stream
    # end cannot print as a step.
    ma = arv[:, 0] <= 130.0
    axT.plot(arv[ma, 0], arv[ma, 1], color=style.INK, linewidth=1.2, zorder=3)
    # The neck's continuation past the stream cut: the sidecar's log where
    # it has written, the hand-measured seeds otherwise; one INK line from
    # the stream's last valid point through the measured points (circles).
    neck = NECK
    nk_path = _src(run, "areal_neck.dat")
    if nk_path.exists():
        try:
            d = np.atleast_2d(np.loadtxt(nk_path))
            if d.size:
                neck = _dedup(np.vstack([NECK, d[:, :2]]))
        except Exception:
            pass
    # one unit of margin: the last circle must not sit on the right spine
    xmax = 5.0 * np.ceil((max(t_end, neck[-1, 0]) + 1.0) / 5.0)
    # The circles start where the x-axis neck leaves the level-1 box
    # (half-width 20; the neck is at r = 20.3 from t = 155): a stage line.
    t_c = float(neck[0, 0])
    # Isotropy of the neck (the directional sidecar, from t = 190): the
    # spread of min R over the axis, face and body diagonals at the last
    # common time.  The throat is spherical; a spread is the grid's.
    spread = None
    nd_path = _src(run, "areal_neck_dirs.dat")
    if nd_path.exists():
        try:
            nd = np.atleast_2d(np.loadtxt(nd_path))
            if nd.size:
                Rs = nd[-1, [1, 3, 5]]
                spread = float((Rs.max() - Rs.min()) / Rs.mean())
        except Exception:
            pass
    # A smooth fit through the measured points (the raw series jitters
    # ~0.1 % on discrete sample shells): a least-squares cubic spline in
    # ln R over the stream from t = 100 PLUS the neck points.  The knot
    # count IS the smoothness guarantee.  Three interior knots -- 120,
    # 150, 175 -- are enough for the coast, the zero crossing and the
    # gentle turn; any denser ladder (8 u and 16 u both scanned,
    # 2026-09-24) lets the tail's +-0.002/u pause-phase undulation --
    # junk-floor territory, H > 4e-2 -- print as dip-bump-dip in the
    # derivative, and an s-tuned smoothing spline wobbled or kinked
    # depending on s.
    from scipy.interpolate import LSQUnivariateSpline  # noqa: PLC0415
    comb = np.vstack([arv[arv[:, 0] >= 100.0, :2], neck[:, :2]])
    knots = np.array([120.0, 150.0, 175.0])
    spl = LSQUnivariateSpline(comb[:, 0], np.log(comb[:, 1]), knots, k=3)
    rms = float(np.sqrt(np.mean((np.exp(spl(neck[:, 0])) - neck[:, 1]) ** 2)))
    # The continuation line: the stream's own tail crossfaded into the
    # fit over t = 130 to the stream end, then the fit through the
    # circles -- continuous with the raw segment at 130 and with the fit
    # at the stream end by construction.
    t_bl = arv[~ma, 0]
    wa = (t_bl - 130.0) / (t_bl[-1] - 130.0)
    r_blend = (1.0 - wa) * arv[~ma, 1] + wa * np.exp(spl(t_bl))
    td = np.arange(t_bl[-1] + 0.5, neck[-1, 0] + 0.25, 0.5)
    # The last raw point leads the polyline: two plot calls that only
    # meet in value still leave a one-sample hole between their ends.
    ext = np.vstack([arv[ma][-1:, :2],
                     np.column_stack([t_bl, r_blend]),
                     np.column_stack([td, np.exp(spl(td))])])
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
    # Under the circles, right of their vline: what they are, and why the
    # fall is not a result -- the neck is direction-dependent (a spherical
    # throat cannot be) and the constraint bath rises under it.  (Above
    # the circles there is no room: two lines between the curve's top and
    # the top ticks either touch the curve or the ticks.)
    tail = (f"circles: the $x$-axis neck,\n"
            f"off level 1 from $t={t_c:.0f}$;\n")
    if spread is not None:
        tail += f"diagonal necks differ by ${100 * spread:.0f}\\,\\%$;\n"
    tail += "$\\mathcal{H}$ $2$e-$2\\to1$e-$1$ across the fall"
    axT.text(neck[-1, 0] - 1.0, 9.35, tail,
             fontsize=7, color=style.MUTED, ha="right", va="top",
             multialignment="right")
    # Two stage lines: inflation onset (10 % departure, t = 66), matched in
    # (b) and (d), and the circles' start, matched in (d) -- where the
    # x-axis neck leaves the level-1 box for the coarsest grid.
    axT.axvline(t_dep, color=style.FAINT, linewidth=0.7, zorder=1)
    axT.axvline(t_c, color=style.FAINT, linewidth=0.7, zorder=1)
    # Label geometry, measured: the curve is flat at 3.89 until t = 66; the
    # whole band above the flat stretch left of t = 60 is empty.  The
    # departure note hangs from the top at its vline, the twin names itself
    # above the flat line, the run caption sits under the rising arc.
    axT.text(2.0, 4.15,
             "the $L=64$ twin rides beneath\nto $t=100$, equal to $0.2\\,\\%$",
             fontsize=7, color=style.CONTEXT, ha="left", va="bottom")
    axT.text(t_dep - 1.5, 9.9, f"$10\\,\\%$ off the flat at $t={t_dep:.0f}$",
             fontsize=7, color=style.MUTED, ha="right", va="top")
    # Above the curve but under the top spine (which clipped earlier,
    # higher placements).
    axT.text(t_rpk - 0.5, 10.35,
             f"stream $\\times{arv[i_rpk, 1] / arv[0, 1]:.2f}$ by $t={t_rpk:.0f}$;\n"
             f"neck peak $\\times{neck[:, 1].max() / arv[0, 1]:.2f}$ "
             f"at $t={neck[np.argmax(neck[:, 1]), 0]:.0f}$",
             fontsize=7, color=style.INK, ha="right", va="bottom",
             multialignment="right")
    if t_sw is not None:
        axT.text(t_sw - 2.0, 6.9,
                 f"stream dropped past $t={t_sw:.0f}$:\n"
                 "its argmin leaves the neck\n"
                 "for the $r=0.5$ cut",
                 fontsize=7, color=style.MUTED, ha="right", va="top")
    # Under the rising arc, centred in the empty band left of the circles.
    axT.text(0.5 * (100.0 + (t_sw if t_sw is not None else xmax)), 3.42,
             "unkicked, $L=128$, level 4, stopped at $t=195$", fontsize=7.5,
             color=style.INK, ha="center", va="bottom")
    axT.set_xlim(0, xmax)
    axT.set_ylim(3.3, 11.8)
    axT.set_ylabel(r"$R_{\rm areal}$")
    axT.set_xlabel(r"$t$")
    axT.text(0.012, 0.93, "(a)", transform=axT.transAxes, ha="left", va="top",
             fontsize=9, color=style.INK)

    # ---- (b) the growth rate: a decelerating coast --------------------------
    # ONE polyline for the whole record: the raw (boxcar-5) gradient while
    # the stream is dense, CROSSFADED into the fit's analytic derivative
    # over t = 110-130 (a linear blend of two smooth curves deep in the
    # coast cannot leave a seam; every hard handover tried, at t = 120 or
    # at the t = 144 stream end, printed as a step because the sparse-knot
    # fit sits ~1e-3/u off the raw curve at any single point).  The fit is
    # in ln R, so its derivative IS d ln R/dt.
    T0, T1 = 110.0, 130.0
    mj = arv[:, 0] < T1
    t_raw = arv[mj, 0][2:]
    w = np.clip((t_raw - T0) / (T1 - T0), 0.0, 1.0)
    r_bl = (1.0 - w) * rate[mj][2:] + w * spl.derivative()(t_raw)
    tb = np.arange(T1, neck[-1, 0] + 0.25, 0.5)
    t_line = np.concatenate([t_raw, tb])
    rate_line = np.concatenate([r_bl, spl.derivative()(tb)])
    axs[0].plot(t_line, rate_line, color=style.INK, linewidth=1.1, zorder=3)
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
    axs[0].set_ylim(-0.006, 0.037)
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
    axs[2].axvline(t_c, color=style.FAINT, linewidth=0.7, zorder=1)
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
    # its ~1e-6 shelf at t ~ 40) sweeps the middle, so the note is four
    # short lines in the bottom band (below 1e-6, empty past t ~ 20),
    # between the t = 66 and the circles' vlines -- both run full height.
    axs[2].text(t_c - 3.0, 0.02,
                "seam bump\n"
                "back by $t=109$,\n"
                "then doubling\n"
                "every $\\sim$$10\\,$u",
                transform=axs[2].get_xaxis_transform(), fontsize=7,
                color=style.MUTED, ha="right", va="bottom",
                multialignment="right")

    for k, ax in enumerate(axs):
        ax.text(0.0, 1.03, f"({'bcd'[k]})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)
        ax.set_xlabel(r"$t$")

    print(f"[single-inflation-L128] live to t = {t_end:.1f}: "
          f"stream valid to t = {arv[-1, 0]:.0f} "
          f"(R {arv[0, 1]:.3f} -> {arv[-1, 1]:.3f}, "
          f"x{arv[i_rpk, 1] / arv[0, 1]:.2f}), stream cut at t = {t_sw}, "
          f"neck {neck[-1, 1]:.3f} at t = {neck[-1, 0]:.0f} "
          f"({len(neck)} measured points, fit rms {rms:.4f}), "
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
