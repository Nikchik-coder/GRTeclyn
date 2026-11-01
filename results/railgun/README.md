# Regular-centre scalar rings: validation data

Package layout: `figures/` contains rendered images; `reports/` contains
regression reports and figure companion JSON/TSV; `studies/` contains complete
run archives. A study's diagnostic JSON stays beside its fields and checksums
so its acceptance evidence remains self-contained. Rejected studies remain
explicitly rejected. No archived numerical content was changed by packaging.

Check the complete inventory and original study checksums:

```bash
grteclyn-wrapper/.venv/bin/python research/railgun/verify_pack.py
```

`figures/uphill-transit.png` shows the verified finite uphill selection and
its small stopping-height difference. Rebuild it with:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_uphill \
  results/railgun/studies/uphill-transit --out results/railgun/figures/uphill-transit.png
```

The November 1 spherical benchmark passes independent checks on 56x8, 72x10 and 96x12. A pure k=1 rotating ring also passes on 72x10, 96x12 and 128x16, with observable drift 3.52e-10. The latest full suite passed 63 GPU tests. These are stationary numerical solutions; 32 finite-radius through-ring particle tracks pass conservation and tolerance checks; dynamical stability remains untested.

- `figures/compactness-scan.png`: three independently accepted amplitude points; rejected points are excluded. Rebuild with `python -m grteclyn_wrapper.visualisation.optimisation.plot_compactness results/railgun/studies/compactness-scan --out results/railgun/figures/compactness-scan.png` using the wrapper environment.
- `figures/frequency-scan.png`: accepted fixed-frequency points; the measured amplitude at radius 5 falls as lapse decreases and dragging strengthens. Rebuild with the same `plot_compactness` command, using `studies/frequency-scan` and `figures/frequency-scan.png`.
- `figures/frequency-073-recovery.png`: independent constraints and off-grid Einstein/Klein–Gordon residuals across the original and three refined grids, with the unchanged acceptance limit.
- `figures/strong-profile-073.png`: matter wall, lapse, dragging and signed magnetic tidal curvature on the certified omega=0.73 ring. `reports/strong-profile-comparison.json` compares the saved weak and strong profiles: peak instantaneous Eulerian linear force per unit spin rises by 78.30, which is not a moving-particle timing ratio.
- `figures/single-ring-frequency-sequence.png`: six accepted frequencies through 0.70; |J| turns over while local shift/lapse grows. Rejected 0.67 is excluded; no sampled ergoregion.
- `studies/branch-seeds/`: all six GPU bound-mode problems passed for new k=2,m=2.5/3 even fields and a k=1,m=1 odd field on two grids. Resolved fixed-background homotopy starts only, all validated=false; nonlinear pure-branch recovery and outer -6/-8 seeding remain pending.
- `studies/strong-profile-073/`: accepted Cartesian core and full signed-axis/equatorial profile for omega=0.73, radius 0.4, degrees 6/8; exact source SHA and all diagnostics retained. Particle results are a separate study.
- `studies/frequency-deep/`: omega=0.70 passes all three refined grids; omega=0.67 fails Newton and independent equations on the first grid. Four solves, unchanged gates; no physical maximum established.
- `studies/frequency-073-refined/`: omega=0.73 passes 96x12 / 128x16 / 160x20. The old coarse constraint failure clears under refinement; all gates unchanged. Final sampled lapse minimum 0.49280, maximum shift/lapse 0.35421, J=-1.35717; no sampled ergoregion. Three solves, observable drift 1.16e-9. Original rejection retained separately.
- `studies/frequency-scan/`: four fixed frequencies 0.85 / 0.82 / 0.79 / 0.76 pass all three grids. Last accepted lapse minimum 0.55818, shift/lapse maximum 0.25191, J=-1.37946, no sampled ergoregion. At 0.73 the coarsest grid fails the independent constraint_c (3.25e-8 > 1e-8); scan stopped after 13 solves, later frequencies unattempted. This is not a physical maximum.
- `studies/compactness-scan/`: three amplitude points 0.06 / 0.075 / 0.095 pass three-grid validation. The 0.12 step fails Newton and is retained rejected; later pins were not attempted. Last accepted frequency 0.874052056468, lapse minimum 0.78022, shift/lapse maximum 0.06179; no sampled ergoregion. Ten solves total. This stopped scan does not establish a maximum spin or compactness.
- `studies/uphill-transit/`: accepted 32-track finite uphill experiment, z=+1 to z=-10. At equal E=0.9255355443835863, +z spin reaches the target and -z spin turns at z=-9.999772414807428; zero spin reaches the target. Two RK tolerances and background/spin reversal pass; worst normalised conservation drift 1.08e-14, nonmarginal RK timing change 6.68e-10. Four missed raw destination events were corrected with independent first-crossing interpolation and terminal invariants. `original/` retains all raw data; zero extra ring tracks were integrated. This is finite endpoint selection, not escape or long-term trapping.
- `reports/gpu_falloff_regression.json`: 25 passing GPU checks, including cubic polynomial projection, analytic finite-sphere flux, independent Cartesian AD, explicit state format, omitted PDE visibility and existing annular acceptance guards.
- `reports/gpu_strong_regression.json`: 21 passing GPU tests for frequency budgets/recovery, matched-energy uphill controls, exact-threshold timing exclusion, TD-MPD transport, Cartesian core/profile and CUDA float64 placement.
- `reports/gpu_frequency_regression.json`: 31 passing CUDA checks, including fixed-frequency recovery of the accepted rotating star, portable state metadata, nonvacuum/nodeless branch guards and existing model/diagnostics.
- `reports/gpu_event_regression.json`: five passing GPU checks, including exact Rindler crossing time, full conserved energy, repaired dense event ordering and CUDA float64 placement.
- `reports/gpu_uphill_regression.json`: 37 passing GPU checks, including analytic Rindler turnaround, flat transmission, odd-parity gradient energy, existing transport and CUDA float64 placement.
- `studies/spherical-initial/`: rejected 40x6 pilot.
- `studies/spherical-diagnostic/`: 40x6/56x8/72x10 diagnostic recovery; study rejected.
- `studies/spherical-validated/`: accepted three-grid background, independent areal-radius ODE reference, configuration, diagnostics and checksums.
- `studies/spherical-to-ring-first/`: unresolved first homotopy, 15 solves and six bisections; preserves all attempted fields and the original coefficient-fit rejection. The separate surface-flux diagnosis is included.
- `studies/spherical-to-ring-resumed/`: corrected-flux continuation; midpoint passes, 62.5% fails independent KG and surface-J checks on 56x8. Cumulative 17 solves/six bisections; no accepted pure ring.
- `studies/ring-validated/`: accepted pure k=1 fields on three grids, full diagnostics/manifests, and the successful refined continuation. M_ADM=0.971450813143, J=-0.992014330336, scalar frequency 0.932692332164 in m=1 units. Density peaks near cylindrical radius 6.16 in the equatorial plane.
- `studies/annular-correction-k12/`: the separately approved fourth solve, two further updates on the saved 256x20 state. The gap remains, but flux mismatch 1.36332e-8 still fails the unchanged 1e-8 gate. No accepted state is exported. The two reused passing-grid records refer to `studies/annular-recovery-k12/`.
- `reports/gpu_annular_correction_regression.json`: 24 passing CUDA checks, including immutable prior-archive checksums and the cumulative four-solve cap.
- `figures/annular-rings-provisional.png`: actual passing 224x18 candidate at its true coordinate scale, labelled provisional because the full study was rejected.
- `studies/annular-recovery-k12/`: coupled k1=1/k2=-12, total-J=0 recovery on 192x16 / 224x18 / 256x20. All Newton solves converged and retained a 1e-6 gap of width 7.61068 with a sampled finite-height channel. **Study rejected:** finest-grid independent angular-momentum flux mismatch 1.33955e-8 exceeds 1e-8. No accepted background or particle passage; all fields and diagnostics retained.
- `reports/gpu_annular_regression.json`: 22 passing GPU checks, including promotion from the linear seed to the total-J border and per-component cylindrical densities against independent Cartesian AD.
- `studies/annular-gap-screen/`: eight GPU linear bound-mode tests on the fixed accepted inner ring. k2=-12 and -16 pass the 1e-6 matter-gap screen on both grids, with widths 7.8630 and 57.6105. These seeds are **not self-consistent two-field spacetimes**; nonlinear backreaction and particle passage remain to validate.
- `studies/counter-rotation/`: accepted k1=+1/k2=-2, zero-total-J state on 72x10 / 96x12 / 128x16. M_ADM=1.132946199392, J1=-0.773443320071468, J2=+0.773443320071473. Nonzero interior dragging max |w|=0.00225517; coordinate octupole tail approaches r^-5. Twelve Newton solves, no splits; all independent gates unchanged. **The fields overlap and fail the separate annular-gap objective.**
- `figures/two-rings.png` and `figures/two-rings-density.png`: actual overlapping baseline surfaces and equatorial energy densities; companion data in `reports/two-rings-density.json` and `.tsv`. The 1e-6 edge criterion fails: inner-component outer radius about 29.88 exceeds outer-component inner radius about 0.010. Peak separation alone is insufficient.
- `figures/counter-dragging.png`: nonzero interior dragging and the measured exterior coordinate octupole tail.
- `studies/ring-transit/`: 32 accepted TD-MPD through-centre tracks, matched energy, spin reversal, two RK tolerances and 1e-9 conservation gates. Worst relative drift 1.90e-13. Fast transit timing split -0.000581712663 for spin +z minus -z. All near-E=1 tracks transmitted; no valve or asymptotic escape result.
- `studies/ring-profile/`: accepted Cartesian core certificate and signed z=-15..15 curvature/matter profiles. Equatorial density peak rho=6.25 on a 0.05-spaced sample; no sampled ergoregion. The scalar vanishes on the axis, while its transverse gradients carry finite energy. Eleven targeted GPU tests passed. `figures/ring-profile.png` plots the saved measurements.
- `reports/gpu_regression.json`: portable GPU test report.
- `reports/gpu_guards_regression.json`: 51-test extended GPU suite, including intrinsic KG, integer-winding seeding and flat through-origin MPD.
- `reports/gpu_baseline_regression.json`: two GPU checks on the accepted spherical fixture; intrinsic KG, Cartesian core certification and a bound k=1 seed pass. No nonlinear homotopy or physical transport was run.
- `reports/gpu_flux_regression.json`: six targeted CUDA checks of exact angular-momentum flux, baseline compatibility and preserved resume budgets.
- `reports/gpu_refinement_regression.json`: full 63-test CUDA suite; includes independent Cartesian verification of endpoint ADM mass and confirms the failed ring remains rejected after measurement corrections.
- `reports/gpu_offaxis_regression.json`: four passing GPU checks including an exact off-axis flat-space crossing and dense signed exit events. This is not a physical between-ring transit.

Implementation and numerical contract: `research/railgun/EQUATIONS.md`. Current work: `research/railgun/STATUS.md`.

Rebuild the meridional scalar-amplitude/frame-dragging figure from this archive:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring \
  results/railgun/studies/ring-validated/accepted.npz --out results/railgun/figures/ring-validated.png
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring \
  results/railgun/studies/ring-validated/accepted.npz --3d --out results/railgun/figures/ring-validated-3d.png
```

