"""Psi4 l=2 modes across the merger refinement ladder, against the target window.

The wormhole-merger campaign needs the collapse signature at the R = 14
extraction sphere.  The collapse sources it over t = 44-51.5; a signal at
radius R lags its source by R, so it crosses R = 14 over t = 58-65.5.  Every
arm so far dies before that, and the AMR refinement ladder (M4e in
research/merger/Plan.md) is the axis that moves the death time.

This module plots what has actually been recorded -- the l = 2 modes at both
extraction radii -- for any number of runs on one axis, with the target
window shaded and each run's death marked, so "how much of the signal do we
have" is a picture rather than a table.

Own module, own output file: it reads finished `small_data/psi4_mode_l2_all.dat`
streams and writes one PNG.  It never touches a run directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

# The physics the plot is drawn against; see research/merger/Plan.md.
COLLAPSE_SOURCE = (44.0, 51.5)
SOURCE_RADIUS = 1.5  # where the collapsing core radiates from

# Signals do not travel at coordinate speed 1: cross-correlating the two
# extraction spheres on the completed t = 80 arms puts the lag at 18.0 code
# units over their 16.0 of coordinate separation (correlation 0.9998).  The
# 12.5 % excess is propagation delay through the mass.  Using the naive
# straight-line estimate put the R = 30 arrival window 3 units early and cost
# a run that stopped at 80 with under half of that window recorded.
PROPAGATION_SLOWDOWN = 18.0 / 16.0

# The sponge zone (extra ramped dissipation, SpongeZone.hpp) occupies
# r = 24 -> 32 in these runs.  R = 30 sits INSIDE it, so that sphere is
# measured in an absorbing layer; flagged on the figure rather than silently
# plotted as if it were a clean detector.
SPONGE_INNER = 24.0


def target_window(radius: float) -> tuple[float, float]:
    """When the collapse signature crosses the sphere at ``radius``."""
    delay = (radius - SOURCE_RADIUS) * PROPAGATION_SLOWDOWN
    return COLLAPSE_SOURCE[0] + delay, COLLAPSE_SOURCE[1] + delay

# Column layout of psi4_mode_l2_all.dat: time, then (Re, Im) for m = -2..2 at
# R = 14, then the same five pairs at R = 30.
_M_ORDER = (-2, -1, 0, 1, 2)


def _column(m: int, radius_index: int) -> tuple[int, int]:
    """Return the (Re, Im) column indices for mode m at the given radius."""
    base = 1 + 10 * radius_index + 2 * _M_ORDER.index(m)
    return base, base + 1


def load_modes(path: Path) -> dict:
    """Read one psi4_mode_l2_all.dat into {t, amp[(m, radius_index)]}."""
    raw = np.loadtxt(path)
    if raw.ndim == 1:
        raw = raw.reshape(1, -1)
    out = {"t": raw[:, 0], "amp": {}, "re": {}}
    for ridx in (0, 1):
        for m in _M_ORDER:
            cre, cim = _column(m, ridx)
            if cim >= raw.shape[1]:
                continue
            re, im = raw[:, cre], raw[:, cim]
            out["amp"][(m, ridx)] = np.hypot(re, im)
            out["re"][(m, ridx)] = re
    return out


def _plot_channel(ax, runs, m, ridx, scale, title, ylabel, window, radius, under=()):
    # The band is the thing every arm is being measured against, so it is drawn
    # first and in the grid's own tone: it is the ruler, not a fifth series.
    ax.axvspan(
        *window,
        color=style.GRID,
        zorder=0,
        label=rf"collapse signature at $R={radius:g}$  ({window[0]:.1f}–{window[1]:.1f})",
    )
    # Arms drawn UNDER the ladder: a fat, pale burgundy stroke, so "the freeze
    # arm runs exactly under the unfrozen one" is something the eye sees rather
    # than something the caption claims.
    for label, data, _kw in under:
        key = (m, ridx)
        if key in data["amp"]:
            ax.plot(data["t"], data["amp"][key] * scale, color=style.BURGUNDY,
                    lw=5.0, alpha=0.25, solid_capstyle="round", zorder=1,
                    label=rf"{label}  (to $t={data['t'][-1]:.1f}$)")

    for label, data, kw in runs:
        key = (m, ridx)
        if key not in data["amp"]:
            continue
        ax.plot(
            data["t"],
            data["amp"][key] * scale,
            marker="o",
            ms=2.0,
            label=rf"{label}  (to $t={data['t'][-1]:.1f}$)",
            **kw,
        )
        # Mark where the stream stops: that is the run's death, and the whole
        # point of the figure is how far short of the window it falls.
        ax.plot(
            data["t"][-1],
            data["amp"][key][-1] * scale,
            marker="x",
            ms=8,
            mew=1.8,
            color=kw["color"],
        )

    ax.set_title(title, loc="left")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, loc="best")


def make_figure(runs, radius_label, ridx, scale, out_path: Path, radius: float, under=()) -> Path:
    style.paper(base=10.0)
    fig, axes = plt.subplots(2, 1, figsize=(8.6, 6.2), sharex=True,
                             constrained_layout=True)
    window = target_window(radius)

    _plot_channel(
        axes[0],
        runs,
        m=2,
        ridx=ridx,
        scale=scale,
        title=r"(a) spinning quadrupole $(\ell,m)=(2,2)$ — the binary channel",
        ylabel=r"$r\,|\Psi_4^{2,2}|$",
        window=window,
        radius=radius,
        under=under,
    )
    _plot_channel(
        axes[1],
        runs,
        m=0,
        ridx=ridx,
        scale=scale,
        title=r"(b) axisymmetric channel $(\ell,m)=(2,0)$ — the head-on-style burst",
        ylabel=r"$r\,|\Psi_4^{2,0}|$",
        window=window,
        radius=radius,
        under=under,
    )

    axes[1].set_xlabel(r"$t$")
    every = list(runs) + list(under)
    right = max(window[1] + 2.0, max(d["t"][-1] for _, d, _ in every) + 2.0)
    axes[1].set_xlim(left=min(d["t"][0] for _, d, _ in every) - 1.0, right=right)

    sponge_note = (
        "  --  NB: this sphere lies INSIDE the sponge zone (r = 24-32), an "
        "absorbing layer; treat amplitudes as indicative"
        if radius > SPONGE_INNER
        else ""
    )
    fig.suptitle(
        rf"$r\,|\Psi_4|$, $\ell=2$, at ${radius_label}$" + "\n"
        "crosses mark each run's end (NaN death, or stop time reached); the "
        f"shaded band is the collapse signature{sponge_note}",
        fontsize=9.5, color=style.MUTED,
    )
    out = style.save(fig, out_path)
    plt.close(fig)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run",
        action="append",
        required=True,
        metavar="LABEL=PATH",
        help="Label and path to a run's psi4_mode_l2_all.dat (repeatable, in "
        "ladder order).",
    )
    ap.add_argument(
        "--under",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="An arm to draw as a fat pale stroke BENEATH the ladder -- for showing "
        "that one arm lies on another (repeatable).",
    )
    ap.add_argument("--out", required=True, type=Path, help="Output PNG path.")
    ap.add_argument(
        "--radius",
        choices=("14", "30"),
        default="14",
        help="Extraction radius to plot (default 14, the one M7 requires).",
    )
    args = ap.parse_args(argv)

    ridx = 0 if args.radius == "14" else 1
    # No rescaling: the extractor already folds the radius into the mode
    # amplitude (`amp = sum(psi4 * conj(Ylm) * W) * r`), so the columns hold
    # r*Psi4 and are directly comparable between spheres.  Measured on the
    # completed t = 80 arms, r*Psi4 at R = 30 matches R = 14 to 1.3 % once the
    # 18-unit light-travel lag is removed -- i.e. Psi4 falls as 1/R, the
    # signature of genuine outgoing radiation.  An extra R/14 here would have
    # double-counted that factor and invented a 2.1x discrepancy.
    scale = 1.0
    radius_label = "R=14" if ridx == 0 else "R=30"


    # A refinement ladder is an ORDERED family: pale for the coarse arm, dark
    # for the fine one, so the reading order of the legend is the reading order
    # of the grid.  The dash cycle rides along, for greyscale.
    specs = list(args.run)
    # Always the ordinal ramp, however few arms there are: a refinement ladder
    # is ordered by construction, and the four categorical hues would throw
    # that away to say nothing in its place.
    kws = style.ordinal_series(len(specs), lw=1.5)
    runs = []
    for i, spec in enumerate(specs):
        label, _, path = spec.partition("=")
        p = Path(path)
        if not p.is_file():
            raise SystemExit(f"no such stream: {p}")
        runs.append((label, load_modes(p), kws[i]))

    under = []
    for spec in args.under:
        label, _, path = spec.partition("=")
        q = Path(path)
        if not q.is_file():
            raise SystemExit(f"no such stream: {q}")
        under.append((label, load_modes(q), None))

    radius = 14.0 if ridx == 0 else 30.0
    out = make_figure(runs, radius_label, ridx, scale, args.out, radius, under)
    print(f"wrote {out}")
    window = target_window(radius)
    for label, data, _kw in runs:
        gap = window[0] - data["t"][-1]
        print(
            f"  {label}: stream ends t = {data['t'][-1]:.2f}, "
            f"{gap:+.2f} from the start of the target window"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
