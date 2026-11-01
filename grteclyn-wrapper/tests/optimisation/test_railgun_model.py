"""Canonical source, parity, centre and charge tests on small tensor grids."""
import dataclasses
import numpy as np
import pytest

from grteclyn_wrapper.optimisation.railgun.model import ScalarField, canonical_rows, exprel
from grteclyn_wrapper.optimisation.matter_equations import MATTER_JET_NAMES, matter_residual_forms


@pytest.mark.parametrize('kwargs', [dict(winding=1.5), dict(winding=True), dict(mass=0),
    dict(amplitude=float('nan')), dict(parity='mixed'), dict(quartic=-1)])
def test_invalid_field(kwargs):
    with pytest.raises(ValueError):
        ScalarField(**kwargs)


@pytest.mark.parametrize('winding', [0, 1, -2, 3])
@pytest.mark.parametrize('parity', ['even', 'odd'])
def test_sources_reduce_to_independently_transcribed_single_field(winding, parity):
    rng = np.random.default_rng(71)
    shape = (2, 3)
    y = np.array([-.7, .1, .8])[None, :]
    jets = {key: .03*rng.normal(size=shape) for key in MATTER_JET_NAMES}
    jets['B'] += 1.
    for key in list(jets):
        if key.startswith(('psi', 'chi', 'z')):
            jets[key] *= 0.
    for suffix in ('', '_x', '_xx', '_y', '_yy'):
        jets['q0'+suffix] = .04*rng.normal(size=shape)
    field = ScalarField(winding=winding, parity=parity, quartic=.3, sextic=.1)
    kw = dict(r=np.array([1., 2.])[:, None], dr=1., ddr=0., y=y)
    got = canonical_rows(jets, [field], [.8], xp=np, **kw)
    q, qx, qxx, qy, qyy = [jets['q0'+s] for s in ('','_x','_xx','_y','_yy')]
    if parity == 'odd':
        p = np.sqrt((1+y)/2)
        zy = p*qy+q/(4*p)
        zyy = p*qyy+qy/(2*p)-q/(16*p**3)
        z, zx, zxx = p*q, p*qx, p*qxx
    else:
        z, zx, zxx, zy, zyy = q, qx, qxx, qy, qyy
    tag = 'z' if winding else 'chi'
    for suffix, value in zip(('','_x','_xx','_y','_yy'), (z,zx,zxx,zy,zyy)):
        jets[tag+suffix] = value
    amp2 = ((1-y)/2)**abs(winding)*z*z
    pot = field.mass**2*amp2+.3*amp2**2+.1*amp2**3
    eff = field.mass**2+.6*amp2+.3*amp2**2
    args = dict(uz=pot, duz=2*eff, oz=.8, kz=winding,
                expm1u=lambda x: exprel(x, np)) if winding else dict(U=pot,dU=2*eff*z,oc2=.8**2)
    expected = matter_residual_forms(np.exp, eta0=0., eta=kw['r'], deta=1.,d2eta=0.,
                                   y=y, jets=jets,V=0.,dV=0.,**args)
    for key in ('E_f','E_w','E_B','E_Nr','E_c','E19'):
        np.testing.assert_allclose(got[key], expected[key], atol=1e-14)
    p = np.sqrt((1+y)/2) if parity == 'odd' else 1.
    np.testing.assert_allclose(got['E_q0'], expected['E_z' if winding else 'E_chi']/p,atol=1e-14)


def test_odd_parity_rows_have_finite_axis_and_equator_limits():
    shape = (2,3)
    jets = {key: np.zeros(shape) for key in MATTER_JET_NAMES}
    jets['B'] += 1.
    for suffix in ('','_x','_xx','_y','_yy'):
        jets['q0'+suffix] = np.ones(shape)*.02
    out = canonical_rows(jets,[ScalarField(parity='odd')],[.9],r=1.,dr=1.,ddr=0.,
                         y=np.array([[-1.,0.,1.]]),xp=np)
    assert all(np.isfinite(v).all() for v in out.values())


def test_independent_fields_add_stress_without_interference():
    shape = (2,3)
    jets = {key: np.zeros(shape) for key in MATTER_JET_NAMES}
    jets['B'] += 1.
    for i in range(2):
        for suffix in ('','_x','_xx','_y','_yy'):
            jets[f'q{i}'+suffix] = np.ones(shape)*.02
    common = dict(r=1.,dr=1.,ddr=0.,y=np.array([[-1.,0.,1.]]),xp=np)
    one = canonical_rows(jets,[ScalarField()],[.9],**common)
    two = canonical_rows(jets,[ScalarField(),ScalarField()],[.9,.9],**common)
    for key in ('E_f','E_w','E_B','E_Nr','E_c','E19'):
        np.testing.assert_allclose(two[key],2*one[key],atol=1e-17)


def test_flat_solution_and_correct_centre_rows():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    vacuum = RingProblem(nx=8,ny=4)
    np.testing.assert_allclose(vacuum.residual(np.zeros(vacuum.n_unknowns)),0.,atol=1e-14)
    p = RingProblem([ScalarField()],nx=8,ny=4)
    u = p.seed()
    assert len(p.residual(u)) == len(u) == p.n_unknowns
    arrays,_ = p.unpack(u)
    assert np.all(arrays['q0'][-1] == 0.)
    # The J condition is an additional border, not a replacement for a KG row.
    pair = RingProblem([ScalarField(),ScalarField(winding=-2)],nx=8,ny=4,target_j=0.)
    assert pair.residual(pair.seed()).shape == (pair.n_unknowns,)
    with pytest.raises(ValueError):
        RingProblem([ScalarField(),ScalarField()],target_j=0.)


def test_charge_normalisation_and_winding_sign():
    from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
    field = ScalarField()
    p = RingProblem([field, dataclasses.replace(field,winding=-1)],nx=96,ny=8,length=1.,target_j=0.)
    arrays = {tag:np.zeros(p.shape) for tag in p.tags}
    radial = p.r[1:]*np.exp(-p.r[1:]**2/2)
    arrays['q0'][1:] = radial[:,None]
    arrays['q1'][1:] = radial[:,None]
    u = p.pack(arrays,[.8,.8])
    charge = np.asarray(p.charge_integrals(u))
    np.testing.assert_allclose(charge,.8*np.sqrt(np.pi)/4,rtol=2e-8)
    assert abs(sum(-f.winding*q for f,q in zip(p.fields,charge))) < 1e-13


def test_three_grid_policy_fails_closed():
    from grteclyn_wrapper.optimisation.railgun.diagnostics import converged_records
    row = dict(verdict='PASS',M_ADM_estimate=1.,J_volume=0.,dragging_max=.1)
    assert converged_records([row,row,row])[0]
    assert not converged_records([row,row])[0]
    assert not converged_records([row,row,dict(row,verdict='REJECT')])[0]
    assert not converged_records([row,row,dict(row,M_ADM_estimate=float('nan'))])[0]
