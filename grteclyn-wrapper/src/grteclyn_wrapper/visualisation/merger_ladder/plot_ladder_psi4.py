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


def _plot_channel(ax, runs, m, ridx, scale, title, ylabel, window, radius):
    for label, data, colour in runs:
        key = (m, ridx)
        if key not in data["amp"]:
            continue
        ax.plot(
            data["t"],
            data["amp"][key] * scale,
            color=colour,
            lw=1.8,
            marker="o",
            ms=2.5,
            label=f"{label}  (to t = {data['t'][-1]:.1f})",
        )
        # Mark where the stream stops: that is the run's death, and the whole
        # point of the figure is how far short of the window it falls.
        ax.plot(
            data["t"][-1],
            data["amp"][key][-1] * scale,
            marker="x",
            ms=9,
            mew=2,
            color=colour,
        )

    ax.axvspan(
        *window,
        color="tab:green",
        alpha=0.13,
        zorder=0,
        label=f"collapse signature at R = {radius:g}  ({window[0]:.1f}-{window[1]:.1f})",
    )
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")


def make_figure(runs, radius_label, ridx, scale, out_path: Path, radius: float) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8.5), sharex=True)
    window = target_window(radius)

    _plot_channel(
        axes[0],
        runs,
        m=2,
        ridx=ridx,
        scale=scale,
        title="Spinning quadrupole (l = 2, m = 2) -- the binary channel",
        ylabel=r"$r\,|\Psi_4|$",
        window=window,
        radius=radius,
    )
    _plot_channel(
        axes[1],
        runs,
        m=0,
        ridx=ridx,
        scale=scale,
        title="Axisymmetric channel (l = 2, m = 0) -- the head-on-style burst",
        ylabel=r"$r\,|\Psi_4|$",
        window=window,
        radius=radius,
    )

    axes[1].set_xlabel("t  (code units)")
    right = max(window[1] + 2.0, max(d["t"][-1] for _, d, _ in runs) + 2.0)
    axes[1].set_xlim(left=min(d["t"][0] for _, d, _ in runs) - 1.0, right=right)

    sponge_note = (
        "  --  NB: this sphere lies INSIDE the sponge zone (r = 24-32), an "
        "absorbing layer; treat amplitudes as indicative"
        if radius > SPONGE_INNER
        else ""
    )
    fig.suptitle(
        f"Wormhole merger: r*Psi4 l = 2 at {radius_label}\n"
        "crosses mark each run's end (NaN death, or stop time reached); the "
        f"shaded band is the collapse signature{sponge_note}",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


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
    radius_label = "R = 14" if ridx == 0 else "R = 30"


    palette = [
        "#777777", "tab:blue", "tab:red", "tab:green", "tab:purple",
        "tab:orange", "tab:brown", "tab:cyan",
    ]
    runs = []
    for i, spec in enumerate(args.run):
        label, _, path = spec.partition("=")
        p = Path(path)
        if not p.is_file():
            raise SystemExit(f"no such stream: {p}")
        runs.append((label, load_modes(p), palette[i % len(palette)]))

    radius = 14.0 if ridx == 0 else 30.0
    out = make_figure(runs, radius_label, ridx, scale, args.out, radius)
    print(f"wrote {out}")
    window = target_window(radius)
    for label, data, _ in runs:
        gap = window[0] - data["t"][-1]
        print(
            f"  {label}: stream ends t = {data['t'][-1]:.2f}, "
            f"{gap:+.2f} from the start of the target window"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
