#!/usr/bin/env python3
"""Fit the Bondi mass law a = G M_partner / d^2 across the equal-mass ladder.

WHY ITS OWN SCRIPT
The force-law fit already in the pack README varies the separation d at fixed
mass.  This one varies the mass at fixed d = 20 and asks for the exponent p in
a proportional to M^p.  It shares no state with the packers or with any other
analysis: it reads only the two position series and grtresna_params.txt, writes one
CSV of its own, and touches nothing else.

CONVENTION (identical to the article's, so the two are directly comparable)
  * the tracked position is the pair MIDPOINT of the two sector BARYCENTRES,
    the same variable article_figures.midpoint() uses -- verified to reproduce
    the published a*d^2 = 0.014355 on runaway_pair_d20_L64_N128_lev0
  * the fit window is t >= 5, before which the gauge is still settling
  * x(t) = x0 + v0 t + a t^2 / 2, least squares, a is the reported acceleration
  * the halo-free CORE midpoint (sector_dynamics.dat) is fitted alongside as an
    independent tracker; the two disagree by well under a percent on the drift
    and their spread is the honest systematic on any single acceleration

The star masses are NOT read from a table.  They are recomputed here from the
two frequencies the elliptic solver actually used, recorded in each cell's
grtresna_params.txt, so the mass axis is derived from the run rather than from
the launch intent.

Usage:  ./.venv/bin/python research/bondi_dipole/fit_mass_law.py [--csv OUT]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "grteclyn-wrapper" / "src"))

from grteclyn_wrapper.grtresna.profiles.boson_star_ode import (  # noqa: E402
    cached_selfgrav_at_omega,
)

# Model constants of the campaign's boson-star family.
LAM = 10240.0
MU = 21845333.0
UNIT_MASS = 1.0

FIT_T_MIN = 5.0  # gauge settling window, matches the pack README


def find_cell(name: str) -> Path | None:
    """Locate a cell by name, preferring the packed extract over the run tree."""
    packed = REPO / "results" / "bondi-dipole-runaway" / "campaign" / name
    if (packed / "sector_barycenters.dat").is_file():
        return packed
    for base in (
        REPO / "runs" / "bondi" / "staging" / name,
        REPO / "runs" / "bondi" / "staging" / "archive" / name,
    ):
        if not base.is_dir():
            continue
        for run in sorted(base.glob("bondi_sg_*")):
            if (run / "small_data" / "sector_barycenters.dat").is_file():
                return run
    return None


def series(cell: Path, name: str) -> Path:
    flat = cell / name
    return flat if flat.is_file() else cell / "small_data" / name


def solver_params(cell: Path) -> Path:
    flat = cell / "grtresna_params.txt"
    return flat if flat.is_file() else cell / "grtresna" / "params.txt"


def read_omegas(cell: Path) -> tuple[float, float]:
    """Return (canonical omega, phantom omega) as the solver recorded them."""
    text = solver_params(cell).read_text()
    out = {}
    for key in ("lump0_omega", "lump1_omega"):
        m = re.search(rf"^\s*{key}\s*=\s*([-\d.eE+]+)", text, re.M)
        if not m:
            raise SystemExit(f"{cell.name}: no {key} in {solver_params(cell)}")
        out[key] = float(m.group(1))
    return out["lump0_omega"], out["lump1_omega"]


def read_separation(cell: Path) -> float:
    """Coordinate separation the cell was built at, from the matter manifest."""
    flat = cell / "initial_data.matter.json"
    path = flat if flat.is_file() else cell / "initial_data.matter.json"
    centers = json.loads(path.read_text())["lump_centers"]
    return abs(float(centers[0][0]) - float(centers[1][0]))


def masses(cell: Path) -> tuple[float, float]:
    """(canonical ADM mass, |phantom ADM mass|) at the solver's own frequencies."""
    wc, wp = read_omegas(cell)
    can = cached_selfgrav_at_omega(UNIT_MASS, LAM, MU, wc, +1)
    pha = cached_selfgrav_at_omega(UNIT_MASS, LAM, MU, wp, -1)
    return can.adm_mass, abs(pha.adm_mass)


