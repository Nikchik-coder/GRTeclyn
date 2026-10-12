#!/usr/bin/env python
"""Check the O(J^2) slow-rotation tables against the full Einstein equations.

The generator (grteclyn_wrapper.analysis.spinning_wormhole.backgrounds,
``slowspin``) solves the perturbation equations of Chew, Kleihaus & Kunz
(arXiv:1608.05253, eqs. 10-13, 19).  This check does not use those
equations: it builds the Ricci tensor of the Kleihaus-Kunz ansatz from the
metric (sympy, ~20 s), evaluates

    E_ab = R_ab + 2 d_a psi d_b psi

on the generated solution (spectral eta derivatives, exact theta ones) and
prints max |E_ab| for J, J/2, J/4.  A correct O(J^2) background has every
residual falling as J^4 (ratio 16 per halving), t-phi as J^3 (ratio 8): the
first neglected orders.  A wrong O(J^2) term shows up as ratio 4.

Residuals are weighted by h^2/eta0^2 (tt, eta-eta), h/eta0^2 (theta-theta)
or 1, so the far zone counts; ee is also divided by its source 2 D^2/eta0^2.

Run (repo root, CPU only, ~1 min):

    grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/check_slowspin_einstein.py \\
        [--eta0 2 --mass 1 --J 1.0 --dgamma 0]
"""

from __future__ import annotations

import argparse
import math

import numpy as np
import sympy as sp

from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import (
    slow_rotation_solution,
)

COMPONENTS = {(0, 0): "tt", (0, 3): "tphi", (3, 3): "phph",
              (1, 1): "ee", (2, 2): "thth", (1, 2): "eth"}
ORDERS = [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]


def ricci_lambdas():
    """R_ab of the KK ansatz (p = 1) as numpy functions of the field jets."""
    t, eta, th, ph = sp.symbols("t eta theta phi", real=True)
    eta0 = sp.Symbol("eta0", positive=True)
    F = sp.Function("f")(eta, th)
    N = sp.Function("nu")(eta, th)
    W = sp.Function("omega")(eta, th)
    h = eta ** 2 + eta0 ** 2
    X = [t, eta, th, ph]
    g = sp.zeros(4)
    g[0, 0] = -sp.exp(F) + sp.exp(-F) * h * sp.sin(th) ** 2 * W ** 2
    g[0, 3] = g[3, 0] = -sp.exp(-F) * h * sp.sin(th) ** 2 * W
    g[3, 3] = sp.exp(-F) * h * sp.sin(th) ** 2
    g[1, 1] = sp.exp(-F) * sp.exp(N)
    g[2, 2] = sp.exp(-F) * sp.exp(N) * h
    gi = sp.simplify(g.inv())
    gam = [[[sp.simplify(sum(gi[a, d] * (sp.diff(g[d, b], X[c])
                                         + sp.diff(g[d, c], X[b])
                                         - sp.diff(g[b, c], X[d]))
                             for d in range(4)) / 2)
             for c in range(4)] for b in range(4)] for a in range(4)]
    # Derivatives -> plain symbols, highest order first so no derivative is
    # hit by the substitution of its own function.
    subs, names = [], []
    for fn, tag in ((F, "f"), (N, "nu"), (W, "w")):
        for i, j in ORDERS:
            expr = fn
            for _ in range(i):
                expr = sp.diff(expr, eta)
            for _ in range(j):
                expr = sp.diff(expr, th)
            sym = sp.Symbol(f"{tag}_{i}{j}")
            subs.append((expr, sym))
            names.append(sym)
    out = {}
    for b, c in COMPONENTS:
        expr = 0
        for a in range(4):
            expr += sp.diff(gam[a][b][c], X[a]) - sp.diff(gam[a][b][a], X[c])
            for d in range(4):
                expr += (gam[a][a][d] * gam[d][b][c]
                         - gam[a][c][d] * gam[d][b][a])
        expr = sp.simplify(expr)
        for old, new in subs:
            expr = expr.subs(old, new)
        assert not expr.atoms(sp.Derivative), (b, c)
        out[(b, c)] = sp.lambdify([eta, th, eta0] + names, expr, "numpy")
    return out, [s.name for s in names]


