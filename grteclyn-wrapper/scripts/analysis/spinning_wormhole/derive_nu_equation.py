#!/usr/bin/env python
"""The second-order nu equation of the Kleihaus-Kunz ansatz, derived and checked.

Chew, Kleihaus & Kunz (arXiv:1608.05253) close their system with eq. (12), a
second-order equation for nu from the Einstein equations that do not see the
scalar field (R_thth = 0 with R_tt, R_tph, R_phph).  The printed form is
wrong: closed-form extremal Kerr satisfies eqs. (10), (11), (13) and (19) and
leaves ~1e-2 in it (derive_xy_equations.py --stage kerr).  This script
derives the equation those components do give, and checks it:

  derive     R_thth of the ansatz (p = 1) with the second derivatives of f
             and omega eliminated by eqs. (10) and (11), scaled to the printed
             principal part d_eta(h s d_eta nu) + s d_thth nu - c d_th nu;
             prints it and its difference from the printed eq. (12)
  kerr       closed-form extremal Kerr (eta0 = 0) closes it at 160 digits;
             the printed eq. (12) does not
  static     the static drainhole closes it (symbolic zero)
  solutions  its residual on saved solver Solutions, which never imposed it,
             against the printed eq. (12)'s, both relative to the size of the
             equation's own terms

Run (repo root, CPU, ~1 min of sympy; capped, as a sympy runaway can OOM the
container -- CLAUDE.md "Environment"):

    (ulimit -v 16777216; grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/derive_nu_equation.py \
        [solution .npz ...])
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_einstein import jets_from_solution  # noqa: E402
from derive_xy_equations import ETA, TH, ckk_residuals  # noqa: E402

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution  # noqa: E402

ETA0 = sp.Symbol("eta0", positive=True)
ORDERS = [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]
SECOND = [(2, 0), (1, 1), (0, 2)]
F, NU, W = (sp.Function(n)(ETA, TH) for n in ("f", "nu", "omega"))
FIELDS = (("f", F), ("nu", NU), ("w", W))
JET = {tag: {ij: sp.Symbol(f"{tag}_{ij[0]}{ij[1]}") for ij in ORDERS} for tag, _ in FIELDS}
JET_SYMS = [JET[tag][ij] for tag, _ in FIELDS for ij in ORDERS]


def deriv(expr, i: int, j: int):
    for _ in range(i):
        expr = sp.diff(expr, ETA)
    for _ in range(j):
        expr = sp.diff(expr, TH)
    return expr


def to_jets(expr):
    """Derivatives of f, nu, omega -> the jet symbols f_ij, nu_ij, w_ij,
    highest order first so no derivative is hit by its own function's."""
    for tag, fn in FIELDS:
        for i, j in ORDERS:
            expr = expr.subs(deriv(fn, i, j), JET[tag][(i, j)])
    assert not expr.atoms(sp.Derivative)
    return expr


def r_thth():
    """R_thth of the ansatz (p = 1), in jet symbols."""
    t, ph = sp.symbols("t phi", real=True)
    h = ETA**2 + ETA0**2
    s = sp.sin(TH)
    X = [t, ETA, TH, ph]
    g = sp.zeros(4)
    g[0, 0] = -sp.exp(F) + sp.exp(-F) * h * s**2 * W**2
    g[0, 3] = g[3, 0] = -sp.exp(-F) * h * s**2 * W
    g[3, 3] = sp.exp(-F) * h * s**2
    g[1, 1] = sp.exp(-F) * sp.exp(NU)
    g[2, 2] = sp.exp(-F) * sp.exp(NU) * h
    gi = sp.simplify(g.inv())
    gam = [[[sp.simplify(sum(gi[a, d] * (sp.diff(g[d, b], X[c]) + sp.diff(g[d, c], X[b])
                                         - sp.diff(g[b, c], X[d])) for d in range(4)) / 2)
             for c in range(4)] for b in range(4)] for a in range(4)]
    b = c = 2
    expr = 0
    for a in range(4):
        expr += sp.diff(gam[a][b][c], X[a]) - sp.diff(gam[a][b][a], X[c])
        for d in range(4):
            expr += gam[a][a][d] * gam[d][b][c] - gam[a][c][d] * gam[d][b][a]
    return to_jets(sp.expand(sp.simplify(expr)))


def derive():
    """(the derived nu equation, the printed eq. (12)), both in jet symbols."""
    R = r_thth()
    ckk = {k: to_jets(v) for k, v in ckk_residuals(F, NU, W, ETA0).items() if k in ("10", "11", "12")}
    sec = [JET[tag][ij] for tag, _ in FIELDS for ij in SECOND]
    for e in (R, *ckk.values()):              # quasi-linear: no products of second derivatives
        assert all(sp.simplify(sp.diff(e, a, b)) == 0 for a in sec for b in sec)
    al, be = sp.symbols("alpha beta")
    comb = R - al * ckk["10"] - be * ckk["11"]
    sol = sp.solve([sp.diff(comb, JET["f"][(2, 0)]), sp.diff(comb, JET["w"][(2, 0)])],
                   [al, be], dict=True)
    assert len(sol) == 1, sol
    nu_eq = comb.subs(sol[0])
    for tag in ("f", "w"):                    # every second derivative of f and omega gone
        for ij in SECOND:
            assert sp.simplify(sp.diff(nu_eq, JET[tag][ij])) == 0, (tag, ij)
    nu_eq = sp.expand(sp.simplify(nu_eq * sp.sin(TH) / sp.diff(nu_eq, JET["nu"][(0, 2)])))
    return nu_eq, sp.expand(ckk["12"])


