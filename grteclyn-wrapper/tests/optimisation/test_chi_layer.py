"""The canonical layer field chi (campaign step 4), CPU only: a
six-field problem with a zero cloud embeds the five-field residual bit
for bit, and the N-row identity survives a nonzero cloud."""

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


def _problems():
    base = dict(eta0=1.0, gamma=0.0, nx=NX, ny=NY,
                prescribe=("J", 0.01))
    five = MatterCollocationProblem(**base)
    six = MatterCollocationProblem(
        **base, chi=(PolynomialPotential.solitonic(0.4, 1.3), 0.37))
    return five, six


def test_zero_cloud_embeds_the_five_field_residual():
    five, six = _problems()
    shape = (NX + 1, NY + 1)
    rng = np.random.default_rng(7)
    d = [0.01 * rng.standard_normal(shape) for _ in range(5)]
    u5 = five.pack(*d, omega_inf=0.05, psi_minus=-3.0)
    u6 = six.pack(*d, omega_inf=0.05, psi_minus=-3.0,
                  dchi=np.zeros(shape))
    r5, r6 = np.asarray(five.residual(u5)), np.asarray(six.residual(u6))
    n = five.n
    # the five field blocks and the border rows agree exactly; the chi
    # block of a zero cloud is exactly zero (E_chi is linear in X there)
    np.testing.assert_array_equal(r6[:5 * n], r5[:5 * n])
    np.testing.assert_array_equal(r6[6 * n:], r5[5 * n:])
    np.testing.assert_array_equal(r6[5 * n:6 * n], np.zeros(n))


def test_nrow_identity_with_a_nonzero_cloud():
    rng = np.random.default_rng(11)
    y = np.linspace(-0.9, 0.9, 5)
    jets = {k: rng.standard_normal((3, 5)) * 0.3 for k in MATTER_JET_NAMES}
    jets["B"] = 1.0 + 0.1 * rng.standard_normal((3, 5))
    eta = rng.standard_normal((3, 1))
    deta = 1.0 + 0.2 * rng.standard_normal((3, 1)) ** 2
    d2eta = 0.3 * rng.standard_normal((3, 1))
    E = matter_residual_forms(
        np.exp, eta0=1.2, y=y[None, :], eta=eta, deta=deta, d2eta=d2eta,
        jets=jets, V=0.21, dV=0.43, U=0.17, dU=0.29, oc2=1.4)
    h = eta**2 + 1.2**2
    lhs = (1.0 - y[None, :]) * E["E_Nr"]
    rhs = E["E_N"] - 2.0 / h * E["E19"] + E["E_B"] / jets["B"]
    np.testing.assert_allclose(lhs, rhs, rtol=0, atol=1e-12)


def test_amplitude_pin_and_frequency_jacobian():
    """Frequency border preserves the fixed-frequency equations and AD."""
    pot = PolynomialPotential.mass(.8)
    args = dict(eta0=1., gamma=-.2, nx=NX, ny=NY,
                prescribe=("J", .01), pin=("R_e", 2.))
    fixed = MatterCollocationProblem(**args, chi=(pot, .4))
    bordered = MatterCollocationProblem(**args, chi=(pot, .4), pin_chi=.02)
    shape = (NX+1, NY+1)
    zeros = np.zeros(shape)
    cloud = .02*(1-fixed.sx[:, None]**2)*np.ones(shape)
    kw = dict(omega_inf=.05, psi_minus=-3., sigma=1.5, xi_t=0., dchi=cloud)
    uf = fixed.pack(zeros, zeros, zeros, zeros, zeros, **kw)
    ub = bordered.pack(zeros, zeros, zeros, zeros, zeros, omega_chi=.4, **kw)
    rb = np.asarray(bordered.residual(ub))
    # Cloud-frequency border is immediately before the two size rows.
    np.testing.assert_allclose(np.delete(rb, -3), fixed.residual(uf), atol=1e-13)
    assert abs(rb[-3]) < 1e-15
    assert bordered.omega_chi_of(ub) == .4
    column = ub.size-3
    h = 1e-6
    delta = np.zeros_like(ub)
    delta[column] = h
    numerical = (bordered.residual(ub+delta)-bordered.residual(ub-delta))/(2*h)
    np.testing.assert_allclose(np.asarray(bordered.jacobian(ub))[:, column], numerical,
                               rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(bordered.diagnostics(ub)["E_c"],
                               fixed.diagnostics(uf)["E_c"], atol=1e-13)


def test_two_cloud_frequency_borders_have_distinct_offsets():
    p = MatterCollocationProblem(eta0=1., gamma=0., nx=NX, ny=NY,
        prescribe=("J", .01), pin=("area", 20.),
        chi=(PolynomialPotential.mass(.8), .3), pin_chi=.02,
        winding=(PolynomialPotential.mass(.9), .5, 1), pin_zeta=.04)
    zeros = np.zeros((NX+1, NY+1))
    u = p.pack(zeros, zeros, zeros, zeros, zeros, dchi=zeros+.02,
               dzeta=zeros+.04, omega_inf=.1, psi_minus=-3., sigma=1.,
               xi_t=0., omega_chi=.3, omega_z=.5)
    assert len(u) == p.n_unknowns
    assert p.omega_chi_of(u) == .3
    assert p.omega_z_of(u) == .5
    assert np.asarray(p.residual(u)).shape == u.shape
