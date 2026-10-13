# Spinning-wormhole campaign — packed results

Nonlinear evolutions of rotating Ellis–Bronnikov wormholes, slow spin to the
extremal Kerr limit. Plan: `research/spinningwormhole/SpinningWormhole.md`;
live state: `research/spinningwormhole/STATUS.md`; code:
`Examples/SpinningWormhole/` (launcher:
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`).

- `binaries.tsv` — the record of every frozen campaign binary (the bin/
  directory itself is untracked).
- `runs_registry.tsv` — one line per run: what it is for, outcome.
- `trust_windows.tsv` — the last trustworthy time per run; movies, figures
  and quoted numbers stop there.
- `campaign/` — packed runs (full `.dat` streams, `evolution_params.txt`,
  `run_manifest.json`, `mots_spectral.dat`; paths scrubbed by
  `grteclyn_wrapper.packaging.scrub_paths`).

## Claims

- `01_static_hold/static_hold_L64_ml3_t100` (2026-10-11; launched as
  `static_hold_L64_t100`, renamed 2026-10-12): the Step 0 anchor.
  The merger's production `single_hold_t100` ran on this exact grid (L = 64,
  N = 128, ml3), and the new table-driven pipeline reproduces it as a
  numerical twin over the FULL record: t = 0 bit-identical, L2_Ham within
  5e-7 (median 0) for all t ≤ 100, collapse milestones within one time unit;
  τ(δR) = 5.27 vs the merger's 5.12 fit; MOTS on every plotfile, horizon
  detaches at t ≈ 61 and shrinks under the phantom flux.  The t > 80
  constraint growth is the same in both runs — a property of this grid, not
  of the new code.  Trust window t ≤ 64.  Constraint overlay:
  the run's `figures/constraint_norms.png` (both curves within linewidth).
- `02_spin_hold/spin_hold_L64_ml3_J025_t100` and `…_J100_t100` (2026-10-12):
  Step 1's first spinning holds, the Step 0 drainhole at J = 0.25 and 1.0 on
  the same grid.  Both throats INFLATE where the static one collapses: the
  same unstable mode with the opposite sign (τ = 5.8 and 5.6 vs 5.26), no
  horizon about the throat (anti-trapped), R_eq 3.90 → 5.34 at t = 64
  (J025) and 4.09 → 7.36 at t = 40 (J100).  In the merger seed arms' terms
  they act as radial kicks ε ≈ −3e-5 and −7e-3, the inflating sign; that
  equivalent kick grows ~J⁴ (×230 for ×4 in J), the size of the O(J²)
  data's own error, so the branch is set by the data, not yet by the spin.
  The spin's own signature is the throat's flattening, at a rate ∝ J².
  Constraints at the static hold's level.  Trust windows t ≤ 64 and t ≤ 57.

## Fast-spin solver

- `solver/solutions.tsv` — every converged solution of the fast-spin
  solver (462 rows, 20 continuation legs: families (a) and (b), the four CKK
  anchor families, the low-spin end of the symmetric family), one row each:
  family, grid and map, the global charges and throat radii in CKK
  conventions, and the identity gates.  Packed from the untracked
  `runs/spinning_p3/` by `python -m
  grteclyn_wrapper.visualisation.spinning_wormhole.solutions`.
- `figures/solver/kk2014_fig1_overlay` (2026-10-13): Kleihaus & Kunz 2014
  Fig. 1 as published, with our symmetric family (eta0 = 1, gamma = 0,
  81 members, v_e 0.02-0.99) as open circles.  M/M0 = mu_+/R, J/J0 =
  2J/R^2, R_p/R and R_A/R all lie on the published wormhole curves within
  the line width over the whole range; the closed-form Kerr curves drawn
  on the calibrated axes (`--check`) land on the printed Kerr curves, which
  fixes both the pixel calibration and the paper's J0 = R^2/2.
