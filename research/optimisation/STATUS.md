# Quantum-budget campaign (campaign F) — status

Started 2026-10-27 on branch `feature/optimisation`.  Plan:
[`Quantum Budget Wormhole Search.md`](Quantum%20Budget%20Wormhole%20Search.md) (steps 1–2 = jobs 0 + F1 are done, below).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/analysis/quantum_budget/` +
`grteclyn-wrapper/scripts/analysis/quantum_budget/` (CPU only, reads the spinning solver's
200 saved solutions in `results/spinningwormhole/solutions/`; no GPU anywhere in F1).
Data: `results/optimisation/` (f_curve.tsv, measurement.json, figures/f_curve.png).
Tests: `grteclyn-wrapper/tests/quantum_budget/` (4, ~6 s).

## RESULTS (2026-10-27, job F1 + the static anchor)

F = the Ford–Roman compliance factor: the worst stationary-observer energy density against the
flat Lorentzian-sampled bound 3/(32 π² τ₀⁴) with τ₀ = the local curvature scale
(max orthonormal Riemann component)^(−1/2); F ≤ 1 means quantum fields could pay.
F scales as (throat size / l_p)² and as f_s⁴ in the sampling fraction; both cancel from F(v_e)/F(0).

- **Static anchor reproduced.** Massless Ellis: pipeline = closed form 4π/3 exactly;
  F(R_eq = 1 m) = 10^70.2 for both families' static members; F ≤ 1 needs R_eq ≤ 0.46–0.49 l_p —
  the published "no macroscopic static wormhole" accounting.
- **Spin is not the lever.** At fixed physical throat radius, F falls only ~1.7 decades along the
  whole ladder: family (a) 10^70.25 → 10^67.5 at v_e 0.99, family (b) 10^70.21 → 10^68.5.
  The 100× total-exotic (D/M) drop does not translate into closing the ~68 remaining decades:
  per the plan's step-2 decision rule, **shape is the lever — the thin-band side (job F4) is the main line.**
  In code units the worst density×window⁴ actually RISES with spin (family (a) fhat 70 → 546);
  the fixed-throat gain is all dilution through the growing R_eq.
- **Every member is tail-illegal.** The phantom field keeps ρ < 0 out to infinity while the local
  curvature window grows, so the pointwise budget ρ ℓ_c⁴ diverges off the throat for every solution
  (`fhat_field_max` documents it).  A compliant design needs the exotic matter confined — the standing
  argument for the thin-band brick.
- **Gates.** Independent check: contracting the frame Riemann must close the (never-imposed) field
  equation — worst defect 5.9e-7 over all 202 measurements.  Self-convergence: point gates ≤ 1e-7
  away from the extremal end (≤ 4e-3 at v_e 0.99); cross-map agreement (arctan vs log legs at equal J)
  median 1.8e-4.  Worst density sits on the equator at every spin.
- **Known rates** (plan step 1b): [`known_rates.tsv`](known_rates.tsv) — Azad et al. m = 0 linear
  rates + our nonlinear refits.  **No m ≥ 1 rate exists in the repo**; the rapid-rotation QNM paper
  and the charged-family perturbation work are needed for the F2 validation targets (papers land in
  articles.md on the word).

## QUEUE

- **F2 — per-m eigenproblem** (paper two; next): linear modes m = 0, 1, 2 on the saved backgrounds;
  validate m = 0 against Azad's C = 1 row and the static rate before any m ≥ 1 claim.
- F1 polish (small): Fewster–Eveson/Fewster–Pfenning curved-space bounds as alternative `qi`
  strategies; the radially transiting observer class with transit-limited sampling; a denser
  near-extremal refinement for the two v_e 0.99 points (conv 4e-3).
- Decisions open: none blocking.  The F definition's conventions (stationary observers, τ₀ = ℓ_c,
  f_s = 1) are in `quantum_budget/conventions.py`; change them there only.

## RULES

CPU jobs under the address-space cap (sympy builds run with `ulimit -v`); no GPU start-up of any
kind without the go; logs under `runs/` (untracked).
