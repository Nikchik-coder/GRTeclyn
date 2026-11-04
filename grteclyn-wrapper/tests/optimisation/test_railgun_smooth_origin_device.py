"""Trace the corrected boundary rows and their Jacobian on the chosen device."""
import os

import numpy as np

from grteclyn_wrapper.optimisation.railgun.model import ScalarField
from grteclyn_wrapper.optimisation.railgun.problem import RingProblem
from grteclyn_wrapper.optimisation.railgun.smooth_origin import SmoothOriginProblem


def test_origin_correction_excludes_irregular_modes_and_retains_interior_rows():
    fields = [ScalarField(winding=1,mass=1.,amplitude=.1,anchor_radius=1.)]
    options = dict(nx=8,ny=4,length=2.5,frequency_targets=[.9])
    corrected = SmoothOriginProblem(fields,**options)
    original = RingProblem(fields,**options)
    if os.environ.get('JAX_PLATFORMS') == 'cuda':
        assert all(d.platform == 'gpu' for d in corrected.jax.devices())
    arrays = {tag:np.zeros(corrected.shape) for tag in corrected.tags}
    arrays['N'][:] = .01*(1+corrected.s[:,None])
    arrays['f'][:] = .01*corrected.y[None,:]
    state = corrected.xp.asarray(corrected.pack(arrays,[.9]))
    new = np.asarray(corrected.residual(state))
    old = np.asarray(original.residual(state))
    for index,tag in enumerate(corrected.tags):
        start = index*corrected.n
        end = (index+1)*corrected.n-(corrected.ny+1)
        np.testing.assert_allclose(new[start:end],old[start:end],atol=1e-11,rtol=1e-11)
        if tag in ('N','f'):
            np.testing.assert_allclose(old[end:end+corrected.ny+1],0,atol=1e-14)
            assert np.max(abs(new[end:end+corrected.ny+1])) > .009
    matrix = np.asarray(corrected.jacobian(state))
    assert matrix.shape == (corrected.n_unknowns,corrected.n_unknowns)
    assert np.all(np.isfinite(matrix))
