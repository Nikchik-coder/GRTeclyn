"""Signed interior potentials must preserve the intended asymptotic vacua."""
import numpy as np
import pytest
from grteclyn_stationary.matter.domain import admissible, shape_diagnostics
from grteclyn_stationary.matter.potentials import PolynomialPotential


def test_negative_interior_has_flat_massive_endpoints():
    q=(-4.2,4.2,0.)
    m,pm=.3,-2.5
    p=PolynomialPotential.kink_q(m,pm,q)
    assert p.V(pm/2)<0
    np.testing.assert_allclose(p.V(np.array([0.,pm])),0.,atol=1e-14)
    np.testing.assert_allclose(p.dV(np.array([0.,pm])),0.,atol=1e-14)
    np.testing.assert_allclose(p.d2V(np.array([0.,pm])),2*m*m,rtol=1e-12)
    assert not admissible(q)
    assert admissible(q,'endpoint-positive')
    info=shape_diagnostics(q)
    assert info['min_Q']==pytest.approx(-.05)
    assert info['min_Q_u']==pytest.approx(.5)
    assert info['Q_end']==pytest.approx(1.)


@pytest.mark.parametrize('q', [(-1.,),(-2.,),(float('nan'),),(float('inf'),)])
def test_bad_endpoints_rejected_in_both_domains(q):
    assert not admissible(q)
    assert not admissible(q,'endpoint-positive')


def test_constant_and_unequal_vacuum_masses():
    assert admissible(())
    assert shape_diagnostics(())['min_Q']==1.
    m,pm=.7,-1.3
    p=PolynomialPotential.kink_q(m,pm,(-4.2,4.4,0.))
    assert p.d2V(0.)==pytest.approx(2*m*m)
    assert p.d2V(pm)==pytest.approx(2*m*m*1.2)


def test_study_refuses_invalid_endpoint_before_diagnostics(monkeypatch):
    from grteclyn_stationary.studies import validation as sv
    monkeypatch.setattr(sv,'volume_budgets',lambda *a,**kw:pytest.fail('invalid shape reached physics checks'))
    row=sv.validate({},dict(m=.3,q=[-2.],potential_domain='endpoint-positive'),
                    dict(verdict='PASS'),reference_peak=None,tidal_factor=1.)
    assert row['rejection_reasons']==['potential_domain']
    assert row['stability']=='not_assessed'