The 3D surface revolves the computed contour at 50% of the peak scalar
amplitude squared; it is not an idealised torus or a sharp matter boundary.

Rebuild the interior/axial profile figure:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_profile \
  results/railgun/studies/ring-profile --out results/railgun/figures/ring-profile.png
```

Rebuild the overlapping two-field baseline and its gap diagnostic:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_two_rings \
  results/railgun/studies/counter-rotation/accepted.npz --out results/railgun/figures/two-rings.png \
  --density-out results/railgun/figures/two-rings-density.png \
  --density-data-dir results/railgun/reports --extent 18
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_counter_dragging \
  results/railgun/studies/counter-rotation --out results/railgun/figures/counter-dragging.png
```

The concentric **target** schematic `research/railgun/annular-gap-target.png`
has a positive annular channel. It is a design diagram, not a solved field.

`reports/gpu_gap_regression.json`: nine passing gap/density/GPU-eigensolver checks. The initial fixture failure is preserved in `reports/gpu_gap_regression_initial.json`; no physical threshold changed.

Rebuild the fixed-frequency resolution diagnostic:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_recovery \
  results/railgun/studies/frequency-scan/frequency_05/grid_72x10.json \
  results/railgun/studies/frequency-073-refined \
  --out results/railgun/figures/frequency-073-recovery.png
```

Rebuild the strong profile and accepted frequency sequence:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_profile \
  results/railgun/studies/strong-profile-073 --out results/railgun/figures/strong-profile-073.png \
  --title 'ω=0.73 single ring: matter wall and certified axial profile'
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_frequency_sequence \
  results/railgun --out results/railgun/figures/single-ring-frequency-sequence.png
```
