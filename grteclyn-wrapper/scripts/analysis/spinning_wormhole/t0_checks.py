"""Step 3 checks of a fast-spin table on the 3D grid, from a run's plotfile.

For each run directory:

1. Throat radii.  The in-code ray minima of the first row of
   data/throat_geometry.dat (R_eq: min over the +x ray of sqrt(gamma_phiphi);
   R_pol: min over the +z ray of z sqrt(gamma_xx)) against the same minima
   taken on the table itself: min over eta of e^{-f/2} sqrt(eta^2 + eta0^2)
   on the equator (mu = 0) and on the axis (mu = 1, where nu = 0).  The
   table's meta R_eq / R_pol are different quantities (the value at the
   area throat, and the meridional circumference / 2 pi), so they are not
   the reference here.
2. Constraints.  Ham and |Mom| of the plotfile (the derived 'constraints'
   plot variables) as L2 norms over coordinate shells about the centre,
   each shell read on the finest level that covers it (the fixed nested
   boxes: level l >= 1 covers |x - c| < tagging_L 2^-(l+1)).  The puncture
   (r -> 0, the far infinity) sits in the innermost shells and is kept apart
   from the throat's; the in-code L2_Ham is level 0 over the whole box.

Several runs of one table at different N give the convergence factor and
order shell by shell (dx ratio from the runs' own base grids).

    python t0_checks.py <run dir> [<run dir> ...] [--index K]

--index picks the K-th plotfile still on scratch (0 = the earliest).
"""
from __future__ import annotations

import argparse
import glob
import math
import re
from pathlib import Path

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import read_spinbg

LEVEL3_EDGES = (0.125, 0.25, 0.5, 1.0, 2.0)


def read_params(run: Path) -> dict[str, str]:
    out = {}
    for line in (run / "params.txt").read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            out[k] = v.strip('"')
    return out


def table_ray_minima(path: str) -> tuple[float, float, float]:
    header, body = read_spinbg(path)
    eta0 = header["eta0"]
    x = np.linspace(header["x_min"], header["x_max"], header["n_x"])[1:-1]
    sqrt_h = np.sqrt((eta0 * np.tan(0.5 * math.pi * x)) ** 2 + eta0**2)
    f = body[:, 1:-1, 0]
    r_eq = float(np.min(np.exp(-0.5 * f[0]) * sqrt_h))
    r_pol = float(np.min(np.exp(-0.5 * f[-1]) * sqrt_h))
    return r_eq, r_pol, eta0


def shells(tag_l: float, max_level: int) -> list[tuple[int, float, float]]:
    """(level, r_in, r_out): each shell on the finest level covering it."""
    half = {lev: tag_l * 2.0 ** -(lev + 1) for lev in range(1, max_level + 1)}
    out = []
    edges = list(LEVEL3_EDGES) + [half[max_level]]
    for a, b in zip(edges, edges[1:]):
        out.append((max_level, a, b))
    for lev in range(max_level - 1, 0, -1):
        out.append((lev, half[lev + 1], half[lev]))
    out.append((0, half[1], 1.5 * half[1]))       # out to the sponge
    return out


