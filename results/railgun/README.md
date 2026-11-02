# Regular-centre scalar rings: validation data

**Stationary single-ring ergoregion validated (November 2).** CMA-ES found
it after five proposals on the unchanged canonical k=1, m=1 branch.
All original checks pass at 128x16 / 160x20 / 192x24. On the finest grid,
omega=0.655065086594, maximum shift/lapse=1.080970704 and maximum
**g_tt=+0.0150110091**. The positive sign agrees across all three grids;
minimum lapse=0.282624975. This is a stationary result, not a dynamical
stability result. Full checks, fields, optimiser history and execution
logs: [ergoregion-cma](studies/ergoregion-cma/); accepted source:
[accepted_ergoregion.npz](studies/ergoregion-cma/accepted_ergoregion.npz).
The earlier [initial reproduction](studies/ergoregion-amplitude-initial/)
and [amplitude continuation](studies/ergoregion-amplitude-r2/) remain
separate, with their original rejections and accepted intermediate ring.
No original run or numerical file was removed or rewritten.

Package layout: [figures/](figures/README.md) groups images into single rings,
two-ring setups, particles and evolution; `reports/` contains
regression reports and figure companion JSON/TSV; `studies/` contains complete
run archives. A study's diagnostic JSON stays beside its fields and checksums
so its acceptance evidence remains self-contained. Rejected studies remain
explicitly rejected. No archived numerical content was changed by packaging.

**Spatial guide to the omega=0.70 ring:** `figures/single-ring/ring070-physics.png`
(also vector SVG) is one equatorial spatial map with measurements attached
directly to the centre, ring wall and surrounding space. The central clock ticks 26.06 minutes
per distant hour; the slowest clock held at fixed coordinates ticks 22.18
minutes at equatorial radius 1.064. The lapse minimum is instead at radius
0.819, not at the origin. Angular dragging peaks at the origin; the drag ratio
peaks at radius 1.237. Both radii are coordinate measurements. No ergoregion
is found. Dense-map/extremum measurements and observer definitions are in
`reports/ring070-physics.json` and its profile TSV. Blue shows the matter;
bold inner/outer outlines mark half-peak energy density, with diffuse tails
extending beyond the outlines. Rebuild without a GPU:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_physics
```

**Separated-ring explanatory figures:**
[the rings, clocks and gap](figures/two-rings/multiring-separated-space.png),
and [the actual particle passage](figures/particles/multiring-particles-in-gap.png).
Each uses one spatial view with plain descriptions attached to locations.
Both have SVG versions beside the PNG. They use only the accepted separated
rings and saved paths; the overlapping configuration is excluded. Numeric
companions are in `reports/multiring-explanatory.json`. Rebuild with:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_multiring_experiments
```

**Verified maximisation restart, seed 272:**
[completed evidence](studies/ergoregion-max-r2-seed272/outcome.json) accepts
peak shift/lapse **5.231237832496** on 160x20 / 192x24 / 224x28. The search
finished normally at its verification budget; all fields, independent checks,
Newton histories and regression logs are retained with verified checksums.
This is a stationary result, with no dynamical stability or global maximum claim.

**Stronger-ring comparison:** [same-scale spatial comparison](figures/single-ring/ergoregion-comparison.png)
([SVG](figures/single-ring/ergoregion-comparison.svg)) shows the previous
accepted ring, the new accepted best and the rejected stronger trial.
Their equatorial peak dragging measures are 1.08, 3.72 and 5.21. **3.72 passed
all three resolutions; 5.21 failed the first-grid Newton acceptance check and
is rejected.** The image now shows these completed decisions. Blue shows relative matter
density; solid outlines mark half its peak and orange marks the equatorial
region where fixed positions are impossible. Purple clocks refer only to the
centre of the hole. All panels share one coordinate-distance scale.
The immutable 19:22 MSK figure-input snapshot, its completed-validation
companion `validated-comparison.json`, source hashes and label audit are in
`reports/ergoregion-comparison/`. Full acceptance and rejection evidence are
archived in `studies/ergoregion-max-validate271/` and `...validate272/`.
The accepted common-point dragging measure is 3.720789536602; all original
equation/flux and three-grid convergence gates pass. Dynamical stability
is untested. This was the best validated ring at the comparison's snapshot;
the continuing search has since accepted stronger rings
(see [current status](../../research/railgun/STATUS.md)).
Rebuild from the saved numeric profiles, without a GPU or cluster access:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_comparison \
  --snapshot results/railgun/reports/ergoregion-comparison/validated-comparison.json
