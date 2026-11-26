"""Stationary rotating Ellis--Bronnikov backgrounds and their observables.

  backgrounds    stationary rotating Ellis-Bronnikov backgrounds written as
                 .spinbg tables, the one input format of
                 Examples/SpinningWormhole (static, slow-rotation O(J^2) and
                 the full numerical family)
  conventions    every sign and normalization (mu+-, J, D, v_e, gamma), in
                 one place
  equations      the CKK field equations as solver residuals, one source of
                 truth shared by numpy/jax and the sympy formulation lock
                 (scripts/analysis/spinning_wormhole/derive_xy_equations.py);
                 holds the collocation problem of the fast-spin solver
  solution       the Solution container: save/load, spectral evaluation
  observables    identity gates (D2, E_c, J flux, Smarr) and throat numbers
  continuation   solve_point (O(J^2)-seeded solve of one background) and
                 run_family (continuation in J)
  adm            ADM mass and angular momentum of 3D data on coordinate
                 spheres, against the table's own metric

Shared grids, maps, Jacobians and Newton iteration live in
grteclyn_stationary.numerics. The fast-spin solver plan is
research/spinningwormhole/SpinningSolver.md.
Run as ``python -m grteclyn_stationary.spinning_wormhole.<module>``.
"""
