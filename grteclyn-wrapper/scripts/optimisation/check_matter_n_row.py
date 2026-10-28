#!/usr/bin/env python
"""Closed-form test of the matter solver's discrete N rows (campaign M).

Substitutes a closed-form N* into the N part of two rows of
matter_residual_forms, built from the forms themselves (B = 1, V = 0,
f = omega = psi = 0; both rows are linear in N's jets there):

  E_N   the derived nu row, imposed until 2026-10-27, now a monitor;
  E_Nr  the row Newton imposes, (1 - y) E_Nr = E_N - (2/h) E19 + E_B / B.

N* has the saved family's shape: N h -> const at both ends, unequal
ends (the drainhole's), angular Chebyshev coefficients falling tenfold
per mode, poles off the real xi axis.  On each grid it prints, per row:
the condition number of the equilibrated operator (rows scaled by their
max element, as newton.py does); the truncation, the discrete operator
on N* minus the exact one, equilibrated; and the error of the discrete
solve with the exact source, everywhere and on the y node next to the
axis at the mask edge |eta| = 20 eta0 (C = 0.05), where h N enters E19,
and the largest error on that y node over the largest elsewhere.

Reading it: E_N's solve error does not follow its truncation.  It sits on
the y node next to the axis (about 9 times the error anywhere else),
flat in xi, so E19 sees it multiplied by h; once the truncation reaches
round-off the error stays 1e4 - 1e5 times above it, and the condition
number grows like ny^4 (2026-10-27: 5e-11 to 2e-9 from 84 x 21 up,
varying from run to run).  E_Nr's error falls with its truncation to
round-off.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/optimisation/check_matter_n_row.py

numpy and sympy only, about a minute; the largest dense operator is
3052 x 3052 (108 x 27).
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import sympy as sp

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
    ArctanMap,
    LogStretchMap,
    lobatto,
)
from grteclyn_wrapper.optimisation.matter_equations import (
    MATTER_JET_NAMES,
    matter_residual_forms,
    row_matrix,
)

GRIDS = ((48, 12), (60, 15), (72, 18), (84, 21), (96, 24), (108, 27),
         (96, 18), (72, 30))
N_JETS = ("N", "N_x", "N_xx", "N_y", "N_yy")
EDGE = 20.0                        # |eta| / eta0 of the read-out


def closed_form(map_name: str, L: int = 4):
    """N*(xi, y) and its xi/y jets as numpy callables.

    C2 = eta0^2 / h and S = eta / sqrt(h) in closed form per map, so the
    expressions stay well conditioned up to the ends."""
    xi, y = sp.symbols("xi y", real=True)
    if map_name == "arctan":
        C2 = sp.cos(sp.pi * xi / 2) ** 2
        S = sp.sin(sp.pi * xi / 2)
    else:
        p, q = (1 + xi) ** L, (1 - xi) ** L
        C2 = 4 * p * q / (p + q) ** 2
        S = (p - q) / (p + q)
    # N h / eta0^2: -0.8 at the throat, -12.7 and -0.8 at the two ends
    radial = C2 * (sp.Rational(-675, 100)
                   + 6 * 4 * C2 / (3 * C2 + 1)
                   - sp.Rational(595, 100) * S)
    angular = sp.Rational(101, 20) / (sp.Rational(101, 20) - y)
    N = radial * angular
    jets = {"N": N, "N_x": sp.diff(N, xi), "N_xx": sp.diff(N, xi, 2),
            "N_y": sp.diff(N, y), "N_yy": sp.diff(N, y, 2)}
    return {k: sp.lambdify((xi, y), v, "numpy") for k, v in jets.items()}


def operator(rmap, eta0: float, nx: int, ny: int, key: str):
    """The N part of form `key` on one grid: the dense matrix the solver
    uses (matter_equations.row_matrix), the exact operator (the form
    itself on exact N jets, at the interior nodes), and the nodes."""
    sx, Dx = lobatto(nx)
    sy, Dy = lobatto(ny)
    xi = sx[1:-1]
    geo = {"eta0": eta0, "eta": rmap.eta(xi)[:, None],
           "deta": rmap.deta(xi)[:, None], "d2eta": rmap.d2eta(xi)[:, None]}
    A = row_matrix(key, "N", y=sy, Dx=Dx, Dy=Dy, **geo)
    shape = (nx - 1, ny + 1)
    zero = np.zeros(shape)

    def form(n_jets):
        jets = {k: zero for k in MATTER_JET_NAMES}
        jets["B"] = np.ones(shape)
        jets.update(n_jets)
        return matter_residual_forms(np.exp, y=sy[None, :], jets=jets,
                                     V=zero, dV=zero, **geo)[key]

    base = form({})
    return A, (lambda n_jets: form(n_jets) - base), sx, sy


def run_case(label: str, rmap, eta0: float, grids) -> None:
    ex = closed_form(rmap.name, getattr(rmap, "L", 4))
    print(f"== {label}: {rmap.describe()}")
    print(f"{'grid':>7} | {'row':<4} {'cond':>8} {'trunc':>8} "
          f"{'err max':>8} {'err y1':>8} {'h err y1':>8} {'y1/rest':>8}")
    for nx, ny in grids:
        for key in ("E_N", "E_Nr"):
            A, exact_op, sx, sy = operator(rmap, eta0, nx, ny, key)
            X, Y = np.meshgrid(sx, sy, indexing="ij")
            exact = {j: np.zeros_like(X) for j in N_JETS}
            for j in N_JETS:
                exact[j][1:-1] = ex[j](X[1:-1], Y[1:-1])
            Nst = exact["N"]                     # N* = 0 at xi = +-1
            Lex = exact_op({j: exact[j][1:-1] for j in N_JETS})
            rhs = np.zeros_like(X)
            rhs[1:-1] = Lex
            scale = 1.0 / np.max(np.abs(A), axis=1)
            trunc = scale * (A @ Nst.ravel() - rhs.ravel())
            s = np.linalg.svd(scale[:, None] * A, compute_uv=False)
            err = (np.linalg.solve(A, rhs.ravel()) - Nst.ravel()).reshape(
                X.shape)
            eta_x = rmap.eta(sx[1:-1]) / eta0
            i = 1 + int(np.argmin(np.abs(np.abs(eta_x) - EDGE)
                                  + 1e-9 * (eta_x > 0)))   # the eta < 0 side
            h_i = eta0**2 * (1.0 + eta_x[i - 1] ** 2)
            y1 = float(np.max(np.abs(err[:, 1])))
            rest = float(np.max(np.abs(np.delete(err, 1, axis=1))))
            print(f"{nx:>3}x{ny:<3} | {key:<4} {s[0] / s[-1]:8.1e} "
                  f"{np.max(np.abs(trunc)):8.1e} {np.max(np.abs(err)):8.1e} "
                  f"{abs(err[i, 1]):8.1e} {h_i * abs(err[i, 1]):8.1e} "
                  f"{y1 / max(rest, 1e-300):8.1f}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true",
                    help="the three smallest grids only")
    args = ap.parse_args()
    grids = GRIDS[:3] if args.quick else GRIDS
    run_case("family (b) grid", ArctanMap(eta0=1.0), 1.0, grids)
    run_case("family (a) log grid", LogStretchMap(eta0=2.0, L=4), 2.0,
             grids)
    return 0


if __name__ == "__main__":
    sys.exit(main())