```

The [physical-claims audit](reports/ergoregion-comparison/claims-audit.json)
checks this accepted 3.72 field directly. It confirms the ergoregion and local
negative-energy directions, rejects the faster-than-light and near-empty-halo
interpretations, and derives a conditional single-decay energy bound.
It does not integrate photon paths or perform an energy-extraction experiment.
Reproduce it on a CPU, without JAX or cluster access:

```bash
grteclyn-wrapper/.venv/bin/python research/railgun/audit_ring_claims.py
```

**November 2: three-grid full 3+1 convergence study complete.** The accepted
omega=0.70 ring was exported to 96^3 / 128^3 / 192^3 Cartesian grids and
evolved with RadialRecipe's canonical complex scalar through t=2. All finished;
all original frames are retained. Maximum charge drift is **0.068895% /
0.017787% / 0.0024917%**. At t=2 the finer pair's interior Ham/Mom orders
are **4.01 / 3.83**; the three-grid charge-change Richardson order is
**4.677** and matter-J order **4.269**, measured with unequal spacings.
These are short unperturbed runs; long-term stability remains untested.

The measured order table and continuum/error estimates are in
`reports/evolution-richardson-070.md` and `.json`. The estimates come from
one three-point asymptotic fit, not an independent error bound. Constraint
orders use the fixed r<8 interior; whole-box boundary-contaminated norms
remain in the archived diagnostics. Figure:
`figures/evolution/ring070-evolution-convergence.png` (also PDF). Rebuild with:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_convergence \
  results/railgun/studies/evolution-070-n96 \
  results/railgun/studies/evolution-070-n128 \
  results/railgun/studies/evolution-070-n192
```

Archives: `studies/evolution-070-n96/`, `studies/evolution-070-n128/`,
`studies/evolution-070-n192/`.
Summary: `reports/evolution-pilot-070.json`. Initial grid figures:
`figures/evolution/ring070-n96-initial.png`, `figures/evolution/ring070-n128-initial.png`.
Rebuild the time comparison from portable numerical slice/diagnostic inputs:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_evolution
```

The completed stationary/particle experiments pass every original acceptance gate:

- **Concentric gapped rings:** `studies/annular-validated-k12/`, k1=+1/k2=-12,
  three grids 192x16/224x18/256x20. Zero volume/infinity J agrees with finite
  Cartesian surface flux to about 1e-13. Clear component-wise 1e-6 gap
  33.29734 < rho < 40.90802; finite-height tube validated.
- **Particles between the rings:** `studies/annular-transit-k12/`, all eight
  matched-energy spin/reversal/two-tolerance tracks reach z=-10 while staying
  inside the tube. Worst relative component density 1.75e-7 and invariant drift
  4.11e-13. The +z minus -z coordinate transit split is 3.58739e-6.
- **Stronger-ring finite spin selection:** `studies/strong-uphill-073-validated/`,
  omega=0.73. At equal energy +z spin reaches the target and -z spin first
  turns back. All 656 full Cartesian MPD substitution checks pass; every
  nonmarginal saved finest track agrees with independent phase timing within
  5.29e-8. Two final phase-order checks agree within 4.52e-12. Original failed
  RK and coarse-quadrature studies remain unchanged and rejected.

Summary: `reports/completed-experiments.json`. Figures:
`figures/two-rings/annular-rings-validated.png`, `figures/particles/annular-transit-k12.png`,
`figures/particles/strong-uphill-073.png`. These demonstrate stationary fields and finite
passages/first turnarounds; no asymptotic escape, energy gain or stability claim.

Check the complete inventory and original study checksums:

```bash
grteclyn-wrapper/.venv/bin/python research/railgun/verify_pack.py
```

`figures/particles/uphill-transit.png` shows the verified finite uphill selection and
its small stopping-height difference. Rebuild it with:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_uphill \
  results/railgun/studies/uphill-transit --out results/railgun/figures/particles/uphill-transit.png
```

