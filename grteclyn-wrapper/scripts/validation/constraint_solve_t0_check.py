#!/usr/bin/env python3
"""Read the t = 0 plotfile of a BinaryWormholeMerger run and grade its
initial data: the Hamiltonian constraint per level about the throats, the ADM
mass from the conformal factor's tail, and each throat's minimal areal radius.

Why this exists
---------------
The base-grid ``L2_Ham`` the code logs does not resolve a throat (the paper
says so), so it cannot tell constraint-solved data (``constraint_solve = 1``,
``Examples/BinaryWormholeMerger/DrainholeConstraintSolve.hpp``) from the
superposition: at dx = 0.5 both sit on the same discretisation floor.  The
finest level can.  This script reads ``Ham`` from a plotfile written with
``amr.derive_plot_vars = constraints`` (which needs ``G_Newton = 1.0`` in the
params -- the derived field's ParmParse has no default) and reports, per level
and over the cells that level owns:

  * rms and max |Ham| on the throat shell, 1.2 < r_throat < 3.0;
  * rms and max |Ham| outside, r_throat >= 3.0.

With ``--mass`` it also fits the monopole of Psi = chi^{-1/4} - 1 on spheres
r = 12 .. 27 about the box centre to A/r + B/r^2 + C/r^3 and reports
M_ADM = 2A (0.2 % on the exact drainhole in an L = 64 box), and scans
coordinate spheres about each throat for the minimal areal radius on the
finest level.

Measured on 2026-09-27 (L = 64, N = 128, level 3, d = 8 head-on from rest):
the superposition's throat-shell rms is 9.7e-3; the solve brings it to
5.1e-6, against 2.1e-6 for the exact single throat on the same grid.

Usage
-----
    constraint_solve_t0_check.py <plotfile> --params <run>/params.txt [--mass]
    constraint_solve_t0_check.py <plotfile> --centers="-4,0,0;4,0,0" [--box-center 32,32,32]

``--params`` reads ``center`` and ``wormhole_centerA/B`` (B dropped when
``wormhole_throat_radius_B = 0``); ``--centers`` gives the offsets from the
box centre by hand, ``;``-separated, and needs the ``=`` because a leading
minus looks like an option to argparse.  Runs in the wrapper venv (yt, scipy).
"""

from __future__ import annotations

import argparse
import math

import numpy as np


def parse_vec(text: str) -> np.ndarray:
    return np.array([float(v) for v in text.replace(",", " ").split()], dtype=float)


def read_params(path: str) -> dict:
    """The keys this script needs from an AMReX params file (values as text)."""
    out: dict = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if "=" not in line:
            continue
        key, val = (t.strip() for t in line.split("=", 1))
        out[key] = val.strip('"')
    return out


def ham_stats(ds, centres, shell=(1.2, 3.0)):
    """Per (level, region): (rms, max) of Ham over the cells the level owns."""
    acc: dict = {}
    for grid in ds.index.grids:
        lev = grid.Level
        ham = np.asarray(grid["boxlib", "Ham"])
        own = np.asarray(grid.child_mask, dtype=bool)
        x, y, z = (np.asarray(grid["index", a]) for a in ("x", "y", "z"))
        rmin = np.full(ham.shape, np.inf)
        for c in centres:
            rmin = np.minimum(
                rmin, np.sqrt((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2)
            )
        dv = float(np.prod(np.asarray(grid.dds)))
        regions = {
            "shell": (rmin > shell[0]) & (rmin < shell[1]),
            "outer": rmin >= shell[1],
        }
        for key, sel in regions.items():
            s = own & sel
            a = acc.setdefault((lev, key), [0.0, 0.0, 0.0])
            a[0] += float(np.sum(ham[s] ** 2) * dv)
            a[1] += float(s.sum() * dv)
            if s.any():
                a[2] = max(a[2], float(np.abs(ham[s]).max()))
    return {
        k: (math.sqrt(v[0] / v[1]) if v[1] > 0 else float("nan"), v[2])
        for k, v in acc.items()
    }


def covering_psi(ds, lev, lo, hi):
    """Psi = chi^{-1/4} on a covering grid of level `lev` over [lo, hi]."""
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - lev)
    n = np.round((np.asarray(hi) - np.asarray(lo)) / dx).astype(int)
    cg = ds.covering_grid(lev, left_edge=lo, dims=n)
    chi = np.asarray(cg["boxlib", "chi"])
    axes = [lo[i] + (np.arange(n[i]) + 0.5) * dx for i in range(3)]
    return axes, chi ** -0.25