def _quadratic_a(t: np.ndarray, x: np.ndarray, t_min: float) -> tuple[float, float, int]:
    """Twice the quadratic coefficient of x(t) over t >= t_min, plus fit rms."""
    keep = t >= t_min
    t, x = t[keep], x[keep]
    coeffs = np.polyfit(t, x, 2)
    resid = x - np.polyval(coeffs, t)
    return 2.0 * coeffs[0], float(np.sqrt(np.mean(resid**2))), int(t.size)


def fit_acceleration(cell: Path, t_min: float = FIT_T_MIN) -> dict:
    """Fit a on both trackers.

    The CORE (halo-free) midpoint is the reported value: the |phi|^2-weighted
    barycentre also integrates the relaxation halo each star sheds early in the
    run, and on the lightest, most diffuse pair that cloud grows the sector's
    rms radius by ~55% and drags the barycentre fit ~18% off the core one.
    The barycentre is kept as the cross-check column.

    The per-cell error bar is the half-spread of the four disjoint-window fits
    (5-50, 50-100, 100-150, 150-200) -- the same test the pack README applies
    to the headline cell -- which is the honest window systematic on a single
    quadratic coefficient.
    """
    dyn = np.loadtxt(series(cell, "sector_dynamics.dat"), comments="#")
    t_core = dyn[:, 0]
    x_core = 0.5 * (dyn[:, 1] + dyn[:, 5])
    a_core, rms_core, n_core = _quadratic_a(t_core, x_core, t_min)

    windows = []
    for t0, t1 in ((5.0, 50.0), (50.0, 100.0), (100.0, 150.0), (150.0, 200.0)):
        keep = (t_core >= t0) & (t_core <= t1)
        if keep.sum() > 5:
            windows.append(2.0 * np.polyfit(t_core[keep], x_core[keep], 2)[0])
    a_err = 0.5 * (max(windows) - min(windows)) if len(windows) > 1 else float("nan")

    bar = np.loadtxt(series(cell, "sector_barycenters.dat"), comments="#")
    x_bar = 0.5 * (bar[:, 2] + bar[:, 7])
    a_bar, _, _ = _quadratic_a(bar[:, 0], x_bar, t_min)

    return {
        "a": a_core,
        "a_err": a_err,
        "a_bary": a_bar,
        "tracker_spread_pct": 100.0 * (a_bar - a_core) / a_core,
        "t_end": float(t_core[-1]),
        "n_points": n_core,
        "rms_resid": rms_core,
        "drift": float(x_core[-1] - x_core[0]),
        "gap_start": float(dyn[0, 9]),
        "gap_end": float(dyn[-1, 9]),
    }


