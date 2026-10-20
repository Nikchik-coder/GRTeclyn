#!/usr/bin/env python3
r"""The 0.2c collapse's gravitational wave in the far zone: the L = 128, N = 256 run to t = 150.

The far-zone run is the paper 0.2c (the L = 64, N = 128 hold) on a box twice as
wide: the same refined boxes about the throat (+-16 / 8 / 4, so the same grid
inside r = 16), the base grid dx = 0.5 out to the face at 64, and a KO sponge at
r = 48-64 with no drive.

(a) the (l, m) = (2, 0) mode of r Psi4 at R = 14, 18, 30, 40, 45 minus its
    t = 0 value (the stationary background's own curvature), against t - R: the
    consumer's stream already carries the factor r, so nothing here multiplies
    by R; the imaginary part stays below 1.1e-3 of the real one (axisymmetry);
(b) the wave against spin: the same mode at R = 14 for this run (the 0.2c)
    and the 0.30c (its t = 130 run), each against t - R - t10 with t10 the
    time its own equatorial deficit reaches 10 %, so the bursts align on each
    rung's collapse.  The static's line is the exact zero of spherical
    symmetry, dashed; its run confirms <= 4.2e-9 before it dies (NaN at
    horizon formation, trust 60) at u = -10.6, short of this window;
(c) the energy radiated in the (2, 0) mode over the burst (t - R - t10 in
    0-45, the pre-burst mean subtracted before integrating),
    E = 1/(16 pi) int |int r Psi4 dt'|^2 dt, over each rung's M_ADM, against
    the spin 8 pi J/A: at R = 18 and, as the measurement spread, R = 14;
(d) the speed of each extremum of (a) between neighbouring spheres, Delta R
    over the difference of its arrival times (each time the vertex of a
    parabola through the three samples about the extremum), against the speed
    of light over the same stretch, Delta R / int dr / c(r) with
    c = alpha sqrt(chi) - beta^r, the radial null speed in these coordinates,
    read on the equator from the run's slice cache over t = 100-145.

Axis labels carry only the quantity (decided 2026-10-20); everything else is
caption material, including the dropped panels' numbers: the far-zone throat
collapses as the L 64 hold's to <= 3.2e-4 of R_eq(0) through t = 100, and the
extrema of (a) are flat in R (the peak holds to 1.5 % over R = 30-45).

Outcome: the wave has one shape in t - R at all five radii, and r Psi4 is flat
in R, a radiative field: over R = 30-45 the peak (2.05e-4 to 2.02e-4) holds to
1.5 %, the troughs to 7.2 % and 2.4 %; R = 14-18 differ more (the peak 2.27e-4
at R = 14).  It grows with spin: aligned on each rung's collapse the 0.30c is
the 0.2c's shape at 1.5x the amplitude (R 14 peak +3.4e-4 vs +2.3e-4) and
2.6-2.8x the energy (E_20/M_ADM 8.0e-7 vs 2.9e-7 at R 18), while the static
stays below 4.2e-9 to its death -- a spherical collapse radiates nothing.
It travels at the speed of light: over R = 30-45 its extrema move
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

Reads only tracked files: the packed runs under
``results/spinningwormhole/campaign/``, the background tables' headers under
``results/spinningwormhole/backgrounds/`` (``headers``), and for (d) the
far-zone pack's ``light_speed_equator.dat``, which ``--light-from-cache``
rebuilds from the run's slice cache under ``runs/``.  Writes
``results/spinningwormhole/figures/farzone_wave_02c`` (PNG + PDF) and, where
``runs/`` holds the run, the same figure into its ``figures/farzone_wave``.

    ... plot_farzone_wave --light-from-cache
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import headers, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign" / "drainhole" / "00_paper_runs"
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"
FARZONE = "spin_hold_L128_ml3_J100_full_farfix_t150"
RUN_DIR = solutions.REPO / "runs" / "spinning_wormhole" / "drainhole" / "00_paper_runs" / FARZONE
# (d)'s light speed against R, kept in the run's pack: its 1.2 GB slice cache stays under runs/
LIGHT = PACKED / FARZONE / "light_speed_equator.dat"
# the rungs of (b) and (c): label, packed run, trust window, background table (None: the static)
SPINS = (
    ("D0", "static_hold_L64_ml3_spdrv0_farfix_t100", 60.0, None),
    ("D21", FARZONE, 150.0, "full_eta2_m1_J100"),
    ("D30", "spin_hold_L64_ml3_ve030a_spdrv0_farfix_t130", 130.0, "fam_a_ve030"),
)
M_STATIC = 1.0              # the massive drainhole's M (a = 2, M = 1): the static has no table
R_SPIN = 14.0               # (b)'s radius: the one every rung extracts
U_SPIN = (-25.0, 46.0)      # (b)'s window in t - R - t10
E_WINDOW = 45.0             # (c) integrates the burst over t - R - t10 in (0, this)
# the extrema of (a) and (d), as windows in t - R
FEATURES = (("trough 1", (68.0, 81.0)), ("peak", (81.0, 93.0)), ("trough 2", (93.0, 106.0)))
T_QUIET = 40.0              # before this r Psi4 stays below 1e-6 (printed)
U_RANGE = (30.0, 110.0)     # (a)'s window in t - R
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


def meta_float(table: str, key: str) -> float:
    """One ``meta <key> <value>`` line from a background table's packed header."""
    return float(headers.meta(table)[key])


