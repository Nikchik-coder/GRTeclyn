"""Offline physics of the spinning-wormhole simulations.

  backgrounds    stationary rotating Ellis-Bronnikov backgrounds written as
                 .spinbg tables, the one input format of
                 Examples/SpinningWormhole (static, slow-rotation O(J^2) and
                 the full numerical family)
  conventions    every sign and normalization (mu+-, J, D, v_e, gamma), in
                 one place
  spectral       Chebyshev-Lobatto collocation pieces and the radial maps
  equations      the CKK field equations as solver residuals, one source of
                 truth shared by numpy/jax and the sympy formulation lock
                 (scripts/analysis/spinning_wormhole/derive_xy_equations.py);
                 holds the collocation problem of the fast-spin solver
  newton         damped Newton with the exact jax Jacobian
  solution       the Solution container: save/load, spectral evaluation
  observables    identity gates (D2, E_c, J flux, Smarr) and throat numbers
  continuation   solve_point (O(J^2)-seeded solve of one background) and
                 run_family (continuation in J)
  adm            ADM mass and angular momentum of 3D data on coordinate
                 spheres, against the table's own metric

The fast-spin solver plan: research/spinningwormhole/SpinningSolver.md.
Run as ``python -m grteclyn_wrapper.analysis.spinning_wormhole.<module>``.
"""
