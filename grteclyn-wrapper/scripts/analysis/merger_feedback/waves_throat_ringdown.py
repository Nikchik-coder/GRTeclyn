#!/usr/bin/env python3
"""The collapsing throat's ringdown (article Sec. VIII.A, queue-2e gate 4):
verify the fitted period against an independent fit, test whether the period
drifts across the window (does the ring follow the falling horizon mass?),
and set it against the Schwarzschild l = 2 fundamental of the horizon's
Misner-Sharp mass at the observation time and at the retarded (emission) time.

Reads only the tracked pack; prints a report; writes nothing.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/waves_throat_ringdown.py
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.optimize import curve_fit

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT

sys.path.insert(0, str(PACK_ROOT / "analysis"))
import queue2e_gates as Q  # noqa: E402

OMEGA_SCHW = 0.3737     # M omega_R of the Schwarzschild l = 2, n = 0 mode (ledger uses 0.374)


def main():
    d = Q.find_run(PACK_ROOT, Q.STRONG)
    t, cols = Q.load(d / "psi4_mode_l2m0.dat")
    m = Q.clean(t, 10.0, Q.T_JUNK_FREE)
    tt, y = Q.after_peak(t[m], cols[10.0][m])
    per, tau, f = Q.ringdown(tt, y)
    print(f"gate 4 (scan fit, R = 10, t = {tt[0]:.0f}-{tt[-1]:.0f}): period {per:.3f}, e-fold {tau:.1f}, "
          f"f = {f:.4f}, cycles in window {(tt[-1] - tt[0]) / per:.2f}")

    # the model at the fitted (f, tau), and its residual
    t0 = tt - tt[0]
    B = np.stack([np.exp(-t0 / tau) * np.cos(2 * np.pi * f * t0),
                  np.exp(-t0 / tau) * np.sin(2 * np.pi * f * t0)], axis=1)
    coef = np.linalg.lstsq(B, y, rcond=None)[0]
    res = y - B @ coef
    print(f"   rms residual / rms signal = {np.sqrt(np.mean(res ** 2)) / np.sqrt(np.mean(y ** 2)):.3f};  "
          f"max |residual| / max |signal| = {np.abs(res).max() / np.abs(y).max():.3f}")

    # independent nonlinear fit
    def model(x, A, ta, fr, ph):
        return A * np.exp(-x / ta) * np.cos(2 * np.pi * fr * x + ph)
    p, cov = curve_fit(model, t0, y, p0=[np.abs(y).max(), tau, f, 0.0], maxfev=20000)
    e = np.sqrt(np.diag(cov))
    print(f"   scipy curve_fit: period {1 / p[2]:.3f} +- {e[2] / p[2] ** 2:.3f}, e-fold {p[1]:.1f} +- {e[1]:.1f}")

    # window dependence (start and end)
    for lo in (26.0, 28.0, 30.0, 32.0):
        for hi in (50.0, 54.0, 58.0):
            w = (tt >= lo) & (tt <= hi)
            r = Q.ringdown(tt[w], y[w])
            if r:
                print(f"   window t = {lo:.0f}-{hi:.0f}: period {r[0]:.2f}, e-fold {r[1]:.1f}")

    # half-periods from the extrema of Re y on the 1-unit record (parabolic refinement)
    tr, yr = t[m], np.real(cols[10.0][m])
    ext = []
    for i in range(1, yr.size - 1):
        if (yr[i] - yr[i - 1]) * (yr[i + 1] - yr[i]) < 0 and tr[i] >= 20:
            a, b, c = yr[i - 1], yr[i], yr[i + 1]
            den = a - 2 * b + c
            dx = 0.5 * (a - c) / den if den else 0.0
            ext.append((tr[i] + dx, b))
    print("   extrema of Re r Psi4 at R = 10 (t, value): "
          + ", ".join(f"({x:.2f}, {v:+.2e})" for x, v in ext))
    hp = [(ext[k + 1][0] - ext[k][0]) for k in range(len(ext) - 1)]
    print("   half-periods between successive extrema: " + ", ".join(f"{h:.2f}" for h in hp)
          + "  -> periods " + ", ".join(f"{2 * h:.1f}" for h in hp))

    # the horizon mass and the Schwarzschild period, at observation and at emission time
    h = np.genfromtxt(d / "horizon_scan.dat", dtype=None, encoding=None, names=True)
    a = h[(h["centre"] == "A") & (h["n_mots"] > 0)]
    ta, Ma = a["time"], a["M_MS_mots"]

    def M_at(x):
        return float(np.interp(x, ta, Ma, left=np.nan, right=np.nan))
    print("   Schwarzschild period 2 pi M_MS / 0.3737 (M_MS of the throat-centred MOTS):")
    for x, _ in ext:
        for lag in (0.0, 8.0, 10.0):
            te = x - lag
            Mx = M_at(te)
            print(f"      extremum at t = {x:5.2f}: M_MS(t - {lag:4.1f} = {te:5.2f}) = {Mx:.3f} -> "
                  f"T_Schw = {2 * np.pi * Mx / OMEGA_SCHW:.2f}", end="")
        print()
    print(f"   mass floor {Ma[(ta >= 26) & (ta <= 58)].min():.4f} at t = "
          f"{ta[(ta >= 26) & (ta <= 58)][np.argmin(Ma[(ta >= 26) & (ta <= 58)])]:.0f};  "
          f"M_MS(26) = {M_at(26):.4f}, M_MS(58) = {M_at(58):.4f}, first MOTS t = {ta[0]:.0f} with {Ma[0]:.3f}")
    for lab, lo, hi in (("late window, observation time t = 43-58", 43, 58),
                        ("same stretch retarded by 8 (emission t = 35-50)", 35, 50),
                        ("same stretch retarded by 10 (emission t = 33-48)", 33, 48),
                        ("whole fit window retarded by 10 (emission t = 16-48)", 16, 48)):
        sel = (ta >= lo) & (ta <= hi)
        Ms = Ma[sel]
        print(f"   {lab}: M_MS {Ms.min():.3f}-{Ms.max():.3f} -> T_Schw "
              f"{2 * np.pi * Ms.min() / OMEGA_SCHW:.2f}-{2 * np.pi * Ms.max() / OMEGA_SCHW:.2f};  measured {per:.2f} is "
              f"{100 * (per / (2 * np.pi * Ms.max() / OMEGA_SCHW) - 1):+.1f} to "
              f"{100 * (per / (2 * np.pi * Ms.min() / OMEGA_SCHW) - 1):+.1f} %")


if __name__ == "__main__":
    main()