def burst_energy(u: np.ndarray, w: np.ndarray) -> float | None:
    """E_20 = 1/(16 pi) int |int r Psi4 dt'|^2 dt over the burst (u in 0 to
    E_WINDOW), the pre-burst mean (u in -20 to 0) subtracted; None when the
    run does not cover the burst at this radius."""
    base = (u >= -20.0) & (u <= 0.0)
    burst = (u >= 0.0) & (u <= E_WINDOW)
    # the 0.30c's t = 130 covers u = 41.0 at R = 18 (its t10 70.001): the burst is
    # over by u ~ 40, so a window reaching 40 is enough
    if burst.sum() < 40 or not base.any() or u[burst][-1] < E_WINDOW - 5.0:
        return None
    y, uu = w[burst] - w[base].mean(), u[burst]
    news = np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(uu))])
    return float(np.trapezoid(np.abs(news) ** 2, uu)) / (16.0 * np.pi)


def rungs() -> list[dict]:
    """Per rung of SPINS: the R_SPIN waveform against t - R - t10 inside the
    trust window, the spin 8 pi J/A (% of extremal), M_ADM, and E_20 per radius."""
    out = []
    for label, run, trust, table in SPINS:
        t, waves = read_psi4(run)
        g = np.loadtxt(PACKED / run / "throat_geometry.dat")
        d = 1.0 - g[:, 1] / g[0, 1]
        j = int(np.flatnonzero(d >= 0.10)[0])
        t10 = float(np.interp(0.10, d[j - 1:j + 1], g[j - 1:j + 1, 0]))
        keep = t <= trust
        out.append(dict(
            label=label, t10=t10,
            frac=100.0 * meta_float(table, "J_over_A_extremal_frac") if table else 0.0,
            m_adm=meta_float(table, "M_ADM") if table else M_STATIC,
            u=t[keep] - R_SPIN - t10, w=waves[R_SPIN][keep],
            energies={r: burst_energy(t[keep] - r - t10, waves[r][keep]) for r in sorted(waves)}))
    return out


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
    """(d)'s light speed against R from the far-zone pack; None without it."""
    if not LIGHT.is_file():
        return None
    r, c = np.loadtxt(LIGHT, unpack=True)
    return r, c


def write_light(light: tuple[np.ndarray, np.ndarray]) -> None:
    """Keep the light speed in the far-zone pack, every digit (the figure reads it back)."""
    np.savetxt(LIGHT, np.column_stack(light), fmt="%.17g", delimiter="\t",
               header=f"radial null speed alpha sqrt(chi) - beta^r on the equator (z slice) of {FARZONE},\n"
                      f"averaged over rings |r - R| < 0.3 and the slices nearest t = "
                      f"{', '.join(f'{t:g}' for t in T_LIGHT)}\n"
                      "R\tc")


def light_speed_from_cache() -> tuple[np.ndarray, np.ndarray] | None:
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


