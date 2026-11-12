"""A shallow crossing followed by a turn must count the first crossing."""
import numpy as np
import pytest
from grteclyn_stationary.railgun.first_crossing import first_crossing


def test_first_crossing_precedes_a_nearby_turn_within_the_same_sample_interval():
    time=np.linspace(0.,1.,101);state=np.zeros((len(time),24))
    state[:,0]=2*time;state[:,3]=-10.000001+(time-1.)**2
    state[:,7]=2*(time-1.)
    result=first_crossing(time,state,-10.)
    assert result['time'][-1]==pytest.approx(.999,abs=1e-11)
    assert result['state'][-1,0]==pytest.approx(1.998,abs=2e-11)
    assert result['state'][-1,3]==pytest.approx(-10.,abs=1e-12)
    assert result['state'][-1,7]<0.
    assert result['audit']['state_max']<1e-11


def test_a_turn_before_the_destination_does_not_become_a_crossing():
    time=np.linspace(0.,1.,101);state=np.zeros((len(time),24))
    state[:,3]=-9.999+(time-1.)**2
    assert first_crossing(time,state,-10.) is None


def test_first_crossing_rejects_nonfinite_saved_states():
    time=np.linspace(0.,1.,101);state=np.zeros((len(time),24));state[50,0]=np.nan
    with pytest.raises(ValueError):first_crossing(time,state,-10.)


def test_recovered_crossing_matches_exact_rindler_time_and_killing_energy():
    from grteclyn_stationary.railgun.transport import MPDSystem
    from grteclyn_stationary.numerics.device import configure_jax
    xp=configure_jax().numpy
    acceleration=.05
    def metric(x):return xp.diag(xp.array([-(1-acceleration*x[3])**2,1.,1.,1.]))
    system=MPDSystem(metric,regular_origin=True)
    state=system.initial_state([0.,0.,1.],speed=-.2,spin=.001)
    energy=system.invariants(state)['energy'];turn_z=(1-energy)/acceleration
    target=turn_z+1e-6
    track=system.integrate(state,duration=10.,inner_radius=0.,max_step=.5,
                          stop_at_turnaround=True,samples=1001,rtol=2e-12,atol=2e-14)
    crossing=first_crossing(track['time'],track['state'],target)
    alpha0=.95;gamma=1/np.sqrt(1-.2**2)
    expected=(alpha0*gamma*.2-np.sqrt(energy**2-(1-acceleration*target)**2))/acceleration
    assert crossing['time'][-1]==pytest.approx(expected,abs=2e-9)
    invariants=system.invariants(crossing['state'][-1])
    assert abs(invariants['energy']-energy)<1e-11
    assert abs(invariants['mass2']-1.)<1e-11
    assert invariants['ssc_max']<1e-12
    direct=system.integrate(state,duration=10.,inner_radius=0.,max_step=.5,target_z=target,
                            stop_at_turnaround=True,samples=1001,rtol=2e-12,atol=2e-14)
    assert direct['stop']=='target_z'
    assert direct['time'][-1]==pytest.approx(expected,abs=2e-9)
