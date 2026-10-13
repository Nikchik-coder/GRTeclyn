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
3. ADM mass and angular momentum (analysis/spinning_wormhole/adm.py) on
   coordinate spheres R = 8, 10, ... inside the sponge, read on level 0.
   M(R) is set against the same integral of the table's own metric on the
   same grid (the difference is the data's error, free of finite-R terms)
   and extrapolated to M_inf; J(R) is R-independent and is set against the
   table's J.  Level-0 cells under finer levels hold averages of the finer
   data, an O(dx^2) part of the difference.

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
from itertools import pairwise
from pathlib import Path

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole import adm
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


def adm_numbers(plt: str, centre: np.ndarray, p: dict[str, str],
                table: str) -> dict:
    """M(R), J(R) on level 0 against the table (module docstring, 3)."""
    import yt
    yt.set_log_level(50)
    ds = yt.load(plt)
    length, n0 = float(p["L"]), int(p["N1"])
    dx0 = length / n0
    r_top = min(float(p.get("sponge_inner_radius", length / 2)) - 2.0,
                length / 2 - 6 * dx0)
    radii = [float(r) for r in np.arange(8.0, r_top + 1e-9, 2.0)]
    n_half = math.ceil((radii[-1] + 6 * dx0) / dx0)
    left = centre - n_half * dx0
    cg = ds.covering_grid(level=0, left_edge=left, dims=[2 * n_half] * 3)
    chi = cg["boxlib", "chi"].d
    trace_k = cg["boxlib", "K"].d
    fields = {}
    for i, j in adm.PAIRS:
        h = cg["boxlib", f"h{i + 1}{j + 1}"].d
        a = cg["boxlib", f"A{i + 1}{j + 1}"].d
        fields[f"g{i + 1}{j + 1}"] = h / chi
        fields[f"K{i + 1}{j + 1}"] = (a + trace_k * h / 3.0) / chi
    grid = adm.UniformGrid(left, dx0, fields)
    ax = (np.arange(2 * n_half) + 0.5) * dx0 - n_half * dx0
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    header, body = read_spinbg(table)
    ref = adm.table_reference(header)
    tgrid = adm.UniformGrid(left, dx0, adm.table_gamma(header, body, X, Y, Z))
    m3 = [adm.adm_mass(grid, centre, r) for r in radii]
    mt = [adm.adm_mass(tgrid, centre, r) for r in radii]
    js = [adm.adm_angular_momentum(grid, centre, r) for r in radii]
    return {"dx0": dx0, "radii": radii, "M3": m3, "Mt": mt, "J": js,
            "Minf3": adm.fit_mass(radii, m3)[0],
            "Minf_table": adm.fit_mass(radii, mt)[0], "ref": ref,
            "dM": max(abs(a - b) for a, b in zip(m3, mt))}


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
        a = adm_numbers(plt, centre, p, table)
        ref_m, ref_j = a["ref"]["M"], a["ref"]["J"]
        print(f"  ADM on level 0 (dx {a['dx0']:.4g}), spheres R = "
              f"{a['radii'][0]:g}..{a['radii'][-1]:g}:")
        print(f"  {'R':>5} {'M 3D':>12} {'M table':>12} {'dM':>10} {'J 3D':>12}")
        for r, m3, mt, j in zip(a["radii"], a["M3"], a["Mt"], a["J"]):
            print(f"  {r:5.1f} {m3:12.6f} {mt:12.6f} {m3 - mt:10.2e} {j:12.6f}")
        j_mean = float(np.mean(a["J"]))
        print(f"  M_inf: 3D {a['Minf3']:.6f}, table on this grid "
              f"{a['Minf_table']:.6f}, table meta "
              f"{'n/a' if ref_m is None else f'{ref_m:.6f}'}")
        print(f"  J: 3D mean {j_mean:.6f} (spread over R "
              f"{np.ptp(a['J']):.1e}), table meta "
              f"{'n/a' if ref_j is None else f'{ref_j:.6f}'}")
        a["J_err"] = None if ref_j is None else abs(j_mean - ref_j)
        results.append((table, dx0, run.name, rows, a))

    by_table: dict[str, list] = {}
    for table, dx0, name, rows, a in results:
        by_table.setdefault(table, []).append((dx0, name, rows, a))
    for table, runs in by_table.items():
        if len(runs) < 2:
            continue
        runs.sort(key=lambda t: -t[0])
        print(f"\n== convergence, {Path(table).name}: "
              + " -> ".join(n for _, n, _, _ in runs))
        print(f"  {'shell r':>14}  factor(Ham) per step [order]   "
              f"factor(Mom) per step [order]")
        for k, row in enumerate(runs[0][2]):
            parts_h, parts_m = [], []
            for (dxa, _, ra, _), (dxb, _, rb, _) in zip(runs, runs[1:]):
                q = math.log(dxa / dxb)
                fh = ra[k]["L2_Ham"] / rb[k]["L2_Ham"]
                fm = ra[k]["L2_Mom"] / rb[k]["L2_Mom"]
                parts_h.append(f"{fh:6.2f} [{math.log(fh) / q:4.1f}]")
                parts_m.append(f"{fm:6.2f} [{math.log(fm) / q:4.1f}]")
            print(f"  {row['r_in']:6.3g} - {row['r_out']:<6.3g}  "
                  f"{'  '.join(parts_h):30s}  {'  '.join(parts_m)}")
        for key, label in (("dM", "max|M 3D - M table|"), ("J_err", "|J - J table|")):
            vals = [(dxa, a[key]) for dxa, _, _, a in runs]
            if any(v is None or v == 0 for _, v in vals):
                continue
            steps = [f"{va / vb:6.2f} [{math.log(va / vb) / math.log(da / db):4.1f}]"
                     for (da, va), (db, vb) in pairwise(vals)]
            print(f"  {label:>20}: " + "  ".join(f"{v:.2e}" for _, v in vals)
                  + "   factor [order] " + "  ".join(steps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
