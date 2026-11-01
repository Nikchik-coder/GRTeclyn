"""Targeted precision retries cannot expand the track budget or change gates."""
from pathlib import Path
import json
import pytest
from grteclyn_wrapper.optimisation.railgun.uphill_precision import preflight


def test_two_failed_controls_are_the_only_eligible_tighter_integrations():
    root=Path(__file__).resolve().parents[3]
    cfg=json.loads((root/'research/railgun/studies/uphill_precision_073.json').read_text())
    args=[root/'results/railgun/studies/strong-uphill-073-initial',
          root/'results/railgun/studies/frequency-073-refined/accepted.npz',
          root/'results/railgun/studies/strong-profile-073']
    plan=preflight(*args,cfg)
    assert plan['max_new_tracks']==2 and plan['cumulative_tracks']==34
    for key,value in [('max_new_tracks',3),('timing_tol',1e-6),('rtol',2e-12)]:
        changed=dict(cfg,**{key:value})
        with pytest.raises(ValueError):preflight(*args,changed)
