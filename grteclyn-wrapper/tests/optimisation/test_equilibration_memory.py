"""Row scaling must preserve the Newton system and reuse its large buffer."""
import importlib

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.solver.device import configure_jax
from grteclyn_wrapper.optimisation.solver.jacobian import chunked_jacfwd
from grteclyn_wrapper.optimisation.solver.newton import _donating_equilibrator

jax=configure_jax()
jnp=jax.numpy


@pytest.mark.parametrize('transposed',[False,True])
def test_scaling_matches_reference_and_aliases_matrix(transposed):
    rng=np.random.default_rng(17)
    matrix=rng.normal(size=(19,19))
    matrix[0]=0.
    matrix[1]*=1e-100
    if transposed: matrix=matrix.T.copy()
    expected_scale=1/np.maximum(np.max(abs(matrix),axis=1),1e-300)
    inp=jnp.array(matrix)
    operation=_donating_equilibrator()
    allocation=operation.lower(inp).compile().memory_analysis()
    assert allocation.alias_size_in_bytes>=matrix.nbytes
    scaled,scale=operation(inp)
    np.testing.assert_allclose(scale,expected_scale,rtol=3e-15)
    np.testing.assert_allclose(scaled,matrix*expected_scale[:,None],rtol=3e-15,atol=1e-15)


def test_column_jacobian_scaling_has_no_matrix_sized_temporary():
    # Include the overlapping final column block of the production producer.
    n=193
    vector=jnp.linspace(-1,1,n)
    jacobian=chunked_jacfwd(lambda x:3*x+jnp.sin(x)+jnp.mean(x),n,32)(vector)
    expected=np.asarray(jacobian).copy()
    scale=1/np.max(abs(expected),axis=1)
    operation=_donating_equilibrator()
    allocation=operation.lower(jacobian).compile().memory_analysis()
    assert allocation.alias_size_in_bytes>=expected.nbytes
    assert allocation.temp_size_in_bytes<expected.nbytes
    actual,actual_scale=operation(jacobian)
    np.testing.assert_allclose(actual,expected*scale[:,None],rtol=3e-15,atol=1e-15)
    np.testing.assert_allclose(actual_scale,scale,rtol=3e-15)


def test_jacobian_assembly_does_not_materialise_full_matrix_temporaries():
    n=1025
    vector=jnp.linspace(-1,1,n)
    def residual(x):
        return 3*x+jnp.sin(x)+jnp.mean(x)+.2*jnp.roll(x,1)
    operation=chunked_jacfwd(residual,n,32).lower(vector).compile()
    allocation=operation.memory_analysis()
    # The old map/slice/transpose path needs extra full-matrix buffers.
    assert allocation.temp_size_in_bytes < n*n*8
    actual=np.asarray(operation(vector))
    expected=np.diag(3+np.cos(np.asarray(vector)))+np.ones((n,n))/n
    expected[np.arange(n),(np.arange(n)-1)%n]+=.2
    np.testing.assert_allclose(actual,expected,rtol=3e-15,atol=1e-15)


def test_donated_scaling_preserves_accelerated_newton_solution(monkeypatch):
    module=importlib.import_module('grteclyn_wrapper.optimisation.solver.newton')
    from jax.scipy.linalg import lu_factor,lu_solve
    # Exercise the accelerated branch on CPU as well as CUDA startup tests.
    monkeypatch.setattr(module,'_cuda_backend',lambda matrix:(
        jnp,jax.jit(lu_factor,donate_argnums=(0,)),lu_solve,_donating_equilibrator()))
    matrix=jnp.asarray([[4.,1.,0.],[0.,3.,-.5],[.2,0.,2.]])
    def residual(x): return matrix@x+.2*jnp.sin(x)-1.
    solution,info=module.newton(residual,chunked_jacfwd(residual,3,2),np.zeros(3),tol=1e-13)
    assert info['converged'] and info['jacobian_evals']>=1
    assert np.max(abs(np.asarray(residual(solution))))<1e-12
