"""Physical annular transit requires both low density and a validated source."""
import hashlib
import json
import numpy as np
import pytest
from grteclyn_wrapper.optimisation.railgun.annular_transit import CONFIG,channel_gate,preflight


def test_channel_checks_both_component_tails_and_trajectory_bounds():
    state=np.zeros((5,24));state[:,1]=37.;state[:,3]=np.linspace(10,-10,5)
    density=np.full((2,5),1e-9);peaks=[.01,.1]
    assert channel_gate(state,density,peaks,35.,39.)['accepted']
    for component in (0,1):
        bad=density.copy();bad[component,2]=2e-6*peaks[component]
        assert not channel_gate(state,bad,peaks,35.,39.)['accepted']
    for index,value in [(1,34.),(3,11.)]:
        bad=state.copy();bad[2,index]=value
        assert not channel_gate(bad,density,peaks,35.,39.)['accepted']


def test_rejected_or_unarchived_background_cannot_launch_tracks(tmp_path):
    source=tmp_path/'accepted.npz'
    meta=dict(validated=True,representation='dragging_quintic_regular_operator_v2',target_j=0.,
              fields=[dict(winding=1),dict(winding=-12)])
    np.savez(source,metadata=json.dumps(meta))
    records=[dict(grid=g,verdict='PASS',finite_height_channel=dict(accepted=True,rho_min=35.,rho_max=39.,z_min=-10.,z_max=10.),
                  annular_gap=dict(edges=[dict(peak_density=.01),dict(peak_density=.1)])) for g in [[192,16],[224,18],[256,20]]]
    outcome=tmp_path/'outcome.json'
    def save(accepted):
        outcome.write_text(json.dumps(dict(accepted=accepted,solves=3,records=records)))
        (tmp_path/'sha256sums.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in (source,outcome)))
    save(False)
    with pytest.raises(ValueError,match='accepted three-grid'):preflight(source,CONFIG)
    save(True);plan=preflight(source,CONFIG)
    assert plan['max_tracks']==8 and plan['launch_rho']==37.
    with pytest.raises(ValueError):preflight(source,dict(CONFIG,max_tracks=9))
    outcome.write_text('{}')
    with pytest.raises(ValueError,match='checksum'):preflight(source,CONFIG)


def test_cartesian_energy_matches_a_homogeneous_complex_scalar():
    from grteclyn_wrapper.optimisation.railgun.annular_transit import density_evaluator
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    from grteclyn_wrapper.optimisation.solver.device import configure_jax
    class Geometry:
        jax=configure_jax();xp=jax.numpy;fields=(ScalarField(winding=0),)
        def metric(self,x):return self.xp.diag(self.xp.array([-1.,1.,1.,1.]))
        def scalar(self,x,i):return .2*self.xp.array([self.xp.cos(.7*x[0]),self.xp.sin(.7*x[0])])
    geometry=Geometry();evaluate=density_evaluator(geometry)
    actual=np.asarray(evaluate(geometry.xp.array([[0.,37.,0.,10.],[1.,37.,0.,-10.]])))
    np.testing.assert_allclose(actual,(1+.7**2)*.2**2/(8*np.pi),atol=1e-16,rtol=1e-13)
