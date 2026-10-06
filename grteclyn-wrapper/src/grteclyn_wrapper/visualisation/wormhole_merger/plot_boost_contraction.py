#!/usr/bin/env python3
r"""The moving throat's Lorentz contraction at t = 0: its shape against p, on 1/gamma.

A throat with ADM momentum p = gamma m v is the exact drainhole boosted to speed
v = p / sqrt(m^2 + p^2) and cut at lab time 0 (wormhole_momentum_model = 1;
BinaryWormholeInitialData, "EXACT BOOST").  In lab coordinates every field of
the slice is a function of the REST-FRAME radius r = |x + (gamma - 1)(e.x) e|:
chi = Psi^-4 det(G)^-1/3 with Psi = e^{-u/2} sqrt(Omega) and det G = 1 + eps(r).
So every chi contour, the throat's included, is an ellipsoid squashed along the
motion by exactly

    1/gamma = m / sqrt(m^2 + p^2).

Measured here on the t = 0 plotfile of one throat per p (level 3, dx = 0.0625,
m = 1, a = 2): chi on a covering grid about the throat, a cubic interpolant
along rays from the centre, and the distance at which chi crosses the value it
has at r = r_c across the motion, for r_c = 1.0, 1.55 (the throat, the areal
radius's minimum at rest) and 2.5.  Axis ratio = mean distance along the motion
(+-y) / mean across it (+-x, +-z).  Bowen-York data (momentum_model = 0, a round
throat with its scalar at rest) are measured for reference from the chi slice
caches of the momentum probes: round at every p (0.998-0.999, the slice
method's own reading at p = 0 being 0.998).  They are kept in the table and
not drawn, since the two methods differ at that level.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_boost_contraction --measure
    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_boost_contraction

``--measure`` reads the runs' t = 0 plotfiles (node-local scratch, through each
run dir's ``scratch`` link) and writes the table and the slices the figure
reads into the pack: ``campaign/02_moving_throat/boost_contraction_t0.tsv`` and
``..._slices.npz``.  The figure reads the pack alone and writes
``figures/02_moving_throat/boost_contraction``.

WHY (the user, 2026-09-29 ~16:55 UTC): the article's section on the boosted
setup needs "the plot for different p of the shape change of the throat,
connected with the analytic equation -- the good proof that it's valid".

STYLE: the house grammar -- ink points, the one gold accent for the analytic
law, grey for the reference, keys above the frames.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, RUNS_ROOT, figure_dir, find_run)

GROUP = "02_moving_throat"
TABLE = "boost_contraction_t0.tsv"
SLICES = "boost_contraction_t0_slices.npz"
# One exact-boost throat per p: the t = 0 shape set (2026-09-29).
RUNS = ((0.0, "t0_single_boost_p000_lbc"), (0.12, "t0_single_boost_p012_lbc"),
        (0.25, "t0_single_boost_p025_lbc"), (0.35, "t0_single_boost_p035_lbc"),
        (0.45, "t0_single_boost_p045_lbc"))
# Bowen-York reference (momentum_model = 0): the momentum probes' t = 0 slices.
BOWEN_YORK = ((0.0, "single_rest_csm_t050"), (0.12, "single_boost_p012_csm_t050"),
              (0.45, "single_boost_p045_csm_t050"))
RADII = (1.0, 1.55, 2.5)     # contour levels: chi at this distance across the motion
SLICE_KEEP = ("p0.00", "p0.45")   # the slices panel (a) draws, kept in the pack
THROAT = 1.55
HALF, LEVEL, MASS = 3.4, 3, 1.0


def inverse_gamma(p, m: float = MASS):
    """1/gamma = m / sqrt(m^2 + p^2)."""
    return m / np.sqrt(m * m + np.asarray(p, dtype=float) ** 2)


def _params(run_dir: pathlib.Path) -> dict[str, list[float]]:
    out = {}
    for line in (run_dir / "params.txt").read_text().splitlines():
        m = re.match(r"^\s*([A-Za-z0-9_.]+)\s*=\s*([^#]*)", line)
        if m:
            try:
                out[m.group(1)] = [float(x) for x in m.group(2).split()]
            except ValueError:
                pass
    return out


def _crossing(values: np.ndarray, s: np.ndarray, level: float) -> float:
    """First s where values (increasing outward from the pit) reach level."""
    k = int(np.argmax(values >= level))
    if k == 0:
        raise ValueError("level not bracketed along the ray")
    f0, f1 = values[k - 1], values[k]
    return float(s[k - 1] + (level - f0) / (f1 - f0) * (s[k] - s[k - 1]))


def _ratios(sample, radii=RADII) -> dict[float, tuple[float, float, float]]:
    """{r_c: (along, across, along/across)} for a sampler sample(dirs, s) ->
    chi along the unit directions (rows of dirs) at distances s."""
    s = np.arange(0.25, HALF - 0.2, 0.002)
    along_dirs = np.array([[0, 1, 0], [0, -1, 0]], float)
    across_dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]], float)
    along_v = sample(along_dirs, s)
    across_v = sample(across_dirs, s)
    out = {}
    for rc in radii:
        k = int(np.argmin(np.abs(s - rc)))
        level = float(np.mean(across_v[:, k]))
        a = np.mean([_crossing(v, s, level) for v in along_v])
        c = np.mean([_crossing(v, s, level) for v in across_v])
        out[rc] = (a, c, a / c)
    return out


def measure_plotfile(plt_dir: pathlib.Path, centre: np.ndarray):
    """Axis ratios at RADII from the 3D t = 0 plotfile, and the chi slice through
    the centre (x across, y along) for the figure."""
    import yt
    from scipy.ndimage import map_coordinates
    yt.set_log_level(50)
    ds = yt.load(str(plt_dir))
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - LEVEL)
    n = int(round(2 * HALF / dx))
    lo = centre - HALF
    cg = ds.covering_grid(LEVEL, left_edge=lo, dims=[n] * 3)
    chi = np.asarray(cg["boxlib", "chi"], dtype=np.float64)

    def at(points: np.ndarray) -> np.ndarray:           # points (..., 3), physical
        idx = (points - lo) / dx - 0.5
        return map_coordinates(chi, np.moveaxis(idx, -1, 0), order=3, mode="nearest")

    def sample(dirs, s):
        pts = centre[None, None, :] + dirs[:, None, :] * s[None, :, None]
        return at(pts)

    ratios = _ratios(sample)
    g = np.arange(-3.0, 3.0001, 0.02)
    X, Y = np.meshgrid(g, g, indexing="xy")
    plane = np.stack([centre[0] + X, centre[1] + Y, np.full_like(X, centre[2])], axis=-1)
    return ratios, g, at(plane).astype(np.float32), float(ds.current_time)


def measure_slice_cache(run_dir: pathlib.Path, centre_xy: np.ndarray):
    """The same axis ratios from a run's z-slice cache at t = 0 (x across, y along):
    for runs whose plotfiles are gone (the Bowen-York probes)."""
    from scipy.ndimage import map_coordinates
    d = np.load(run_dir / "frames" / "_slice_cache" / "chi_z" / "slice_0000.npz")
    arr = d["arr"].astype(np.float64)                  # arr[row = y, col = x]
    x0, x1, y0, y1 = (float(v) for v in d["extent"])
    ny, nx = arr.shape
    hx, hy = (x1 - x0) / nx, (y1 - y0) / ny

    def sample(dirs, s):
        out = []
        for dvec in dirs:
            if dvec[2] != 0:                           # no z in a z slice: use x again
                dvec = np.array([dvec[2], 0, 0])
            px = centre_xy[0] + dvec[0] * s
            py = centre_xy[1] + dvec[1] * s
            out.append(map_coordinates(arr, [(py - y0) / hy - 0.5, (px - x0) / hx - 0.5],
                                       order=3, mode="nearest"))
        return np.array(out)

    return _ratios(sample)


def measure(pack_root=PACK_ROOT, runs_root=RUNS_ROOT) -> pathlib.Path:
    rows, slices = [], {}
    for p, name in RUNS:
        run = find_run(runs_root, name)
        prm = _params(run)
        centre = np.array(prm["center"]) + np.array(prm["wormhole_centerA"])
        ratios, g, sl, t = measure_plotfile(run / "scratch" / "BinaryWormholePlt00000", centre)
        slices[f"p{p:.2f}"] = sl
        for rc, (a, c, q) in ratios.items():
            rows.append(("exact_boost", p, rc, a, c, q, float(inverse_gamma(p)), name))
        print(f"[contraction] {name}: t = {t:g}, ratio at r_c = 1.55: "
              f"{ratios[THROAT][2]:.5f} (1/gamma {float(inverse_gamma(p)):.5f})")
    for p, name in BOWEN_YORK:
        run = find_run(runs_root, name)
        prm = _params(run)
        centre = np.array(prm["center"]) + np.array(prm["wormhole_centerA"])
        ratios = measure_slice_cache(run, centre[:2])
        for rc, (a, c, q) in ratios.items():
            rows.append(("bowen_york_slice", p, rc, a, c, q, 1.0, name))
        print(f"[contraction] {name} (Bowen-York, slice cache): ratio at r_c = 1.55: "
              f"{ratios[THROAT][2]:.5f}")
    out_dir = pathlib.Path(pack_root) / "campaign" / GROUP
    tsv = out_dir / TABLE
    with tsv.open("w", encoding="utf-8") as f:
        f.write("# The moving throat's t = 0 axis ratio (along/across the motion) of the chi\n"
                "# contour through r_c across the motion; m = 1, a = 2, level 3.  Written by\n"
                "# plot_boost_contraction --measure.  exact_boost: the 3D t = 0 plotfile;\n"
                "# bowen_york_slice: the z = 32 chi slice cache (momentum_model = 0).\n")
        f.write("setup\tp\tr_c\talong\tacross\tratio\tinv_gamma\trun\n")
        for r in rows:
            f.write(f"{r[0]}\t{r[1]:.2f}\t{r[2]:.2f}\t{r[3]:.6f}\t{r[4]:.6f}\t{r[5]:.6f}"
                    f"\t{r[6]:.6f}\t{r[7]}\n")
    g = np.arange(-3.0, 3.0001, 0.02)
    keep = np.abs(g) <= 2.0 + 1e-9                     # the panel shows |x|, |y| < 1.9
    np.savez_compressed(out_dir / SLICES, grid=g[keep],
                        **{k: v[np.ix_(keep, keep)] for k, v in slices.items() if k in SLICE_KEEP})
    print(f"[contraction] wrote {tsv} and {out_dir / SLICES}")
    return tsv


def _table(pack_root=PACK_ROOT):
    rows = []
    for line in (pathlib.Path(pack_root) / "campaign" / GROUP / TABLE).read_text().splitlines():
        if line.startswith("#") or line.startswith("setup"):
            continue
        f = line.split("\t")
        rows.append((f[0], float(f[1]), float(f[2]), float(f[5]), float(f[6])))
    return rows


def figure(pack_root=PACK_ROOT):
    rows = _table(pack_root)
    sl = np.load(pathlib.Path(pack_root) / "campaign" / GROUP / SLICES)
    g = sl["grid"]
    fig, axes = plt.subplots(1, 3, figsize=(7.05, 2.35), constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[1.0, 1.25, 1.25]))
    ax_a, ax_b, ax_c = axes

    # (a) the throat's chi contour in the plane through its centre, at rest and
    # at the fastest p, on the analytic ellipse x^2 + (gamma y)^2 = r_t^2.
    # Line weights and limits tightened 2026-09-30 (the user: "looks childish,
    # update it for the PRD level style"): hairline contours, the frame cut to
    # the contours' own span, the house base size (10, as the other strips).
    shown = ((0.0, style.FAINT, 0.9, r"$p=0$"),
             (0.45, style.INK, 1.1, r"$p=0.45$ ($v=0.41$)"))
    th = np.linspace(0, 2 * np.pi, 400)
    handles = []
    i0 = int(np.argmin(np.abs(g - THROAT)))
    j0 = int(np.argmin(np.abs(g - 0.0)))
    for p, col, lw, lab in shown:
        z = sl[f"p{p:.2f}"]
        level = float(z[j0, i0])                       # chi at (x = r_t, y = 0)
        ax_a.contour(g, g, z, levels=[level], colors=[col], linewidths=lw, zorder=3)
        handles.append((Line2D([], [], color=col, lw=lw), lab))
    # The analytic throat of the moving one: the rest-frame sphere r = r_t.
    ax_a.plot(THROAT * np.cos(th), THROAT * float(inverse_gamma(0.45)) * np.sin(th),
              color=style.GOLD, lw=1.0, linestyle=(0, (3, 2)), zorder=4)
    handles.append((Line2D([], [], color=style.GOLD, lw=1.0, linestyle=(0, (3, 2))),
                    r"$x^2+\gamma^2y^2=r_t^2$"))
    # The same law continued toward the disc limit (the user, 2026-09-30:
    # "update panel (a) with a few extra ellipses", then "less ellipses pls"
    # -- three read busy, two stay): prediction alone, no data behind these
    # -- panel (b)'s curve past the measured range, drawn as shapes.
    for v in (0.7, 0.95):
        gy = math.sqrt(1.0 - v * v)
        ax_a.plot(THROAT * np.cos(th), THROAT * gy * np.sin(th),
                  color=style.GOLD, lw=0.7, linestyle=(0, (3, 2)), zorder=2)
        # Inside its own arc: above it the tag ran into the v = 0.41 pair.
        ax_a.text(0.0, THROAT * gy - 0.08, rf"$v={v:g}$", fontsize=6,
                  color=style.GOLD, ha="center", va="top")
    ax_a.set_aspect("equal")
    ax_a.set_xlim(-1.75, 1.75)
    ax_a.set_ylim(-1.75, 1.75)
    ax_a.set_xticks([-1, 0, 1])
    ax_a.set_yticks([-1, 0, 1])
    ax_a.set_xlabel(r"$x$ (across)")
    ax_a.set_ylabel(r"$y$ (along the motion)")
    style.legend_top(ax_a, handles, ncol=2)

    # (b) the axis ratio against the boost speed, on 1/gamma -- no free
    # parameter -- drawn to v = c, where the throat flattens to a disc (the
    # user, 2026-09-30: "lets also plot predictions till v = c").  The speed
    # axis is the one on which the law reaches its limit: v = 1 is p = inf.
    vs = np.linspace(0.0, 1.0, 400)
    ax_b.plot(vs, np.sqrt(1.0 - vs * vs), color=style.GOLD, lw=1.1, zorder=2)
    eb = [(p / math.sqrt(1.0 + p * p), q)
          for s, p, rc, q, _ in rows if s == "exact_boost" and rc == THROAT]
    ax_b.plot(*zip(*eb), linestyle="none", marker="o", ms=2.8, color=style.INK, zorder=4)
    ax_b.set_xlim(-0.02, 1.02)
    ax_b.set_ylim(0.0, 1.06)
    ax_b.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax_b.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax_b.set_xlabel(r"$v$ (boost speed, $c=1$)")
    ax_b.set_ylabel("axis ratio along/across")
    keys_b = [(Line2D([], [], color=style.GOLD, lw=1.1), r"$1/\gamma=\sqrt{1-v^2}$"),
              (Line2D([], [], linestyle="none", marker="o", ms=2.8, color=style.INK),
               "measured (throat contour)")]
    style.legend_top(ax_b, keys_b, ncol=1, borderpad=0.6)

    # (c) the residual at the three contour levels.  The axis hugs the data
    # (all of it within 6e-5, on the positive side): the old symmetric +-0.1
    # band was three quarters empty and read the residuals as scatter.
    marks = {1.0: ("v", style.MUTED), THROAT: ("o", style.INK), 2.5: ("^", style.CONTEXT)}
    keys_c = []
    res = [(rc, p / math.sqrt(1.0 + p * p), 1e3 * (q - ig))
           for s, p, rc, q, ig in rows if s == "exact_boost"]
    for rc, (mk, col) in marks.items():
        pts = [(v, r) for c, v, r in res if c == rc]
        ax_c.plot(*zip(*pts), linestyle="none", marker=mk, ms=2.8, color=col, zorder=3)
        keys_c.append((Line2D([], [], linestyle="none", marker=mk, ms=2.8, color=col),
                       rf"$r_c={rc:g}$"))
    ax_c.axhline(0.0, color=style.GOLD, lw=1.0, zorder=2)
    ax_c.set_xlim(-0.015, 0.43)
    hi = max(r for _, _, r in res)
    lo = min(0.0, min(r for _, _, r in res))
    ax_c.set_ylim(lo - 0.12 * (hi - lo) - 0.006, hi + 0.25 * (hi - lo))
    ax_c.set_xlabel(r"$v$")
    ax_c.set_ylabel(r"$10^3\,(\mathrm{ratio}-1/\gamma)$")
    style.legend_top(ax_c, keys_c, ncol=3, borderpad=0.6)
    style.tag_keys(fig, axes, ["(a)", "(b)", "(c)"])
    return fig


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true",
                    help="read the t = 0 plotfiles and write the table and slices first")
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.measure:
        measure(args.pack_root, args.runs_root)
    style.prd(base=10.0)
    fig = figure(args.pack_root)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "boost_contraction.png")
    problems = style.label_audit(fig)
    for msg in problems:
        print(f"[contraction] label audit: {msg}")
    png = style.save(fig, out)
    print(f"[contraction] wrote {png} (+pdf); label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
