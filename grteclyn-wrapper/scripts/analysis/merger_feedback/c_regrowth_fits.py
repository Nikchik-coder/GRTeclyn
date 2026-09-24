#!/usr/bin/env python3
r"""Fits to the single-throat MOTS histories of Fig. 3 (task C(c)(i), 2026-09-24).

Descriptive only: the forms are compared by their rms residual and by AIC
(n ln(RSS/n) + 2k), on the throat-centred oriented scan (horizon_scan.dat,
centre A -- the rows plot_horizon_regrowth draws).  Per arm and quantity
(R_mots, M_MS):

  SHRINK, MOTS formation -> radius floor
    tanh      y = y_f + A [1 - tanh((t - t0)/w)] / 2          (4 parameters)
    exp-late  y = y_f + B exp(-(t - t0)/tau), fitted on the last 12 units
              before the floor (3 parameters)
  REGROWTH, floor -> end of record
    linear    y = y_f + s (t - t_f)                            (2)
    exp-sat   y = y_inf - B exp(-(t - t_f)/tau)                (3)
    tanh      y = y_f + A [1 + tanh((t - t0)/w)] / 2           (4)
    power     y = y_f + C (t - t_f)^p                          (3; t_f fixed at the floor)

Arms: level 3 (single_eps_p1e2_t100), level 4 spherical
(single_eps_p1e2_q1e2_ml4_scalar_t100: its binary never read the eps_2 key, so
its data are the +1e-2 kick alone -- runs_index.tsv), level 4 + eps_2 = 0.005,
level 4 + eps_2 = 0.05, and the pure-quadrupole arm (shrink only).

    grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/c_regrowth_fits.py
"""

from __future__ import annotations

import math
import pathlib
import sys
import warnings

import numpy as np
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore")
REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "merger" / "article" / "claims"))
import extract_single as es  # noqa: E402

ARMS = [("single_eps_p1e2_t100", "level 3, eps=+1e-2"),
        ("single_eps_p1e2_q1e2_ml4_scalar_t100", "level 4, eps=+1e-2 (spherical)"),
        ("single_eps_p1e2_q5e3_ml4_t100", "level 4, +eps2=0.005"),
        ("single_eps_p1e2_q5e2_ml4_t100", "level 4, +eps2=0.05"),
        ("single_pureq_q1e2_ml4_t100", "level 4, pure quadrupole")]


def f_tanh_dn(t, yf, A, t0, w): return yf + A * (1 - np.tanh((t - t0) / w)) / 2
def f_tanh_up(t, yf, A, t0, w): return yf + A * (1 + np.tanh((t - t0) / w)) / 2
def f_exp_dn(t, yf, B, tau): return yf + B * np.exp(-(t - T0[0]) / tau)
def f_lin(t, yf, s): return yf + s * (t - T0[0])
def f_exp_sat(t, yinf, B, tau): return yinf - B * np.exp(-(t - T0[0]) / tau)
def f_pow(t, yf, C, p): return yf + C * np.clip(t - T0[0], 0, None) ** p


T0 = [0.0]   # reference time shared by the fixed-origin forms


def fit(f, t, y, p0):
    try:
        p, cov = curve_fit(f, t, y, p0=p0, maxfev=40000)
    except Exception:
        return None
    res = y - f(t, *p)
    n, k = len(y), len(p)
    rss = float(np.sum(res**2))
    err = np.sqrt(np.clip(np.diag(cov), 0, None)) if cov is not None else np.full(k, np.nan)
    return dict(p=p, err=err, rms=math.sqrt(rss / n), aic=n * math.log(max(rss, 1e-300) / n) + 2 * k, n=n)


def show(label, r, names):
    if r is None:
        print(f"      {label:9s} failed"); return
    ps = ", ".join(f"{nm}={v:.4g}±{e:.2g}" for nm, v, e in zip(names, r["p"], r["err"]))
    print(f"      {label:9s} rms={r['rms']:.2e}  AIC={r['aic']:7.1f}  {ps}")


def main() -> int:
    for run, label in ARMS:
        a = es._mots(run, "A")
        t, R, M = a[:, 0], a[:, 1], a[:, 2]
        i = int(np.argmin(R))
        print(f"== {label}  ({run}): MOTS t={t[0]:.0f}..{t[-1]:.0f}, floor t={t[i]:.0f}")
        for qname, y in (("R_mots", R), ("M_MS", M)):
            print(f"   {qname}:")
            ts, ys = t[: i + 1], y[: i + 1]
            print(f"    shrink t={ts[0]:.0f}-{ts[-1]:.0f} ({len(ts)} rows)")
            show("tanh", fit(f_tanh_dn, ts, ys, [ys[-1], ys[0] - ys[-1], ts.mean(), 5.0]), ["y_f", "A", "t0", "w"])
            sel = ts >= ts[-1] - 12
            T0[0] = ts[sel][0]
            show("exp-late", fit(f_exp_dn, ts[sel], ys[sel], [ys[-1], ys[sel][0] - ys[-1], 4.0]), ["y_f", "B", "tau"])
            if i >= len(t) - 3:
                continue
            tg, yg = t[i:], y[i:]
            T0[0] = tg[0]
            print(f"    regrowth t={tg[0]:.0f}-{tg[-1]:.0f} ({len(tg)} rows), gain {100*(yg[-1]/yg[0]-1):.2f}%")
            show("linear", fit(f_lin, tg, yg, [yg[0], 0.004]), ["y_f", "slope"])
            show("exp-sat", fit(f_exp_sat, tg, yg, [yg[-1] + 0.02, yg[-1] - yg[0], 30.0]), ["y_inf", "B", "tau"])
            show("tanh", fit(f_tanh_up, tg, yg, [yg[0], yg[-1] - yg[0], tg.mean(), 15.0]), ["y_f", "A", "t0", "w"])
            show("power", fit(f_pow, tg, yg, [yg[0], 0.005, 1.0]), ["y_f", "C", "p"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