def on_fields(expr, f, nu, w, eta0):
    """``expr`` with the jets of explicit fields f, nu, w substituted."""
    sub = {ETA0: eta0}
    for tag, field in (("f", f), ("nu", nu), ("w", w)):
        for i, j in ORDERS:
            sub[JET[tag][(i, j)]] = deriv(field, i, j)
    return expr.subs(sub)


def check_kerr(nu_eq, eq12) -> bool:
    """Extremal Kerr (a = M, eta0 = 0, r = eta + M), as in derive_xy_equations."""
    M = sp.Symbol("M", positive=True)
    r = ETA + M
    sig = r**2 + M**2 * sp.cos(TH) ** 2
    gpp = r**2 + M**2 + 2 * M**3 * r * sp.sin(TH) ** 2 / sig     # g_phph / sin^2
    f = -sp.log(gpp / ETA**2)
    w = 2 * M**2 * r / (sig * gpp)
    nu = sp.log(sig / ETA**2) + f
    new, old = (on_fields(e, f, nu, w, 0) for e in (nu_eq, eq12))
    pts = [{ETA: sp.Rational(7, 10), TH: sp.Rational(9, 10), M: 1},
           {ETA: sp.Rational(3, 2), TH: sp.Rational(1, 3), M: 1},
           {ETA: 4, TH: sp.Rational(6, 5), M: 2}]
    worst_new = max(abs(new.subs(p).evalf(160)) for p in pts)
    least_old = min(abs(old.subs(p).evalf(160)) for p in pts)
    print(f"kerr: derived max |residual| {sp.N(worst_new, 3)}, printed eq. (12) min {sp.N(least_old, 3)}")
    return worst_new <= sp.Float(1e-150) and least_old >= sp.Float(1e-4)


def check_static(nu_eq) -> bool:
    gam = sp.Symbol("gamma", real=True)
    f = gam / 2 * (1 - 2 / sp.pi * sp.atan(ETA / ETA0))
    zero = sp.simplify(on_fields(nu_eq, f, sp.Integer(0), sp.Integer(0), ETA0))
    print(f"static drainhole: derived residual simplifies to {zero}")
    return zero == 0


def check_solutions(nu_eq, eq12, paths, c_gate: float = 0.05) -> None:
    """max |residual| over the interior nodes and away from the ends (eta0^2/h >= c_gate^2),
    relative to the largest |term| of the derived equation at that node."""
    args = [ETA, TH, ETA0] + JET_SYMS
    lam_new, lam_old = (sp.lambdify(args, e, "numpy") for e in (nu_eq, eq12))
    lam_terms = [sp.lambdify(args, t, "numpy") for t in sp.Add.make_args(nu_eq)]
    for path in paths:
        sol = Solution.load(path)
        jets = jets_from_solution(sol)
        ix = iy = slice(1, -1)
        eta = sol.radial_map.eta(sol.sx[ix])[:, None]
        th = 0.5 * np.arccos(np.clip(sol.sy[iy][None, :], -1.0, 1.0))
        shape = jets["f_00"].shape
        vals = [np.broadcast_to(eta, shape), np.broadcast_to(th, shape), sol.eta0] + \
               [jets[s.name] for s in JET_SYMS]
        scale = np.max([np.abs(np.asarray(t(*vals)) * np.ones(shape)) for t in lam_terms], axis=0)
        mask = sol.eta0**2 / (eta**2 + sol.eta0**2) * np.ones(shape) >= c_gate**2
        row = []
        for lam in (lam_new, lam_old):
            e = np.abs(np.asarray(lam(*vals)) * np.ones(shape))
            row.append(f"{e.max():.1e} / {(e[mask] / scale[mask]).max():.1e}")
        obs = sol.observables
        print(f"{os.path.basename(path)} (v_e {obs.get('v_e', float('nan')):.3f}, "
              f"J {obs.get('J', float('nan')):.4g}): derived {row[0]}   printed (12) {row[1]}"
              f"   (max |E|  /  max |E|/|term|, C >= {c_gate})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solutions", nargs="*", help="saved Solution .npz paths")
    args = ap.parse_args()
    nu_eq, eq12 = derive()
    s, c = sp.symbols("s c")
    show = lambda e: sp.collect(sp.expand(e.subs({sp.sin(TH): s, sp.cos(TH): c})),  # noqa: E731
                                [JET["nu"][ij] for ij in ORDERS], sp.factor)
    print("derived nu equation (0 = ...):")
    sp.pprint(show(nu_eq), wrap_line=False)
    print("derived minus printed eq. (12):")
    sp.pprint(sp.factor(show(nu_eq - eq12)), wrap_line=False)
    ok = check_kerr(nu_eq, eq12)
    ok = check_static(nu_eq) and ok
    if args.solutions:
        check_solutions(nu_eq, eq12, args.solutions)
    print("all symbolic checks pass" if ok else "SYMBOLIC CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
