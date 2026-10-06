#!/usr/bin/env python3
"""Parameter-matched linear growth rate of the production drainhole (a = 2, m = 1).

The campaign's massive Ellis-Bronnikov drainhole is the gamma1 = m/a member of the
static family of Gonzalez, Guzman & Sarbach, CQG 26, 015010 (2009) [GGS I], Eq. (13),
with b = a, gamma0 = -pi*gamma1/2 (alpha -> 1 at the positive-mass end).  This script

  derive  re-derives, with sympy, the l = 0 linearised Einstein-ghost-scalar equations for
          g = -e^{2d}dt^2 + e^{2a}dx^2 + e^{2c}dOmega^2 and checks GGS I's master equation
          (23)-(24), zero mode (28) and regular potential W (32) against them, plus a second,
          independent reduction in the gauge dPhi = 0;
  A       solves GGS I Eq. (40), -chi'' + (bbar^2 + Wbar) chi = 0 in rho_bar, by shooting;
  B       solves the same operator by Chebyshev collocation (eigenvalue problem);
  C       solves the dPhi = 0 gauge ODE for dc = dr/r (it does not use W or the Darboux map),
          directly in production coordinates, so beta = lambda in units of M; the throat is an
          apparent singularity (Frobenius exponents 0, 3) bridged by the ODE's own series.

T = tau*alpha_th/R_star = GGS's tau_unstable/r_throat.  Prints closed forms, convergence,
GGS Table I reproduction, the gamma1 -> infinity limit (their Eq. 43), and the comparison with
the measured plateau rates (read through the claims extractors when the pack is present).

Usage: linear_mode.py [--no-derive] [--quick] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigvals
from scipy.optimize import brentq

A_PROD, M_PROD = 2.0, 1.0                         # production throat (clmThroatA, clmThroatM)
GGS_TABLE_I = {0: .846, .1: .841, .2: .826, .3: .805, .4: .782, .5: .758, .6: .737, .7: .718,
               .8: .701, .9: .687, 1: .675, 1.2: .656, 1.4: .642, 1.6: .631, 1.8: .624, 2: .618,
               2.5: .608, 3: .602, 3.5: .599, 4: .597, 4.5: .595, 5: .594, 5.5: .593, 6: .592,
               6.5: .592, 7: .591, 7.5: .591, 8: .590, 8.5: .590, 9: .590, 9.5: .590, 10: .590}
GGS_LIMIT = 0.588                                 # GGS I Sec. IV A, 1/beta_hat of Eq. (43)


# ------------------------------------------------------------------ symbolic derivation
def derive() -> list[tuple[str, float]]:
    """Every check returns a residual that must vanish (exactly, or ~1e-30 at 40 digits)."""
    import sympy as sp
    out: list[tuple[str, float]] = []

    def rec(name, val):
        try:
            v = float(abs(sp.N(val, 40))) if not isinstance(val, float) else val
        except TypeError:                                      # did not reduce to a number
            v = math.inf
        out.append((name, v))
        print(f"  [{'ok' if v < 1e-25 else 'FAIL'}] {name}: {v:.1e}")

    t, x, th, ph = sp.symbols("t x theta phi", real=True)
    b, g1, g0, P1, beta, eps = sp.symbols("b gamma1 gamma0 Phi1 beta epsilon", real=True)
    kap = -8 * sp.pi                                           # R_ab = kappa d_aPhi d_bPhi
    D, A, C, F = (sp.Function(n)(t, x) for n in ("d", "a", "c", "Phi"))
    X = [t, x, th, ph]
    g = sp.diag(-sp.exp(2 * D), sp.exp(2 * A), sp.exp(2 * C), sp.exp(2 * C) * sp.sin(th) ** 2)
    gi = g.inv()
    Gam = [[[sum(gi[i, l] * (sp.diff(g[l, j], X[k]) + sp.diff(g[l, k], X[j]) - sp.diff(g[j, k], X[l]))
                 for l in range(4)) / 2 for k in range(4)] for j in range(4)] for i in range(4)]

    def ric(j, k):
        return sp.simplify(sum(sp.diff(Gam[i][j][k], X[i]) - sp.diff(Gam[i][j][i], X[k])
                               + sum(Gam[i][i][l] * Gam[l][j][k] - Gam[i][k][l] * Gam[l][j][i]
                                     for l in range(4)) for i in range(4)))
    E = {jk: ric(*jk) - kap * sp.diff(F, X[jk[0]]) * sp.diff(F, X[jk[1]])
         for jk in [(0, 0), (0, 1), (1, 1), (2, 2)]}
    sq = sp.exp(D + A + 2 * C)
    E["box"] = (sp.diff(sq * gi[0, 0] * sp.diff(F, t), t) + sp.diff(sq * gi[1, 1] * sp.diff(F, x), x)) / sq

    # background: GGS I Eqs. (11)-(14)
    d0 = g1 * sp.atan(x / b) + g0
    a0, c0, F0 = -d0, sp.log(x ** 2 + b ** 2) / 2 - g1 * sp.atan(x / b) - g0, P1 * sp.atan(x / b)
    P1sq = -2 * (1 + g1 ** 2) / kap
    bg = {D: d0, A: a0, C: c0, F: F0}
    for k, v in E.items():
        rec(f"background solves E_{k}", sp.simplify(sp.simplify(v.subs(bg).doit()).subs(P1 ** 2, P1sq)))
    # campaign data (isotropic r) = GGS family with b = a, gamma1 = m/a, gamma0 = -pi gamma1/2
    r, aa, m = sp.symbols("r a m", positive=True)
    xr, Om = r - aa ** 2 / (4 * r), 1 + aa ** 2 / (4 * r ** 2)
    rec("dx/dr = Omega", sp.simplify(sp.diff(xr, r) - Om))
    rec("x^2 + a^2 = r^2 Omega^2", sp.simplify(xr ** 2 + aa ** 2 - (r * Om) ** 2))
    rec("u = d0(b=a, gamma1=m/a, gamma0=-pi m/2a)",
        sp.simplify((m / aa) * (sp.atan(xr / aa) - sp.pi / 2) - d0.subs({x: xr, b: aa, g1: m / aa, g0: -m / aa * sp.pi / 2})))
    rec("4 pi a^2 C^2 = a^2+m^2 <=> -kappa Phi1^2 = 2(1+gamma1^2)",
        sp.simplify(P1sq.subs(g1, m / aa) - (aa ** 2 + m ** 2) / (4 * sp.pi * aa ** 2)))

    # linearise
    dD, dA, dC, dF = (sp.Function(n)(t, x) for n in ("dd", "da", "dc", "dPhi"))
    pert = {D: d0 + eps * dD, A: a0 + eps * dA, C: c0 + eps * dC, F: F0 + eps * dF}
    L = {k: sp.simplify(sp.diff(v.subs(pert).doit(), eps).subs(eps, 0)) for k, v in E.items()}
    cx, Fx, dx0 = sp.diff(c0, x), sp.diff(F0, x), sp.diff(d0, x)
    random.seed(7)

    def rpts(n, extra=()):
        for _ in range(n):
            v = {x: sp.Rational(random.randint(-300, 300), 97), b: sp.Rational(random.randint(20, 300), 97),
                 g1: sp.Rational(random.randint(0, 300), 113), g0: sp.Rational(random.randint(-200, 200), 89)}
            for s in extra:
                v[s] = sp.Rational(random.randint(-300, 300), 71)
            v[P1] = sp.sqrt(P1sq.subs(v))
            yield v

    # (i) GGS master equation in the gauge dc = 0 (Psi = e^c dPhi is gauge invariant)
    L0 = {k: v.subs(dC, 0).doit() for k, v in L.items()}
    da_s = -4 * sp.pi * Fx * dF / cx                           # E_tx: 8pi Phi_x dPhi_t + 2 c_x da_t = 0
    rec("E_tx^(1)[dc=0] solved by da = kappa Phi_x dPhi/(2 c_x)", sp.simplify(L0[(0, 1)].subs(dA, da_s).doit()))
    s_ddx = sp.Symbol("ddx")
    ddx_s = sp.solve(L0[(2, 2)].subs(dA, da_s).doit().subs(sp.Derivative(dD, x), s_ddx), s_ddx)[0]
    Psi = sp.Function("Psi")(t, x)
    wv = L0["box"].subs(dA, da_s).doit().subs(sp.Derivative(dD, x), ddx_s).subs(dF, sp.exp(-c0) * Psi).doit()
    Ptt, Pxx, Px, P0 = sp.symbols("Ptt Pxx Px P0")
    wv = sp.expand(wv.subs({sp.Derivative(Psi, (t, 2)): Ptt, sp.Derivative(Psi, (x, 2)): Pxx})
                   .subs(sp.Derivative(Psi, x), Px).subs(Psi, P0))
    co = {s: wv.coeff(s) for s in (Ptt, Pxx, Px, P0)}
    edma = sp.exp(d0 - a0)
    V = sp.exp(4 * g1 * sp.atan(x / b) + 4 * g0) / (x ** 2 + b ** 2) * (
        1 - (x - g1 * b) ** 2 / (x ** 2 + b ** 2) + 2 * (1 + g1 ** 2) * b ** 2 / (x - g1 * b) ** 2)
    for name, e in [("master eq: Psi_xx coefficient = -e^{2(d-a)}", co[Pxx] + edma ** 2 * co[Ptt]),
                    ("master eq: Psi_x coefficient = -e^{d-a}(e^{d-a})_x", co[Px] + edma * sp.diff(edma, x) * co[Ptt]),
                    ("master eq: potential = GGS I Eq. (24)", co[P0] - V * co[Ptt])]:
        rec(name + " [12 random points, 40 digits]",
            max(abs(sp.N(e.subs(v), 40)) / abs(sp.N(co[Ptt].subs(v), 40)) for v in rpts(12)))
    Psi0 = sp.exp(c0) / (x - g1 * b) * (1 + g1 / b * (b + g1 * x) / (1 + g1 ** 2) * sp.atan(x / b))
    rec("zero mode Psi0 (GGS I Eq. 28) solves the static master eq",
        sp.simplify(-edma * sp.diff(edma * sp.diff(Psi0, x), x) + V * Psi0))
    # (ii) regular potential W = -V + 2 (dPsi0/Psi0)^2 at b = 1, gamma0 = 0 vs GGS I Eq. (32)
    u1 = {b: 1, g0: 0}
    E2 = sp.exp(2 * g1 * sp.atan(x))
    Wm = (-V + 2 * (E2 * sp.diff(Psi0, x) / Psi0) ** 2).subs(u1)
    Fg = 1 + g1 / (1 + g1 ** 2) * (1 + g1 * x) * sp.atan(x)
    Fgx = sp.diff(Fg, x)
    W32 = sp.exp(4 * g1 * sp.atan(x)) * (-3 / (1 + x ** 2) + 3 * (x - g1) ** 2 / (1 + x ** 2) ** 2 + 2 * (Fgx / Fg) ** 2
                                         - 4 * g1 / (1 + x ** 2) * Fgx / Fg + 4 * g1 / (1 + g1 ** 2) * (x - g1) / (Fg * (1 + x ** 2) ** 2))
    rec("W = -V + 2(dPsi0/Psi0)^2 equals GGS I Eq. (32) [12 random points]",
        max(abs(sp.N((Wm - W32).subs(v), 40)) / (1 + abs(sp.N(W32.subs(v), 40))) for v in rpts(12)))
    rec("massless W = -3/(1+x^2)^2", sp.simplify(W32.subs(g1, 0) + 3 / (1 + x ** 2) ** 2))
    y = sp.Symbol("y")
    for gv in (sp.Rational(1, 2), sp.Rational(1, 10), 3):
        ser = sp.series(W32.subs(g1, gv).subs(x, gv + y), y, 0, 1).removeO()
        rec(f"W regular at the throat, gamma1={gv} (sum |Laurent y^-1..-3|)",
            sum(abs(sp.simplify(ser.coeff(y, -k))) for k in (1, 2, 3)))
    # (iii) independent reduction in the gauge dPhi = 0, modes e^{beta t}
    L1 = {k: v.subs(dF, 0).doit() for k, v in L.items()}
    rec("box^(1)[dPhi=0] prop. to d_x(dd - da + 2 dc)",
        sp.simplify(L1["box"].subs(dD, dA - 2 * dC).doit()))
    z = sp.Function("z")(x)
    da_m = (sp.diff(z, x) + (cx - dx0) * z) / cx               # E_tx^(1) integrated in t
    mode = {dC: sp.exp(beta * t) * z, dA: sp.exp(beta * t) * da_m, dD: sp.exp(beta * t) * (da_m - 2 * z)}
    res = {k: sp.simplify(L1[k].subs(mode).doit().subs(t, 0)) for k in [(0, 0), (0, 1), (1, 1), (2, 2), "box"]}
    rec("E_tx^(1) and box^(1) on the dPhi=0 mode ansatz", sp.simplify(abs(res[(0, 1)]) + abs(res["box"])))
    ode = cx * (beta ** 2 * z - sp.exp(d0 - a0 - 2 * c0) * sp.diff(sp.exp(d0 - a0 + 2 * c0) * sp.diff(z, x), x)) \
        + 2 * sp.exp(2 * (d0 - c0)) * (sp.diff(z, x) - dx0 * z)
    rec("E_thth^(1) = ODE_dc / (c_x e^{2(d-c)})",
        sp.simplify(res[(2, 2)] - ode / (cx * sp.exp(2 * (d0 - c0)))))
    zpp = sp.solve(ode, sp.Derivative(z, (x, 2)))[0]
    Z0, Z1 = sp.symbols("Z0 Z1")
    for k in [(0, 0), (1, 1)]:
        e = res[k].subs(sp.Derivative(z, (x, 3)), sp.diff(zpp, x)).subs(sp.Derivative(z, (x, 2)), zpp)
        e = e.subs(sp.Derivative(z, (x, 2)), zpp).subs(sp.Derivative(z, x), Z1).subs(z, Z0)
        rec(f"E_{k}^(1) implied by ODE_dc [8 random points incl. beta, z, z']",
            max(abs(sp.N(e.subs(v), 40)) for v in rpts(8, extra=(beta, Z0, Z1))))
    # Frobenius at the throat: exponents {0, 3}, compatibility at order 3 for all beta
    for gv in (sp.Rational(1, 2), 0, 2):
        o = ode.subs({b: 1, g0: 0, g1: gv})
        cs = sp.symbols("c0:6")
        zz = sum(cs[n] * y ** n for n in range(6))
        ex = sp.expand(sp.series(o.subs(z, zz.subs(y, x - gv)).doit().subs(x, gv + y), y, 0, 4).removeO())
        sol = {}
        for n in (1, 2):
            sol[cs[n]] = sp.solve(ex.coeff(y, n - 1).subs(sol), cs[n])[0]
        rem = sp.simplify(ex.coeff(y, 2).subs(sol))
        rec(f"Frobenius gamma1={gv}: c3 free (exponents 0, 3) and order-3 compatibility holds for all beta",
            abs(sp.diff(rem, cs[3])) + abs(sp.simplify(rem.subs(cs[3], 0))))
    return out


# ------------------------------------------------------------------ numerics
RT = dict(method="DOP853", rtol=1e-12, atol=1e-14)


def bracket(x, g):
    """GGS I Eq. (32) bracket: W = e^{4 g atan x} * bracket (b = 1, gamma0 = 0)."""
    at, q = np.arctan(x), 1 + x * x
    F = 1 + g / (1 + g * g) * (1 + g * x) * at
    Fx = g / (1 + g * g) * ((1 + g * x) / q + g * at)
    return -3 / q + 3 * (x - g) ** 2 / q ** 2 + 2 * (Fx / F) ** 2 - 4 * g / q * Fx / F + 4 * g / (1 + g * g) * (x - g) / (F * q * q)


def _shoot_rho(bb, afun, wfun, xt, kP=40.0, rtol=1e-12):
    """Wronskian mismatch at the throat for -chi'' + (bb^2 + W(x)) chi = 0, dx/drho = a(x)."""
    rt = dict(RT, rtol=rtol)
    P = kP / bb
    out = []
    for sgn in (+1, -1):
        x0 = solve_ivp(lambda _, v: [afun(v[0])], [0, sgn * P], [xt], **rt).y[0, -1]
        k = math.sqrt(bb * bb + max(wfun(x0), -0.5 * bb * bb))
        s = solve_ivp(lambda _, v: [afun(v[0]), v[2], (bb * bb + wfun(v[0])) * v[1]],
                      [sgn * P, 0.0], [x0, 1.0, -sgn * k], **rt)
        out.append(s.y[1:, -1])
    (cR, pR), (cL, pL) = out
    return (cR * pL - cL * pR) / math.hypot(cR, pR) / math.hypot(cL, pL)


def _roots(f, grid):
    v = [f(p) for p in grid]
    return [brentq(f, grid[i], grid[i + 1], xtol=1e-15, rtol=1e-14, maxiter=200)
            for i in range(len(grid) - 1) if np.sign(v[i]) != np.sign(v[i + 1])]


def T_solverA(g, kP=40.0, rtol=1e-12):
    """GGS I Eq. (40); returns (list of T roots for T in [0.35, 1.6])."""
    s = math.sqrt(1 + g * g)
    afun = lambda x: math.exp(2 * g * (math.atan(x) - math.atan(g)))
    wfun = lambda x: afun(x) ** 2 * bracket(x, g)
    grid = np.sort(1 / (s * np.geomspace(0.35, 1.6, 24)))
    return [1 / (s * r) for r in _roots(lambda bb: _shoot_rho(bb, afun, wfun, g, kP, rtol), grid)]


def T_limit(kP=40.0, rtol=1e-12):
    """GGS I Eq. (43), the gamma1 -> infinity limit; T = 1/beta_hat."""
    afun = lambda z: math.exp(2 * (1 - 1 / z)) if z > 1e-3 else 0.0
    wfun = lambda z: afun(z) ** 2 * (2 / z ** 2 - 10 / z ** 3 + 3 / z ** 4) if z > 1e-3 else 0.0
    grid = np.sort(1 / np.geomspace(0.35, 1.6, 24))
    return [1 / r for r in _roots(lambda bb: _shoot_rho(bb, afun, wfun, 1.0, kP, rtol), grid)]


def cheb(N):
    s = np.cos(np.pi * np.arange(N + 1) / N)
    c = np.hstack([2, np.ones(N - 1), 2]) * (-1) ** np.arange(N + 1)
    dS = s[:, None] - s[None, :]
    Dm = np.outer(c, 1 / c) / (dS + np.eye(N + 1))
    return Dm - np.diag(Dm.sum(1)), s


def T_solverB(g, N=160, L=2.0):
    """GGS I Eq. (30), b=1, gamma0=0: -E(E chi_x)_x + W chi = -beta^2 chi, E = e^{2g atan x};
    x = g + L tan(pi s/2), Chebyshev in s, chi = 0 at s = +-1.  Returns (T, lowest two eigenvalues)."""
    Dm, s = cheb(N)
    th = np.pi * s[1:-1] / 2
    x = g + L * np.tan(th)
    ixs = np.zeros(N + 1)
    ixs[1:-1] = np.cos(th) ** 2 / (L * np.pi / 2)
    E = np.zeros(N + 1)
    E[1:-1] = np.exp(2 * g * np.arctan(x))
    Dx = (E * ixs)[:, None] * Dm
    Amat = -(Dx @ Dx)[1:-1, 1:-1] + np.diag(np.exp(4 * g * np.arctan(x)) * bracket(x, g))
    ev = np.sort(eigvals(Amat).real)
    beta = math.sqrt(-ev[0])
    return math.exp(2 * g * math.atan(g)) / (beta * math.sqrt(1 + g * g)), ev[:2]


def _taylor_basis(g, b, g0, beta, nmax):
    """Analytic local solutions of ODE_dc at the throat x0 = g b: (z0, z3) = (1, 0) and (0, 1)."""
    x0 = g * b
    q0 = x0 * x0 + b * b
    f = np.zeros(nmax + 4)                                  # f = e^{-4 g atan(x/b) - 4 g0}: q f' = -4 g b f
    f[0] = math.exp(-4 * g * math.atan(x0 / b) - 4 * g0)
    for n in range(nmax + 3):
        f[n + 1] = (-4 * g * b * f[n] - 2 * x0 * n * f[n] - (n - 1) * (f[n - 1] if n else 0.0)) / (q0 * (n + 1))
    h = np.zeros(nmax + 3)                                  # (x - x0) q f
    for k in range(1, nmax + 3):
        h[k] = q0 * f[k - 1] + (2 * x0 * f[k - 2] if k >= 2 else 0) + (f[k - 3] if k >= 3 else 0)
    basis = []
    for z0, z3 in ((1.0, 0.0), (0.0, 1.0)):
        zc = np.zeros(nmax + 1)
        zc[0] = z0
        for n in range(nmax):
            if n == 2:                                       # indicial root 3: c3 free, compatibility
                comp = 2 * g * b * zc[2] - beta ** 2 * (h[1] * zc[1] + h[2] * zc[0])
                assert abs(comp) < 1e-9 * (1 + abs(beta ** 2 * h[2] * zc[0])), comp
                zc[3] = z3
                continue
            conv = sum(h[k] * zc[n - k] for k in range(1, n + 1))
            rhs = (2 * x0 * n * (n - 2) + 2 * g * b) * zc[n] + ((n - 1) * (n - 2) * zc[n - 1] if n else 0) - beta ** 2 * conv
            zc[n + 1] = -rhs / (q0 * (n + 1) * (n - 2))
        basis.append(zc)
    return basis


def _mism_dc(beta, g, b, g0, kX=40.0, delta=None, rtol=1e-12, nmax=100, Xmin=8.0):
    """ODE_dc: (x-x0)[(x^2+b^2) z']' - 2(x^2+b^2) z' + 2 g b z = beta^2 (x-x0)(x^2+b^2) e^{-4g atan(x/b)-4g0} z."""
    rt = dict(RT, rtol=rtol)
    x0 = g * b
    delta = 0.3 * math.hypot(x0, b) if delta is None else delta
    B = _taylor_basis(g, b, g0, beta, nmax)
    ev = lambda zc, yy: (np.polyval(zc[::-1], yy), np.polyval((np.arange(1, len(zc)) * zc[1:])[::-1], yy))

    def rhs(x, v):
        q = x * x + b * b
        return [v[1], -((2 * x * (x - x0) - 2 * q) * v[1]
                        + (2 * g * b - beta ** 2 * (x - x0) * q * math.exp(-4 * g * math.atan(x / b) - 4 * g0)) * v[0]) / ((x - x0) * q)]
    co = []
    for sgn in (+1, -1):
        k = beta * math.exp(-sgn * math.pi * g - 2 * g0)
        X = x0 + sgn * max(kX / k, Xmin * b)
        s = solve_ivp(rhs, [X, x0 + sgn * delta], [1.0, -sgn * k * (1 + 2 * g * b / X)], **rt)
        Mb = np.array([ev(B[0], sgn * delta), ev(B[1], sgn * delta)]).T
        co.append(np.linalg.solve(Mb, s.y[:, -1]))
    (a1, b1), (a2, b2) = co
    return (a1 * b2 - b1 * a2) / math.hypot(a1, b1) / math.hypot(a2, b2)


def solverC(a, m, gauge="production", **kw):
    """dPhi = 0 gauge.  production: b = a, gamma0 = -pi m/(2a) -> beta = lambda [1/M].
    Returns list of (T, beta)."""
    g = m / a
    b, g0 = (a, -math.pi * g / 2) if gauge == "production" else (1.0, 0.0)
    a_th = math.exp(g * math.atan(g) + g0)
    r_th = b * math.sqrt(1 + g * g) * math.exp(-g * math.atan(g) - g0)
    grid = np.sort(a_th / (r_th * np.geomspace(0.35, 1.6, 24)))
    return [(a_th / (r * r_th), r) for r in _roots(lambda be: _mism_dc(be, g, b, g0, **kw), grid)]


def closed_forms(a=A_PROD, m=M_PROD):
    import mpmath as mp
    mp.mp.dps = 30
    a, m = mp.mpf(a), mp.mpf(m)
    rt = (m + mp.sqrt(m * m + a * a)) / 2
    X = (rt - a * a / (4 * rt)) / a
    u = (m / a) * (mp.atan(X) - mp.pi / 2)
    out = {"r_t": rt, "golden_ratio": (1 + mp.sqrt(5)) / 2, "X_t": X, "R_min": mp.e ** (-u) * mp.sqrt(a * a + m * m),
           "R_min_closed": mp.sqrt(5) * mp.e ** (mp.atan(2) / 2), "alpha_th": mp.e ** u, "alpha_th_closed": mp.e ** (-mp.atan(2) / 2)}
    out["R_over_alpha"] = out["R_min"] / out["alpha_th"]
    return {k: float(v) for k, v in out.items()}


def measured():
    """Unrounded plateau fits through the ledger's own extractors (fallback: ledger notes)."""
    root = pathlib.Path(__file__).resolve().parents[4]
    try:
        sys.path.insert(0, str(root / "research/merger/article/claims"))
        import lib  # noqa: E402,F401  (registers the pack paths)
        import extract_single as es  # noqa: E402
        return {lv: {"rate": es.single_plateau(run=r, what="rate"), "sd": es.single_plateau(run=r, what="sd"),
                     "tau": es.single_plateau(run=r, what="tau"), "T": es.single_proper_efold(run=r), "src": f"extract_single ({r})"}
                for lv, r in (("level 3", "single_hold_t100"), ("level 4", "single_hold_ml4_t100"))}
    except Exception as exc:  # pack absent
        print(f"  (claims extractors unavailable: {exc}; using ledger notes)")
        return {"level 3": {"rate": 0.1702, "sd": 0.0025, "tau": 5.875, "T": 0.8684, "src": "ledger_single.tsv notes"},
                "level 4": {"rate": 0.1902, "sd": 0.0022, "tau": 5.259, "T": 0.7772, "src": "ledger_single.tsv notes"}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-derive", action="store_true")
    ap.add_argument("--quick", action="store_true", help="skip the full Table I sweep and large-gamma1 runs")
    ap.add_argument("--json")
    args = ap.parse_args()
    t0 = time.time()
    R: dict = {}
    print("== 1. Closed forms, a = 2, m = 1")
    cf = closed_forms()
    R["closed_forms"] = cf
    for k, v in cf.items():
        print(f"  {k:16s} {v:.10f}")
    if not args.no_derive:
        print("== 2. Symbolic derivation checks (sympy)")
        chk = derive()
        R["derive_max_residual"] = max(v for _, v in chk)
        R["derive_n_checks"] = len(chk)
        print(f"  {len(chk)} checks, max residual {R['derive_max_residual']:.1e}   ({time.time() - t0:.0f}s)")
    g = M_PROD / A_PROD
    print(f"== 3. The unstable mode at gamma1 = m/a = {g}")
    print("  solver A (shooting, GGS I Eq. 40): T for kP x rtol")
    RA = {}
    for kP in (20.0, 30.0, 40.0, 60.0):
        for rtol in (1e-9, 1e-11, 1e-13):
            T = T_solverA(g, kP, rtol)
            RA[f"kP={kP},rtol={rtol}"] = T
            print(f"    kP={kP:4.0f} rtol={rtol:.0e}: n_roots={len(T)} T={T[0]:.12f}")
    print("  solver B (Chebyshev, GGS I Eq. 30): T for N x L  [lowest two eigenvalues]")
    RB = {}
    for L in (1.0, 2.0, 4.0):
        for N in (40, 80, 160, 320):
            T, ev = T_solverB(g, N, L)
            RB[f"N={N},L={L}"] = T
            print(f"    L={L:3.1f} N={N:3d}: T={T:.12f}  eig=({ev[0]:+.10f}, {ev[1]:+.3e})")
    print("  solver C (dPhi=0 gauge ODE, production coords a=2, m=1): lambda [1/M]")
    RC = {}
    for kX in (20.0, 40.0, 60.0):
        for dl in (0.4, 0.7, 1.0):
            for rtol in (1e-10, 1e-12):
                sol = solverC(A_PROD, M_PROD, kX=kX, delta=dl, rtol=rtol)
                RC[f"kX={kX},delta={dl},rtol={rtol}"] = sol
                print(f"    kX={kX:3.0f} delta={dl:.1f} rtol={rtol:.0e}: n_roots={len(sol)} lambda={sol[0][1]:.12f} T={sol[0][0]:.12f}")
    TA = RA["kP=40.0,rtol=1e-13"][0]
    TB = RB["N=320,L=2.0"]
    TC, lamC = RC["kX=40.0,delta=0.7,rtol=1e-12"][0]
    lam_from_T = cf["alpha_th"] / (TA * cf["R_min"])
    R.update(solverA=RA, solverB=RB, solverC=RC, T_A=TA, T_B=TB, T_C=TC, lambda_C=lamC, lambda_from_TA=lam_from_T,
             tau_M=1 / lamC)
    print(f"  => T = {TA:.10f} (A) {TB:.10f} (B) {TC:.10f} (C);  lambda = {lamC:.10f}/M (C direct), "
          f"{lam_from_T:.10f}/M (A via alpha_th/(T R_min));  tau = {1 / lamC:.6f} M")
    print("== 4. Validation against GGS I")
    rows = []
    gl = list(GGS_TABLE_I) if not args.quick else [0, 0.5, 1, 2]
    for gv in gl:
        T = T_solverA(float(gv))
        rows.append((gv, GGS_TABLE_I[gv], T[0], len(T)))
        print(f"  gamma1={gv:5}: GGS {GGS_TABLE_I[gv]:.3f}  here {T[0]:.6f}  (n_roots {len(T)}, rounds {'equal' if round(T[0], 3) == GGS_TABLE_I[gv] else 'DIFFER'})")
    R["tableI"] = rows
    T0c = solverC(1.0, 0.0, gauge="unit")
    T0b = T_solverB(0.0, 160, 2.0)[0]
    R["massless_B"], R["massless_C"] = T0b, T0c[0][0]
    print(f"  massless end, solvers B / C: {T0b:.10f} / {T0c[0][0]:.10f}  (GGS {GGS_TABLE_I[0]})")
    if not args.quick:
        big = {gv: T_solverA(gv)[0] for gv in (20.0, 50.0, 100.0)}
        TL = T_limit()
        R["large_gamma1"], R["limit_eq43"] = big, TL
        print("  large gamma1: " + ", ".join(f"T({k:.0f}) = {v:.5f}" for k, v in big.items())
              + f";  Eq. (43) limit 1/beta_hat = {TL[0]:.5f} (n_roots {len(TL)}; GGS {GGS_LIMIT}, table end 0.590)")
    print("== 5. Against the measured plateau rates (3D runs, R_min(t) plateau fits, coordinate time)")
    meas = measured()
    R["measured"] = meas
    for lv, d in meas.items():
        print(f"  {lv}: tau = {d['tau']:.4f} M (rate {d['rate']:.4f} +- {d['sd']:.4f}), T = {d['T']:.4f}  ->  "
              f"tau/tau_lin - 1 = {100 * (d['tau'] * lamC - 1):+.2f}%,  rate/lambda - 1 = {100 * (d['rate'] / lamC - 1):+.2f}% "
              f"({(lamC - d['rate']) / d['sd']:.1f} sd),  T/T_GGS(0.758) - 1 = {100 * (d['T'] / 0.758 - 1):+.2f}%   [{d['src']}]")
    print(f"done in {time.time() - t0:.0f}s")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
