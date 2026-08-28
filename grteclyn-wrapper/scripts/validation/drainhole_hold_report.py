#!/usr/bin/env python3
"""Score a single-drainhole static-hold run against the closed form.

research/merger/FIx.md, implementation plan Stage 1.

The massive Ellis-Bronnikov drainhole is an EXACT fixed point of the evolved
CCZ4 + 1+log + Gamma-driver system: the spatial metric is conformally flat so
Gamma^i = 0, K = A_ij = Theta = 0, the shift starts and stays at zero, and
alpha = e^u is stationary because K = 0.  So the exact solution at time t is the
exact solution at t = 0, and every deviation is error with no physics mixed in.
That is what makes this a usable convergence test and not merely a plot.

Two numbers are worth having and they answer different questions:

  * R_areal_min(t), the throat.  This is what Stage 1's benchmark is stated in.
    It comes from the consumer's areal_radius.dat.
  * the error PROFILE err(r, t) = |chi_num - chi_exact| / chi_exact.  This is
    what says WHERE the error is born, and it is the number that settled Stage
    1: at sigma = 2.0 the profile is a front that starts at the compactified
    origin and creeps outward until it reaches the throat around t ~ 20, so the
    apparent "throat collapse" is contamination, not the Ellis-Bronnikov mode.
    A genuine throat instability would peak AT the throat instead.

Do not read min(chi) as a throat tracker.  For a wormhole the global minimum of
chi is the compactified far infinity at rbar -> 0, not the minimal surface; see
the header of params_stage1_hold.txt.

Usage:
    drainhole_hold_report.py RUN_DIR [RUN_DIR ...] [-a A] [-m M] [--times ...]

RUN_DIR is a campaign run directory (it must contain small_data/ and the
plotfiles must still be on scratch for the profile half; the R(t) half needs
only small_data/areal_radius.dat).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

# Radii to sample the profile at.  Spread across the three zones that behave
# differently: inside the collar, between collar and throat, at the throat, and
# out in the asymptotically flat region where nothing should ever happen.
DEFAULT_RADII = (0.11, 0.33, 0.45, 0.82, 1.19, 1.57, 1.94, 2.94, 4.88, 9.76)


def chi_exact(rbar: np.ndarray, a: float, m: float) -> np.ndarray:
    """chi = e^{2u} / Omega^2 for the massive drainhole in isotropic coords."""
    x = (rbar - a * a / (4.0 * rbar)) / a
    omega = 1.0 + a * a / (4.0 * rbar * rbar)
    u = (m / a) * (np.arctan(x) - 0.5 * math.pi)
    return np.exp(2.0 * u) / (omega * omega)


def throat_analytic(a: float, m: float) -> tuple[float, float, float]:
    """(rbar, areal radius, chi) at the minimal surface, which sits at l = m."""
    rbar = 0.5 * (m + math.hypot(m, a))
    u = (m / a) * (math.atan(m / a) - 0.5 * math.pi)
    omega = 1.0 + a * a / (4.0 * rbar * rbar)
    return rbar, math.exp(-u) * math.hypot(m, a), math.exp(2.0 * u) / (omega * omega)


def read_areal(run_dir: Path) -> np.ndarray | None:
    path = run_dir / "small_data" / "areal_radius.dat"
    if not path.exists():
        return None
    rows = np.loadtxt(path, comments="#", ndmin=2)
    return rows if rows.size else None


def profile(plotfile: Path, centre, a: float, m: float, radii):
    """Sample chi along +x and return (t, [(r, chi_num, chi_exact, relerr)])."""
    import yt

    yt.set_log_level(50)
    ds = yt.load(str(plotfile))
    c = np.asarray(centre, dtype=float)
    ray = ds.ray(c, [float(ds.domain_right_edge[0]), c[1], c[2]])
    # The true |x - centre|, not the x-offset: a centre on a cell corner leaves
    # every sampled cell offset by half a cell in y and z, which understates r
    # badly at the innermost sample -- exactly where the error lives.
    d = [np.asarray(ray[("index", ax)], dtype=float) - c[i]
         for i, ax in enumerate("xyz")]
    r = np.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    chi = np.asarray(ray[("boxlib", "chi")], dtype=float)
    order = np.argsort(r)
    r, chi = r[order], chi[order]
    exact = chi_exact(r, a, m)
    out = []
    for want in radii:
        i = int(np.argmin(np.abs(r - want)))
        out.append((r[i], chi[i], exact[i], abs(chi[i] - exact[i]) / exact[i]))
    return float(ds.current_time), out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("-a", type=float, default=2.0, help="drainhole scale a")
    ap.add_argument("-m", type=float, default=1.0, help="drainhole mass m")
    ap.add_argument("--centre", type=float, nargs=3, default=None,
                    help="box centre (default: read `center` from the run's params.txt)")
    ap.add_argument("--scratch", type=Path, default=Path("/tmp/grteclyn_scratch"),
                    help="where the plotfiles are")
    ap.add_argument("--times", type=float, nargs="+", default=None,
                    help="times to profile; omit to skip the profile half")
    args = ap.parse_args()

    rbar_t, r_min_t, chi_t = throat_analytic(args.a, args.m)
    print(f"Drainhole a = {args.a}, m = {args.m}  ->  M_ADM = {args.m}")
    print(f"  minimal surface at rbar = {rbar_t:.4f}, areal radius R_min = "
          f"{r_min_t:.4f}, chi = {chi_t:.4f}\n")

    print("=== throat, R_areal_min(t) ===")
    header = f"{'t':>7}"
    series = {}
    for d in args.run_dirs:
        rows = read_areal(d)
        if rows is None:
            print(f"  ({d.name}: no areal_radius.dat)")
            continue
        series[d.name] = rows
        header += f" {d.name[:22]:>22}"
    if series:
        print(header)
        all_t = sorted({float(t) for rows in series.values() for t in rows[:, 0]})
        for t in all_t:
            line = f"{t:7.2f}"
            for name, rows in series.items():
                i = np.where(np.isclose(rows[:, 0], t))[0]
                line += f" {rows[i[0], 1]:22.4f}" if len(i) else f" {'-':>22}"
            print(line)
        print()
        for name, rows in series.items():
            drift = (rows[-1, 1] - r_min_t) / r_min_t
            print(f"  {name}: last t = {rows[-1, 0]:.2f}, R = {rows[-1, 1]:.4f}, "
                  f"drift from analytic = {100 * drift:+.2f}%")
    print()

    if args.times is None:
        return 0

    print("=== error profile, |chi_num - chi_exact| / chi_exact ===")
    print("(a front that starts at the origin and creeps out is contamination;")
    print(" a genuine throat mode would peak at the throat instead)\n")
    for d in args.run_dirs:
        centre = args.centre
        if centre is None:
            params = d / "params.txt"
            centre = [32.0, 32.0, 32.0]
            if params.exists():
                for line in params.read_text().splitlines():
                    if line.strip().startswith("center"):
                        vals = line.split("#")[0].split("=")[1].split()
                        if len(vals) == 3:
                            centre = [float(v) for v in vals]
                        break
        print(f"--- {d.name} (centre {centre}) ---")
        hdr = f"{'rbar':>7}" + "".join(f" {'t=' + format(t, '.0f'):>10}" for t in args.times)
        print(hdr)
        cols = []
        for t in args.times:
            step = int(round(t / 0.01))  # dt = dt_multiplier * dx_coarse = 0.01
            pf = args.scratch / d.name / f"BinaryWormholePlt{step:05d}"
            if not pf.exists():
                cols.append(None)
                continue
            cols.append(profile(pf, centre, args.a, args.m, DEFAULT_RADII)[1])
        for i, want in enumerate(DEFAULT_RADII):
            line = f"{want:7.2f}"
            for col in cols:
                line += f" {col[i][3]:10.2e}" if col else f" {'-':>10}"
            print(line)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
