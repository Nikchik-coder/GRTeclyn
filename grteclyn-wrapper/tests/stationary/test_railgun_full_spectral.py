"""Retain sub-ulp angular dragging modes without changing the PDE."""

import numpy as np

from grteclyn_stationary.railgun.smooth_full_spectral import (
    SmoothFullSpectralProblem,
)
from grteclyn_stationary.railgun.smooth_spectral import SmoothSpectralProblem
from grteclyn_stationary.railgun.model import ScalarField
from grteclyn_stationary.railgun.workflow import save_state, load_state


def test_prepared_recovery_changes_only_the_representation_and_approval():
    from grteclyn_stationary.railgun.full_spectral_recovery import plan
    from grteclyn_stationary.railgun.smooth_spectral_recovery import plan as previous

    proposed, old = plan(), previous()
    cfg = dict(proposed['config'])
    old_cfg = dict(old['config'])
    for key in ('discretisation', 'approval'):
        cfg.pop(key)
        old_cfg.pop(key)
    assert cfg == old_cfg
    assert proposed['all_interior_rows_retained']
    assert proposed['independent_cartesian_flux']
    assert proposed['infinity_angular_momentum_measured']
    assert proposed['numerical_execution'] is False
    assert proposed['checkpoints'] is False


def problem(cls=SmoothFullSpectralProblem, nx=12, ny=4):
    return cls(
        [ScalarField(winding=1, mass=1.0, amplitude=0.1)],
        nx=nx,
        ny=ny,
        length=2.5,
        central_lapse=0.9,
    )


def test_tiny_angular_dragging_derivatives_survive_nodal_rounding():
    p = problem()
    u = np.zeros(p.n_unknowns)
    u[-1] = 0.8
    c = p.dragging_coefficients(u)
    c[0, 0] = 0.1
    c[0, 2] = 1e-20
    np.testing.assert_array_equal(p.raw_dragging(u)[0], np.full(p.ny + 1, 0.1))
    expected = 4e-20 * (1 - p.s[:, None]) ** 3 * np.ones((1, p.ny + 1))
    for xp, value in ((np, u), (p.xp, p.xp.asarray(u))):
        fn = lambda v: p.dragging_jets(v, xp)["w_yy"]
        actual = fn(value) if xp is np else p.jax.jit(fn)(value)
        np.testing.assert_allclose(np.asarray(actual), expected, rtol=2e-14, atol=1e-33)


def test_all_rows_match_old_representation_for_manufactured_polynomial():
    p = problem()
    old = problem(SmoothSpectralProblem)
    u = np.zeros(p.n_unknowns)
    u[-1] = 0.8
    for key in ("f", "N", "b", "w"):
        c = p.raw_metric(u, key)
        c[0, 0] = 0.003
        c[1, 0] = 0.001
        c[2, 2] = 0.0001
    u[4*p.n:5*p.n] = np.broadcast_to(
        0.03*(1-p.s[:, None])**2, p.shape
    ).ravel()
    v = u.copy()
    v[p.n : 2 * p.n] = p.raw_dragging(u).ravel()
    np.testing.assert_allclose(p.residual(u), old.residual(v), rtol=1e-9, atol=3e-12)
    np.testing.assert_allclose(
        p.infinity_boundary(u), old.infinity_boundary(v), rtol=1e-9, atol=3e-12
    )
    assert np.isfinite(np.asarray(p.jacobian(u))).all()
    assert p.omitted_row_count == 0


def test_full_dragging_coefficients_survive_archive_geometry_and_refinement(tmp_path):
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.dragging_falloff import (
        FactoredDraggingGeometry,
    )

    p = problem()
    u = np.zeros(p.n_unknowns)
    u[-1] = 0.8
    c = p.dragging_coefficients(u)
    c[0, 0] = 0.1
    c[3, 2] = 1e-20
    path = tmp_path / "field.npz"
    save_state(path, p, u)
    other, v, _ = load_state(path)
    assert isinstance(other, SmoothFullSpectralProblem)
    np.testing.assert_array_equal(u, v)
    np.testing.assert_array_equal(RingGeometry(p, u).dragging_h, c)
    np.testing.assert_array_equal(FactoredDraggingGeometry(p, u).h_coefficients, c)
    bigger = problem(nx=16, ny=6)
    new = bigger.transfer(p, u)
    np.testing.assert_array_equal(bigger.dragging_coefficients(new)[:13, :5], c)
    same = p.transfer(p, u)
    np.testing.assert_array_equal(same, u)


def test_old_representation_transfers_without_changing_physical_field():
    old = problem(SmoothSpectralProblem)
    new = problem()
    u = np.zeros(old.n_unknowns)
    u[-1] = 0.8
    old.raw_metric(u, "f")[0, 0] = -0.1
    old.raw_metric(u, "w")[0] = 0.02 + 0.001 * old.y**2
    v = new.transfer(old, u)
    for name, a in old.unpack(u)[0].items():
        np.testing.assert_allclose(new.unpack(v)[0][name], a, rtol=0, atol=2e-15)


def test_common_point_observables_preserve_full_dragging_representation(tmp_path):
    from grteclyn_stationary.railgun.ergoregion_scan import (
        common_metric_samples,
    )

    old = problem(SmoothSpectralProblem)
    new = problem()
    u = np.zeros(old.n_unknowns)
    u[-1] = 0.8
    old.raw_metric(u, "f")[0, 0] = -0.1
    old.raw_metric(u, "w")[0] = 0.02 + 0.001 * old.y**2
    a, b = tmp_path / "old.npz", tmp_path / "new.npz"
    save_state(a, old, u)
    save_state(b, new, new.transfer(old, u))
    before, after = common_metric_samples(a), common_metric_samples(b)
    for key in ("lapse_min", "gtt_max", "shift_norm_over_lapse_max"):
        np.testing.assert_allclose(before[key], after[key], rtol=3e-14, atol=1e-15)
