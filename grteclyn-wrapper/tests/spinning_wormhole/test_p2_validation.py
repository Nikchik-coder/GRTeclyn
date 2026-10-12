"""P2 gates (SpinningSolver.md): the identity matrix on real solutions,
J^4 agreement with the O(J^2) generator, the J = 1 benchmark, and the
extremal-Kerr regression that pins the published eq. (12) typo."""

from __future__ import annotations

import math

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import (
    slow_rotation_solution,
)
from grteclyn_wrapper.analysis.spinning_wormhole.continuation import (
    seed_from_slowspin,
    solve_point,
)
from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
    CollocationProblem,
    residual_forms,
)
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval

ETA0, GAMMA = 2.0, -math.pi


def test_kerr_closes_the_forms_and_breaks_the_printed_eq12():
    # Extremal Kerr (a = M, eta0 = 0) in closed form: E_f, E_w, E_c, D2
    # vanish; the PUBLISHED eq. 12 leaves ~1e-3 -- the 2016 paper's typo
    # (2026-10-12).  Full symbolic proof: derive_xy_equations.py --stage
    # kerr; this is its fast numeric shadow.
    import sympy as sp

    xi, y, M = sp.symbols("xi y M", positive=False), None, None
    xi = sp.Symbol("xi", positive=True)
    yv = sp.Symbol("y", real=True)
    Mv = sp.Symbol("M", positive=True)
    r = xi + Mv
    Sig = r**2 + Mv**2 * (1 + yv) / 2
    gpp = r**2 + Mv**2 + 2 * Mv**3 * r * (1 - yv) / (2 * Sig)
    F = -sp.log(gpp / xi**2)
    W = 2 * Mv**2 * r / (Sig * gpp)
    Nbar = (sp.log(Sig / xi**2) + F) / ((1 - yv) / 2)
    jets = {}
    for tag, e in (("f", F), ("w", W), ("N", Nbar)):
        jets[tag] = e
        jets[f"{tag}_x"] = sp.diff(e, xi)
        jets[f"{tag}_xx"] = sp.diff(e, xi, 2)
        jets[f"{tag}_y"] = sp.diff(e, yv)
        jets[f"{tag}_yy"] = sp.diff(e, yv, 2)
    E = residual_forms(sp.exp, eta0=0, y=yv, eta=xi, deta=sp.Integer(1),
                       d2eta=sp.Integer(0), jets=jets)
    at = {xi: sp.Rational(7, 10), yv: sp.Rational(-1, 3), Mv: 1}
    for key in ("E_f", "E_w", "E_c", "D2"):
        assert abs(float(E[key].subs(at).evalf(30))) <= 1e-25, key
    assert abs(float(E["E_N"].subs(at).evalf(30))) >= 1e-3


def test_identity_gates_on_a_real_solution():
    sol, info = solve_point(eta0=ETA0, gamma=GAMMA, J=0.25, nx=48, ny=12)
    assert info["converged"] and info["res_scaled_inf"] <= 1e-12
    g = sol.gates
    # Thresholds: the plan's proposals, floored by the 2026-10-12
    # measurements (Ec 4.7e-10, D2 1.8e-12, Jsp 1.5e-10 at 48 x 12).
    assert g["Ec_rel"] <= 5e-9, g
    assert g["D2_spread"] <= 1e-10, g
    assert g["J_spread"] <= 5e-9, g
    assert g["smarr_rel"] <= 1e-10, g
    assert g["tail_max"] <= 1e-11, g
    assert sol.meta["n_solve"]["res_Ec"] <= 1e-11
    assert sol.meta["n_solve"]["res_E19"] <= 1e-11
    # J is prescribed through the flux row; the measured flux must return it
    assert abs(g["J_flux"] - 0.25) <= 1e-10


def test_j4_agreement_with_the_slowspin_generator():
    ss = slow_rotation_solution(ETA0, GAMMA, 96)
    ratios = {"f": [], "w": [], "N": []}
    for J in (0.05, 0.1, 0.2):
        sol, info = solve_point(eta0=ETA0, gamma=GAMMA, J=J, nx=48, ny=12,
                                with_observables=False)
        p = CollocationProblem(eta0=ETA0, gamma=GAMMA, nx=48, ny=12,
                               prescribe=("J", J))
        df0, dw0, winf0 = seed_from_slowspin(p, J)
        n_oj2 = (J * J * cheb_eval(ss["s"], ss["n"], p.sx)[:, None]
                 * np.ones((1, p.ny + 1)))
        ratios["f"].append(float(np.max(np.abs(sol.F - (p.f_bg + df0)))) / J**4)
        ratios["w"].append(float(np.max(np.abs(
            sol.W - (winf0 * p.q + dw0)))) / J**3)
        ratios["N"].append(float(np.max(np.abs(sol.N - n_oj2))) / J**4)
    for key, r in ratios.items():
        assert max(r) / min(r) <= 1.05, (key, r)   # constant within 5 %


def test_j1_drainhole_benchmark():
    # The O(J^2) generator's numbers at J = 1 (J/M^2 ~ 0.8): the full
    # solution must land within the O(J^2) truncation of each sector --
    # J^4-sector (f: M, D, R) within ~2.5 %, the omega sector carries a
    # relative J^2-sized correction (~13 % measured 2026-10-12).
    sol, info = solve_point(eta0=ETA0, gamma=GAMMA, J=1.0, nx=64, ny=16)
    o = sol.observables
    assert math.isclose(o["M_ADM"], 1.128, rel_tol=0.025)
    assert math.isclose(o["D"], 2.196, rel_tol=0.01)
    assert math.isclose(o["R_eq"], 4.087, rel_tol=0.02)
    assert math.isclose(o["Omega_throat"], 0.0587, rel_tol=0.15)
    assert math.isclose(o["omega_inf"], 0.0936, rel_tol=0.15)
    assert sol.gates["Ec_rel"] <= 5e-9
    assert sol.gates["D2_spread"] <= 1e-10
    # throat flattening: R_eq > R_pol once it spins
    assert o["R_eq"] > o["R_pol"]
    assert 0.15 <= o["v_e"] <= 0.3
