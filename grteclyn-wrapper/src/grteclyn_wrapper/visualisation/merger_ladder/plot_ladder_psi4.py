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
EXTRACTION_RADIUS = 14.0
TARGET_WINDOW = (
    COLLAPSE_SOURCE[0] + EXTRACTION_RADIUS,
    COLLAPSE_SOURCE[1] + EXTRACTION_RADIUS,
)

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


def _plot_channel(ax, runs, m, ridx, scale, title, ylabel):
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
        *TARGET_WINDOW,
        color="tab:green",
        alpha=0.13,
        zorder=0,
        label=f"collapse signature at R = {EXTRACTION_RADIUS:g}",
    )
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")


def make_figure(runs, radius_label, ridx, scale, out_path: Path) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    _plot_channel(
        axes[0],
        runs,
        m=2,
        ridx=ridx,
        scale=scale,
        title="Spinning quadrupole (l = 2, m = 2) -- the binary channel",
        ylabel=r"$|\Psi_4|$",
    )
    _plot_channel(
        axes[1],
        runs,
        m=0,
        ridx=ridx,
        scale=scale,
        title="Axisymmetric channel (l = 2, m = 0) -- the head-on-style burst",
        ylabel=r"$|\Psi_4|$",
    )

    axes[1].set_xlabel("t  (code units)")
    right = max(TARGET_WINDOW[1] + 2.0, max(d["t"][-1] for _, d, _ in runs) + 2.0)
    axes[1].set_xlim(left=min(d["t"][0] for _, d, _ in runs) - 1.0, right=right)

    fig.suptitle(
        f"Wormhole merger: Psi4 l = 2 at {radius_label} across the refinement ladder\n"
        "crosses mark each run's NaN death; the shaded band is the collapse "
        "signature we are trying to reach",
        fontsize=12,
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
    # R = 30 amplitudes are compared after the 1/R falloff is divided out.
    scale = 1.0 if ridx == 0 else 30.0 / 14.0
    radius_label = (
        "R = 14" if ridx == 0 else "R = 30 (scaled by R/14)"
    )

    palette = ["#777777", "tab:blue", "tab:red", "tab:green", "tab:purple"]
    runs = []
    for i, spec in enumerate(args.run):
        label, _, path = spec.partition("=")
        p = Path(path)
        if not p.is_file():
            raise SystemExit(f"no such stream: {p}")
        runs.append((label, load_modes(p), palette[i % len(palette)]))

    out = make_figure(runs, radius_label, ridx, scale, args.out)
    print(f"wrote {out}")
    for label, data, _ in runs:
        gap = TARGET_WINDOW[0] - data["t"][-1]
        print(
            f"  {label}: stream ends t = {data['t'][-1]:.2f}, "
            f"{gap:+.2f} from the start of the target window"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