def adm_mass(ds, box_center, radii=(12, 15, 18, 21, 24, 27)):
    from scipy.interpolate import RegularGridInterpolator

    left = np.asarray(ds.domain_left_edge, dtype=float)
    right = np.asarray(ds.domain_right_edge, dtype=float)
    axes, psi = covering_psi(ds, 0, left, right)
    f = RegularGridInterpolator(axes, psi)
    nth, nph = 48, 96
    th = (np.arange(nth) + 0.5) * math.pi / nth
    ph = np.arange(nph) * 2 * math.pi / nph
    T, P = np.meshgrid(th, ph, indexing="ij")
    wgt = np.sin(T) / np.sin(T).sum()
    rs = np.asarray(radii, dtype=float)
    mono = []
    for r in rs:
        pts = np.stack(
            [
                box_center[0] + r * np.sin(T) * np.cos(P),
                box_center[1] + r * np.sin(T) * np.sin(P),
                box_center[2] + r * np.cos(T),
            ],
            -1,
        )
        mono.append(float(np.sum(f(pts) * wgt)) - 1.0)
    design = np.stack([1 / rs, 1 / rs**2, 1 / rs**3], 1)
    coef = np.linalg.lstsq(design, np.asarray(mono), rcond=None)[0]
    return 2.0 * coef[0]


def throat_rmin(ds, centre, r_range=(1.0, 3.2), dr=0.01, half=4.0):
    """Minimum over coordinate spheres about `centre` of sqrt(A / 4 pi),
    A = oint Psi^4 r^2 dOmega, on the finest level."""
    from scipy.interpolate import RegularGridInterpolator

    lev = ds.index.max_level
    axes, psi = covering_psi(ds, lev, list(centre - half), list(centre + half))
    f = RegularGridInterpolator(axes, psi, bounds_error=False, fill_value=None)
    nth, nph = 40, 80
    th = (np.arange(nth) + 0.5) * math.pi / nth
    ph = np.arange(nph) * 2 * math.pi / nph
    T, P = np.meshgrid(th, ph, indexing="ij")
    d_omega = np.sin(T) * (math.pi / nth) * (2 * math.pi / nph)
    best = (np.inf, 0.0)
    for r in np.arange(r_range[0], r_range[1], dr):
        pts = np.stack(
            [
                centre[0] + r * np.sin(T) * np.cos(P),
                centre[1] + r * np.sin(T) * np.sin(P),
                centre[2] + r * np.cos(T),
            ],
            -1,
        )
        area = float(np.sum(f(pts) ** 4 * d_omega)) * r * r
        areal = math.sqrt(area / (4 * math.pi))
        if areal < best[0]:
            best = (areal, float(r))
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plotfile")
    ap.add_argument("--params", help="the run's params.txt: center, wormhole_centerA/B")
    ap.add_argument(
        "--centers", help='throat centres as offsets from the box centre, "-4,0,0;4,0,0"',
    )
    ap.add_argument("--box-center", default=None, help="default 32,32,32, or the params' center")
    ap.add_argument("--mass", action="store_true", help="ADM mass and throat R_min")
    args = ap.parse_args()

    box_center = np.array([32.0, 32.0, 32.0])
    offsets: list = []
    if args.params:
        prm = read_params(args.params)
        if "center" in prm:
            box_center = parse_vec(prm["center"])
        offsets.append(parse_vec(prm.get("wormhole_centerA", "0 0 0")))
        if float(prm.get("wormhole_throat_radius_B", "1")) > 0.0:
            offsets.append(parse_vec(prm.get("wormhole_centerB", "0 0 0"))
                           if "wormhole_centerB" in prm else -offsets[0])
    if args.centers:
        offsets = [parse_vec(c) for c in args.centers.split(";") if c.strip()]
    if args.box_center:
        box_center = parse_vec(args.box_center)
    if not offsets:
        ap.error("give --params or --centers")

    import yt

    yt.set_log_level(50)
    ds = yt.load(args.plotfile)
    centres = [box_center + off for off in offsets]

    stats = ham_stats(ds, centres)
    print(f"{args.plotfile}: time {float(ds.current_time):.4f}, "
          f"levels 0-{ds.index.max_level}")
    for lev in range(ds.index.max_level + 1):
        sh = stats.get((lev, "shell"), (float("nan"), 0.0))
        ou = stats.get((lev, "outer"), (float("nan"), 0.0))
        print(f"  level {lev}: throat shell rms {sh[0]:.3e} max {sh[1]:.3e} | "
              f"r >= 3 rms {ou[0]:.3e} max {ou[1]:.3e}")

    if args.mass:
        print(f"  M_ADM (monopole fit, r = 12-27): {adm_mass(ds, box_center):.4f}")
        for i, c in enumerate(centres):
            areal, r = throat_rmin(ds, c)
            print(f"  throat {'AB'[i] if i < 2 else i}: R_min {areal:.4f} at r = {r:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
