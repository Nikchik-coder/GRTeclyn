"""P1 gates: manufactured solutions fall exponentially to <= 1e-12, the
static members are recovered from perturbed guesses to <= 1e-13, and one
64 x 16 solve stays under 30 s (SpinningSolver.md P1)."""

from __future__ import annotations

import math
import time

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
    CollocationProblem,
)
from grteclyn_wrapper.analysis.spinning_wormhole.newton import newton


def _manufactured(problem):
    """Smooth target fields with zero values at xi = +-1 (so the physical
    Dirichlet rows hold), plus the sources that make them exact solutions.

    The sources come from the same residual evaluated on the EXACT jets of
    the targets (closed forms below), so the test checks the solver, not
    the differentiation matrices.
    """
    sx, sy = problem.sx, problem.sy
    xi = sx[:, None]
    y = sy[None, :]
    c = np.cos(0.5 * math.pi * xi)
    f_t = 0.3 * c**2 * (1 + 0.4 * y)
    w_t = 0.05 * c**2 * (1.0 - 0.3 * y * y)

    def jets_of(amp, ang, ang_y, ang_yy):
        s_ = np.sin(0.5 * math.pi * xi)
        return {
            "": amp * c**2 * ang,
            "_x": -amp * math.pi * c * s_ * ang,
            "_xx": -amp * math.pi**2 * 0.5 * np.cos(math.pi * xi) * ang,
            "_y": amp * c**2 * ang_y,
            "_yy": amp * c**2 * ang_yy,
        }

    one = np.ones_like(y)
    jf = jets_of(0.3, 1 + 0.4 * y, 0.4 * one, 0.0 * one)
    jw = jets_of(0.05, 1 - 0.3 * y * y, -0.6 * y, -0.6 * one)
    jets = {f"f{k}": v for k, v in jf.items()}
    jets.update({f"w{k}": v for k, v in jw.items()})
    for name in ("N", "N_x", "N_xx", "N_y", "N_yy"):
        jets[name] = np.zeros_like(f_t)

    from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
        residual_forms,
    )
    interior = {k: v[1:-1] for k, v in jets.items()}
    E = residual_forms(np.exp, eta0=problem.eta0, y=y, eta=problem.eta_i,
                       deta=problem.deta_i, d2eta=problem.d2eta_i,
                       jets=interior)
    return f_t, w_t, E["E_f"], E["E_w"]


def _solve_manufactured(nx, ny):
    p = CollocationProblem(eta0=2.0, gamma=0.0, nx=nx, ny=ny,
                           prescribe=("omega_inf", 0.0))
    f_t, w_t, src_f, src_w = _manufactured(p)
    p.source_f[1:-1] = src_f
    p.source_w[1:-1] = src_w
    u0 = p.pack(np.zeros_like(f_t), np.zeros_like(w_t))
    u, info = newton(p.residual, p.jacobian, u0, tol=1e-12)
    assert info["converged"], info
    df, dw, _ = p.unpack(u)
    return max(float(np.max(np.abs(p.f_bg + df - f_t))),
               float(np.max(np.abs(dw - w_t))))


def test_manufactured_solution_converges_exponentially():
    errs = [_solve_manufactured(nx, ny)
            for nx, ny in ((6, 4), (10, 6), (16, 8))]
    # At least two decades per refinement (exponential, not algebraic,
    # decay), down to the measured solve floor: a 1e-12 scaled-residual
    # Newton leaves ~4e-12 in the fields (measured 2026-10-12 at 16 x 6
    # and 24 x 8, identical, so it is the linear-algebra floor, not
    # truncation; the plan allows moving the 1e-12 proposal to the floor).
    assert errs[2] <= 5e-12, errs
    assert errs[0] / max(errs[1], 1e-300) >= 1e2, errs
    assert errs[1] / max(errs[2], 1e-300) >= 1e2, errs


@pytest.mark.parametrize("gamma", [0.0, -math.pi])
def test_static_member_recovered_from_perturbed_guess(gamma):
    p = CollocationProblem(eta0=2.0, gamma=gamma, nx=32, ny=8,
                           prescribe=("omega_inf", 0.0))
    rng = np.random.default_rng(7)
    shape = (p.nx + 1, p.ny + 1)
    df0 = 0.05 * np.cos(0.5 * math.pi * p.sx[:, None]) ** 2 \
        * (1 + 0.5 * p.sy[None, :]) + 0.01 * rng.standard_normal(shape) \
        * np.cos(0.5 * math.pi * p.sx[:, None]) ** 2
    u0 = p.pack(df0, np.zeros(shape))
    u, info = newton(p.residual, p.jacobian, u0, tol=1e-12)
    assert info["converged"], info
    F, W = p.fields(u)
    assert float(np.max(np.abs(F - p.f_bg))) <= 1e-13
    assert float(np.max(np.abs(W))) <= 1e-13
    # The N solve on the static member: zero source, zero N.
    N = p.solve_N(F, W)
    assert float(np.max(np.abs(N))) <= 1e-13


def test_one_production_size_solve_is_fast_enough():
    p = CollocationProblem(eta0=2.0, gamma=-math.pi, nx=64, ny=16,
                           prescribe=("omega_inf", 0.0))
    shape = (p.nx + 1, p.ny + 1)
    u0 = p.pack(0.02 * np.cos(0.5 * math.pi * p.sx[:, None]) ** 2
                * np.ones((1, p.ny + 1)), np.zeros(shape))
    t0 = time.time()
    u, info = newton(p.residual, p.jacobian, u0, tol=1e-12)
    wall = time.time() - t0
    assert info["converged"], info
    assert wall <= 30.0, f"64 x 16 solve took {wall:.1f} s"


def test_n_solve_reproduces_the_symmetric_closed_form():
    # At gamma = 0 the N equation is EXACTLY the O(J^2) one (it is linear in
    # N and its source is quadratic in omega = J w1 with f = 0), and the
    # closed form is N = -9 J^2 / (eta0^2 h) (backgrounds.py docstring).
    from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import (
        slow_rotation_omega,
    )
    eta0, J = 2.0, 0.5
    p = CollocationProblem(eta0=eta0, gamma=0.0, nx=48, ny=8,
                           prescribe=("omega_inf", 0.0))
    chi = np.arctan(np.concatenate([[np.inf], p.eta_i[:, 0], [-np.inf]]) / eta0)
    W = J * slow_rotation_omega(eta0, 0.0, chi)[:, None] * np.ones((1, p.ny + 1))
    F = np.zeros_like(W)
    N = p.solve_N(F, W)
    h = np.concatenate([[np.inf], p.h_i[:, 0], [np.inf]])
    ref = -9.0 * J * J / (eta0**2 * h)[:, None] * np.ones((1, p.ny + 1))
    assert float(np.max(np.abs(N - ref))) <= 1e-11
