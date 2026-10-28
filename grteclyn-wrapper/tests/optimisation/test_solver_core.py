"""The solver core on a small nonlinear system, CPU only: column-block
Jacobians equal jax.jacfwd (a padded last block included), WH_JAC_CHUNK
changes no value, and Newton converges on the host path."""

from __future__ import annotations

import importlib.util

import numpy as np
import pytest

if importlib.util.find_spec("jax") is None:
    pytest.skip("jax is not installed (the spinning-solver extra)",
                allow_module_level=True)

from grteclyn_wrapper.optimisation.solver.device import configure_jax  # noqa: E402
from grteclyn_wrapper.optimisation.solver.jacobian import (  # noqa: E402
    chunked_jacfwd,
    dense_jacobian,
)
from grteclyn_wrapper.optimisation.solver.newton import newton  # noqa: E402

jax = configure_jax()
jnp = jax.numpy

N = 7
A = (4.0 * np.eye(N) + np.diag(np.ones(N - 1), 1)
     - 0.5 * np.diag(np.ones(N - 1), -1))


def _residual(u, a):
    """Nonlinear, with a traced extra argument like the problems' J."""
    return jnp.asarray(A) @ u + a * jnp.sin(u) + 0.1 * u**3 - 1.0


def _reference(u, a):
    return np.asarray(jax.jacfwd(_residual)(u, a))


@pytest.mark.parametrize("chunk", [1, 3, N])
def test_chunked_jacfwd_equals_jacfwd(chunk):
    u = jnp.linspace(-0.4, 0.7, N)
    got = np.asarray(chunked_jacfwd(_residual, N, chunk)(u, 0.3))
    np.testing.assert_allclose(got, _reference(u, 0.3), rtol=0, atol=1e-14)


@pytest.mark.parametrize("setting", ["0", "3"])
def test_jac_chunk_setting_changes_no_value(monkeypatch, setting):
    monkeypatch.setenv("WH_JAC_CHUNK", setting)
    u = jnp.linspace(-0.4, 0.7, N)
    got = np.asarray(dense_jacobian(_residual, N)(u, 0.3))
    np.testing.assert_allclose(got, _reference(u, 0.3), rtol=0, atol=1e-14)


def test_newton_converges_on_the_host():
    jac = dense_jacobian(_residual, N)
    u, info = newton(lambda v: _residual(v, 0.3), lambda v: jac(v, 0.3),
                     np.zeros(N), tol=1e-13)
    assert info["converged"], info
    assert isinstance(u, np.ndarray)
    assert float(np.max(np.abs(np.asarray(_residual(u, 0.3))))) < 1e-12