The November 1 spherical benchmark passes independent checks on 56x8, 72x10 and 96x12. A pure k=1 rotating ring also passes on 72x10, 96x12 and 128x16, with observable drift 3.52e-10. The latest full suite passed 63 GPU tests. These are stationary numerical solutions; 32 finite-radius through-ring particle tracks pass conservation and tolerance checks; dynamical stability remains untested.

- `figures/single-ring/scans/compactness-scan.png`: three independently accepted amplitude points; rejected points are excluded. Rebuild with `python -m grteclyn_wrapper.visualisation.optimisation.plot_compactness results/railgun/studies/compactness-scan --out results/railgun/figures/single-ring/scans/compactness-scan.png` using the wrapper environment.
- `figures/single-ring/scans/frequency-scan.png`: accepted fixed-frequency points; the measured amplitude at radius 5 falls as lapse decreases and dragging strengthens. Rebuild with the same `plot_compactness` command, using `studies/frequency-scan` and `figures/single-ring/scans/frequency-scan.png`.
- `figures/single-ring/scans/frequency-073-recovery.png`: independent constraints and off-grid Einstein/Klein–Gordon residuals across the original and three refined grids, with the unchanged acceptance limit.
- `figures/single-ring/strong-profile-073.png`: matter wall, lapse, dragging and signed magnetic tidal curvature on the certified omega=0.73 ring. `reports/strong-profile-comparison.json` compares the saved weak and strong profiles: peak instantaneous Eulerian linear force per unit spin rises by 78.30, which is not a moving-particle timing ratio.
- `figures/single-ring/scans/single-ring-frequency-sequence.png`: six accepted frequencies through 0.70; |J| turns over while local shift/lapse grows. Rejected 0.67 is excluded; no sampled ergoregion.
- `studies/strong-uphill-073-precision/`: two tighter controls at rtol=2e-13 pass conservation and preserve classification, but timing changes 1.88654e-7 / 2.03222e-7 still exceed 1e-7. Rejected, all 32 originals retained under original/; 34 cumulative tracks, no accepted strong-ring timing or selection claim.
- `studies/strong-uphill-073-initial/`: all 32 tracks complete, conservation/classification/reversal checks pass; study rejected by two timing differences above the unchanged 1e-7 gate. Originals retained unchanged; the separate two-track audit also remains rejected.
- `studies/annular-quintic-k12/`: first 192x16 solve converges and passes all original field/flux/gap/channel checks, but the added infinity angular equation fails (relative residual 80.58). Rejected; no later grids or off-axis particles.
- `reports/gpu_precision_regression.json` and `reports/gpu_quintic_regression.json`: 18 and 34 passing targeted GPU checks, including float64 placement, exact leading momentum modes and manufactured quintic fields.
- `studies/annular-falloff-k12-cubic/`: first cubic-falloff solve passes original finite-radius flux/field/gap/channel tests but fails the added literal-infinity coefficient test. This rejected study exports no accepted field; the separate regular-cubic recovery above passes.
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
- `figures/two-rings/provisional/annular-rings-provisional.png`: actual passing 224x18 candidate at its true coordinate scale, labelled provisional because the full study was rejected.
- `studies/annular-recovery-k12/`: coupled k1=1/k2=-12, total-J=0 recovery on 192x16 / 224x18 / 256x20. All Newton solves converged and retained a 1e-6 gap of width 7.61068 with a sampled finite-height channel. **Study rejected:** finest-grid independent angular-momentum flux mismatch 1.33955e-8 exceeds 1e-8. No accepted background or particle passage; all fields and diagnostics retained.
- `reports/gpu_annular_regression.json`: 22 passing GPU checks, including promotion from the linear seed to the total-J border and per-component cylindrical densities against independent Cartesian AD.
- `studies/annular-gap-screen/`: eight GPU linear bound-mode tests on the fixed accepted inner ring. k2=-12 and -16 pass the 1e-6 matter-gap screen on both grids, with widths 7.8630 and 57.6105. These seeds are **not self-consistent two-field spacetimes**; nonlinear backreaction and particle passage remain to validate.
- `studies/counter-rotation/`: accepted k1=+1/k2=-2, zero-total-J state on 72x10 / 96x12 / 128x16. M_ADM=1.132946199392, J1=-0.773443320071468, J2=+0.773443320071473. Nonzero interior dragging max |w|=0.00225517; coordinate octupole tail approaches r^-5. Twelve Newton solves, no splits; all independent gates unchanged. **The fields overlap and fail the separate annular-gap objective.**
- `figures/two-rings/overlapping/two-rings.png` and `figures/two-rings/overlapping/two-rings-density.png`: actual overlapping baseline surfaces and equatorial energy densities; companion data in `reports/two-rings-density.json` and `.tsv`. The 1e-6 edge criterion fails: inner-component outer radius about 29.88 exceeds outer-component inner radius about 0.010. Peak separation alone is insufficient.
- `figures/two-rings/overlapping/counter-dragging.png`: nonzero interior dragging and the measured exterior coordinate octupole tail.
- `studies/ring-transit/`: 32 accepted TD-MPD through-centre tracks, matched energy, spin reversal, two RK tolerances and 1e-9 conservation gates. Worst relative drift 1.90e-13. Fast transit timing split -0.000581712663 for spin +z minus -z. All near-E=1 tracks transmitted; no valve or asymptotic escape result.
- `studies/ring-profile/`: accepted Cartesian core certificate and signed z=-15..15 curvature/matter profiles. Equatorial density peak rho=6.25 on a 0.05-spaced sample; no sampled ergoregion. The scalar vanishes on the axis, while its transverse gradients carry finite energy. Eleven targeted GPU tests passed. `figures/single-ring/ring-profile.png` plots the saved measurements.
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
  results/railgun/studies/ring-validated/accepted.npz --out results/railgun/figures/single-ring/ring-validated.png
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring \
  results/railgun/studies/ring-validated/accepted.npz --3d --out results/railgun/figures/single-ring/ring-validated-3d.png
