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
    t = 0 value (the stationary background's own curvature), against t - R: the
    consumer's stream already carries the factor r, so nothing here multiplies
    by R; the imaginary part stays below 1.1e-3 of the real one (axisymmetry);
(c) the three extrema of (b) at each radius, in absolute value: the first
    trough (t - R in 68-81), the peak (81-93) and the second trough (93-106);
(d) the speed of each extremum between neighbouring spheres, Delta R over the
    difference of its arrival times (each time the vertex of a parabola through
    the three samples about the extremum), against the speed of light over the
    same stretch, Delta R / int dr / c(r) with c = alpha sqrt(chi) - beta^r, the
    radial null speed in these coordinates (conformal metric ~ flat there), read
    on the equator from the run's slice cache over t = 100-145.

Outcome: the throat collapses as in the L = 64 hold (the deficits differ by at
most 3.2e-4 of R_eq(0) through t = 100), so the box and the sponge never reach
it; the wave has one shape in t - R at all five radii, and r Psi4 is flat in
R, a radiative field: over R = 30-45 the peak (2.05e-4 to 2.02e-4) holds to
1.5 %, the troughs to 7.2 % and 2.4 %; R = 14-18 differ more (the peak 2.27e-4
at R = 14).  It travels at the speed of light: over R = 30-45 its extrema move
at 0.951-0.963 in coordinate units (fits through R = 30, 40, 45), where light
moves at 0.94-0.95 (the lapse and conformal factor of the mass-1.1 background;
c = 1 only far out): within 1 % of light over R = 40-45 and 2.5 % over 30-40.
Further in they run ahead of light, 4-5 % over R = 18-30 and up to 15 % over
14-18, as the near-field part fades and moves the extrema in t - R (an
extremum is not a signal front).  Each panel's numbers are printed.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_farzone_wave
    ... plot_farzone_wave --palette house
    ... plot_farzone_wave --colors "#c6dbef,#9ecae1,#4292c6,#2171b5,#08306b"

Colours (``--palette``): ``rgb``, the spinning paper's scheme and the default,
draws the radii in its blue, light (R = 14) to dark (R = 45), and the speed of
light in its red; ``house`` is the house ordinal ramp with an ink light speed.
``--colors`` takes five colours, innermost radius first.

Reads the packed runs under ``results/spinningwormhole/campaign/`` and, for (d),
the far-zone run's slice cache under ``runs/``; writes
``results/spinningwormhole/figures/farzone_wave_02c`` (PNG + PDF) and the same
figure into the run's ``figures/farzone_wave``.
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
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"
FARZONE = "spin_hold_L128_ml3_J100_full_farfix_t150"
HOLD = "spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100"
RUN_DIR = solutions.REPO / "runs" / "spinning_wormhole" / "drainhole" / "00_paper_runs" / FARZONE
# the extrema of (c) and (d), as windows in t - R
FEATURES = (("trough 1", (68.0, 81.0)), ("peak", (81.0, 93.0)), ("trough 2", (93.0, 106.0)))
T_HOLD = 100.0              # the L = 64 hold's stop: the throat comparison runs to here
T_QUIET = 40.0              # before this r Psi4 stays below 1e-6 (printed)
U_RANGE = (30.0, 110.0)     # (b)'s window in t - R
T_LIGHT = np.arange(100.0, 146.0, 5.0)   # the slices the light speed is averaged over
R_FAR = 30.0                # the far zone: the speed fits use R >= this
SPIN_BLUE, SPIN_RED = "#1f77b4", "#d62728"


def blue_ramp(n: int) -> tuple[str, ...]:
    """``n`` steps of the spinning blue, light to dark, the lightest still a line on white."""
    base = np.array(mcolors.to_rgb(SPIN_BLUE))
    light, dark = base + 0.55 * (1.0 - base), base * 0.45
    return tuple(mcolors.to_hex(light + (dark - light) * x) for x in np.linspace(0.0, 1.0, n))


# 2026-10-13: the spinning paper colours red / green / blue; gold is the merger paper's accent.
PALETTES = {
    "rgb": dict(radii=blue_ramp, light=SPIN_RED),
    "house": dict(radii=style.ordinal, light=style.INK),
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
    """Per feature, (R, arrival time, r Psi4) of the extremum inside its window,
    the time and value from the parabola through the three samples about it."""
    out = {}
    for name, (u0, u1) in FEATURES:
        rows = []
        for r, w in waves.items():
            u = t - r
            m = np.flatnonzero((u >= u0) & (u <= u1))
            if not m.size or u[m[-1]] < u1 - 1.0:      # the window not fully inside the run
                continue
            y = w.real
            j = m[np.argmax(y[m]) if name == "peak" else np.argmin(y[m])]
            y0, y1, y2 = y[j - 1], y[j], y[j + 1]
            s = 0.5 * (y0 - y2) / (y0 - 2.0 * y1 + y2)  # the vertex, in samples from j
            rows.append((r, t[j] + s * (t[j + 1] - t[j]), y1 - 0.25 * (y0 - y2) * s))
        out[name] = rows
    return out


def light_speed() -> tuple[np.ndarray, np.ndarray] | None:
    """The radial null speed alpha sqrt(chi) - beta^r on the equator, averaged over
    rings and over the slices at T_LIGHT, from the run's slice cache; None without it."""
    cache = RUN_DIR / "frames" / "_slice_cache"
    if not cache.is_dir():
        return None
    files = {f: sorted((cache / f"{f}_z").glob("*.npz")) for f in ("lapse", "chi", "shift1", "shift2")}
    times = np.array([float(np.load(p)["time"]) for p in files["lapse"]])
    radii = np.arange(10.0, 48.01, 0.25)
    profiles = []
    for tt in T_LIGHT:
        k = int(np.argmin(np.abs(times - tt)))
        alpha, chi, bx, by = (np.load(files[f][k])["arr"] for f in ("lapse", "chi", "shift1", "shift2"))
        e = np.load(files["lapse"][k])["extent"]
        ny, nx = alpha.shape
        x = np.linspace(e[0], e[1], nx) - 0.5 * (e[0] + e[1])
        y = np.linspace(e[2], e[3], ny) - 0.5 * (e[2] + e[3])
        X, Y = np.meshgrid(x, y)
        r = np.hypot(X, Y)
        c = alpha * np.sqrt(np.clip(chi, 0.0, None)) - (bx * X + by * Y) / np.maximum(r, 1e-9)
        profiles.append([np.nanmean(c[np.abs(r - rr) < 0.3]) for rr in radii])
    return radii, np.mean(profiles, axis=0)


def speeds(feats, light):
    """Per feature, (R_mid, measured speed, light's speed over the same stretch) per neighbouring pair."""
    out = {}
    for name, rows in feats.items():
        r, ta, _ = np.array(rows).T
        pairs = []
        for (ra, tA), (rb, tB) in zip(zip(r, ta), zip(r[1:], ta[1:])):
            v_light = np.nan
            if light is not None:
                rr = np.linspace(ra, rb, 200)
                v_light = (rb - ra) / np.trapezoid(1.0 / np.interp(rr, *light), rr)
            pairs.append((0.5 * (ra + rb), (rb - ra) / (tB - tA), v_light))
        out[name] = pairs
    return out


def draw(t, waves, throat, look, light) -> plt.Figure:
    style.prd(8.0)
    fig, ax = plt.subplot_mosaic([["a", "b"], ["c", "d"]], figsize=(7.0, 4.8), layout="constrained")
    radii = sorted(waves)
    lines = style.ordinal_series(len(radii), lw=1.1)
    for line, c in zip(lines, look["radii"]):
        line["color"] = c

    # (a) the throat, both boxes, and the difference of their deficits
    (tf, df), (th, dh) = throat["far"], throat["hold"]
    keep = tf <= T_HOLD
    diff = np.abs(df[keep] - np.interp(tf[keep], th, dh))
    entries = [(ax["a"].plot(tf, df, color=style.INK, lw=1.3)[0], r"$L=128$, $N=256$"),
               (ax["a"].plot(th, dh, color=style.CONTEXT, lw=1.1, ls=(0, (4.0, 2.0)))[0],
                r"$L=64$, $N=128$"),
               (ax["a"].plot(tf[keep], diff, color=style.MUTED, lw=0.7)[0], "difference")]
    ax["a"].set(yscale="log", ylim=(1e-7, 1.0), xlim=(0.0, tf[-1]), xlabel=r"$t$",
                ylabel=r"$1-R_{\rm eq}/R_{\rm eq}(0)$")
    style.legend_top(ax["a"], entries, ncol=3)

    # (b) the wave against t - R
    handles = [(ax["b"].plot(t - r, 1e4 * waves[r].real, **line)[0], rf"$R={r:g}$")
               for r, line in zip(radii, lines)]
    ax["b"].axhline(0.0, color=style.GRID, lw=0.6, zorder=0)
    ax["b"].set(xlim=U_RANGE, xlabel=r"$t-R$", ylabel=r"$10^4\, r\,\Delta\psi_4^{20}$")
    style.legend_top(ax["b"], handles, ncol=len(radii))

    # (c) the extrema against R; (d) their speed between neighbouring spheres
    feats = extrema(t, waves)
    marks = {"trough 1": dict(marker="o", mfc="none", color=style.CONTEXT),
             "peak": dict(marker="o", color=style.INK),
             "trough 2": dict(marker="s", mfc="none", color=style.CONTEXT)}
    entries_d, entries_e = [], []
    for name, rows in feats.items():
        r, _, y = np.array(rows).T
        entries_d.append((ax["c"].plot(r, 1e4 * np.abs(y), ls="-", lw=0.7, ms=4.0, **marks[name])[0], name))
    vel = speeds(feats, light)
    for name, pairs in vel.items():
        rm, v, _ = np.array(pairs).T
        entries_e.append((ax["d"].plot(rm, v, ls="-", lw=0.7, ms=4.0, **marks[name])[0], name))
    if light is not None:
        rm, _, vl = np.array(vel["peak"]).T
        entries_e.append((ax["d"].plot(rm, vl, color=look["light"], lw=1.1, marker="x", ms=4.5)[0],
                          "light, over the same stretch"))
    entries_e.append((ax["d"].axhline(1.0, color=style.MUTED, lw=0.8, ls=(0, (3.0, 2.0)), zorder=1),
                      r"$c=1$"))
    ax["c"].set(xlim=(10.0, 48.0), ylim=(0.0, 2.6), xlabel=r"$R$",
                ylabel=r"$10^4\, |r\,\Delta\psi_4^{20}|$ at the extremum")
    ax["d"].set(xlim=(10.0, 48.0), ylim=(0.84, 1.02), xlabel=r"$R$ (between neighbouring spheres)",
                ylabel=r"speed $\Delta R/\Delta t$")
    for key in ("c", "d"):
        ax[key].set_xticks(radii)
    # the marker handles' extent pads past the key's left edge: inset the key a little
    style.legend_top(ax["c"], entries_d, ncol=3, borderpad=0.6)
    style.legend_top(ax["d"], entries_e, ncol=3, borderpad=0.6)
    keys = ("a", "b", "c", "d")
    style.tag_keys(fig, [ax[k] for k in keys], [f"({k})" for k in keys])
    return fig


def report(t, waves, throat, light) -> None:
    (tf, df), (th, dh) = throat["far"], throat["hold"]
    keep = tf <= T_HOLD
    diff = np.abs(df[keep] - np.interp(tf[keep], th, dh))
    print(f"(a) deficit at t 60 / 100 / {tf[-1]:.0f}: far {np.interp(60, tf, df):.4f} / "
          f"{np.interp(100, tf, df):.4f} / {df[-1]:.4f}; hold {np.interp(60, th, dh):.4f} / "
          f"{np.interp(100, th, dh):.4f}; max |difference| to t {T_HOLD:g} {diff.max():.1e}")
    quiet = {r: np.abs(w[t <= T_QUIET]).max() for r, w in waves.items()}
    print("(b) max |r dPsi4| to t %g: " % T_QUIET + ", ".join(f"R {r:g} {q:.1e}" for r, q in quiet.items()))
    print("    max |Im| / max |Re|: " + ", ".join(
        f"R {r:g} {np.abs(w.imag).max() / np.abs(w.real).max():.1e}" for r, w in waves.items()))
    feats = extrema(t, waves)
    for name, rows in feats.items():
        ys = np.array([y for _, _, y in rows])
        far = np.array([abs(y) for r, _, y in rows if r >= R_FAR])
        print(f"(c) {name}: " + ", ".join(f"R {r:g} {y:+.3e} at t-R {ta - r:.1f}" for r, ta, y in rows)
              + f"; spread {100 * (np.abs(ys).max() / np.abs(ys).min() - 1):.1f} %, "
              f"over R >= {R_FAR:g} {100 * (far.max() / far.min() - 1):.1f} %")
    for name, pairs in speeds(feats, light).items():
        r, ta, _ = np.array(feats[name]).T
        far = r >= R_FAR
        fit = 1.0 / np.polyfit(r[far], ta[far], 1)[0]
        print(f"(d) {name}: " + ", ".join(f"R {rm:g}: {v:.3f} (light {vl:.3f})" for rm, v, vl in pairs)
              + f"; fit over R >= {R_FAR:g}: {fit:.3f}")
    if light is None:
        print("(d) no slice cache: the light speed is not drawn")
    else:
        print("(d) light, alpha sqrt(chi) - beta^r at R 14 / 30 / 45: " + " / ".join(
            f"{np.interp(r, *light):.3f}" for r in (14.0, 30.0, 45.0)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="output stem (default results/spinningwormhole/figures/farzone_wave_02c, "
                         "and the run's figures/farzone_wave)")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="rgb",
                    help="colour scheme (default rgb, the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="five comma-separated colours for the radii, innermost first")
    args = ap.parse_args(argv)

    t, waves = read_psi4(FARZONE)
    look = dict(PALETTES[args.palette])
    look["radii"] = look["radii"](len(waves))
    if args.colors:
        look["radii"] = tuple(c.strip() for c in args.colors.split(","))
        if len(look["radii"]) != len(waves):
            ap.error(f"--colors takes exactly {len(waves)} colours")
    throat = {"far": read_deficit(FARZONE), "hold": read_deficit(HOLD)}
    light = light_speed()
    fig = draw(t, waves, throat, look, light)
    problems = style.label_audit(fig)
    outs = [args.out] if args.out else [FIGURES / "farzone_wave_02c", RUN_DIR / "figures" / "farzone_wave"]
    pngs = [style.save(fig, out) for out in outs if out.parent.is_dir()]

    report(t, waves, throat, light)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    for png in pngs:
        print(f"wrote {png.relative_to(solutions.REPO) if png.is_relative_to(solutions.REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
