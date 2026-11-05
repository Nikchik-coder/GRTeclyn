"""Only the explicitly revised exterior-ring preference may change."""
import copy
import pytest
from grteclyn_wrapper.optimisation.ringwormhole_overlap import assess


def rows():
    return [dict(nx=n,ny=m,verdict='ABOVE_GATE',rejection_reasons=['ring_does_not_surround_throat'],
        X_full=2.5,E_b=1.,Q_b=1.,J_measured=-.5,ring_peak_radius=2.1,
        equatorial_shift_over_lapse_max=.8,throat_gtt_max=-.1,throat_shift_over_lapse_max=.8,
        offgrid_pass=True,surface_verified=True,tidal_converged=True)
        for n,m in [(210,36),(224,38),(240,40)]]


def test_accept_overlap_without_mutating_original_checks():
    r=rows();before=copy.deepcopy(r);result=assess(r)
    assert result['passed'] and not result['throat_ergoregion_resolved']
    assert r==before


@pytest.mark.parametrize('reason',['ordinary_energy_budget','tidal_limit','reflection_symmetry','offgrid_equations'])
def test_other_rejections_cannot_be_removed(reason):
    r=rows();r[1]['rejection_reasons'].append(reason)
    assert not assess(r)['passed']


def test_three_grids_and_independent_checks_still_required():
    r=rows();assert not assess(r[:2])['passed']
    r[0]['offgrid_pass']=False;assert not assess(r)['passed']
    r=rows();r[-1]['X_full']*=1.01;assert not assess(r)['passed']
