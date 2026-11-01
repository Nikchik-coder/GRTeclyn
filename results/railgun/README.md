# Regular-centre scalar rings: validation data

The November 1 spherical benchmark passes independent checks on 56x8, 72x10 and 96x12. A pure k=1 rotating ring also passes on 72x10, 96x12 and 128x16, with observable drift 3.52e-10. The latest full suite passed 63 GPU tests. These are stationary numerical solutions; 32 finite-radius through-ring particle tracks pass conservation and tolerance checks; dynamical stability remains untested.

- `spherical-initial/`: rejected 40x6 pilot.
- `spherical-diagnostic/`: 40x6/56x8/72x10 diagnostic recovery; study rejected.
- `spherical-validated/`: accepted three-grid background, independent areal-radius ODE reference, configuration, diagnostics and checksums.
- `spherical-to-ring-first/`: unresolved first homotopy, 15 solves and six bisections; preserves all attempted fields and the original coefficient-fit rejection. The separate surface-flux diagnosis is included.
- `spherical-to-ring-resumed/`: corrected-flux continuation; midpoint passes, 62.5% fails independent KG and surface-J checks on 56x8. Cumulative 17 solves/six bisections; no accepted pure ring.
- `ring-validated/`: accepted pure k=1 fields on three grids, full diagnostics/manifests, and the successful refined continuation. M_ADM=0.971450813143, J=-0.992014330336, scalar frequency 0.932692332164 in m=1 units. Density peaks near cylindrical radius 6.16 in the equatorial plane.
- `ring-transit/`: 32 accepted TD-MPD through-centre tracks, matched energy, spin reversal, two RK tolerances and 1e-9 conservation gates. Worst relative drift 1.90e-13. Fast transit timing split -0.000581712663 for spin +z minus -z. All near-E=1 tracks transmitted; no valve or asymptotic escape result.
- `ring-profile/`: accepted Cartesian core certificate and signed z=-15..15 curvature/matter profiles. Equatorial density peak rho=6.25 on a 0.05-spaced sample; no sampled ergoregion. The scalar vanishes on the axis, while its transverse gradients carry finite energy. Eleven targeted GPU tests passed. `ring-profile.png` plots the saved measurements.
- `gpu_regression.json`: portable GPU test report.
- `gpu_guards_regression.json`: 51-test extended GPU suite, including intrinsic KG, integer-winding seeding and flat through-origin MPD.
- `gpu_baseline_regression.json`: two GPU checks on the accepted spherical fixture; intrinsic KG, Cartesian core certification and a bound k=1 seed pass. No nonlinear homotopy or physical transport was run.
- `gpu_flux_regression.json`: six targeted CUDA checks of exact angular-momentum flux, baseline compatibility and preserved resume budgets.
- `gpu_refinement_regression.json`: full 63-test CUDA suite; includes independent Cartesian verification of endpoint ADM mass and confirms the failed ring remains rejected after measurement corrections.

Implementation and numerical contract: `research/railgun/EQUATIONS.md`. Current work: `research/railgun/STATUS.md`.

Rebuild the meridional scalar-amplitude/frame-dragging figure from this archive:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring \
  results/railgun/ring-validated/accepted.npz --out results/railgun/ring-validated.png
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring \
  results/railgun/ring-validated/accepted.npz --3d --out results/railgun/ring-validated-3d.png
```

The 3D surface revolves the computed contour at 50% of the peak scalar
amplitude squared; it is not an idealised torus or a sharp matter boundary.

Rebuild the interior/axial profile figure:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_profile \
  results/railgun/ring-profile --out results/railgun/ring-profile.png
```
