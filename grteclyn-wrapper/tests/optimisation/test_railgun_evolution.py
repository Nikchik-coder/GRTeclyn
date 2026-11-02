"""Independent metric, phase, sign and coordinate checks for ring grid export."""
import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.evolution import (
    COMPONENTS, SYMMETRIC, algebraic_checks, grid_points, source_contract, state_evaluator,
)
from grteclyn_wrapper.optimisation.solver.device import configure_jax


def matrices(state):
    h = np.zeros((3, 3)); a = np.zeros((3, 3))
    for c, (i, j) in enumerate(SYMMETRIC):
        h[i, j] = h[j, i] = state[1+c]
        a[i, j] = a[j, i] = state[8+c]
    return h, a


def test_flat_harmonic_scalar_has_positive_normal_momentum_and_correct_normalization():
    jax = configure_jax(); xp = jax.numpy
    def scalar(x):
        return .3*xp.array([xp.cos(.7*x[0]), xp.sin(.7*x[0])])
    evaluate = state_evaluator(lambda x: xp.diag(xp.array([-1., 1., 1., 1.])), scalar, jax)
    states, density = map(np.asarray, evaluate(xp.array([[0., 0., 0., 0.]])))
    state = states[0]; h, a = matrices(state)
    np.testing.assert_allclose(h, np.eye(3), atol=1e-15)
    np.testing.assert_allclose(a, 0, atol=1e-15)
    assert state[25] == pytest.approx(.3/np.sqrt(4*np.pi))
    assert state[28] == pytest.approx(.21/np.sqrt(4*np.pi))
    assert state[26] == 0 and state[27] == 0
    assert density[0, 0] == pytest.approx(.7*.3**2/(4*np.pi))
    assert algebraic_checks(states)['accepted']
    assert COMPONENTS[27:] == ['phi_lump0', 'Pi_lump0']


def test_differential_rotation_gives_nonzero_extrinsic_curvature_and_J_minus_k_Q():
    jax = configure_jax(); xp = jax.numpy
    # Euclidean spatial metric, spatially varying rotation, constant lapse.
    # Direct Killing-vector formula: K_ij=-(w_i eta_j+w_j eta_i)/(2 alpha).
    alpha, omega, coeff = .8, .7, .03
    def metric(x):
        eta = xp.array([-x[2], x[1], 0.]); w = coeff*xp.sum(x[1:]**2)
        g = xp.eye(4).at[0, 0].set(-alpha**2+w*w*(x[1]**2+x[2]**2))
        return g.at[0, 1:].set(-w*eta).at[1:, 0].set(-w*eta)
    def scalar(x):
        phase = omega*x[0]
        return xp.array([x[1]*xp.cos(phase)-x[2]*xp.sin(phase),
                         x[1]*xp.sin(phase)+x[2]*xp.cos(phase)])
    x = np.array([0., 1.2, -.4, .7])
    states, density = map(np.asarray, state_evaluator(metric, scalar, jax)(xp.asarray(x[None])))
    state = states[0]; h, a = matrices(state)
    eta = np.array([-x[2], x[1], 0.]); dw = 2*coeff*x[1:]
    expected = -(np.outer(dw, eta)+np.outer(eta, dw))/(2*alpha)
    np.testing.assert_allclose(a, expected, atol=2e-15)
    assert state[7] == pytest.approx(0, abs=1e-15)
    np.testing.assert_allclose(state[15:18], 0, atol=1e-15)
    w = coeff*np.sum(x[1:]**2)
    factor = (omega+w)/alpha/np.sqrt(4*np.pi)
    np.testing.assert_allclose(state[[26, 28]], factor*np.array([-x[2], x[1]]), atol=1e-15)
    assert density[0, 1] == pytest.approx(-density[0, 0], abs=1e-15)
    assert algebraic_checks(states)['accepted']


def test_nonconformally_flat_geometry_keeps_contracted_connections():
    jax = configure_jax(); xp = jax.numpy
    # det(gamma)=1: h=diag(exp(2ax),exp(-2ax),1), chi=1.
    # Gamma^x=-partial_x h^xx=2a exp(-2ax), the other components vanish.
    rate = .2
    def metric(x):
        return xp.diag(xp.array([-1., xp.exp(2*rate*x[1]), xp.exp(-2*rate*x[1]), 1.]))
    evaluate = state_evaluator(metric, lambda x: xp.zeros(2), jax)
    states, _ = evaluate(xp.array([[0., .4, .2, -.3]]))
    np.testing.assert_allclose(np.asarray(states)[0, 15:18],
                               [2*rate*np.exp(-2*rate*.4), 0, 0], atol=1e-15)