# n_cheb 64: the second eta derivatives, weighted by h^2 near the
# infinities, hit a roundoff floor from ~96 nodes up (tt first) -- the
# solution itself is converged at 48.
def residuals(ricci, names, eta0, gamma, J, dgamma, n_cheb=64, n_th=33):
    sol = slow_rotation_solution(eta0, gamma, n_cheb)
    chi = sol["chi"]
    c2 = np.cos(chi) ** 2
    deta = (c2 / eta0)[:, None] * sol["dchi"]          # d/d eta on the nodes

    def d(v):
        return deta @ v

    th = np.linspace(0.05, 0.5 * math.pi, n_th)
    one = np.ones_like(th)
    p2 = (3 * np.cos(th) ** 2 - 1) / 2
    p2t, p2tt = -3 * np.sin(th) * np.cos(th), -3 * np.cos(2 * th)
    s2, s2t, s2tt = np.sin(th) ** 2, np.sin(2 * th), 2 * np.cos(2 * th)
    J2 = J * J
    F = sol["f0"] + J2 * (sol["A"] + dgamma / eta0 ** 4 * sol["Ahom"])
    B, n = J2 * sol["B"], J2 * sol["n"]
    w = J * sol["w1"]
    w_e = -6 * J * np.exp(2 * sol["f0"]) * c2 ** 2 / eta0 ** 4
    zero = np.zeros((chi.size, th.size))
    jets = {
        "f_00": np.outer(F, one) + np.outer(B, p2),
        "f_10": np.outer(d(F), one) + np.outer(d(B), p2),
        "f_20": np.outer(d(d(F)), one) + np.outer(d(d(B)), p2),
        "f_01": np.outer(B, p2t), "f_02": np.outer(B, p2tt),
        "f_11": np.outer(d(B), p2t),
        "nu_00": np.outer(n, s2), "nu_10": np.outer(d(n), s2),
        "nu_20": np.outer(d(d(n)), s2), "nu_01": np.outer(n, s2t),
        "nu_02": np.outer(n, s2tt), "nu_11": np.outer(d(n), s2t),
        "w_00": np.outer(w, one), "w_10": np.outer(w_e, one),
        "w_20": np.outer(d(w_e), one), "w_01": zero, "w_02": zero,
        "w_11": zero,
    }
    inner = slice(1, -1)                                # drop the infinities
    ETA = np.outer(eta0 * np.tan(chi[inner]), one)
    TH = np.outer(np.ones(chi.size - 2), th)
    h = ETA ** 2 + eta0 ** 2
    args = [ETA, TH, eta0] + [jets[nm][inner] for nm in names]
    mass0 = -gamma * eta0 / (2 * math.pi)
    D2 = (eta0 ** 2 + mass0 ** 2
          + J2 * (sol["dD2"] + dgamma / eta0 ** 4 * sol["dD2_per_dgamma"]))
    out = {}
    for (b, c), fn in ricci.items():
        E = np.asarray(fn(*args)) * np.ones_like(h)
        if (b, c) == (1, 1):
            E = (E + 2 * D2 / h ** 2) * h ** 2 / (2 * D2)
        elif (b, c) == (0, 0):
            E = E * h ** 2 / eta0 ** 2
        elif (b, c) == (2, 2):
            E = E * h / eta0 ** 2
        out[COMPONENTS[(b, c)]] = float(np.max(np.abs(E)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--eta0", type=float, default=2.0)
    ap.add_argument("--mass", type=float, default=1.0,
                    help="static drainhole mass (0: symmetric family)")
    ap.add_argument("--J", type=float, default=1.0)
    ap.add_argument("--dgamma", type=float, default=0.0)
    a = ap.parse_args()
    gamma = -2 * math.pi * a.mass / a.eta0
    ricci, names = ricci_lambdas()
    prev = None
    for J in (a.J, a.J / 2, a.J / 4):
        res = residuals(ricci, names, a.eta0, gamma, J, a.dgamma)
        line = "  ".join(f"{k} {v:.2e}" for k, v in res.items())
        if prev:
            line += "   ratio " + " ".join(
                f"{k} {prev[k] / max(res[k], 1e-300):.1f}" for k in res)
        print(f"eta0 {a.eta0} mass {a.mass} J {J:.4g}: {line}", flush=True)
        prev = res
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
