"""Spectral building blocks: nodes, derivatives, transforms, maps (P0/P1)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole import spectral


def test_lobatto_differentiates_polynomials_exactly():
    s, d = spectral.lobatto(16)
    assert np.max(np.abs(d @ s**5 - 5 * s**4)) <= 1e-12


def test_lobatto_spectral_convergence_on_exp():
    s, d = spectral.lobatto(24)
    assert np.max(np.abs(d @ np.exp(s) - np.exp(s))) <= 1e-10


def test_cheb_coeffs_recovers_a_known_series():
    s, _ = spectral.lobatto(16)
    t3 = 4 * s**3 - 3 * s
    t7 = np.cos(7 * np.arccos(np.clip(s, -1, 1)))
    a = spectral.cheb_coeffs(t3 - 2 * t7)
    ref = np.zeros(17)
    ref[3], ref[7] = 1.0, -2.0
    assert np.max(np.abs(a - ref)) <= 1e-13


def test_tail_ratio_separates_smooth_from_rough():
    s, _ = spectral.lobatto(48)
    assert spectral.tail_ratio(np.exp(s)) <= 1e-14
    rough = np.cos(47 * np.arccos(np.clip(s, -1, 1)))
    assert spectral.tail_ratio(rough) >= 0.5


def test_cheb_eval_interpolates_between_nodes_and_vectorizes():
    s, _ = spectral.lobatto(32)
    probe = np.array([-0.9371, -0.25, 0.0, 0.33, 1.0])
    vals2d = np.stack([np.exp(s), np.sin(2 * s)], axis=1)
    out = spectral.cheb_eval(s, vals2d, probe)
    assert np.max(np.abs(out[:, 0] - np.exp(probe))) <= 1e-12
    assert np.max(np.abs(out[:, 1] - np.sin(2 * probe))) <= 1e-12


@pytest.mark.parametrize("m", [spectral.ArctanMap(eta0=2.0),
                               spectral.LogStretchMap(eta0=2.0, L=4)])
def test_maps_roundtrip_and_derivatives(m):
    xi = np.array([-0.83, -0.2, 0.05, 0.4, 0.77])
    assert np.max(np.abs(m.xi_of_eta(m.eta(xi)) - xi)) <= 1e-13
    eps = 1e-6
    fd1 = (m.eta(xi + eps) - m.eta(xi - eps)) / (2 * eps)
    fd2 = (m.deta(xi + eps) - m.deta(xi - eps)) / (2 * eps)
    assert np.max(np.abs(fd1 / m.deta(xi) - 1)) <= 1e-8
    assert np.max(np.abs(fd2 / m.d2eta(xi) - 1)) <= 1e-7


def test_logstretch_rejects_odd_l():
    with pytest.raises(ValueError):
        spectral.LogStretchMap(eta0=1.0, L=3)