def test_time_dependent_metric_uses_minus_time_derivative_in_extrinsic_curvature():
    jax = configure_jax(); xp = jax.numpy
    hubble = .1
    def metric(x):
        return xp.diag(xp.array([-1., xp.exp(2*hubble*x[0]),
                                xp.exp(2*hubble*x[0]), xp.exp(2*hubble*x[0])]))
    states, _ = state_evaluator(metric, lambda x: xp.zeros(2), jax)(xp.zeros((1, 4)))
    state = np.asarray(states)[0]
    assert state[7] == pytest.approx(-3*hubble)
    np.testing.assert_allclose(state[8:14], 0, atol=1e-16)


def test_ghost_padding_matches_loader_cell_centres_without_a_second_interpolation():
    n, length, ghosts = 16, 32., 4
    points, indices = grid_points(n, length, ghosts, 0, 24**3)
    world = points[:, 1:] + length/2
    file_origin = -ghosts*length/n
    # ExternalGridInitialData computes (p-origin)/dx-.5.
    reconstructed_indices = (world-file_origin)/(length/n)-.5
    np.testing.assert_allclose(reconstructed_indices, indices, atol=0)
    chosen = indices[:, 0] == ghosts
    assert np.all(points[chosen, 1] == -15.)
    assert np.isfinite(points).all()


def test_unarchived_field_is_rejected_before_device_start(tmp_path):
    # A checksum archive with no payload cannot establish source identity.
    (tmp_path/'sha256sums.txt').write_text('')
    source = tmp_path/'accepted.npz'
    source.write_bytes(b'not a solution')
    with pytest.raises(ValueError, match='checksummed'):
        source_contract(source)


def test_pilot_requires_a_certified_matching_export_and_explicit_checkpoint_choice(tmp_path):
    import json
    from grteclyn_wrapper.optimisation.railgun.evolution import digest
    from grteclyn_wrapper.optimisation.railgun.evolution_pilot import prepare
    grid = tmp_path/'initial.gridinit'
    header = ('GRTECLYN_GRID_INIT_V2\nnum_components 29\n'
              f'component_names {" ".join(COMPONENTS)}\n'
              'nx_ny_nz 104 104 104\n'
              f'dx {32/96:.17e} {32/96:.17e} {32/96:.17e}\n'
              f'origin {-4*32/96:.17e} {-4*32/96:.17e} {-4*32/96:.17e}\n'
              'END_HEADER\n').encode('ascii')
    with grid.open('wb') as stream:
        stream.write(header)
        # Sparse placeholder: header and extent only, never a physical export.
        stream.truncate(len(header)+104**3*29*8)
    manifest = dict(components=COMPONENTS, matter_model='grtresna_complex_scalar',
                    perturbation='none', n=96, length=32., ghosts=4, frequency=.70, mass=1.)
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    (tmp_path/'outcome.json').write_text(json.dumps(dict(accepted=True, gridinit_sha256=digest(grid))))
    (tmp_path/'corridor.json').write_text(json.dumps(dict(accepted=False)))
    template = tmp_path/'pilot.txt'
    with pytest.raises(ValueError, match='certified'):
        prepare(tmp_path, template, checkpoints='off')
    assert not template.exists()
    (tmp_path/'corridor.json').write_text(json.dumps(dict(accepted=True)))
    with pytest.raises(ValueError, match='without checkpoints'):
        prepare(tmp_path, template, checkpoints='on')
    plan = prepare(tmp_path, template, checkpoints='off')
    assert plan['stop_time'] == 2. and plan['max_level'] == 0
    text = template.read_text()
    assert 'recipe_scalar_sign = 1' in text and 'calculate_complex_scalar_diagnostics = 1' in text
    assert 'center = 16 16 16' in text and 'lo_boundary = 1 1 1' in text
    assert 'amr.checkpoint_files_output = 0' in text
    with pytest.raises(ValueError, match='overwrite'):
        prepare(tmp_path, template, checkpoints='off')
    manifest['frequency'] = .67
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='certified'):
        prepare(tmp_path, tmp_path/'other.txt', checkpoints='off')


def test_malformed_grid_layout_is_rejected(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.evolution import grid_layout
    path = tmp_path/'bad.gridinit'
    path.write_bytes(b'GRTECLYN_GRID_INIT_V2\nnum_components 2\n')
    with pytest.raises(ValueError, match='header'):
        grid_layout(path)