def shell_norms(plt: str, centre: np.ndarray, spec) -> list[dict]:
    import yt
    yt.set_log_level(50)
    ds = yt.load(plt)
    acc = {s: np.zeros(4) for s in spec}          # ham2 dV, mom2 dV, dV, max
    for g in ds.index.grids:
        lev = g.Level
        mine = [s for s in spec if s[0] == lev]
        if not mine:
            continue
        dds = g.dds.d
        n = g.ActiveDimensions
        axes = [g.LeftEdge.d[i] + dds[i] * (np.arange(n[i]) + 0.5) - centre[i]
                for i in range(3)]
        X, Y, Z = np.meshgrid(*axes, indexing="ij")
        r = np.sqrt(X * X + Y * Y + Z * Z)
        rmin, rmax = r.min(), r.max()
        if all(rmax < a or rmin >= b for _, a, b in mine):
            continue
        ham = g["boxlib", "Ham"].d
        mom2 = sum(g["boxlib", f"Mom{i}"].d ** 2 for i in (1, 2, 3))
        dv = float(np.prod(dds))
        for s in mine:
            m = (r >= s[1]) & (r < s[2])
            if not m.any():
                continue
            a = acc[s]
            a[0] += float(np.sum(ham[m] ** 2)) * dv
            a[1] += float(np.sum(mom2[m])) * dv
            a[2] += float(m.sum()) * dv
            a[3] = max(a[3], float(np.max(np.abs(ham[m]))))
    rows = []
    for s in spec:
        a = acc[s]
        if a[2] > 0:
            rows.append({"level": s[0], "r_in": s[1], "r_out": s[2],
                         "L2_Ham": math.sqrt(a[0] / a[2]),
                         "L2_Mom": math.sqrt(a[1] / a[2]),
                         "max_Ham": a[3]})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--index", type=int, default=0)
    args = ap.parse_args()

    results = []
    for run in map(Path, args.runs):
        p = read_params(run)
        table = p["spinning_background_file"]
        centre = np.array([float(v) for v in p["center"].split()])
        dx0 = float(p["L"]) / float(p["N1"])
        plts = sorted(glob.glob(p["amr.plot_file"] + "[0-9]*"))
        plts = [q for q in plts if re.search(r"\d+$", q)]
        if len(plts) <= args.index:
            print(f"{run.name}: no plotfile #{args.index} on scratch")
            continue
        plt = plts[args.index]
        spec = shells(float(p["tagging_L"]), int(p["max_level"]))
        rows = shell_norms(plt, centre, spec)
        geo = np.loadtxt(run / "data" / "throat_geometry.dat", ndmin=2)
        l2 = np.loadtxt(run / "data" / "constraint_norms.dat", ndmin=2)
        r_eq_t, r_pol_t, eta0 = table_ray_minima(table)
        print(f"\n== {run.name}  ({Path(plt).name}, dx0 {dx0:.4g}, "
              f"table {Path(table).name})")
        print(f"  throat rays t=0: R_eq {geo[0, 1]:.6f} vs table "
              f"{r_eq_t:.6f} ({geo[0, 1] / r_eq_t - 1:+.2e}); R_pol "
              f"{geo[0, 2]:.6f} vs table {r_pol_t:.6f} "
              f"({geo[0, 2] / r_pol_t - 1:+.2e})")
        print(f"  in-code level-0 L2 t=0: Ham {l2[0, 1]:.3e}  Mom "
              f"{l2[0, 2]:.3e}")
        print(f"  {'lev':>3} {'shell r':>14} {'L2_Ham':>10} {'L2_Mom':>10} "
              f"{'max|Ham|':>10}")
        for row in rows:
            print(f"  {row['level']:>3} {row['r_in']:6.3g} - "
                  f"{row['r_out']:<6.3g} {row['L2_Ham']:10.3e} "
                  f"{row['L2_Mom']:10.3e} {row['max_Ham']:10.3e}")
        results.append((table, dx0, run.name, rows))

    by_table: dict[str, list] = {}
    for table, dx0, name, rows in results:
        by_table.setdefault(table, []).append((dx0, name, rows))
    for table, runs in by_table.items():
        if len(runs) < 2:
            continue
        runs.sort(key=lambda t: -t[0])
        print(f"\n== convergence, {Path(table).name}: "
              + " -> ".join(n for _, n, _ in runs))
        print(f"  {'shell r':>14}  factor(Ham) per step [order]   "
              f"factor(Mom) per step [order]")
        for k, row in enumerate(runs[0][2]):
            parts_h, parts_m = [], []
            for (dxa, _, ra), (dxb, _, rb) in zip(runs, runs[1:]):
                q = math.log(dxa / dxb)
                fh = ra[k]["L2_Ham"] / rb[k]["L2_Ham"]
                fm = ra[k]["L2_Mom"] / rb[k]["L2_Mom"]
                parts_h.append(f"{fh:6.2f} [{math.log(fh) / q:4.1f}]")
                parts_m.append(f"{fm:6.2f} [{math.log(fm) / q:4.1f}]")
            print(f"  {row['r_in']:6.3g} - {row['r_out']:<6.3g}  "
                  f"{'  '.join(parts_h):30s}  {'  '.join(parts_m)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
