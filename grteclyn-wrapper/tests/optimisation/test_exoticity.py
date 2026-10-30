"""Throat radii and the two bills; X itself is unchanged."""

import math

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto
from grteclyn_wrapper.optimisation.exoticity import exotic_x, throat


def _sphere(eta0=2.0, nx=16, ny=8):
    rmap = ArctanMap(eta0=eta0)
    sx, Dx = lobatto(nx)
    sy, _ = lobatto(ny)
    F = np.zeros((nx + 1, ny + 1))
    N = np.zeros_like(F)
    B = np.ones_like(F)
    PSI = np.zeros_like(F)
    return eta0, rmap, sx, sy, Dx, F, N, B, PSI


def test_spherical_throat_radii_agree():
    eta0, rmap, sx, sy, Dx, F, N, B, _ = _sphere()
    th = throat(eta0, rmap, sx, sy, Dx, F, N, B)
    assert th["R_e"] == pytest.approx(eta0, rel=1e-6)
    assert th["R_A"] == pytest.approx(eta0, rel=1e-5)
    assert th["R_pol"] == pytest.approx(eta0, rel=1e-5)
    assert th["area_throat"] == pytest.approx(4.0 * math.pi * eta0**2, rel=1e-5)


def test_exotic_x_keeps_fig3e_and_adds_areal_bill():
    eta0, rmap, sx, sy, Dx, F, N, B, PSI = _sphere()
    xv = exotic_x(eta0, rmap, sx, sy, Dx, F, N, B, PSI)
    assert xv["X"] == pytest.approx(abs(xv["VIQ"]) / xv["R_e"], rel=0, abs=0)
    assert xv["X_A"] == pytest.approx(abs(xv["VIQ"]) / xv["R_A"], rel=1e-12)
    assert xv["X"] == pytest.approx(xv["X_A"], rel=1e-5)
