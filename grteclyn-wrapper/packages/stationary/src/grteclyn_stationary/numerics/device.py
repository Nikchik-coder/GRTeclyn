"""Where the solver's jax runs: platform, precision, threads, card.

jax reads these switches when it first starts, so order matters: a script
calls ``select_device`` (from its --gpu / --jac-chunk flags) before it
builds a problem, and the problem constructor calls ``configure_jax``
before it traces anything.

- CPU by default: the cards are shared with live evolutions, and nothing
  starts on one without the go.  JAX_PLATFORMS=cuda, plus
  CUDA_VISIBLE_DEVICES to pick a free card, opts a run onto a GPU.
- float64 always.
- A modest XLA thread pool: the container advertises 128 CPUs but is
  quota-capped at 24, and XLA's default one-thread-per-CPU pool both
  busts a ulimit -v sandbox (pthread_create EAGAIN) and would throttle
  live runs.
"""

from __future__ import annotations

import os

__all__ = ["configure_jax", "select_device"]


def select_device(card: int | None = None,
                  jac_chunk: int | None = None) -> None:
    """Send the next jax start to CUDA card ``card`` (None: the CPU) and
    set the Jacobian's column block (jacobian.dense_jacobian).  Call before
    the first jax import."""
    if card is not None:
        os.environ["JAX_PLATFORMS"] = "cuda"
        os.environ["CUDA_VISIBLE_DEVICES"] = str(card)
        # take only what the solve uses on a shared card, and give it back
        # between solves.  2026-10-28: the default bfc pool (capped at 75 %
        # of the card, grow-only) fragments across a ladder's per-mass
        # solves -- at 180x36 (n = 32k) every m > 0 Jacobian died asking
        # for a contiguous 16.9 GiB the pool had but could not compact.
        os.environ.setdefault("XLA_PYTHON_CLIENT_ALLOCATOR", "cuda_async")
    if jac_chunk is not None:
        os.environ["WH_JAC_CHUNK"] = str(jac_chunk)


def configure_jax():
    """The jax module with the thread cap, the platform and float64 set."""
    os.environ.setdefault(
        "XLA_FLAGS",
        "--xla_cpu_multi_thread_eigen=false "
        "intra_op_parallelism_threads=8")

    import jax

    jax.config.update("jax_platforms",
                      os.environ.get("JAX_PLATFORMS", "cpu"))
    jax.config.update("jax_enable_x64", True)
    return jax
