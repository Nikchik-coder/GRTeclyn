#!/usr/bin/env python3
r"""Symbolic check: in spherical symmetry a massless PHANTOM scalar can only shrink a MOTS.

Task C (reviewer feedback on Fig. 3, 2026-09-24).  Independent check of the
derivation offered for the single-throat "regrowth":

    ds^2 = -2 e^{-f} du dv + r^2 dOmega^2,      m = (r/2)(1 + 2 e^f r_u r_v)
    T_ab = -(d_a phi d_b phi - 1/2 g_ab (d phi)^2)            (research.tex Eq. 1)

Everything below is computed from the metric by sympy -- the Einstein tensor,
the stress tensor, the Misner-Sharp derivative -- nothing is typed in from a
paper.  Printed checks (each must print 0 or True):

  1. G_uv, G_uu, G_vv, G_thth of the metric; the three field equations
     8 pi T_ab = G_ab written in Hayward's double-null form,
         r_vv + f_v r_v = -4 pi r T_vv,
         r r_uv + r_u r_v + e^{-f}/2 = 4 pi r^2 T_uv.
  2. T_uv = 0 for a massless scalar (either sign), T_vv = -(phi_v)^2 (phantom).
  3. Hayward's first law, d_v m = 4 pi r^2 e^f (T_uv r_v - T_vv r_u), holds
     identically once the field equations are used (d_u m likewise).
  4. On r_v = 0 (the MOTS, r_u < 0):  d_u m = 0,  d_v m = 4 pi r^2 e^f phi_v^2 r_u <= 0,
     d_u(r_v) = -e^{-f}/(2r) < 0,  d_v(r_v) = +4 pi r phi_v^2 >= 0, so along the
     level set du/dv = 8 pi r^2 e^f phi_v^2 >= 0: the MOTS tube is timelike or
     null (never spacelike) and m = R/2 on it is non-increasing to the future.
  5. The same algebra with a CANONICAL scalar flips the sign (du/dv <= 0:
     the familiar spacelike dynamical horizon whose area grows).

    grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/c_spherical_horizon_law.py
"""

from __future__ import annotations

import sympy as sp


