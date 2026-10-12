#!/usr/bin/env python
"""Derive the correction to the published C = 0 b0 (PLB eq. 2.7) and verify it.

Background: check_azad_closed_forms.py showed the printed w, h0, phi20 are
exact (every residual 0), while the printed b0 fails the rr field equation
and disagrees with the PRD companion's own Fig. 1 for r < 0.  Because the
field equations are linear in b0, the correct function is

    b0_true = b0_printed + d,     L[d] = -res_PLB,

and the b0 operator collapses to L[d] = 2r/(r^2+r0^2) d'  (derived
symbolically; no d term), so d is ONE quadrature:

    d'(r)  = -(r^2+r0^2)/(2r) res_PLB(r)
    dd/du  = -(r0^2/2) sec^4(u)/tan(u) res_u(u),    r = r0 tan(u).

In u the integrand splits into ~60 independent terms (trig polynomials and
1/(u-pi/2)^k pieces from the phi in phi20's denominator, whose Si/Ci
fragments must cancel in the sum).  Each term integrates in its own forked
worker -- sympy is single-threaded, the terms are independent.

Stages, all logged with timestamps: build Ricci -> res_PLB -> integrand
terms -> parallel term integrals -> sum, Si/Ci audit, d/du back-check ->
decay normalisation at r -> +infinity -> parallel 3-equation verification
with the corrected b0 -> the correction in u and r form.

Run (repo root; CPU only):

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/derive_b0_correction.py \
        [--procs N] > b0_correction.log 2>&1 &

Success: "d/du check" and all three VERIFY lines print 0.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
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
uu = sp.Symbol("u", real=True)

A20 = 3 * J**2 / (r * r0**3) * (phi + sp.pi / 2 - 3 * r / (2 * r0)
                                - 4 / sp.pi
                                - (3 * r**2 + 4 * r0**2) / (2 * R2 * phi))

# Globals filled in main() before the fork; workers inherit them.
TERMS: list[sp.Expr] = []
B0C: sp.Expr = sp.S(0)


def integrate_term(i: int) -> tuple[int, sp.Expr]:
    it = sp.integrate(TERMS[i], uu)
    return i, it


def verify_component(nm: str) -> tuple[str, sp.Expr]:
    ee = sp.diff(cz.COMPONENTS[nm], eps, 2).subs(eps, 0) / 2
    pr = cz.project_l0(ee.subs({cz.h0: cz.H0, cz.b0: B0C,
                                cz.p20: A20}).doit()).doit()
    pu = pr.xreplace({sp.atan(r / r0): uu}).subs(r, r0 * sp.tan(uu))
    pu = sp.simplify(sp.radsimp(sp.expand(sp.together(pu))))
    if pu != 0:
        pu = sp.simplify(sp.expand_trig(pu))
    return nm, pu


def main() -> int:
    global TERMS, B0C
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--procs", type=int,
                    default=min(16, os.cpu_count() or 1))
    args = ap.parse_args()

    cz.build()
    log("build done")

    e2 = sp.diff(cz.COMPONENTS["rr"], eps, 2).subs(eps, 0) / 2
    res = cz.project_l0(e2.subs({cz.h0: cz.H0, cz.b0: cz.B0,
                                 cz.p20: A20}).doit()).doit()
    res_u = res.xreplace({sp.atan(r / r0): uu}).subs(r, r0 * sp.tan(uu))
    res_u = sp.cancel(sp.expand(sp.together(res_u)))
    log("res_PLB ready")

    integrand = sp.cancel(-(r0**2 / 2) / (sp.cos(uu)**4 * sp.tan(uu)) * res_u)
    integrand = sp.expand(sp.expand_trig(sp.cancel(sp.together(integrand))))
    TERMS = list(sp.Add.make_args(integrand))
    log(f"integrand: {len(TERMS)} terms; forking {args.procs} workers")

    ctx = mp.get_context("fork")  # inherit the built globals
    d_u = sp.S(0)
    bad = 0
    t_int = time.time()
    with ctx.Pool(processes=min(args.procs, len(TERMS))) as pool:
        for i, it in pool.imap_unordered(integrate_term,
                                         range(len(TERMS))):
            if it.has(sp.Integral):
                bad += 1
                log(f"UNINTEGRATED term {i}: {TERMS[i]}")
            d_u += it
    log(f"term integrals done in {time.time() - t_int:.1f}s, "
        f"{bad} unintegrated")
    if bad:
        return 1

    d_u = sp.simplify(sp.expand(d_u))
    log(f"raw d(u) = {d_u}")
    log(f"special functions left: {d_u.atoms(sp.Si, sp.Ci) or 'none'}")

    chk = sp.simplify(sp.expand_trig(sp.simplify(
        sp.diff(d_u, uu) - sp.expand(integrand))))
    log(f"d/du check (0 = good): {chk}")

    s_ = sp.Symbol("s", positive=True)
    lim = sp.limit(d_u.subs(uu, sp.pi / 2 - s_), s_, 0, "+")
    log(f"d at u = pi/2 before shift: {lim}")
    d_u = sp.simplify(d_u - lim)
    log(f"d(u) FINAL = {d_u}")

    d_r = d_u.subs(uu, sp.atan(r / r0))
    B0C = cz.B0 + d_r
    with ctx.Pool(processes=3) as pool:
        for nm, pu in pool.imap_unordered(verify_component,
                                          ("tt", "rr", "ang")):
            log(f"VERIFY {nm} residual with corrected b0: {pu}")

    log(f"correction d(r) = {sp.simplify(d_r)}")
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
