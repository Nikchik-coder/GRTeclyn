"""The rotating KG frequency is quadratic and retains angular coupling."""
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
from grteclyn_wrapper.optimisation.railgun.model import ScalarField
from grteclyn_wrapper.optimisation.railgun.counter_rotation import linear_rotating_seed


def test_constant_dragging_shifts_the_full_two_dimensional_bound_frequency():
    p=RingProblem([ScalarField(winding=1),ScalarField(winding=-2,amplitude=.001)],nx=40,ny=4,length=5.)
    arrays,freq=p.unpack(p.seed())
    for tag in ('w','N','b'):arrays[tag]*=0.
    arrays['f'][1:]=-.8/np.sqrt(1+(p.r[1:,None]/5)**2)
    _,static=linear_rotating_seed(p,p.pack(arrays,freq))
    arrays['w'][:]=.002
    seed,rotating=linear_rotating_seed(p,p.pack(arrays,freq))
    assert rotating['frequency']==pytest.approx(static['frequency']+.004,abs=1e-9)
    assert rotating['printed_pde_relative_residual']<1e-8
    q,_=p.unpack(seed)
    assert float(p.anchors[1]@q['q1'][:,-1])==pytest.approx(.001,abs=1e-13)
    np.testing.assert_array_equal(q['q1'][[0,-1]],0.)
    arrays['f'][1:]+= .02*np.exp(-(p.r[1:,None]/5.)**2)*p.y[None,:]
    nonspherical,record=linear_rotating_seed(p,p.pack(arrays,freq))
    q,_=p.unpack(nonspherical)
    assert np.max(np.ptp(q['q1'],axis=1))>1e-4*np.max(abs(q['q1']))
    assert record['printed_pde_relative_residual']<1e-8


def test_quadratic_seed_refuses_an_unbound_flat_background():
    p=RingProblem([ScalarField(winding=1),ScalarField(winding=-2,amplitude=.001)],nx=24,ny=4)
    a,f=p.unpack(p.seed())
    for tag in ('f','w','N','b'):a[tag]*=0.
    with pytest.raises(RuntimeError,match='no resolved nodeless'):
        linear_rotating_seed(p,p.pack(a,f))


def test_cusolver_bound_mode_agrees_with_the_host_reference():
    p=RingProblem([ScalarField(winding=1),ScalarField(winding=-2,amplitude=.001)],nx=32,ny=4,length=5.)
    if p.jax.devices()[0].platform!='gpu':pytest.skip('cuSOLVER regression requires GPU')
    a,f=p.unpack(p.seed())
    for tag in ('w','N','b'):a[tag]*=0.
    a['f'][1:]=-.8/np.sqrt(1+(p.r[1:,None]/5)**2)
    _,host=linear_rotating_seed(p,p.pack(a,f))
    _,gpu=linear_rotating_seed(p,p.pack(a,f),eigensolver='cusolver')
    assert gpu['eigensolver']=='cusolver'
    assert gpu['frequency']==pytest.approx(host['frequency'],abs=1e-9)
    assert gpu['printed_pde_relative_residual']<1e-8
