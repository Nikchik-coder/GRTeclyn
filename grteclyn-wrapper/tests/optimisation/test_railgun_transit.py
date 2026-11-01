"""A signed destination is an event, rather than a sampled crossing estimate."""
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.solver.device import configure_jax
from grteclyn_wrapper.optimisation.railgun.transport import MPDSystem


def test_exact_flat_transit_event_and_dense_samples():
    xp=configure_jax().numpy
    system=MPDSystem(lambda x:xp.diag(xp.array([-1.,1.,1.,1.])),regular_origin=True)
    state=system.initial_state([0.,0.,1.],speed=-.5,spin=.001)
    track=system.integrate(state,duration=10.,inner_radius=0.,target_z=-1.,samples=101)
    assert track['success'] and track['stop']=='target_z'
    assert track['state'].shape==(101,24)
    assert track['state'][-1,3]==pytest.approx(-1.,abs=1e-13)
    assert track['state'][-1,0]==pytest.approx(4.,abs=1e-12)
    np.testing.assert_allclose(track['state'][:,3],1.-.5*track['state'][:,0],atol=1e-12)
    with pytest.raises(ValueError,match='below'):
        system.integrate(state,target_z=1.)


def test_strict_transport_gate_rejects_small_relative_spin_drift():
    from grteclyn_wrapper.optimisation.railgun.transit import strict_gates
    first=dict(mass2=1.,spin2=1e-6,energy=1.1,angular_momentum=.001)
    track=dict(invariants=[first],absolute_drift=dict.fromkeys(first,0.),
               integrator_success=True,stop='target_z',ssc_max=0.,norm_error=0.)
    assert strict_gates(track)['accepted']
    track['absolute_drift']['spin2']=2e-15
    assert not strict_gates(track)['accepted']
    track['absolute_drift']['spin2']=0.
    track['stop']='spin_limit'
    assert not strict_gates(track)['accepted']


def test_off_axis_flat_transit_retains_its_launch_radius():
    xp=configure_jax().numpy
    system=MPDSystem(lambda x:xp.diag(xp.array([-1.,1.,1.,1.])))
    state=system.initial_state([2.,0.,1.],speed=-.5,spin=.001)
    track=system.integrate(state,duration=10.,target_z=-1.,samples=101)
    assert track['success'] and track['stop']=='target_z'
    np.testing.assert_allclose(track['state'][:,1],2.,atol=1e-13)
    np.testing.assert_allclose(track['state'][:,2],0.,atol=1e-13)
    assert track['state'][-1,3]==pytest.approx(-1.,abs=1e-13)
