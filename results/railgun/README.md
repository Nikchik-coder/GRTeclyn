# Regular-centre scalar rings: validation data

The November 1 spherical benchmark passes independent checks on 56x8, 72x10 and 96x12. The extended suite passed 51 GPU tests, followed by two checks against the saved spherical star. This validates the spherical numerical baseline and implementation safeguards, not a rotating ring or dynamical stability.

- `spherical-initial/`: rejected 40x6 pilot.
- `spherical-diagnostic/`: 40x6/56x8/72x10 diagnostic recovery; study rejected.
- `spherical-validated/`: accepted three-grid background, independent areal-radius ODE reference, configuration, diagnostics and checksums.
- `gpu_regression.json`: portable GPU test report.
- `gpu_guards_regression.json`: 51-test extended GPU suite, including intrinsic KG, integer-winding seeding and flat through-origin MPD.
- `gpu_baseline_regression.json`: two GPU checks on the accepted spherical fixture; intrinsic KG, Cartesian core certification and a bound k=1 seed pass. No nonlinear homotopy or physical transport was run.

Implementation and numerical contract: `research/railgun/EQUATIONS.md`. Current work: `research/railgun/STATUS.md`.