def draw(t, waves, spins, look, light) -> plt.Figure:
    style.prd(8.0)
    # 2026-10-20: one row, a strip across the page top (the 2 x 2 grid took half a page)
    fig, ax = plt.subplot_mosaic([["a", "b", "c", "d"]], figsize=(7.05, 2.25), layout="constrained",
                                 width_ratios=(1.25, 1.15, 0.8, 1.0))
    radii = sorted(waves)
    lines = style.ordinal_series(len(radii), lw=1.1)
    for line, c in zip(lines, look["radii"]):
        line["color"] = c

    # (a) the wave against t - R, every radius
    handles = [(ax["a"].plot(t - r, 1e4 * waves[r].real, **line)[0], rf"$R={r:g}$")
               for r, line in zip(radii, lines)]
    ax["a"].axhline(0.0, color=style.GRID, lw=0.6, zorder=0)
    ax["a"].set(xlim=U_RANGE, xlabel=r"$t-R$", ylabel=r"$10^4\, r\,\Delta\psi_4^{20}$")
    ax["a"].set_xticks(np.arange(40.0, U_RANGE[1] + 1.0, 20.0))
    style.legend_top(ax["a"], handles, ncol=3)

    # (b) the wave against spin at R_SPIN, aligned on each rung's collapse.  The
    # static's line is the exact zero of spherical symmetry (dashed: a symmetry
    # statement, not a stream) -- the run confirms <= 4.2e-9 before it dies at
    # u = -10.6, short of this window.
    entries_b = []
    for sp, c in zip(spins, look["spins"]):
        if sp["label"] == "D0":
            entries_b.append((ax["b"].plot(U_SPIN, [0.0, 0.0], color=c, lw=0.9,
                                           ls=(0, (4.0, 2.0)))[0], sp["label"]))
        else:
            entries_b.append((ax["b"].plot(sp["u"], 1e4 * sp["w"].real, color=c, lw=1.1)[0],
                              sp["label"]))
    ax["b"].axhline(0.0, color=style.GRID, lw=0.6, zorder=0)
    ax["b"].set(xlim=U_SPIN, xlabel=r"$t-R-t_{10}$", ylabel=r"$10^4\, r\,\Delta\psi_4^{20}$")
    style.legend_top(ax["b"], entries_b, ncol=len(spins))

    # (c) the (2, 0) energy over M_ADM against spin, at R = 18 and 14
    entries_c = []
    for r, mark in ((18.0, dict(marker="o", color=style.INK)),
                    (14.0, dict(marker="o", mfc="none", color=style.CONTEXT))):
        x = [sp["frac"] for sp in spins]
        y = [1e7 * (sp["energies"].get(r) or 0.0) / sp["m_adm"] for sp in spins]
        entries_c.append((ax["c"].plot(x, y, ls="-", lw=0.7, ms=4.0, **mark)[0], rf"$R={r:g}$"))
    ax["c"].set(xlim=(-2.0, 22.0), ylim=(-0.4, 9.0), xlabel=r"$8\pi J/A$ [%]",
                ylabel=r"$10^7\, E_{20}/M_{\rm ADM}$")
    ax["c"].set_xticks([sp["frac"] for sp in spins], [f"{sp['frac']:.1f}" for sp in spins])
    style.legend_top(ax["c"], entries_c, ncol=1, borderpad=0.6)

    # (d) the extrema's speed between neighbouring spheres, against light
    feats = extrema(t, waves)
    marks = {"trough 1": dict(marker="o", mfc="none", color=style.CONTEXT),
             "peak": dict(marker="o", color=style.INK),
             "trough 2": dict(marker="s", mfc="none", color=style.CONTEXT)}
    entries_d = []
    vel = speeds(feats, light)
    for name, pairs in vel.items():
        rm, v, _ = np.array(pairs).T
        entries_d.append((ax["d"].plot(rm, v, ls="-", lw=0.7, ms=4.0, **marks[name])[0], name))
    if light is not None:
        rm, _, vl = np.array(vel["peak"]).T
        entries_d.append((ax["d"].plot(rm, vl, color=look["light"], lw=1.1, marker="x", ms=4.5)[0],
                          "light"))
    entries_d.append((ax["d"].axhline(1.0, color=style.MUTED, lw=0.8, ls=(0, (3.0, 2.0)), zorder=1),
                      r"$c=1$"))
    ax["d"].set(xlim=(10.0, 48.0), ylim=(0.84, 1.02), xlabel=r"$R$",
                ylabel=r"$\Delta R/\Delta t$")
    ax["d"].set_xticks(radii)
    # the marker handles' extent pads past the key's left edge: inset the key a little
    style.legend_top(ax["d"], entries_d, ncol=2, borderpad=0.6)
    keys = ("a", "b", "c", "d")
    style.tag_keys(fig, [ax[k] for k in keys], [f"({k})" for k in keys], row="last")
    return fig


