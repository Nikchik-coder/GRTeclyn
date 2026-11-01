"""Gap acceptance uses resolved component edges, not displaced maxima."""
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.railgun.gap import annular_gap


def test_thin_concentric_rings_have_a_resolved_annular_gap():
    r=np.linspace(0.,20.,4001)
    density=np.array([np.exp(-((r-4.)/.3)**2),.2*np.exp(-((r-10.)/.4)**2)])
    result=annular_gap(r,density)
    assert result['accepted'],result['reasons']
    assert result['inner_ring_outer_radius']<result['outer_ring_inner_radius']
    assert result['gap_width']>3.
    assert max(result['corridor']['sampled_relative_density_max'])<1e-6
    assert not result['exact_vacuum_claim']


def test_distinct_peaks_with_overlapping_tails_fail():
    r=np.linspace(0.,40.,4001)
    density=np.array([np.exp(-((r-6.)/3.)**2),.1*np.exp(-((r-8.)/3.)**2)])
    result=annular_gap(r,density)
    assert not result['accepted']
    assert result['gap_width']<0.
    assert 'no_resolved_annular_gap' in result['reasons']


def test_a_radial_node_between_inner_peaks_is_not_an_outer_edge():
    r=np.linspace(0.,20.,4001)
    density=np.array([np.exp(-((r-4.)/.3)**2)+.2*np.exp(-((r-12.)/.3)**2),
                      .5*np.exp(-((r-9.)/.3)**2)])
    assert not annular_gap(r,density)['accepted']


def test_tail_domain_and_nonfinite_data_fail_closed():
    r=np.linspace(0.,8.,401)
    density=np.array([np.exp(-((r-4.)/3.)**2),np.exp(-((r-6.)/.3)**2)])
    result=annular_gap(r,density)
    assert not result['accepted'] and 'inner_ring_outer_tail_unresolved' in result['reasons']
    density[1,50]=np.nan
    with pytest.raises(ValueError):annular_gap(r,density)


def test_spectral_energy_density_matches_archived_cartesian_derivatives():
    import json
    from pathlib import Path
    from grteclyn_wrapper.optimisation.railgun.gap import equatorial_densities
    root=Path(__file__).resolve().parents[3]/'results/railgun'
    if not (root/'ring-profile/equator.tsv').exists():pytest.skip('saved Cartesian profile unavailable')
    data=np.loadtxt(root/'ring-profile/equator.tsv')[1:]
    with np.load(root/'ring-validated/accepted.npz') as archive:
        metadata=json.loads(str(archive['metadata']));u=archive['u']
    density=equatorial_densities(metadata,u,data[:,0])[0]
    np.testing.assert_allclose(density,data[:,2],atol=2e-13,rtol=1e-9)