```

The 3D surface revolves the computed contour at 50% of the peak scalar
amplitude squared; it is not an idealised torus or a sharp matter boundary.

Rebuild the interior/axial profile figure:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_profile \
  results/railgun/studies/ring-profile --out results/railgun/figures/single-ring/ring-profile.png
```

Rebuild the overlapping two-field baseline and its gap diagnostic:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_two_rings \
  results/railgun/studies/counter-rotation/accepted.npz --out results/railgun/figures/two-rings/overlapping/two-rings.png \
  --density-out results/railgun/figures/two-rings/overlapping/two-rings-density.png \
  --density-data-dir results/railgun/reports --extent 18
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_counter_dragging \
  results/railgun/studies/counter-rotation --out results/railgun/figures/two-rings/overlapping/counter-dragging.png
```

The concentric **target** schematic `research/railgun/annular-gap-target.png`
has a positive annular channel. It is a design diagram, not a solved field.

`reports/gpu_gap_regression.json`: nine passing gap/density/GPU-eigensolver checks. The initial fixture failure is preserved in `reports/gpu_gap_regression_initial.json`; no physical threshold changed.

Rebuild the fixed-frequency resolution diagnostic:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_recovery \
  results/railgun/studies/frequency-scan/frequency_05/grid_72x10.json \
  results/railgun/studies/frequency-073-refined \
  --out results/railgun/figures/single-ring/scans/frequency-073-recovery.png
```

Rebuild the strong profile and accepted frequency sequence:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_ring_profile \
  results/railgun/studies/strong-profile-073 --out results/railgun/figures/single-ring/strong-profile-073.png \
  --title 'ω=0.73 single ring: matter wall and certified axial profile'
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_frequency_sequence \
  results/railgun --out results/railgun/figures/single-ring/scans/single-ring-frequency-sequence.png
```


Rebuild the newly accepted figures with the wrapper environment:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_annular_rings \
  results/railgun/studies/annular-validated-k12 --out results/railgun/figures/two-rings/annular-rings-validated.png
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_annular_transit \
  results/railgun/studies/annular-transit-k12 --out results/railgun/figures/particles/annular-transit-k12.png
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_uphill \
  results/railgun/studies/strong-uphill-073-validated --out results/railgun/figures/particles/strong-uphill-073.png \
  --title 'Stronger ring (ω=0.73): validated finite spin selection'
```
