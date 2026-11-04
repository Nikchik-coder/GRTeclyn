"""Independent Cartesian curvature checks away from the rotation axis."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

PATH = Path("grteclyn-wrapper/scripts/campaigns/railgun/audit_cartesian_curvature.py")
SPEC = importlib.util.spec_from_file_location("cartesian_audit", PATH)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_rotating_flat_metric_is_flat_away_from_axis():
    d = np.longdouble
    coeff = {key: np.zeros((1, 1), dtype=d) for key in ("f", "N", "b", "w")}
    coeff["w"][0, 0] = d(".4")
    jets = audit.jets(coeff, [d(0), d(".3"), d(".2"), d(".5")], d("2.5"))
    assert abs(jets[0][0, 1]) > 0  # Exercise a non-diagonal inverse metric.
    assert np.max(abs(audit.riemann(jets))) < 1e-17


def test_schwarzschild_off_axis_has_exact_kretschmann_and_zero_ricci():
    d = np.longdouble
    point = [d(0), d("1.2"), d(".8"), d("1.4")]
    x = [audit.Jet(v, np.eye(4, dtype=d)[i]) for i, v in enumerate(point)]
    r = (x[1] ** 2 + x[2] ** 2 + x[3] ** 2) ** d(".5")
    mass = d(".2")
    u = mass / (2 * r)
    g = [[audit.Jet(0) for _ in range(4)] for _ in range(4)]
    g[0][0] = -(((1 - u) / (1 + u)) ** 2)
    for i in (1, 2, 3):
        g[i][i] = (1 + u) ** 4
    jets = audit.metric_array(g)
    riem = audit.riemann(jets)
    assert np.max(abs(np.einsum("abad->bd", riem))) < 1e-17
    diag = np.diag(jets[0])
    lower = diag[:, None, None, None] * riem
    iv = 1 / diag
    k = np.einsum("abcd,abcd,a,b,c,d->", lower, lower, iv, iv, iv, iv)
    areal = r.v * (1 + u.v) ** 2
    assert float(k) == pytest.approx(float(48 * mass**2 / areal**6), rel=2e-15)


def test_saved_field_mismatch_is_reproduced_and_isolated_to_dragging():
    source = Path(
        "results/railgun/studies/ergo372-smooth-spectral-20261104/accepted.npz"
    )
    report = audit.audit(source)
    error = report["equatorial_points"][0]["maximum"]
    assert abs(error - 1.236984736863178e-7) < 2e-12
    assert error > 1e-8
    assert report["diagnostic_replacement_remaining"]["w"] < 1e-10
    for key in ("f", "C", "H"):
        assert report["diagnostic_replacement_remaining"][key] > 1e-8
