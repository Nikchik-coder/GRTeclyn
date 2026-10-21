"""ADM mass and angular momentum on coordinate spheres (adm.py, Step 3 A1)."""

from __future__ import annotations

import math

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole import adm

RADII = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0]
CENTRE = np.zeros(3)


def _grid(dx: float = 0.5, half: float = 26.0):
    n = round(2 * half / dx)
    lower = np.full(3, -half)
    ax = lower[0] + (np.arange(n) + 0.5) * dx
    return (lower, *np.meshgrid(ax, ax, ax, indexing="ij"))


def _static_psi4(X, Y, Z, eta0: float, mass: float) -> np.ndarray:
    """e^{-f} Omega^2: the static drainhole is conformally flat."""
    r = np.sqrt(X * X + Y * Y + Z * Z)
    eta = r - eta0**2 / (4 * r)
    gamma = -2 * math.pi * mass / eta0
    f = 0.5 * gamma * (1 - (2 / math.pi) * np.arctan(eta / eta0))
    return np.exp(-f) * (1 + eta0**2 / (4 * r * r)) ** 2


def _diag(psi4: np.ndarray) -> dict[str, np.ndarray]:
    return {f"g{i + 1}{j + 1}": psi4 if i == j else np.zeros_like(psi4)
            for i, j in adm.PAIRS}


def _static_table(eta0: float, mass: float):
    x = np.linspace(-1.0, 1.0, 1025)
    body = np.zeros((65, x.size, 6))
    body[..., 0] = (0.5 * (-2 * math.pi * mass / eta0) * (1 - x))[None, :]
    header = {"eta0": eta0, "x_min": -1.0, "x_max": 1.0,
              "meta": [f"family static drainhole mass {mass!r} (v_e = 0)"]}
    return header, body


def test_mass_of_the_static_drainhole():
    lower, X, Y, Z = _grid()
    grid = adm.UniformGrid(lower, 0.5, _diag(_static_psi4(X, Y, Z, 2.0, 1.0)))
    m_inf, resid = adm.fit_mass(RADII, [adm.adm_mass(grid, CENTRE, r) for r in RADII])
    assert abs(m_inf - 1.0) <= 1e-3
    assert resid <= 1e-5


def test_massless_symmetric_throat_extrapolates_to_zero():
    lower, X, Y, Z = _grid()
    grid = adm.UniformGrid(lower, 0.5, _diag(_static_psi4(X, Y, Z, 2.0, 0.0)))
    masses = [adm.adm_mass(grid, CENTRE, r) for r in RADII]
    # flat-formula M(R) = Omega(R) eta0^2 / (2R) exactly: the phantom
    # energy outside R, which vanishes as R -> infinity
    for r, m in zip(RADII, masses):
        assert abs(m - (1 + 4.0 / (4 * r * r)) * 4.0 / (2 * r)) <= 1e-5
    assert abs(adm.fit_mass(RADII, masses)[0]) <= 1e-4


def test_table_metric_matches_the_exact_static_metric():
    lower, X, Y, Z = _grid()
    header, body = _static_table(2.0, 1.0)
    exact = adm.UniformGrid(lower, 0.5, _diag(_static_psi4(X, Y, Z, 2.0, 1.0)))
    table = adm.UniformGrid(lower, 0.5, adm.table_gamma(header, body, X, Y, Z))
    for r in (8.0, 16.0):
        assert abs(adm.adm_mass(exact, CENTRE, r)
                   - adm.adm_mass(table, CENTRE, r)) <= 1e-10
    assert adm.table_reference(header) == {"M": 1.0, "J": 0.0}


def test_table_metric_keeps_phi_phi_and_radial_parts():
    """gamma_phiphi = e^{-f} Omega^2 rho^2 and gamma_rr = e^{-f} Omega^2 e^nu."""
    header, body = _static_table(2.0, 0.0)
    body[..., 1] = 0.3                       # nu_bar
    X, Y, Z = np.array([3.0]), np.array([4.0]), np.array([5.0])
    g = adm.table_gamma(header, body, X, Y, Z)
    m = np.array([[g["g11"][0], g["g12"][0], g["g13"][0]],
                  [g["g12"][0], g["g22"][0], g["g23"][0]],
                  [g["g13"][0], g["g23"][0], g["g33"][0]]])
    r2, rho2 = 50.0, 25.0
    base = (1 + 4.0 / (4 * r2)) ** 2
    p, x = np.array([-4.0, 3.0, 0.0]), np.array([3.0, 4.0, 5.0])
    assert abs(p @ m @ p - base * rho2) <= 1e-12 * base * rho2
    assert abs(x @ m @ x - base * math.exp(0.3 * rho2 / r2) * r2) <= 1e-10 * r2


def test_angular_momentum_is_the_same_on_every_sphere():
    """Bowen-York spin on the drainhole's conformal factor: J(R) = S."""
    lower, X, Y, Z = _grid(0.5)
    psi4 = _static_psi4(X, Y, Z, 2.0, 1.0)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    n = (X / r, Y / r, Z / r)
    s = 0.7
    # A_ij = (3 / r^3) [eps_ki3 n^k n_j + eps_kj3 n^k n_i] S, flat and TT
    cross = (-n[1], n[0], np.zeros_like(r))          # eps_ki3 n^k
    fields = _diag(psi4)
    for i, j in adm.PAIRS:
        a = 3 * s * (cross[i] * n[j] + cross[j] * n[i]) / r**3
        fields[f"K{i + 1}{j + 1}"] = a / np.sqrt(psi4)
    grid = adm.UniformGrid(lower, 0.5, fields)
    js = [adm.adm_angular_momentum(grid, CENTRE, rr) for rr in (8.0, 14.0, 22.0)]
    assert max(abs(j - s) for j in js) <= 1e-4


def test_angular_momentum_sign_follows_the_initial_data():
    """K_ij = -(w_i m_j + w_j m_i) / 2 with omega = 2J / r^3 gives +J."""
    lower, X, Y, Z = _grid(0.5)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    j_true = 0.3
    dw = [-6 * j_true * c / r**5 for c in (X, Y, Z)]
    m = (-Y, X, np.zeros_like(X))
    fields = _diag(np.ones_like(X))
    for i, j in adm.PAIRS:
        fields[f"K{i + 1}{j + 1}"] = -(dw[i] * m[j] + dw[j] * m[i]) / 2
    grid = adm.UniformGrid(lower, 0.5, fields)
    assert abs(adm.adm_angular_momentum(grid, CENTRE, 12.0) - j_true) <= 1e-4
