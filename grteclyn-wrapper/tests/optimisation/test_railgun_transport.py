"""Exact flat-space transport and spin/Killing checks on rotating Kerr geometry."""
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.solver.device import configure_jax
from grteclyn_wrapper.optimisation.railgun.transport import MPDSystem, matched_controls

jax=configure_jax()
xp=jax.numpy


def flat(x):
    return xp.diag(xp.array([-1.,1.,1.,1.]))


def test_flat_spinning_trajectory_and_spin_condition():
    system=MPDSystem(flat)
    state=system.initial_state([0.,0.,5.],spin=.02,speed=.2)
    initial=system.invariants(state)
    assert initial['mass2'] == pytest.approx(1.,abs=1e-13)
    assert initial['spin2'] == pytest.approx(.02**2,abs=1e-13)
    assert initial['angular_momentum'] == pytest.approx(.02,abs=1e-13)
    assert initial['ssc_max'] < 1e-13
    result=system.integrate(state,duration=.5,max_step=.1)
    assert result['success']
    expected=state[:4]+.5*state[4:8]
    np.testing.assert_allclose(result['state'][-1,:4],expected,atol=1e-12)
    assert max(result['absolute_drift'].values()) < 1e-12
    assert result['ssc_max'] < 1e-12


def test_zero_spin_and_matched_launch_energy():
    system=MPDSystem(flat)
    controls=matched_controls(system,[0.,0.,5.],spin=.01,speed=.2)
    for state in controls.values():
        assert system.invariants(state)['energy'] == pytest.approx(1/np.sqrt(.96),abs=1e-12)
    np.testing.assert_allclose(controls['positive'][8:],-controls['negative'][8:],atol=1e-14)
    np.testing.assert_array_equal(controls['zero'][8:],0.)


def test_inner_stop_is_explicit_and_does_not_cross_origin():
    system=MPDSystem(flat)
    state=system.initial_state([0.,0.,1.],speed=-.5)
    track=system.integrate(state,duration=5.,inner_radius=.2,max_step=.1)
    assert track['stop']=='inner_radius'
    assert np.linalg.norm(track['state'][-1,1:4]) == pytest.approx(.2,abs=1e-10)


def test_rotating_background_spin_force_and_killing_integrals():
    def kerr(x):
        a=.4
        rr=xp.sum(x[1:]**2)
        r2=.5*(rr-a*a+xp.sqrt((rr-a*a)**2+4*a*a*x[3]**2))
        r=xp.sqrt(r2)
        ell=xp.array([1.,(r*x[1]+a*x[2])/(r2+a*a),
                      (r*x[2]-a*x[1])/(r2+a*a),x[3]/r])
        return flat(x)+2*r**3/(r**4+a*a*x[3]**2)*xp.outer(ell,ell)
    system=MPDSystem(kerr)
    states=[system.initial_state([0.,0.,6.],spin=s,speed=.1) for s in (-.002,0.,.002)]
    forces=[np.asarray(system._rhs_jit(xp.asarray(s)))[4:8] for s in states]
    assert np.max(abs(forces[2]-forces[0])) > 1e-8
    np.testing.assert_allclose((forces[2]+forces[0])/2,forces[1],atol=2e-7)
    track=system.integrate(states[-1],duration=.2,max_step=.05)
    assert track['success']
    assert max(track['absolute_drift'].values()) < 1e-8
    assert track['ssc_max'] < 1e-8
    assert track['norm_error'] < 1e-12


def test_inward_controls_retain_the_inward_velocity_branch():
    system=MPDSystem(flat)
    for state in matched_controls(system,[0.,0.,1.],spin=.01,speed=-.2).values():
        assert state[7] < 0.


def test_certified_cartesian_corridor_crosses_the_origin_with_spin():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    from grteclyn_wrapper.optimisation.railgun.geometry import RingGeometry
    from grteclyn_wrapper.optimisation.railgun.corridor import CartesianCorridor
    p=RingProblem(nx=8,ny=4)
    core=CartesianCorridor(RingGeometry(p,np.zeros(p.n_unknowns)),radius=.5,degree=3)
    certificate=core.certify()
    assert certificate['accepted'],certificate['maxima']
    np.testing.assert_allclose(core.metric(xp.zeros(4)),np.diag([-1.,1.,1.,1.]),atol=1e-13)
    assert np.isfinite(core.tensors(xp.zeros(4))[2]).all()
    system=MPDSystem(core.metric,regular_origin=True)
    state=system.initial_state([0.,0.,.3],speed=-.3,spin=.001)
    track=system.integrate(state,duration=2.,inner_radius=0.,max_step=.1)
    assert track['success']
    assert track['state'][-1,3] < 0.
    assert track['stop']=='duration'
    assert track['ssc_max'] < 1e-10
    with pytest.raises(ValueError):
        MPDSystem(flat).integrate(state,inner_radius=0.)