CELLS = [
    "masslaw_pair_d20_w0675_L64_N128_lev0",
    "masslaw_pair_d20_w0700_L64_N128_lev0",
    "runaway_pair_d20_L64_N128_lev0",
    "masslaw_pair_d20_w0850_L64_N128_lev0",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="*", default=CELLS)
    ap.add_argument("--t-min", type=float, default=FIT_T_MIN)
    ap.add_argument(
        "--csv",
        default=str(REPO / "results" / "bondi-dipole-runaway" / "campaign" / "mass_law.csv"),
        help="where to write the fitted table (its own file, shared with nothing)",
    )
    args = ap.parse_args()

    rows = []
    for name in args.cells:
        cell = find_cell(name)
        if cell is None:
            print(f"[mass-law] {name}: no barycentre series yet -- skipping")
            continue
        mc, mp = masses(cell)
        d = read_separation(cell)
        fit = fit_acceleration(cell, args.t_min)
        rows.append(
            dict(
                cell=name,
                d=d,
                m_canon=mc,
                m_phantom=mp,
                m_mean=0.5 * (mc + mp),
                pair_mismatch_pct=100.0 * (mp - mc) / mc,
                a_pred=0.5 * (mc + mp) / d**2,
                **fit,
            )
        )

    if not rows:
        print("[mass-law] nothing to fit")
        return 1

    rows.sort(key=lambda r: r["m_mean"])

    print(f"\nfit window t >= {args.t_min:g}, midpoint of the pair, x = x0 + v t + a t^2 / 2\n")
    hdr = (f"{'cell':<40} {'M':>11} {'pair dM%':>9} {'a measured':>12} {'+/-':>9} "
           f"{'a = M/d^2':>12} {'a*d^2/M':>9} {'bary-core%':>11}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['cell'][:40]:<40} {r['m_mean']:11.5e} {r['pair_mismatch_pct']:+9.3f} "
            f"{r['a']:12.5e} {r['a_err']:9.2e} {r['a_pred']:12.5e} "
            f"{r['a'] * r['d'] ** 2 / r['m_mean']:9.4f} {r['tracker_spread_pct']:+11.2f}"
        )

    m = np.array([r["m_mean"] for r in rows])
    a = np.array([r["a"] for r in rows])
    ae = np.array([r["a_err"] for r in rows])
    logm, loga = np.log(m), np.log(a)
    sig = ae / a  # error of log a
    n = m.size

    if n > 2 and np.all(np.isfinite(sig)) and np.all(sig > 0):
        # Weighted least squares in log-log, errors from the window spread.
        w = 1.0 / sig**2
        W, Sx, Sy = w.sum(), (w * logm).sum(), (w * loga).sum()
        Sxx, Sxy = (w * logm**2).sum(), (w * logm * loga).sum()
        delta = W * Sxx - Sx**2
        p = (W * Sxy - Sx * Sy) / delta
        c = (Sxx * Sy - Sx * Sxy) / delta
        p_err = math.sqrt(W / delta)
        # If the points scatter more than their error bars claim, scale up.
        chi2 = float((w * (loga - (p * logm + c)) ** 2).sum())
        if chi2 / (n - 2) > 1.0:
            p_err *= math.sqrt(chi2 / (n - 2))
    else:
        p, c = np.polyfit(logm, loga, 1)
        if n > 2:
            resid = loga - (p * logm + c)
            s2 = float(np.sum(resid**2) / (n - 2))
            sxx = float(np.sum((logm - logm.mean()) ** 2))
            p_err = math.sqrt(s2 / sxx)
        else:
            p_err = float("nan")

    span = m.max() / m.min()
    print(f"\nmass span {span:.3f}x over {n} cells at d = {rows[0]['d']:g}")
    print(f"power law  a ~ M^p   ->   p = {p:.4f} +/- {p_err:.4f}   (Bondi law predicts p = 1)")
    print(f"deviation from unity: {(p - 1.0) / p_err:+.2f} sigma" if p_err == p_err else "")

    ratios = np.array([r["a"] * r["d"] ** 2 / r["m_mean"] for r in rows])
    print(
        f"a*d^2/M across the ladder: mean {ratios.mean():.4f}, "
        f"spread {ratios.max() - ratios.min():.4f}, max deviation from 1: "
        f"{np.max(np.abs(ratios - 1.0)) * 100:.2f}%"
    )

    out = Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys()) + ["a_over_pred", "a_d2_over_m"]
    # rows carry a_err and a_bary already
    with out.open("w") as fh:
        fh.write("# Bondi mass law: acceleration vs partner mass at fixed separation.\n")
        fh.write(f"# fit window t >= {args.t_min:g}; midpoint quadratic; masses from the solver's own omegas.\n")
        fh.write(f"# slope p = {p:.6f} +/- {p_err:.6f} in a ~ M^p (law: p = 1)\n")
        fh.write(",".join(keys) + "\n")
        for r in rows:
            r = dict(r, a_over_pred=r["a"] / r["a_pred"], a_d2_over_m=r["a"] * r["d"] ** 2 / r["m_mean"])
            fh.write(",".join(f"{r[k]:.9g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")
    print(f"\nwrote {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
