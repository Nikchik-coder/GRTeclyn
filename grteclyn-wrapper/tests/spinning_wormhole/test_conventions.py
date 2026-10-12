"""P0 gate: the static member satisfies every solver form at machine
precision through the NUMERIC pipeline (the symbolic proof is
scripts/analysis/spinning_wormhole/derive_xy_equations.py --stage static).

The jets here are analytic (f linear in x, so f_x = -gamma/2, f_xx = 0):
this isolates equations.residual_forms and the map formulas from the
differentiation matrix, whose own round-off floor is P1's business.
"""

from __future__ import annotations

import math

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole import conventions as cv
from grteclyn_wrapper.analysis.spinning_wormhole import spectral
from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
    JET_NAMES,
    residual_forms,
)

ETA0, GAMMA = 2.0, -math.pi            # family (a): the a = 2, M = 1 drainhole


def _static_residuals(nx: int = 48, ny: int = 12):
    sx, _ = spectral.lobatto(nx)
    sy, _ = spectral.lobatto(ny)
    xi = sx[1:-1][:, None]             # PDE rows: interior radial nodes only
    y = sy[None, :]
    shape = np.broadcast_shapes(xi.shape, y.shape)
    zero = np.zeros(shape)
    jets = dict.fromkeys(JET_NAMES, zero)
    jets["f"] = np.broadcast_to(cv.static_f_of_x(xi, GAMMA), shape)
    jets["f_x"] = np.full(shape, -0.5 * GAMMA)
    m = spectral.ArctanMap(eta0=ETA0)
    return residual_forms(np.exp, eta0=ETA0, y=y, eta=m.eta(xi),
                          deta=m.deta(xi), d2eta=m.d2eta(xi), jets=jets)


def test_static_member_zeroes_the_imposed_and_monitored_forms():
    E = _static_residuals()
    for key in ("E_f", "E_w", "E_N", "E_c"):
        assert np.max(np.abs(E[key])) <= 1e-13, key


def test_static_member_d2_is_the_ckk_constant():
    E = _static_residuals()
    mu_p = cv.mass_of_gamma(GAMMA, ETA0)
    d2 = ETA0 * ETA0 + mu_p * mu_p
    assert np.max(np.abs(E["D2"] - d2)) <= 1e-13 * d2


def test_mu_signs_and_the_mass_map():
    # CKK eq. 17 with the brief's sign fix: mu_+ = -gamma eta0 / (2 pi) > 0
    # for the drainhole (gamma < 0), and f_x = -gamma/2 at both ends.
    mu_p = cv.mu_plus_from_fx(-0.5 * GAMMA, ETA0)
    assert math.isclose(mu_p, cv.mass_of_gamma(GAMMA, ETA0), rel_tol=1e-15)
    assert math.isclose(mu_p, 1.0, rel_tol=1e-15)      # a = 2, M = 1
    assert math.isclose(cv.gamma_of_mass(1.0, 2.0), -math.pi, rel_tol=1e-15)
    # mu_- = -(eta0/pi) f_x(-1) = -mu_+ for the static member.
    mu_m = cv.mu_minus_from_fx(-0.5 * GAMMA, ETA0)
    assert math.isclose(mu_m, -mu_p, rel_tol=1e-15)


def test_static_smarr_and_member_table():
    ref = cv.static_member(ETA0, GAMMA)
    assert cv.smarr_residual(ref["mu_plus"], ref["mu_minus"],
                             ref["omega_minus_inf"], ref["J"]) == 0.0
    assert math.isclose(ref["D"], math.sqrt(5.0), rel_tol=1e-15)
    assert ref["M_ADM"] == ref["mu_plus"] == 1.0
    assert ref["eta_throat"] == 1.0
    assert cv.v_e(ref["M_ADM"], 0.0) == 0.0


def test_static_phi_slope_matches_backgrounds_table():
    # The .spinbg static generator writes phi = sqrt(eta0^2+m^2)/(eta0
    # sqrt(4 pi)) (pi/2)(x - 1); conventions must reproduce it exactly.
    x = np.linspace(-1.0, 1.0, 7)
    ref = (math.sqrt(ETA0**2 + 1.0) / (ETA0 * math.sqrt(4 * math.pi))
           * 0.5 * math.pi * (x - 1.0))
    assert np.max(np.abs(cv.static_phi_of_x(x, ETA0, GAMMA) - ref)) <= 1e-15
