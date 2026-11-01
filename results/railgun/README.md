# Regular-centre scalar rings: validation data

The November 1 spherical benchmark passes independent checks on 56x8, 72x10 and 96x12. GPU regressions: 45 passed. This validates the spherical numerical baseline, not a rotating ring or dynamical stability.

- `spherical-initial/`: rejected 40x6 pilot.
- `spherical-diagnostic/`: 40x6/56x8/72x10 diagnostic recovery; study rejected.
- `spherical-validated/`: accepted three-grid background, independent areal-radius ODE reference, configuration, diagnostics and checksums.
- `gpu_regression.json`: portable GPU test report.

Implementation and numerical contract: `research/railgun/EQUATIONS.md`. Current work: `research/railgun/STATUS.md`.
