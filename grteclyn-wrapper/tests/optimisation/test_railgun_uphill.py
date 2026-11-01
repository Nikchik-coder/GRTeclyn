"""Analytic turnaround, matched energy brackets and bounded new experiments."""
import json
from pathlib import Path
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.railgun.uphill import energy_regimes,validate_config

ROOT=Path(__file__).resolve().parents[3]


def test_threshold_scan_brackets_all_three_rest_energies():
    thresholds=dict(zero=.95,positive=.950001,negative=.949999)
    energies=energy_regimes(thresholds,1e-7)
    assert energies['requested_offset']==pytest.approx(.9500001)
    assert energies['below_all']<min(thresholds.values())
    assert energies['above_all']>max(thresholds.values())
    assert thresholds['negative']<energies['between_spin_thresholds']<thresholds['positive']
    thresholds['positive']=np.nan
    with pytest.raises(ValueError):energy_regimes(thresholds,1e-7)


def test_uphill_dry_plan_refuses_an_unbudgeted_track_count():
    config=json.loads((ROOT/'research/railgun/studies/uphill_transit.json').read_text())
    assert validate_config(config)['tracks']==32
    config['max_tracks']=64
    with pytest.raises(ValueError):validate_config(config)


def test_compactness_budget_preserves_three_grid_acceptance():
    from grteclyn_wrapper.optimisation.railgun.compactness import preflight
    config=json.loads((ROOT/'research/railgun/studies/compactness_scan.json').read_text())
    source=ROOT/'results/railgun/studies/ring-validated/accepted.npz'
    assert preflight(source,config)['max_solves']==21
    config['max_solves']=42
    with pytest.raises(ValueError):preflight(source,config)


def test_uphill_turnaround_agrees_with_exact_rindler_geodesic():
    from grteclyn_wrapper.optimisation.railgun.transport import MPDSystem
    from grteclyn_wrapper.optimisation.solver.device import configure_jax
    jax=configure_jax();xp=jax.numpy
    def rindler(x):return xp.diag(xp.array([-(1-.05*x[3])**2,1.,1.,1.]))
    system=MPDSystem(rindler,regular_origin=True)
    state=system.initial_state([0.,0.,1.],speed=-.2,spin=.001)
    energy=system.invariants(state)['energy']
    result=system.integrate(state,duration=10.,inner_radius=0.,target_z=-1.,max_step=.1,
                            rtol=2e-12,atol=2e-14,stop_at_turnaround=True)
    assert result['stop']=='turnaround'
    assert result['state'][-1,3]==pytest.approx((1-energy)/.05,abs=2e-10)
    assert abs(float(system._rhs_jit(xp.asarray(result['state'][-1]))[3]))<1e-10
    assert result['absolute_drift']['energy']<1e-11


def test_flat_transmission_does_not_trigger_a_turnaround():
    from grteclyn_wrapper.optimisation.railgun.transport import MPDSystem
    from grteclyn_wrapper.optimisation.solver.device import configure_jax
    xp=configure_jax().numpy
    system=MPDSystem(lambda x:xp.diag(xp.array([-1.,1.,1.,1.])),regular_origin=True)
    state=system.initial_state([2.,0.,1.],speed=-.2)
    result=system.integrate(state,duration=20.,inner_radius=0.,target_z=-1.,max_step=.5,
                            stop_at_turnaround=True)
    assert result['stop']=='target_z'
    with pytest.raises(ValueError,match='initially decreasing'):
        state=system.initial_state([2.,0.,1.],speed=.2)
        system.integrate(state,inner_radius=0.,stop_at_turnaround=True)
