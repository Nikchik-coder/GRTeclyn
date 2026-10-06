"""Orientation-corrected horizon scan on analytic data.

Kerr-Schild Schwarzschild (a slice that crosses the future horizon): the
outermost MOTS is at r = 2M, its Misner-Sharp mass is M, and every shell
inside is trapped.  A time-symmetric Ellis throat (psi^2 = 1 + b^2 / 4 r^2):
no MOTS, no trapped shell, the areal minimum R = b at r = b/2 -- while the
naive +r orientation would call the whole interior trapped (Defect 2).
"""

from __future__ import annotations

import numpy as np
import pytest

from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.horizon import (
    STATE_FIELDS,
    oriented_shell_scan,
    read_tracked_centres,
    resolve_centres,
    summarise,
)


def _grid(half: float, dx: float):
    N = int(round(2 * half / dx))
    ax = np.arange(N) * dx + dx / 2 - half
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"))
    r = np.clip(np.sqrt((X**2).sum(0)), 1e-6, None)
    return X, r


def _conformal_fields(gamma: np.ndarray, Kij: np.ndarray) -> dict:
    """(gamma_ij, K_ij) -> the CCZ4 state the scan reads (chi, h_ij, K, A_ij)."""
    det = np.linalg.det(np.moveaxis(gamma, (0, 1), (-2, -1)))
    chi = det ** (-1.0 / 3.0)
    h = chi * gamma
    ginv = np.moveaxis(np.linalg.inv(np.moveaxis(gamma, (0, 1), (-2, -1))), (-2, -1), (0, 1))
    K = np.einsum("ab...,ab...->...", ginv, Kij)
    A = chi * (Kij - gamma * (K / 3.0))
    f = {"chi": chi, "K": K}
    for a in range(3):
        for b in range(a, 3):
            f[f"h{a+1}{b+1}"] = h[a, b]
            f[f"A{a+1}{b+1}"] = A[a, b]
    assert set(f) == set(STATE_FIELDS)
    return f


def test_kerr_schild_schwarzschild_finds_its_horizon():
    M, half, dx = 0.5, 1.6, 0.04
    X, r = _grid(half, dx)
    n = X / r
    delta = np.eye(3)[:, :, None, None, None]
    nn = n[:, None] * n[None, :]
    gamma = delta + (2 * M / r) * nn
    alpha = 1.0 / np.sqrt(1.0 + 2 * M / r)
    Kij = (2 * M * alpha / r**2) * (delta - (2 + M / r) * nn)
    scan = oriented_shell_scan(_conformal_fields(gamma, Kij), dx, half, rmin=0.3, dr=0.02)
    s = summarise(scan)
    assert s.n_mots == 1
    assert s.theta_out_min_inside < 0.0  # the inside of a horizon is trapped
    assert abs(s.r_mots - 2 * M) < 0.06          # horizon at r = 2M (areal R = r here)
    assert abs(s.R_mots - 2 * M) < 0.06
    assert abs(s.M_MS_mots - M) < 0.05
    assert s.n_trapped > 0                        # the inside of the horizon is trapped
    inside = scan.rs < 2 * M - 0.1
    assert np.all(scan.out_max[inside] < 0) and np.all(scan.in_max[inside] < 0)


def test_ellis_throat_is_not_a_horizon():
    b, half, dx = 1.0, 1.6, 0.04
    X, r = _grid(half, dx)
    psi2 = 1.0 + b * b / (4.0 * r * r)
    chi = psi2**-2
    f = {k: np.zeros_like(chi) for k in STATE_FIELDS}
    f["chi"] = chi
    for k in ("h11", "h22", "h33"):
        f[k] = np.ones_like(chi)
    scan = oriented_shell_scan(f, dx, half, rmin=0.25, dr=0.02)
    s = summarise(scan)
    assert s.n_mots == 0
    assert s.n_trapped == 0
    assert abs(s.R_min - b) < 0.02 * b            # areal radius of the throat is b
    assert abs(s.r_at_min - b / 2) < 0.03         # at coordinate radius b/2
    # both expansions vanish on the minimal surface (theta_out * theta_in ~ 0)
    assert abs(s.theta_out_max_at_min) < 0.15 and abs(s.theta_in_max_at_min) < 0.15
    # outside the throat: plain untrapped space
    outside = scan.rs > b / 2 + 0.15
    assert np.all(scan.out_min[outside] > 0) and np.all(scan.in_max[outside] < 0)
    # the naive orientation calls the interior trapped -- the bug this replaces
    assert scan.naive_trapped[scan.rs < b / 2 - 0.1].all()


def test_tracked_centres(tmp_path):
    p = tmp_path / "binary_throat_diagnostics.dat"
    p.write_text(
        "# time sep xA yA zA chiA lapseA xB yB zB chiB lapseB\n"
        "0.0 8.0 0.0 0.0 4.0 1e-3 0.2 0.0 0.0 -4.0 1e-3 0.2\n"
        "1.0 7.0 0.0 0.0 3.5 1e-3 0.2 0.0 0.0 -3.5 1e-3 0.2\n"
    )
    cs = read_tracked_centres(str(p), 1.0, (32.0, 32.0, 32.0))
    assert [c[0] for c in cs] == ["A", "B"]
    assert np.allclose(cs[0][1], [32.0, 32.0, 35.5]) and np.allclose(cs[1][1], [32.0, 32.0, 28.5])
    single = resolve_centres({"center": (32.0, 32.0, 32.0)}, 0.0)
    assert len(single) == 1 and np.allclose(single[0][1], [32.0, 32.0, 32.0])
    two = resolve_centres({"center": (0, 0, 0), "horizon_centers": [1, 2, 3, 4, 5, 6]}, 0.0)
    assert len(two) == 2 and np.allclose(two[1][1], [4, 5, 6])
    with pytest.raises(ValueError):
        resolve_centres({"center": (0, 0, 0), "horizon_centers": [1, 2]}, 0.0)


def test_no_mots_at_an_orientation_flip():
    """theta_out changes sign wherever dR/dr does; that alone is not a MOTS."""
    from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.horizon import (
        ShellScan,
        summarise,
    )

    rs = np.linspace(0.5, 3.0, 11)
    # R(r) with a local maximum at r = 1.5: the orientation flips there.
    R = 10.0 - (rs - 1.5) ** 2
    dRdr = np.gradient(R, rs)
    out = np.where(rs < 1.5, -0.01, 0.01)  # sign flip riding on the flip of dR/dr
    inn = -0.02 * np.ones_like(rs)
    scan = ShellScan(
        rs=rs, R=R, dRdr=dRdr, out_min=out, out_max=out, in_min=inn, in_max=inn,
        M_MS=np.zeros_like(rs), naive_trapped=np.zeros_like(rs, dtype=bool),
    )
    assert summarise(scan).n_mots == 0

    # Control: the same crossing where R is monotonic is a genuine MOTS.
    R2 = 2.0 + rs
    scan2 = ShellScan(
        rs=rs, R=R2, dRdr=np.gradient(R2, rs), out_min=out, out_max=out, in_min=inn,
        in_max=inn, M_MS=R2 / 2, naive_trapped=np.zeros_like(rs, dtype=bool),
    )
    s2 = summarise(scan2)
    assert s2.n_mots == 1
    assert abs(s2.r_mots - 1.5) < 0.13
