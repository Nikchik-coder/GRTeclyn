"""The winding field zeta (campaign step 5), CPU only: a problem with
zero clouds embeds the five-field residual bit for bit, the N-row
identity survives a nonzero winding cloud on a grid that includes the
axis node, and the half-line quadrature behind the J bookkeeping is
exact."""

from __future__ import annotations

import importlib.util

import numpy as np
import pytest

if importlib.util.find_spec("jax") is None:
    pytest.skip("jax is not installed (the spinning-solver extra)",
                allow_module_level=True)

from grteclyn_wrapper.optimisation.matter_equations import (  # noqa: E402
    MATTER_JET_NAMES,
    MatterCollocationProblem,
    matter_residual_forms,
)
from grteclyn_wrapper.optimisation.potentials import (  # noqa: E402
    PolynomialPotential,
)

NX, NY = 8, 4

#: an even winding potential, m_z = 0.9 with a quartic term
UZ_POT = PolynomialPotential((0.0, 0.0, 0.81, 0.0, -0.3))


def _problems():
    base = dict(eta0=1.0, gamma=0.0, nx=NX, ny=NY,
                prescribe=("J", 0.01))
    five = MatterCollocationProblem(**base)
    seven = MatterCollocationProblem(
        **base, chi=(PolynomialPotential.solitonic(0.4, 1.3), 0.37),
        winding=(UZ_POT, 0.8, 1))
    return five, seven


def test_zero_clouds_embed_the_five_field_residual():
    five, seven = _problems()
    shape = (NX + 1, NY + 1)
    rng = np.random.default_rng(7)
    d = [0.01 * rng.standard_normal(shape) for _ in range(5)]
    u5 = five.pack(*d, omega_inf=0.05, psi_minus=-3.0)
    u7 = seven.pack(*d, omega_inf=0.05, psi_minus=-3.0,
                    dchi=np.zeros(shape), dzeta=np.zeros(shape))
    r5, r7 = np.asarray(five.residual(u5)), np.asarray(seven.residual(u7))
    n = five.n
    # the five field blocks and the border rows agree to round-off (the
    # winding terms are exact zeros, but the larger jitted graph lets
    # XLA reassociate shared sums by a ulp); the chi and zeta blocks of
    # zero clouds are zero (E_chi and E_z are linear in them there)
    np.testing.assert_allclose(r7[:5 * n], r5[:5 * n], rtol=0, atol=1e-14)
    np.testing.assert_allclose(r7[7 * n:], r5[5 * n:], rtol=0, atol=1e-14)
    np.testing.assert_allclose(r7[5 * n:7 * n], np.zeros(2 * n),
                               rtol=0, atol=1e-14)


def test_nrow_identity_with_a_winding_cloud_on_the_axis():
    rng = np.random.default_rng(13)
    # both the axis node y = 1 (where expm1u's u = 0) and the equator
    y = np.array([-1.0, -0.4, 0.2, 0.7, 1.0])
    jets = {k: rng.standard_normal((3, 5)) * 0.3 for k in MATTER_JET_NAMES}
    jets["B"] = 1.0 + 0.1 * rng.standard_normal((3, 5))
    eta = rng.standard_normal((3, 1))
    deta = 1.0 + 0.2 * rng.standard_normal((3, 1)) ** 2
    d2eta = 0.3 * rng.standard_normal((3, 1))
    h = eta**2 + 1.2**2
    expm1u = MatterCollocationProblem._expm1u(np)
    for kz in (-2, -1, 1, 2):
        E = matter_residual_forms(
            np.exp, eta0=1.2, y=y[None, :], eta=eta, deta=deta,
            d2eta=d2eta, jets=jets, V=0.21, dV=0.43, U=0.17, dU=0.29,
            oc2=1.4, uz=0.11, duz=0.23, oz=0.9, kz=kz, expm1u=expm1u)
        for key, val in E.items():
            assert np.isfinite(np.asarray(val)).all(), (key, kz)
        lhs = (1.0 - y[None, :]) * E["E_Nr"]
        rhs = E["E_N"] - 2.0 / h * E["E19"] + E["E_B"] / jets["B"]
        np.testing.assert_allclose(lhs, rhs, rtol=0, atol=1e-12)


def test_half_line_quadrature_is_exact():
    _, seven = _problems()
    assert abs(seven.int_half @ seven.sx**3 - 0.25) < 1e-13
    assert abs(seven.int_half @ np.ones(NX + 1) - 1.0) < 1e-13


def test_j_matter_tail_matches_the_row_integral():
    _, seven = _problems()
    shape = (NX + 1, NY + 1)
    rng = np.random.default_rng(3)
    d = [0.01 * rng.standard_normal(shape) for _ in range(5)]
    dzeta = 0.1 * rng.standard_normal(shape)
    dzeta[0] = dzeta[-1] = 0.0
    u = seven.pack(*d, omega_inf=0.05, psi_minus=-3.0,
                   dchi=np.zeros(shape), dzeta=dzeta)
    fields = [np.asarray(a) for a in seven.fields(u)]
    F, W, Nf, B = fields[:4]
    zeta = fields[6]
    jm = float(seven.j_matter(F, Nf, B, W, zeta, 0.8))
    tail = seven.diagnostics(u)["j_matter_tail"][seven.mid - 1]
    assert abs(jm - tail) < 1e-12 * max(1.0, abs(jm))
