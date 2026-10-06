#!/usr/bin/env python3
r"""The eps = +-0.1 arms: do both collapse, what goes NaN, and when (task C(a), 2026-09-24).

Reads the pack only (single_eps_{p,m}1e1_t100, with single_eps_p1e3_t100 and
single_eps_p1e2_t100 for comparison) and prints, per arm:

  * the throat: R_min(t) from areal_radius.dat and the oriented scan
    (horizon_scan.dat, centre A): initial value, extremum, last reading;
  * the horizon: first scan with a MOTS (areal orientation), R_mots and M_MS
    at the first and last MOTS rows;
  * the lapse and the origin: global min alpha and min chi and where they sit
    (collapse_diagnostics.dat), the first time chi reaches the 1e-8 floor,
    max|K| before the overflow;
  * the death: last row, the NaN'd field and level (run_tail.log);
  * the initial data (closed form): R(r) = r e^{-u} Omega (1 + eps g)^2 at t = 0,
    whether the minimal surface has become a maximum flanked by two minima
    (a "bag"), and the kick at which that happens: R''(r_t) = 0.

    grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/c_eps01_fates.py
"""

from __future__ import annotations

import math
import pathlib
import re
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "merger" / "article" / "claims"))
import lib  # noqa: E402
import extract_single as es  # noqa: E402

A, M = 2.0, 1.0
W = A / 4.0
R_T = 0.5 * (M + math.sqrt(M * M + A * A))
ARMS = [("single_eps_p1e1_t100", +0.1), ("single_eps_m1e1_t100", -0.1),
        ("single_eps_p1e3_t100", +1e-3), ("single_eps_p1e2_t100", +1e-2)]


def areal_R(r: np.ndarray, eps: float) -> np.ndarray:
    X = (r - A * A / (4 * r)) / A
    u = (M / A) * (np.arctan(X) - 0.5 * math.pi)
    omega = 1 + A * A / (4 * r * r)
    g = np.exp(-((r - R_T) / W) ** 2)
    return r * np.exp(-u) * omega * (1 + eps * g) ** 2


def initial_structure(eps: float) -> str:
    r = np.linspace(0.05, 6.0, 200001)
    R = areal_R(r, eps)
    dR = np.gradient(R, r)
    k = np.where(np.diff(np.sign(dR)) != 0)[0]
    kinds = []
    for i in k:
        kinds.append(("min" if dR[i] < 0 else "max", r[i], R[i]))
    return "; ".join(f"{t} R={R_:.3f} at r={r_:.3f}" for t, r_, R_ in kinds)


def bag_threshold() -> float:
    """Smallest eps > 0 for which R''(r_t) <= 0 (the minimal surface turns maximal)."""
    h = 1e-4
    def Rpp(eps):
        return (areal_R(np.array([R_T + h]), eps) - 2 * areal_R(np.array([R_T]), eps)
                + areal_R(np.array([R_T - h]), eps))[0] / h**2
    lo, hi = 0.0, 0.2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if Rpp(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def death(run: str) -> str:
    txt = (lib.run_dir(run) / "run_tail.log").read_text(errors="replace")
    m = re.search(r"NaN diagnostic: rank=\d+ level=(\d+) component=\d+ name=(\S+)", txt)
    return f"NaN in {m.group(2)} on level {m.group(1)}" if m else "no NaN in the tail"


def main() -> int:
    for run, eps in ARMS:
        print(f"== {run} (eps = {eps:+g})")
        ar = lib.stream(run, "areal_radius.dat")[1]
        i_ext = int(np.argmax(ar[:, 1])) if eps < 0 else int(np.argmax(ar[:, 1][: max(3, len(ar) // 3)]))
        print(f"   R_min (areal_radius): t=0 {ar[0,1]:.3f}; max {ar[i_ext,1]:.3f} at t={ar[i_ext,0]:.0f};"
              f" last {ar[-1,1]:.3f} at t={ar[-1,0]:.0f} (r_at_min {ar[0,2]:.2f} -> {ar[-1,2]:.2f})")
        try:
            mo = es._mots(run, "A")
            print(f"   oriented scan MOTS: first t={mo[0,0]:.0f} (R={mo[0,1]:.3f}, M_MS={mo[0,2]:.3f});"
                  f" last t={mo[-1,0]:.0f} (R={mo[-1,1]:.3f}, M_MS={mo[-1,2]:.3f}); rows {len(mo)}")
        except ValueError:
            print("   oriented scan: no MOTS")
        names, cd = lib.stream(run, "collapse_diagnostics.dat")
        c = {n: cd[:, i] for i, n in enumerate(names)}
        t = c["time"]
        healthy = t <= t[-1] - 0.05
        k0 = int(np.argmin(c["min_lapse"][healthy]))
        floor = np.where(c["min_chi"] <= 1.0000001e-8)[0]
        jump = np.where((c["min_chi"] > 30 * np.median(c["min_chi"][: max(10, len(t) // 3)])))[0]
        print(f"   lapse: min alpha {c['min_lapse'][0]:.3f} at t=0 (origin); lowest before the last 0.05 u:"
              f" {c['min_lapse'][healthy][k0]:.3f} at t={t[healthy][k0]:.2f};"
              f" at t={t[healthy][-1]:.2f}: {c['min_lapse'][healthy][-1]:.3f} at"
              f" ({c['min_lapse_x'][healthy][-1]:+.3f},{c['min_lapse_y'][healthy][-1]:+.3f},{c['min_lapse_z'][healthy][-1]:+.3f})")
        print(f"   origin chi: {c['min_chi'][0]:.1e} at t=0;"
              + (f" floor 1e-8 first at t={t[floor[0]]:.2f};" if floor.size else " never at the 1e-8 floor;")
              + (f" jumps x30 above its early median from t={t[jump[0]]:.2f} ({c['min_chi'][jump[0]]:.1e})" if jump.size else ""))
        kK = np.where(np.isfinite(c["max_abs_K"]))[0]
        print(f"   max|K|: {c['max_abs_K'][kK][-3]:.3g}, {c['max_abs_K'][kK][-2]:.3g}, {c['max_abs_K'][kK][-1]:.3g}"
              f" at t = {t[kK][-3]:.2f}, {t[kK][-2]:.2f}, {t[kK][-1]:.2f} (last rows)")
        print(f"   death: last row t={lib.last_time(run=run, file='constraint_norms.dat'):.2f}; {death(run)}")
        print(f"   t=0 structure (closed form): {initial_structure(eps)}")
    print(f"minimal surface turns maximal (a bag between two minima) for eps > {bag_threshold():.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
