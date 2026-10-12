#!/usr/bin/env python
"""Find the faulty printed function of the C = 0 O(J^2) solution and correct it.

check_azad_closed_forms.py: with Azad et al. (2.6)-(2.7) at C = 0 the tt and
ang residuals vanish and the rr residual does not.  The linear l = 0
operators of the three equations (stage 1 prints them) say which printed
function is at fault:

    tt :  h0'' + 2r/(r^2+r0^2) h0'                              h0 only
    ang:  -2r h0' + 2r b0' + 4 b0                               no phi20
    rr :  -h0'' + 2r/(r^2+r0^2) b0' + 4r0/(r^2+r0^2) phi20'

tt holds, so h0 is right; given h0, ang fixes b0 up to c/r^2 (singular at
the throat), so the printed b0 is right too; phi20 enters rr alone, so the
rr residual fixes phi20 up to an additive constant:

    dphi20' = -(r^2+r0^2)/(4 r0) res_rr.

(Correcting b0 from rr alone, the previous attempt, breaks ang, and its
quadrature has a non-elementary piece, int tan(v)/v dv, with a log
singularity at the throat; term-wise sympy integrate grew without bound.)

The quadrature needs no integrate() heuristics: with p = atan(r/r0) - pi/2
every coefficient is rational in r and p' = r0/(r^2+r0^2), so
dphi20' = sum_k C_k(r) p^k and the ansatz dphi20 = sum_k D_k(r) p^k solves
level by level with rational integrals only (an atan(r/r0) piece at one
level is the integration constant of the level above).  Normalised so that
phi20 -> 0 at r -> +infinity.

Every check is exact: after atan(r/r0) -> p + pi/2 a residual is a rational
function of (r, p), and p is transcendental over the rational functions of
r, so the residual vanishes identically iff it cancels to 0.

Run (repo root; CPU only, one core, about a minute):

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/derive_phi20_correction.py \
        > phi20_correction.log 2>&1

Success: the back-check, "phi20 - phi * printed" and the four VERIFY lines
(tt, rr, ang, scalar) all print 0.
"""

from __future__ import annotations

import os
import sys
import time

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_azad_closed_forms as cz  # noqa: E402

T0 = time.time()


def log(msg: str) -> None:
    print(f"[{time.time() - T0:8.1f}s pid {os.getpid()}] {msg}", flush=True)


r, r0, J, eps = cz.r, cz.r0, cz.J, cz.eps
phi, R2 = cz.phi, cz.R2
AT = sp.atan(r / r0)
p = sp.Symbol("p")                  # p = phi(r) = atan(r/r0) - pi/2
dp = r0 / R2                        # p'(r)

# Azad et al. eq. (2.7), phi20 as printed (the dimensionless 4/pi reading).
A20 = 3 * J**2 / (r * r0**3) * (phi + sp.pi / 2 - 3 * r / (2 * r0)
                                - 4 / sp.pi
                                - (3 * r**2 + 4 * r0**2) / (2 * R2 * phi))
UNKNOWNS = {"h0": cz.h0, "b0": cz.b0, "phi20": cz.p20}
PRINTED = {cz.h0: cz.H0, cz.b0: cz.B0, cz.p20: A20}


def to_p(expr: sp.Expr) -> sp.Expr:
    """atan(r/r0) -> p + pi/2, cancelled: a rational function of (r, p)."""
    out = sp.cancel(sp.together(expr.xreplace({AT: p + sp.pi / 2})))
    assert not out.has(sp.atan), out.atoms(sp.atan)
    return out


def order2_l0(expr: sp.Expr, sol: dict) -> sp.Expr:
    """O(eps^2) part of a field equation, sol substituted, projected on l = 0."""
    e2 = sp.diff(expr, eps, 2).subs(eps, 0) / 2
    return cz.project_l0(e2.subs(sol).doit()).doit()


def box_phi() -> sp.Expr:
    """Box Phi for Phi = phi + eps^2 phi20(r), the phantom field equation.

    Phi depends on r only and g is block-diagonal in r, so
    Box Phi = g^rr Phi'' + (g^rr)' Phi' + g^rr Phi' (ln -det g)' / 2.
    """
    g = cz.metric()
    grr = sp.cancel(g.inv()[1, 1])
    mdet = sp.factor(-g.det())
    Phi = phi + eps**2 * cz.p20
    dPhi = sp.diff(Phi, r)
    return (grr * sp.diff(dPhi, r) + sp.diff(grr, r) * dPhi
            + grr * dPhi * sp.cancel(sp.diff(mdet, r) / mdet) / 2)


