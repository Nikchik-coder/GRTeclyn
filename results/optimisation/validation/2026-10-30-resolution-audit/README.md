# D30 resolution-check audit, 2026-10-30

These 12 records evaluate the original saved polynomial on four grids without
Newton steps or dense Jacobians. All five imposed equations, the two unused
constraints, spin conservation and boundary/pin rows are included. Times are
CPU evaluation times on four threads, not GPU solve times. `imposed_core` uses
the existing C >= 0.05 monitor region; `imposed_all` includes the compactified
far ends and is recorded separately. These are coordinate-weighted stationary
residuals, not the Cartesian evolution Hamiltonian/momentum norms.

For e0374, the largest core imposed residual is 5.99e-9 and both independent
constraints remain below 2.00e-9. Its bill changes by less than 2e-14 relatively.
The existing full re-solve instead raises E19 to 1.11e-4 and E_c to 4.70e-5.
The original minimum e0391 still misses the independent 1e-8 threshold under
interpolation (E19 reaches 3.03e-8); its bill being unchanged does not clear it.
The already cleared e0137 has comparable far-end residuals to the other seeds.

This supports inexpensive residual screening before expensive re-solving; it
neither establishes continuum convergence nor proves that e0374 is ready for
an evolution. The accepted workflow is screening each new CMA best, then
independently refining the finalist. Failed refinement leaves no validated
result and never triggers an evolution.

The e0374 and e0137 seeds are packed in the adjacent
`2026-10-30-alternatives/d30_audit/e0374_seed.npz` and
`2026-10-30-alternatives/d30/seed.npz`; e0391's original search NPZ is `e0391_seed.npz` in this directory. Its initial/refined diagnostics are in
`2026-10-30-d0-d30/d30/`. The reusable checker is
`python -m grteclyn_wrapper.optimisation.resolution <seed> --out <directory>`.
It uses 150x30, 180x36 and 210x42 for these seeds; the additional 174x35 row
in this audit samples a different angular grid.
