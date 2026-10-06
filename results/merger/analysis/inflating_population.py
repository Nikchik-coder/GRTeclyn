#!/usr/bin/env python3
"""The inflating branch as a population member (paper Secs. IV.D and X,
"The inflating half of the population"): every number quoted there, from the
pack.  Numpy only; reads results/merger/campaign.

Ledger rows this script backs (claims/ledger_single.tsv, ledger_detector.tsv;
the registered extractors are single_f4_pop and detector_stall, plus
waves_scalar_energy for the quiet-window shed):

  clmInfStoreDeficit   R*/2 - m, the Misner-Sharp deficit of the field outside
                       the static throat -- the turnover ending's candidate
                       reservoir (closed form).
  clmInfShedQuiet      |int -flux_kin dt| through R=18 to t=80 on the level-4
                       scalar arm of Sec. VIII.G, whose exterior slicing is
                       still quiet over that window.
  clmInfShedKin/Geo    the same integral on F4 (L=512, level 5) through the
                       coordinate-60 sphere to t=T_WALL=218, raw and with the
                       alpha^2 chi^-1/2 factor of Sec. VIII.F from the packed
                       shell profiles.  The pair brackets the true outflow:
                       the 1+log front collapses the lapse at the sphere
                       (alpha ~ 0.04 by the wall) before the monopole grows,
                       and Pi carries 1/alpha, so the kinematic reading is
                       inflated and the shell-minimum correction over-suppresses.
  clmInfEfoldNeck      ln(R_wall/R0) of F4's neck: areal e-folds in the record.
  clmInfEfoldBoundary  ln(R_hk/R0) at the theta_k = 0 boundary's last clean
                       sample (t = 212).
  clmInfBoundarySpeed  mean d(R_hk)/dt over the record (and over its last 50
                       units, printed for the "no slowing" statement).
  clmInfDcGpc          comoving distance to z_e = 20 (flat LCDM, H0 = 67.7,
                       Omega_m = 0.31: plot_heavy_seeds' cosmology).
  clmInfStallLo/Hi     the percolation bound: mouths of comoving density n may
                       grow to (3/(4 pi n))^(1/3) before overlapping, so
                       non-overlap since z_e caps the mean comoving expansion
                       speed at that radius over D_c -- for n = 10^-2 (Lo) and
                       10^-4 (Hi) Mpc^-3, the seed abundances of Sec. X.B.
  clmInfStallFactor    the recorded boundary speed over the loosest bound.

Run:  grteclyn-wrapper/.venv/bin/python results/merger/analysis/inflating_population.py
"""
from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

PACK = pathlib.Path(__file__).resolve().parents[1] / "campaign"
F4 = PACK / "01_single_throat/seed/single_eps_m1e2_L512_ml5_oct_t400"
QUIET = PACK / "01_single_throat/seed/single_pureq_q1e2_ml4_scalar_t100"
T_WALL = 218.0          # F4's trust window (results/merger/trust_windows.tsv)
T_QUIET = 80.0          # the counted window of Sec. VIII.G
A, M = 2.0, 1.0         # the production throat
H0_KMSMPC, OMEGA_M = 67.7, 0.31
Z_EMIT = 20.0
N_RANGE = (1e-4, 1e-2)  # seed abundances, Mpc^-3 (Sec. X.B)


def stream(path: pathlib.Path):
    names = None
    with path.open() as fh:
        for line in fh:
            if line.startswith("#") and "time" in line:
                names = line.lstrip("#").split()
    data = np.loadtxt(path)
    return {n: data[:, i] for i, n in enumerate(names)}


def main() -> int:
    # -- the store: R*/2 - m (closed form, paper Sec. II.B)
    r_star = math.sqrt(A**2 + M**2) * math.exp((M / A) * math.atan(A / M))
    store = r_star / 2.0 - M
    print(f"store R*/2 - m               = {store:.4f}   (R* = {r_star:.4f})")

    # -- quiet-window shed (level-4 arm, R=18, t <= 80)
    s = stream(QUIET / "scalar_modes.dat")
    k = s["time"] <= T_QUIET
    e_quiet = abs(np.trapezoid(-s["R18_scalar_flux_kin"][k], s["time"][k]))
    print(f"shed, quiet window (R=18,80) = {e_quiet:.4f}   ({e_quiet / store * 100:.1f}% of the store)")

    # -- F4: shed through the coordinate-60 sphere, kinematic and geometric
    s = stream(F4 / "scalar_modes.dat")
    p = stream(F4 / "core_radial_profile.dat")
    ts = s["time"]
    alpha = np.interp(ts, p["time"], p["lapse_min_r60.25"])
    chi = np.interp(ts, p["time"], p["chi_min_r60.25"])
    k = ts <= T_WALL
    for name, flux in (("kin", s["R60_scalar_flux_kin"]),
                       ("geo", s["R60_scalar_flux_kin"] * alpha**2 / np.sqrt(chi))):
        e = abs(np.trapezoid(-flux[k], ts[k]))
        print(f"shed, F4 (r=60, {name}, 218)   = {e:.4f}   ({e / store:.2f}x the store)")

    # -- F4: e-folds and the boundary's speed
    n = stream(F4 / "neck_horizons.dat")
    t, r_neck, r_hk = n["time"], n["R_neck"], n["R_hk"]
    r0 = r_neck[0]
    i_wall = int(np.argmin(np.abs(t - T_WALL)))
    # theta_k track: last sample before its first jump (> 2x cell-to-cell step)
    jumps = np.where(np.abs(np.diff(r_hk)) > 8.0)[0]
    i_hk = int(jumps[0]) if jumps.size else len(r_hk) - 1
    print(f"e-folds, neck                = {math.log(r_neck[i_wall] / r0):.3f}   "
          f"(R {r0:.3f} -> {r_neck[i_wall]:.2f})")
    print(f"e-folds, theta_k boundary    = {math.log(r_hk[i_hk] / r0):.3f}   "
          f"(R -> {r_hk[i_hk]:.1f} at t = {t[i_hk]:.0f})")
    v = (r_hk[i_hk] - r_hk[0]) / t[i_hk]
    late = (t >= t[i_hk] - 50.0) & (t <= t[i_hk])
    v_late = float(np.polyfit(t[late], r_hk[late], 1)[0])
    print(f"boundary speed               = {v:.4f} c  (last 50 units: {v_late:.4f} c)")

    # -- percolation bound
    zz = np.linspace(0.0, Z_EMIT, 200001)
    e_z = np.sqrt(OMEGA_M * (1.0 + zz) ** 3 + (1.0 - OMEGA_M))
    d_c = 299792.458 / H0_KMSMPC * float(np.trapezoid(1.0 / e_z, zz))
    print(f"D_c(z={Z_EMIT:.0f})                     = {d_c:.0f} Mpc = {d_c / 1e3:.2f} Gpc")
    for n_mpc in N_RANGE:
        r_max = (3.0 / (4.0 * math.pi * n_mpc)) ** (1.0 / 3.0)
        vmax = r_max / d_c
        print(f"n = {n_mpc:g}: overlap at R = {r_max:6.2f} Mpc -> vbar_max = {vmax:.3e} c"
              f"   (recorded/bound = {v / vmax:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