def laurent(f: sp.Expr) -> dict[int, sp.Expr]:
    """{k: C_k(r)} with f = sum_k C_k(r) p^k (f rational in r and p)."""
    num, den = sp.fraction(sp.cancel(f))
    dterms = sp.Poly(den, p).terms()
    assert len(dterms) == 1, f"denominator not a monomial in p: {den}"
    (m,), dc = dterms[0]
    return {k - m: sp.cancel(c / dc) for (k,), c in sp.Poly(num, p).terms()}


def integrate_laurent(C: dict[int, sp.Expr]) -> sp.Expr:
    """sum_k D_k(r) p^k with d/dr of it = sum_k C_k p^k, D_k rational.

    The p^k coefficient of the derivative is D_k' + (k+1) D_{k+1} p', so
    k >= 0 is solved downwards from the top; an alpha atan(r/r0) term in
    the integral at level k is removed by the constant alpha/(k+1) in
    D_{k+1}.  k <= -1 is algebraic upwards from the bottom, and the p^-1
    equation, D_-1' = C_-1, is then a pure check.  Raises if a log (or a
    nonzero p^-1 mismatch) leaves the ansatz.
    """
    top, low = max(C), min(C)
    D = {top + 1: sp.S(0)}
    for k in range(top, -1, -1):
        rhs = sp.cancel(C.get(k, 0) - (k + 1) * D[k + 1] * dp)
        integral = sp.expand(sp.integrate(sp.apart(rhs, r), r))
        alpha = integral.coeff(AT)
        rest = sp.expand(integral - alpha * AT)
        if rest.has(sp.log, sp.atan):
            raise ValueError(f"level {k}: integral leaves the ansatz: {rest}")
        D[k + 1] = sp.cancel(D[k + 1] + alpha / (k + 1))
        D[k] = sp.cancel(rest)
        log(f"D[{k}] = {sp.factor(D[k])}  (constant {alpha / (k + 1)} "
            f"into D[{k + 1}])")
    if low < 0:
        D[low] = sp.S(0)
    for k in range(low, -1):
        D[k + 1] = sp.cancel((C.get(k, 0) - sp.diff(D[k], r))
                             / ((k + 1) * dp))
        log(f"D[{k + 1}] = {sp.factor(D[k + 1])}")
    mismatch = sp.cancel(C.get(-1, 0) - sp.diff(D.get(-1, 0), r))
    log(f"p^-1 equation D[-1]' = C[-1] (0 = elementary): {mismatch}")
    if mismatch != 0:
        raise ValueError("p^-1 coefficient has no rational antiderivative")
    return sum(Dk * p**k for k, Dk in D.items())


def main() -> int:
    cz.build()
    log("build done")

    lam, X = sp.Symbol("lam"), sp.Function("X")(r)
    for nm in ("tt", "rr", "ang"):
        for name, F in UNKNOWNS.items():
            sol = dict(PRINTED)
            sol[F] = PRINTED[F] + lam * X
            op = sp.diff(order2_l0(cz.COMPONENTS[nm], sol), lam)
            log(f"operator {nm} on {name}: {sp.simplify(sp.expand(op))}")

    res = to_p(order2_l0(cz.COMPONENTS["rr"], PRINTED))
    C = laurent(-R2 / (4 * r0) * res)
    log(f"dphi20' Laurent powers in p: {sorted(C)}")
    dphi = integrate_laurent(C)
    back = sp.cancel(sp.diff(dphi, r) + sp.diff(dphi, p) * dp
                     - sum(Ck * p**k for k, Ck in C.items()))
    log(f"d/dr back-check (0 = good): {back}")

    phi20 = to_p(A20) + dphi
    inf = sp.limit(phi20.subs(p, phi), r, sp.oo)
    log(f"phi20 at r = +inf before shift: {inf}")
    phi20 = sp.cancel(phi20 - inf)
    log(f"phi20 - phi * printed (0 = missing factor phi): "
        f"{sp.cancel(phi20 - p * to_p(A20))}")
    log(f"phi20 FINAL, p = phi: {sp.collect(sp.expand(phi20), p, sp.factor)}")

    fixed = dict(PRINTED)
    fixed[cz.p20] = phi20.subs(p, phi)
    box = box_phi()
    log(f"scalar O(eps^0) residual: {to_p(box.subs(eps, 0).doit())}")
    log(f"scalar residual with printed phi20: "
        f"{sp.factor(to_p(order2_l0(box, PRINTED)))}")
    for nm, ex in (("tt", cz.COMPONENTS["tt"]), ("rr", cz.COMPONENTS["rr"]),
                   ("ang", cz.COMPONENTS["ang"]), ("scalar", box)):
        log(f"VERIFY {nm} residual with corrected phi20: "
            f"{to_p(order2_l0(ex, fixed))}")
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