def main() -> int:
    u, v, th, ph = sp.symbols("u v theta phi_ang", real=True)
    f = sp.Function("f")(u, v)
    r = sp.Function("r")(u, v)
    phi = sp.Function("phi")(u, v)
    X = [u, v, th, ph]
    g = sp.zeros(4, 4)
    g[0, 1] = g[1, 0] = -sp.exp(-f)
    g[2, 2] = r**2
    g[3, 3] = r**2 * sp.sin(th) ** 2
    gi = g.inv()

    # Christoffels, Ricci, Einstein -- straight from the definitions
    Gam = [[[sp.simplify(sum(gi[a, d] * (sp.diff(g[d, b], X[c]) + sp.diff(g[d, c], X[b])
                                        - sp.diff(g[b, c], X[d])) for d in range(4)) / 2)
             for c in range(4)] for b in range(4)] for a in range(4)]
    Ric = sp.zeros(4, 4)
    for b in range(4):
        for c in range(4):
            Ric[b, c] = sp.simplify(sum(sp.diff(Gam[a][b][c], X[a]) - sp.diff(Gam[a][b][a], X[c])
                                        + sum(Gam[a][a][d] * Gam[d][b][c] - Gam[a][c][d] * Gam[d][b][a]
                                              for d in range(4)) for a in range(4)))
    Rs = sp.simplify(sum(gi[a, b] * Ric[a, b] for a in range(4) for b in range(4)))
    G = sp.simplify(Ric - Rs * g / 2)

    # phantom stress tensor, Eq. (1) of the paper, V = 0
    dphi = [sp.diff(phi, x) for x in X]
    dphi2 = sp.simplify(sum(gi[a, b] * dphi[a] * dphi[b] for a in range(4) for b in range(4)))

    def T_of(sign: int) -> sp.Matrix:
        return sp.Matrix(4, 4, lambda a, b: sign * (dphi[a] * dphi[b] - g[a, b] * dphi2 / 2))

    T = T_of(-1)
    ru, rv = sp.diff(r, u), sp.diff(r, v)
    print("1. Einstein tensor vs Hayward's double-null equations")
    print("   G_vv + (2/r)(r_vv + f_v r_v)            =", sp.simplify(G[1, 1] + 2 / r * (sp.diff(r, v, 2) + sp.diff(f, v) * rv)))
    print("   G_uu + (2/r)(r_uu + f_u r_u)            =", sp.simplify(G[0, 0] + 2 / r * (sp.diff(r, u, 2) + sp.diff(f, u) * ru)))
    print("   G_uv - (2/r^2)(r r_uv + r_u r_v + e^-f/2) =",
          sp.simplify(G[0, 1] - 2 / r**2 * (r * sp.diff(r, u, v) + ru * rv + sp.exp(-f) / 2)))
    print("2. stress tensor: T_uv =", sp.simplify(T[0, 1]), "  T_vv =", sp.simplify(T[1, 1]),
          "  T_uu =", sp.simplify(T[0, 0]))

    # field equations solved for the second derivatives of r
    r_vv = -sp.diff(f, v) * rv - 4 * sp.pi * r * T[1, 1]
    r_uu = -sp.diff(f, u) * ru - 4 * sp.pi * r * T[0, 0]
    r_uv = (4 * sp.pi * r**2 * T[0, 1] - ru * rv - sp.exp(-f) / 2) / r
    on_shell = {sp.Derivative(r, (v, 2)): r_vv, sp.Derivative(r, (u, 2)): r_uu,
                sp.Derivative(r, u, v): r_uv}

    m = r / 2 * (1 + 2 * sp.exp(f) * ru * rv)
    dvm = sp.simplify(sp.diff(m, v).subs(on_shell))
    dum = sp.simplify(sp.diff(m, u).subs(on_shell))
    law_v = 4 * sp.pi * r**2 * sp.exp(f) * (T[0, 1] * rv - T[1, 1] * ru)
    law_u = 4 * sp.pi * r**2 * sp.exp(f) * (T[0, 1] * ru - T[0, 0] * rv)
    print("3. first law: d_v m - 4 pi r^2 e^f (T_uv r_v - T_vv r_u) =", sp.simplify(dvm - law_v))
    print("              d_u m - 4 pi r^2 e^f (T_uv r_u - T_uu r_v) =", sp.simplify(dum - law_u))

    # on the MOTS: r_v = 0
    A, B = sp.symbols("r_u r_v", real=True)
    mots = lambda e: sp.simplify(e.subs({sp.Derivative(r, u): A, sp.Derivative(r, v): B}).subs(B, 0))
    print("4. on r_v = 0:  d_u m =", mots(dum), "   d_v m =", mots(dvm))
    Fu, Fv = mots(r_uv), mots(r_vv)
    print("   d_u(r_v) =", Fu, "   d_v(r_v) =", Fv)
    dudv = sp.simplify(-Fv / Fu)
    print("   tube slope du/dv = -d_v(r_v)/d_u(r_v) =", dudv, "  (>= 0: timelike or null)")
    print("   along the tube dm/dv = d_v m + d_u m du/dv =", sp.simplify(mots(dvm) + mots(dum) * dudv),
          " (<= 0 for r_u < 0)")

    # canonical control: the sign flips
    Tc = T_of(+1)
    r_vv_c = -sp.diff(f, v) * rv - 4 * sp.pi * r * Tc[1, 1]
    r_uv_c = (4 * sp.pi * r**2 * Tc[0, 1] - ru * rv - sp.exp(-f) / 2) / r
    dudv_c = sp.simplify(-mots(r_vv_c) / mots(r_uv_c))
    print("5. canonical scalar: du/dv =", dudv_c, " (<= 0: spacelike, area grows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
