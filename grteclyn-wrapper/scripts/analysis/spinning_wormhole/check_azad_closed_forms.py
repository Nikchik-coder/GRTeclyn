#!/usr/bin/env python
"""Verify Azad et al. (2.6)-(2.7) (C = 0) against the exact field equations.

Fully symbolic, no numerics.  Builds the Ricci tensor of the
Hartle-Thorne-gauge metric (their eq. 2.3, l = 2 sector off -- it decouples
from l = 0 at this order, k0 = 0), expands the Einstein-phantom equations
E_ab = R_ab + 2 d_a Phi d_b Phi to O(eps^2), projects on l = 0, substitutes
the paper's closed forms and simplifies each residual to closed form.
Residual 0 = the printed formulas are exact.

Checked equations and the printed-formula question they settle:
  O(eps)   t-phi        -> w(r), eq. (2.6)
  O(eps^2) tt, rr, ang  -> h0, b0, phi20, eq. (2.7), including which reading
                           of the "4/(pi r0)" term is right: the bracket's
                           other terms are dimensionless, so it is tried both
                           as 4/pi and as printed.

sympy is single-threaded, so each (equation, reading) residual runs in its
own forked worker; the Ricci tensor is computed once in the parent and
inherited (fork start method -- forkserver would re-import and recompute).
The heavy step is the final simplify of tt and rr (tens of minutes each);
the workers log start and end of every stage so slow and stuck are
distinguishable.

Run (from the repo root, any node with the wrapper venv):

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/check_azad_closed_forms.py \
        [--procs N] > azad_check.log 2>&1 &

Six residual lines end in "residual: 0" on success; "done" is last.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import time

import sympy as sp

T0 = time.time()


def log(msg: str) -> None:
    print(f"[{time.time() - T0:8.1f}s pid {os.getpid()}] {msg}", flush=True)


t, r, th, ph = sp.symbols("t r theta phi", real=True)
X = [t, r, th, ph]
r0 = sp.Symbol("r0", positive=True)
J, eps = sp.symbols("J epsilon", real=True)
R2 = r**2 + r0**2
s = sp.sin(th)


def ricci(g: sp.Matrix) -> sp.Matrix:
    """Ricci tensor of a 4-metric g on coordinates X (textbook formula)."""
    ginv = sp.simplify(g.inv())
    n = 4
    dg = [[[sp.diff(g[a, b], X[c]) for c in range(n)] for b in range(n)]
          for a in range(n)]
    Gam = [[[sp.S(0)] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(b, n):
                val = sum(ginv[a, d] * (dg[d][b][c] + dg[d][c][b] - dg[b][c][d])
                          for d in range(n)) / 2
                val = sp.simplify(val)
                Gam[a][b][c] = Gam[a][c][b] = val
    R = sp.zeros(n)
    for b in range(n):
        for c in range(b, n):
            val = sp.S(0)
            for a in range(n):
                val += sp.diff(Gam[a][b][c], X[a]) - sp.diff(Gam[a][b][a], X[c])
                for d in range(n):
                    val += Gam[a][a][d] * Gam[d][b][c] \
                        - Gam[a][c][d] * Gam[d][b][a]
            R[b, c] = R[c, b] = val
    return R


# --- background and perturbation (C = 0) --------------------------------
# Static EB: f = 0, Phi = phi(r); first order: w(r); second order, l = 0:
# h0, b0, phi20 generic until substitution.
h0, b0, p20 = (sp.Function(n)(r) for n in ("h0", "b0", "phi20"))
phi = sp.atan(r / r0) - sp.pi / 2
w = 3 * J / r0**3 * (sp.pi / 2 - sp.atan(r / r0) - r * r0 / R2)  # eq. (2.6)

# Azad et al. eq. (2.7); DM is the printed Delta M.
DM = 3 * J**2 * (sp.pi**2 - 8) / (2 * sp.pi * r0**3)
B0 = DM / r * (1 - phi * r0 / r) + 6 * J**2 / (r * r0**3) * (r0 / r + phi) \
    - 3 * J**2 / (r**2 * r0**2) * phi**2
H0 = 3 * J**2 / r0**4 * (phi**2 + (sp.pi**2 - 8) / (2 * sp.pi) * phi
                         - r0**2 / R2)
READINGS = {"4/pi": 4 / sp.pi, "4/(pi r0)": 4 / (sp.pi * r0)}

# Globals filled by build() in the parent, inherited by forked workers.
COMPONENTS: dict[str, sp.Expr] = {}


def metric() -> sp.Matrix:
    """The O(eps^2) metric on X: eq. (2.3), l = 2 sector off, k0 = 0."""
    g = sp.zeros(4)
    g[0, 0] = -(1 + 2 * eps**2 * h0) + R2 * s**2 * eps**2 * w**2
    g[0, 3] = g[3, 0] = -R2 * s**2 * eps * w
    g[3, 3] = R2 * s**2
    g[1, 1] = 1 + 2 * eps**2 * b0
    g[2, 2] = R2
    return g


def build() -> None:
    g = metric()
    log("metric set; computing Ricci")
    Ric = ricci(g)
    log("Ricci done")

    Phi = phi + eps**2 * p20
    dPhi = [0, sp.diff(Phi, r), 0, 0]
    E = sp.Matrix(4, 4, lambda a, c: Ric[a, c] + 2 * dPhi[a] * dPhi[c])

    e1 = sp.simplify(sp.diff(E[0, 3], eps).subs(eps, 0))
    log(f"O(eps) tphi residual: {e1}")

    COMPONENTS["tt"] = E[0, 0]
    COMPONENTS["rr"] = E[1, 1]
    COMPONENTS["ang"] = E[2, 2] + E[3, 3] / s**2


def project_l0(expr: sp.Expr) -> sp.Expr:
    """(1/2) integral of expr*sin(theta) over [0, pi], term by term.

    Exact and fast: each top-level term first has its theta-FREE factors
    (the radial jungle) split off unexpanded -- a whole-expression expand is
    what ran for hours -- then only the small theta-dependent remainder is
    expanded, and each distinct theta factor integrates once from a cache.
    (A Poly split over (sin, cos) is NOT safe here: simplify leaves
    sin(2 theta) and tan(theta) atoms, which Poly silently holds as
    constant coefficients and the projection comes out theta-dependent.)
    """
    acc: dict[sp.Expr, sp.Expr] = {}
    for term in sp.Add.make_args(expr):
        rfree, dep = term.as_independent(th)
        for sub in sp.Add.make_args(sp.expand(dep)):
            rp, tp = sub.as_independent(th)
            acc[tp] = acc.get(tp, sp.S(0)) + rfree * rp
    out = sp.S(0)
    for tp, coeff in acc.items():
        out += coeff * sp.integrate(tp * s, (th, 0, sp.pi))
    return out / 2


def residual(task: tuple[str, str, str]) -> tuple[str, str, sp.Expr]:
    nm, reading, variable = task
    four = READINGS[reading]
    A20 = 3 * J**2 / (r * r0**3) * (phi + sp.pi / 2 - 3 * r / (2 * r0) - four
                                    - (3 * r**2 + 4 * r0**2) / (2 * R2 * phi))
    log(f"{nm} [{reading}]: expanding to O(eps^2)")
    e2 = sp.diff(COMPONENTS[nm], eps, 2).subs(eps, 0) / 2
    e2 = e2.subs({h0: H0, b0: B0, p20: A20}).doit()
    if variable == "u":
        # Exact change of variable r = r0 tan(u) (bijective on u in
        # (-pi/2, pi/2)): atan(r/r0) becomes the plain symbol u and every
        # coefficient a trig polynomial, which simplify handles in seconds
        # instead of hours.  Zero here iff zero in r.
        uu = sp.Symbol("u", real=True)
        e2 = e2.xreplace({sp.atan(r / r0): uu}).subs(r, r0 * sp.tan(uu))
    log(f"{nm} [{reading}]: projecting on l = 0")
    proj = project_l0(e2)
    log(f"{nm} [{reading}]: simplifying the residual ({variable} variable)")
    res = sp.simplify(sp.radsimp(sp.expand(sp.together(proj))))
    if res != 0:
        res = sp.simplify(sp.expand_trig(res))
    return nm, reading, res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--procs", type=int, default=min(6, os.cpu_count() or 1),
                    help="worker processes (6 independent tasks; default "
                    "min(6, cores))")
    ap.add_argument("--variable", choices=("r", "u"), default="r",
                    help="simplify the residual in r as it stands, or after "
                    "the exact substitution r = r0 tan(u) (same zeros, "
                    "orders of magnitude faster)")
    args = ap.parse_args()

    build()
    tasks = [(nm, rd, args.variable)
             for rd in READINGS for nm in ("tt", "rr", "ang")]
    log(f"forking {min(args.procs, len(tasks))} workers for {len(tasks)} tasks")
    ctx = mp.get_context("fork")  # inherit the Ricci; forkserver recomputes it
    failures = 0
    with ctx.Pool(processes=min(args.procs, len(tasks))) as pool:
        for nm, reading, res in pool.imap_unordered(residual, tasks):
            log(f"RESULT {nm} [{reading}] residual: {res}")
            if res != 0:
                failures += 1
    log(f"done, {failures} nonzero residuals")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
