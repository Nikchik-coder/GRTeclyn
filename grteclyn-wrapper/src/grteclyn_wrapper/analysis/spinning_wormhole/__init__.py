"""The spinning-wormhole campaign's offline physics.

  backgrounds    stationary rotating Ellis-Bronnikov backgrounds written as
                 .spinbg tables, the one input format of
                 Examples/SpinningWormhole (static and slow-rotation O(J^2)
                 now; the full numerical family arrives through the same file)
  conventions    every sign and normalization (mu+-, J, D, v_e, gamma), in
                 one place
  spectral       Chebyshev-Lobatto collocation pieces and the radial maps
  equations      the CKK field equations as solver residuals, one source of
                 truth shared by numpy/jax and the sympy formulation lock
                 (scripts/analysis/spinning_wormhole/derive_xy_equations.py)

The fast-spin solver plan: research/spinningwormhole/SpinningSolver.md.
Run as ``python -m grteclyn_wrapper.analysis.spinning_wormhole.<module>``.
"""