def report(t, waves, spins, light) -> None:
    quiet = {r: np.abs(w[t <= T_QUIET]).max() for r, w in waves.items()}
    print("(a) max |r dPsi4| to t %g: " % T_QUIET + ", ".join(f"R {r:g} {q:.1e}" for r, q in quiet.items()))
    for sp in spins:
        burst = (sp["u"] >= 0.0) & (sp["u"] <= E_WINDOW)
        w = sp["w"].real
        if burst.any() and sp["label"] != "D0":
            print(f"(b) {sp['label']}: t10 {sp['t10']:.2f}; R {R_SPIN:g} trough {w[burst].min():+.2e} at "
                  f"u {sp['u'][burst][np.argmin(w[burst])]:.1f}, peak {w[burst].max():+.2e} at "
                  f"u {sp['u'][burst][np.argmax(w[burst])]:.1f}")
        else:
            print(f"(b) {sp['label']}: t10 {sp['t10']:.2f}; max |r dPsi4| {np.abs(w).max():.1e} "
                  f"to its end (u {sp['u'][-1]:.1f})")
        es = {r: e for r, e in sp["energies"].items() if e is not None}
        print(f"(c) {sp['label']}: M_ADM {sp['m_adm']:.3f}; E_20: "
              + (", ".join(f"R {r:g} {e:.2e} (/M {1e7 * e / sp['m_adm']:.2f}e-7)" for r, e in es.items())
                 if es else "no covered burst"))
    print("    max |Im| / max |Re|: " + ", ".join(
        f"R {r:g} {np.abs(w.imag).max() / np.abs(w.real).max():.1e}" for r, w in waves.items()))
    feats = extrema(t, waves)
    for name, rows in feats.items():
        ys = np.array([y for _, _, y in rows])
        far = np.array([abs(y) for r, _, y in rows if r >= R_FAR])
        print(f"(a) {name}: " + ", ".join(f"R {r:g} {y:+.3e} at t-R {ta - r:.1f}" for r, ta, y in rows)
              + f"; spread {100 * (np.abs(ys).max() / np.abs(ys).min() - 1):.1f} %, "
              f"over R >= {R_FAR:g} {100 * (far.max() / far.min() - 1):.1f} %")
    for name, pairs in speeds(feats, light).items():
        r, ta, _ = np.array(feats[name]).T
        far = r >= R_FAR
        fit = 1.0 / np.polyfit(r[far], ta[far], 1)[0]
        print(f"(d) {name}: " + ", ".join(f"R {rm:g}: {v:.3f} (light {vl:.3f})" for rm, v, vl in pairs)
              + f"; fit over R >= {R_FAR:g}: {fit:.3f}")
    if light is None:
        print("(d) no light speed in the far-zone pack: the light speed is not drawn")
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
    ap.add_argument("--light-from-cache", action="store_true",
                    help="recompute (d)'s light speed from the run's slice cache under runs/ "
                         "and rewrite the packed light_speed_equator.dat")
    args = ap.parse_args(argv)
    if args.light_from_cache:
        light = light_speed_from_cache()
        if light is None:
            ap.error(f"no slice cache under {RUN_DIR}")
        write_light(light)

    t, waves = read_psi4(FARZONE)
    look = dict(PALETTES[args.palette])
    look["spins"] = (style.CONTEXT,) + tuple(look["radii"](2))
    look["radii"] = look["radii"](len(waves))
    if args.colors:
        look["radii"] = tuple(c.strip() for c in args.colors.split(","))
        if len(look["radii"]) != len(waves):
            ap.error(f"--colors takes exactly {len(waves)} colours")
    spins = rungs()
    light = light_speed()
    fig = draw(t, waves, spins, look, light)
    problems = style.label_audit(fig)
    outs = [args.out] if args.out else [FIGURES / "farzone_wave_02c", RUN_DIR / "figures" / "farzone_wave"]
    pngs = [style.save(fig, out) for out in outs if out.parent.is_dir()]

    report(t, waves, spins, light)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    for png in pngs:
        print(f"wrote {png.relative_to(solutions.REPO) if png.is_relative_to(solutions.REPO) else png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
