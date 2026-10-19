#!/usr/bin/env python3
r"""The 0.2c collapse's gravitational wave in the far zone: the L = 128, N = 256 run to t = 150.

The far-zone run is the paper 0.2c (the L = 64, N = 128 hold) on a box twice as
wide: the same refined boxes about the throat (+-16 / 8 / 4, so the same grid
inside r = 16), the base grid dx = 0.5 out to the face at 64, and a KO sponge at
r = 48-64 with no drive.

(a) the throat: the equatorial circumferential radius's deficit
    1 - R_eq / R_eq(0) (``throat_geometry.dat``) in the far-zone run and in the
    L = 64 hold, and the difference of the two deficits;
(b) the (l, m) = (2, 0) mode of r Psi4 at R = 14, 18, 30, 40, 45 minus its
    t = 0 value (the stationary background's own curvature), against t: the
    consumer's stream already carries the factor r, so nothing here multiplies
    by R; the imaginary part stays below 1.1e-3 of the real one (axisymmetry);
(c) the same against t - R;
(d) the three extrema of (c) at each radius, in absolute value: the first
    trough (t - R in 68-81), the peak (81-93) and the second trough (93-106).

Outcome: the throat collapses as in the L = 64 hold (the deficits differ by at
most 3.2e-4 of R_eq(0) through t = 100), so the box and the sponge never reach
it; the wave has one shape in t - R at all five radii, outgoing at c, and
r Psi4 is flat in R, a radiative field: over R = 30-45 the peak (2.05e-4 to
2.02e-4) holds to 1.3 %, the troughs to 6.5 % and 1.8 %; R = 14-18 differ more
(the peak 2.27e-4 at R = 14).  Each panel's numbers are printed.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_farzone_wave
    ... plot_farzone_wave --palette house
    ... plot_farzone_wave --colors "#c6dbef,#9ecae1,#4292c6,#2171b5,#08306b"

Colours (``--palette``): ``rgb``, the spinning paper's scheme and the default,
draws the radii in its blue, light (R = 14) to dark (R = 45); ``house`` is the
house ordinal ramp.  ``--colors`` takes five colours, innermost radius first.

Reads the packed runs under ``results/spinningwormhole/campaign/``; writes
``<the far-zone run>/figures/farzone_wave`` (PNG + PDF) unless ``--out`` says
otherwise.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign" / "drainhole" / "00_paper_runs"
FARZONE = "spin_hold_L128_ml3_J100_full_farfix_t150"
HOLD = "spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100"
RUNS = solutions.REPO / "runs" / "spinning_wormhole" / "drainhole" / "00_paper_runs"
# the extrema of (d), as windows in t - R
FEATURES = (("trough 1", (68.0, 81.0)), ("peak", (81.0, 93.0)), ("trough 2", (93.0, 106.0)))
T_HOLD = 100.0              # the L = 64 hold's stop: the throat comparison runs to here
T_FROM = 40.0               # (b) starts here: before it r Psi4 stays below 1e-6
U_RANGE = (30.0, 110.0)     # (c)'s window in t - R
TITLE = dict(loc="left", fontsize=7.0, pad=3.0)
SPIN_BLUE = "#1f77b4"


def blue_ramp(n: int) -> tuple[str, ...]:
    """``n`` steps of the spinning blue, light to dark, the lightest still a line on white."""
    base = np.array(mcolors.to_rgb(SPIN_BLUE))
    light, dark = base + 0.55 * (1.0 - base), base * 0.45
    return tuple(mcolors.to_hex(light + (dark - light) * x) for x in np.linspace(0.0, 1.0, n))


# 2026-10-13: the spinning paper colours red / green / blue; gold is the merger paper's accent.
PALETTES = {
    "rgb": blue_ramp,
    "house": style.ordinal,
}


def read_psi4(run: str) -> tuple[np.ndarray, dict[float, np.ndarray]]:
    """Time and, per radius, r Psi4^20 minus its t = 0 value (complex)."""
    path = PACKED / run / "psi4_mode_l2m0.dat"
    with open(path) as f:
        names = f.readline().split()[2:]
    data = np.loadtxt(path)
    radii = [float(n.split("=")[1].rstrip(")")) for n in names[::2]]
    return data[:, 0], {r: (data[:, 1 + 2 * i] - data[0, 1 + 2 * i])
                        + 1j * (data[:, 2 + 2 * i] - data[0, 2 + 2 * i]) for i, r in enumerate(radii)}


def read_deficit(run: str) -> tuple[np.ndarray, np.ndarray]:
    g = np.loadtxt(PACKED / run / "throat_geometry.dat")
    return g[:, 0], 1.0 - g[:, 1] / g[0, 1]


def extrema(t: np.ndarray, waves: dict[float, np.ndarray]) -> dict[str, list[tuple[float, float, float]]]:
    """Per feature, (R, t - R, r Psi4) of the extremum inside its window."""
    out = {}
    for name, (u0, u1) in FEATURES:
        rows = []
        for r, w in waves.items():
            u = t - r
            m = (u >= u0) & (u <= u1)
            if not m.any() or u[m][-1] < u1 - 1.0:      # the window not fully inside the run
                continue
            y = w.real[m]
            j = np.argmax(y) if name == "peak" else np.argmin(y)
            rows.append((r, u[m][j], y[j]))
        out[name] = rows
    return out


def draw(t, waves, throat, colours) -> plt.Figure:
    style.prd(8.0)
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.6), layout="constrained")
    (ax_a, ax_b), (ax_c, ax_d) = axes
    radii = sorted(waves)
    lines = style.ordinal_series(len(radii), lw=1.1)
    for line, c in zip(lines, colours):
        line["color"] = c

    # (a) the throat, both boxes, and the difference of their deficits
    (tf, df), (th, dh) = throat["far"], throat["hold"]
    keep = tf <= T_HOLD
    diff = np.abs(df[keep] - np.interp(tf[keep], th, dh))
    entries = [(ax_a.plot(tf, df, color=style.INK, lw=1.3)[0], r"$L=128$, $N=256$ (far zone)"),
               (ax_a.plot(th, dh, color=style.CONTEXT, lw=1.1, ls=(0, (4.0, 2.0)))[0],
                r"$L=64$, $N=128$ (the hold)"),
               (ax_a.plot(tf[keep], diff, color=style.MUTED, lw=0.7)[0], "their difference")]
    ax_a.set(yscale="log", ylim=(1e-7, 1.0), xlim=(0.0, tf[-1]), xlabel=r"$t$",
             ylabel=r"$1-R_{\rm eq}/R_{\rm eq}(0)$")
    style.legend_top(ax_a, entries, ncol=2)

    # (b) and (c): the wave against t and against t - R
    for ax, shift, xlim, xlabel in ((ax_b, False, (T_FROM, t[-1]), r"$t$"),
                                    (ax_c, True, U_RANGE, r"$t-R$")):
        handles = []
        for r, line in zip(radii, lines):
            x = t - r if shift else t
            handles.append((ax.plot(x, 1e4 * waves[r].real, **line)[0], rf"$R={r:g}$"))
        ax.axhline(0.0, color=style.GRID, lw=0.6, zorder=0)
        ax.set(xlim=xlim, xlabel=xlabel, ylabel=r"$10^4\, r\,\Delta\psi_4^{20}$")
        style.legend_top(ax, handles, ncol=len(radii))

    # (d) the extrema against R
    feats = extrema(t, waves)
    marks = {"trough 1": dict(marker="o", mfc="none", color=style.CONTEXT),
             "peak": dict(marker="o", color=style.INK),
             "trough 2": dict(marker="s", mfc="none", color=style.CONTEXT)}
    entries = []
    for name, rows in feats.items():
        r, _, y = np.array(rows).T
        entries.append((ax_d.plot(r, 1e4 * np.abs(y), ls="-", lw=0.7, ms=4.0, **marks[name])[0], name))
    ax_d.set(xlim=(10.0, 48.0), ylim=(0.0, 2.6), xlabel=r"$R$",
             ylabel=r"$10^4\, |r\,\Delta\psi_4^{20}|$ at the extremum")
    ax_d.set_xticks(radii)
    # the marker handles' extent pads past the key's left edge: inset the key a little
    style.legend_top(ax_d, entries, ncol=3, borderpad=0.6)
    style.tag_keys(fig, axes.flat, ["(a)", "(b)", "(c)", "(d)"])
    return fig


def report(t, waves, throat) -> None:
    (tf, df), (th, dh) = throat["far"], throat["hold"]
    keep = tf <= T_HOLD
    diff = np.abs(df[keep] - np.interp(tf[keep], th, dh))
    print(f"(a) deficit at t 60 / 100 / {tf[-1]:.0f}: far {np.interp(60, tf, df):.4f} / "
          f"{np.interp(100, tf, df):.4f} / {df[-1]:.4f}; hold {np.interp(60, th, dh):.4f} / "
          f"{np.interp(100, th, dh):.4f}; max |difference| to t {T_HOLD:g} {diff.max():.1e}")
    quiet = {r: np.abs(w[t <= T_FROM]).max() for r, w in waves.items()}
    print("(b) max |r dPsi4| to t %g: " % T_FROM + ", ".join(f"R {r:g} {q:.1e}" for r, q in quiet.items()))
    print("    max |Im| / max |Re|: " + ", ".join(
        f"R {r:g} {np.abs(w.imag).max() / np.abs(w.real).max():.1e}" for r, w in waves.items()))
    for name, rows in extrema(t, waves).items():
        ys = np.array([y for _, _, y in rows])
        print(f"(d) {name}: " + ", ".join(f"R {r:g} {y:+.3e} at t-R {u:.0f}" for r, u, y in rows)
              + f"; spread {100 * (np.abs(ys).max() / np.abs(ys).min() - 1):.1f} %")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="output stem (default <the far-zone run>/figures/farzone_wave)")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="rgb",
                    help="colour scheme (default rgb, the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="five comma-separated colours for the radii, innermost first")
    args = ap.parse_args(argv)

    t, waves = read_psi4(FARZONE)
    colours = PALETTES[args.palette](len(waves))
    if args.colors:
        colours = tuple(c.strip() for c in args.colors.split(","))
        if len(colours) != len(waves):
            ap.error(f"--colors takes exactly {len(waves)} colours")
    throat = {"far": read_deficit(FARZONE), "hold": read_deficit(HOLD)}
    fig = draw(t, waves, throat, colours)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out or RUNS / FARZONE / "figures" / "farzone_wave")

    report(t, waves, throat)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    print(f"wrote {png.relative_to(solutions.REPO) if png.is_relative_to(solutions.REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
