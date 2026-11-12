"""The solver core: physics-free numerics, numpy / scipy / jax only.

  newton     damped Newton: equilibrated dense LU, Armijo backtracking,
             chord steps; on the host (scipy) or, when the Jacobian
             arrives on a CUDA card, the whole solve on the card
  jacobian   exact dense Jacobians of a jitted residual: jax.jacfwd or
             chunked_jacfwd in column blocks (WH_JAC_CHUNK)
  device     where jax runs: CPU by default, a CUDA card on request,
             float64, the XLA thread cap
  spectral   Chebyshev grids, differentiation, interpolation and radial maps

Nothing here imports another wrapper subsystem, so the folder can be lifted out
whole (tests/stationary/test_layout.py).  Importing it starts no jax.
"""
