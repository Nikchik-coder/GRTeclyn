"""A phase polish cannot reset the MPD or quadrature budget."""
import json
from pathlib import Path
import pytest
from grteclyn_stationary.railgun.axial_phase_polish import CONFIG,preflight


def test_only_the_two_failed_coarse_phase_controls_can_be_polished():
    root=Path(__file__).resolve().parents[3]
    args=(root/'results/railgun/studies/strong-axis-audit-initial',
          root/'results/railgun/studies/frequency-073-refined/accepted.npz',
          root/'results/railgun/studies/strong-profile-073')
    plan=preflight(*args,CONFIG)
    assert plan['max_new_quadratures']==2 and plan['cumulative_quadratures']==34
    assert plan['new_mpd_tracks']==0 and plan['new_mpd_points']==0
    for change in [dict(order=64),dict(max_new_quadratures=3),dict(timing_tol=1e-6)]:
        with pytest.raises(ValueError):preflight(*args,dict(CONFIG,**change))
