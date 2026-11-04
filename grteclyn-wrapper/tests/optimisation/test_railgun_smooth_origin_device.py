"""Trace the corrected boundary rows and their Jacobian on the chosen device."""
import os

import numpy as np
import pytest

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


@pytest.mark.parametrize('ny',[28,32,36])
def test_fixed_lapse_has_exact_zero_residual_for_equal_centre_values(ny):
    fields = [ScalarField(winding=1,mass=1.,amplitude=.1,anchor_radius=1.)]
    problem = SmoothOriginProblem(fields,nx=8,ny=ny,length=2.5,
                                 central_lapse=.12993066385192364)
    xp = problem.xp
    arrays = {tag:xp.zeros(problem.shape) for tag in problem.tags}
    target = 2*xp.log(problem.central_lapse)
    arrays['f'] = xp.full(problem.shape,target)
    state = xp.concatenate([arrays[tag].ravel() for tag in problem.tags]+[xp.array([.9])])
    residual = np.asarray(problem.residual(state))
    assert residual[-1] == 0.
    np.testing.assert_array_equal(residual[problem.n-ny-1:problem.n],0.)


def test_jitted_border_resolves_one_ulp_offsets_without_a_rounding_floor():
    from grteclyn_wrapper.optimisation.solver.device import configure_jax
    jax = configure_jax()
    xp = jax.numpy
    target = float(2*xp.log(.12993066385192364))
    stable = jax.jit(lambda values: xp.mean(values-target))
    derivative = jax.jit(jax.jacfwd(stable))
    for n in (29,33,37):
        for value in (target,np.nextafter(target,np.inf),np.nextafter(target,-np.inf)):
            values = xp.full(n,value)
            assert float(stable(values)) == value-target
            np.testing.assert_allclose(derivative(values),np.full(n,1/n),rtol=1e-15)
