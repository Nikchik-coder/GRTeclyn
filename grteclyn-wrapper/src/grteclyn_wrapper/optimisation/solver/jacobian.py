"""Exact dense Jacobians of a jitted residual.

``dense_jacobian`` is what a problem class calls: jax.jacfwd of its
residual, or ``chunked_jacfwd`` in column blocks when WH_JAC_CHUNK > 0.
The block is required on the card (the unchunked jacfwd's intermediates
outgrow the 80 GB H100 on the large grids) and is the way the CPU reaches
them too (40 GB OOM at 108x28, 2026-10-27).  Default: 1024 columns on gpu,
unchunked on cpu.
"""

from __future__ import annotations

import os

__all__ = ["chunked_jacfwd", "dense_jacobian"]


def chunked_jacfwd(residual, n, chunk):
    """The dense square Jacobian of ``residual``, ``chunk`` columns at a time.

    jax.jacfwd pushes all n tangents through the residual graph at once,
    and those intermediates are what overflow the large grids (40 GB at
    108x28, 2026-10-27); lax.map over column blocks keeps only ``chunk``
    of them live.  Same values (one jvp per basis vector), one jit, no
    per-block retrace.  Extra positional arguments pass through to
    ``residual``, traced, like the jacfwd path.
    """
    import jax
    import jax.numpy as jnp

    n_blocks = -(-n // chunk)
    cols = jnp.arange(n_blocks * chunk).reshape(n_blocks, chunk)

    @jax.jit
    def jac(u, *args):
        def block(c):
            keep = (c < n).astype(u.dtype)
            basis = jnp.zeros((chunk, n), u.dtype).at[
                jnp.arange(chunk), jnp.minimum(c, n - 1)].set(keep)
            return jax.vmap(
                lambda v: jax.jvp(lambda uu: residual(uu, *args),
                                  (u,), (v,))[1])(basis)
        rows = jax.lax.map(block, cols)      # (n_blocks, chunk, n): J^T rows
        return rows.reshape(n_blocks * chunk, n)[:n].T

    return jac


def dense_jacobian(residual, n):
    """The jitted Jacobian of ``residual(u, *args)`` in u (n unknowns),
    built as WH_JAC_CHUNK and the platform say (module docstring)."""
    from .device import configure_jax

    jax = configure_jax()
    chunk = int(os.environ.get(
        "WH_JAC_CHUNK",
        "1024" if jax.devices()[0].platform == "gpu" else "0"))
    if chunk > 0:
        return chunked_jacfwd(residual, n, min(chunk, n))
    return jax.jit(jax.jacfwd(residual, argnums=0))
