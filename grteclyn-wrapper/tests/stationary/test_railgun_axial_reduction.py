"""Axis first integrals checked against analytic transit and full MPD motion."""
import numpy as np
from grteclyn_stationary.railgun.axial_reduction import AxialMetric


def flat_axis(w=0.):
    return AxialMetric(dict(f=[0.],b=[0.],w=[w],length=6.),
                       dict(f=[0.],C=[1.],w=[w]),.4)


def test_flat_phase_and_spin_corrected_energy_match_exact_transit():
    for spin in (0.,.001,-.001):
        metric=flat_axis(.03);gamma=1.2;energy=gamma+spin*.03
        a=metric.phase(energy,spin,order=8);b=metric.phase(energy,spin,order=16)
        expected=11*gamma/np.sqrt(gamma*gamma-1)
        assert a['classification']=='transmitted'
        assert abs(a['coordinate_time']-expected)<1e-12
        assert abs(a['coordinate_time']-b['coordinate_time'])<1e-12
        state,rhs=metric.state_and_rhs(.1,energy,spin)
        assert abs(state[4]-gamma)<1e-14
        np.testing.assert_allclose(rhs[4:],0,atol=1e-16)


def test_first_turning_height_and_regular_phase_have_independent_precision():
    metric=AxialMetric(dict(f=[.2,.3],b=[0.],w=[0.],length=6.),
                       dict(f=[-.1],C=[np.exp(.1)],w=[0.]),.4)
    energy=1.08;s=(2*np.log(energy)-.2)/.3;expected=-6*(1+s)/(1-s)
    a=metric.phase(energy,0.,order=8);b=metric.phase(energy,0.,order=16)
    assert a['classification']=='reflected'
    assert abs(a['final_z']-expected)<1e-12
    assert abs(a['coordinate_time']-b['coordinate_time'])<1e-9


def test_substitution_into_full_cartesian_mpd_in_a_smooth_dragging_metric():
    from grteclyn_stationary.railgun.transport import MPDSystem
    from grteclyn_stationary.numerics.device import configure_jax
    jax=configure_jax();xp=jax.numpy
    class AnalyticAxis(AxialMetric):
        def __init__(self):pass
        def values(self,z,*,derivative=False):
            a=1+.02*z*z;c=1+.01*z*z;w=.03/(1+z*z)
            v=dict(A=a,C=c,w=w,f=np.log(a));d=dict(A=.04*z,C=.02*z,w=-.06*z/(1+z*z)**2,f=.04*z/a)
            return (v,d) if derivative else v
    def metric(x):
        z=x[3];a=1+.02*z*z;c=1+.01*z*z;w=.03/(1+z*z)
        v=xp.array([-x[2],x[1],0.]);g=xp.zeros((4,4))
        g=g.at[0,0].set(-a+c*w*w*(x[1]**2+x[2]**2))
        g=g.at[0,1:].set(-c*w*v).at[1:,0].set(-c*w*v)
        return g.at[1:,1:].set(c*xp.eye(3))
    system=MPDSystem(metric,regular_origin=True);axis=AnalyticAxis()
    for spin in (0.,.001,-.001):
        for z in (-1.,0.,.5):
            state,expected=axis.state_and_rhs(z,1.2,spin)
            np.testing.assert_allclose(system._rhs_jit(state),expected,atol=2e-14,rtol=2e-12)
            inv=system.invariants(state)
            assert abs(inv['mass2']-1)<1e-14
            assert abs(inv['energy']-1.2)<1e-14
            assert abs(inv['spin2']-spin*spin)<1e-14
