# Bondi dipole paper — status

One page, current only. Paper: [`bondi_dipole.tex`](bondi_dipole.tex), arXiv:2608.24577 (v1). Data:
[`results/bondi-dipole-runaway/`](../../results/bondi-dipole-runaway/README.md), tag `v1.0-bondi-dipole`. Code:
`Examples/RadialRecipe/`, launchers `grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh` and
`run_single_selfgrav.sh`. Runs: `runs/bondi/` (untracked; filed by question since 10-23, live runs in `staging/`
only: `runs/bondi/README.md`; the pack in the same groups, `campaign/NN_group/<run>`, with `runs_registry.tsv`).
Writing rules: [`../WRITING_STANDARDS.md`](../WRITING_STANDARDS.md). Branch `feature/fix_bondi`, cut from
`feature/spinning` on 2026-10-22 (develop carries no `research/`; its code is the same).

## Journal trail

- PRD, then CQG: rejected (dates not recorded).
- GRG: sent to review, rejected 2026-10-20 on presentation (undefined symbols and lab vocabulary, too many numbers,
  no convergence test), no invitation to resubmit. The reports are kept locally only, in `referee/` (git-excluded).
- Next: EPJC (open access through SCOAP3; confirm it charges no APC), fallback IJMPD.

## Current status (2026-10-23, 12:15 MSK)

The paper's simulations carry a numerical error that changes its numbers: the evolution integrated in time at first
order instead of fourth (below). It is fixed and verified, and the whole paper is to be rerun on the fixed code and
fixed initial data (Queued). Live now: the reference pair PM10 at N 128 / 192 / 256 to t 200 and the lone
negative-mass star M at N 128 / 192, the convergence appendix and the first corrected headline numbers.

So far (t 28): the constraints converge at order 3.6 / 4.0 (Ham) and 3.0 / 3.7 (Mom), N 128→192 / 192→256, against
1.2–1.6 in the paper's runs; ΔX and a converge at about order 4. ΔX(28) is 4.9 / 7.0 / 11.9 % below the paper's at
N 256 / 192 / 128, and a fitted over 5 ≤ t ≤ 28 is 7.8 % below at N 256 (1.527 against 1.657 × 10⁻⁴ on the same
window; the paper quotes 1.55 × 10⁻⁴ over 5 ≤ t ≤ 200). The gaps shrink as Δx¹ and grow with t: the old runs'
time-integration error. The model, the tests and the qualitative result are untouched; every number changes.

Figures: `python -m grteclyn_wrapper.visualisation.bondi_dipole convergence` draws both sets into
`results/bondi-dipole-runaway/figures/convergence_pair` / `convergence_lone` (constraints by region with the
order-2 / order-4 rescaled curves, and the motion); the article's figures now live there too (`\graphicspath`).
Report at any time (progress, order table, ΔX / d / a against the paper's runs):
`grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/bondi_dipole/study_report.py [--study pair|lone]`.

## What was wrong (final)

Four numerical defects, none in the model. By effect on the paper's numbers:

1. **First-order time integration.** `RadialRecipeLevel::specificEvalRHS` called AMReX's `FillPatch` on every
   Runge–Kutta stage. FillPatch overwrites the stage's valid cells with the old and new states interpolated to the
   stage time, so RK4's mid stages saw U + k dt/4 instead of U + k dt/2 and the scheme fell to first order; with
   dt = 0.02 Δx that is first order in Δx. It anti-damps each star's oscillating field (∝ ω² dt), so the matter
   density drifts ahead of the geometry inside the stars. In the paper: constraint orders capped at ~1.2–1.5, and ΔX
   and a carry an O(Δx) error that grows with time, which the N 192–256 difference (the paper's error bars)
   understated. Fixed in c12664fd, RadialRecipe only (binary `runs/bondi/bin/main3d_rkfix_aa0dc4a1-dirty_2026-10-23.ex`,
   md5 f4253171, aa0dc4a1 plus that commit). The same call sits in BinaryWormholeMerger and SupportedWormholeCollapse
   (the merger paper's runs); SpinningWormhole switched it off on 10-17 (`rk_stage_refill = 0`).
2. **A lapse step in the star tables.** Each tabulated star joins its integrated interior to an analytic exterior at
   r ≈ 5.2, and the two lapses did not meet (±4–5 × 10⁻⁵). The lapse does not enter the t = 0 constraints, so every
   t = 0 check passed; the first step turned the step into a momentum violation growing like N^1.5 (momentum order
   −1.4 at t 0 in the paper's runs). Fixed in the profile builder (`_lapse_join`, value and slope; α∞ moves by
   4 × 10⁻⁶).
3. **The face layer of the initial data.** The converter painted each face's outermost layer of χ and α from a solve
   cell outside the evolution box (steps up to 3 × 10⁻⁴ on five faces). This is the paper's t = 0 rise of the
   Hamiltonian norm with resolution, which App. A blames on the solve-to-evolution transfer (the boundary-masked
   norm falls instead). Fixed in the converter, e3992acf.
4. **Solver and painter disagreed on the matter.** GRTresna's Im Π divided by each star's own lapse, the painted data
   by the summed lapse; |∇φ|² came from a linear interpolant, the painted field from a spline; the star frequency was
   read as a rotation rate. A t = 0 violation of ~8 × 10⁻⁷ at every N. Fixed in GRTresna
   `fix/bondi-solve-matches-painter` 9a85e6a (worktree `GRTresna_bondi_fix`, binary
   `runs/bondi/bin/grtresna_BosonStarBH_9a85e6a_2026-10-22.MPI.ex`).

Stays by design: the elliptic solve is second order (the t = 0 Hamiltonian converges at 2.0; the evolution's 4 takes
over as the solve's error is carried out), and the profile's field tail beyond r 5.19 sits on a vacuum exterior (1.9 %
of the ADM mass in the tail), which the solve repairs in ψ.

Verified 10-23: the lone painted star on a 16-unit box (Δx 0.25 → 0.0625) converges in the core at order 4.4–5.2 on
the fixed binary against 1.0 before, with a 380× smaller core drift at N 256; the pair to t 10 on the same data
reaches interior Ham 3.8 and Mom 3.7 (N 192→256) against 1.2 and 2.5 on the old binary, so the integrator, not the
data, set the cap. The full debugging record: `git show b81850d7:research/bondi_dipole/STATUS.md`.

## Live

All on the fixed binary and fixed data (pair: `facefix_*`, read; lone: fresh solves on `GRTresna_bondi_fix`), no
checkpoints (on the word), frames off except PM10 N 256 (frames and slice cache, as the paper's figure run). Each
run's `launch.sh` is in its dir under `runs/bondi/staging/`; against the paper's run only the binary, the data, the
card, the run dir and `constraint_shells_dt` 0.1 differ.

| run | node / card | t (18:30) | stop | speed | ETA |
|---|---|---|---|---|---|
| `rkfix_pair_d10_L64_N128_lev0_t200` (PM10) | 1st / 0 | 200, done 13:01 MSK, no NaN | 200 | 81 u/h | ΔX(200) 2.648, a(5–200) 1.274 × 10⁻⁴: −8.1 % / −12.0 % against the paper's N 128 |
| `rkfix_pair_d10_L64_N192_lev0_t200` | 1st / 0 | 200, done 15:20 MSK, no NaN | 200 | 56 u/h | ΔX(200) 2.846, a(5–200) 1.427 × 10⁻⁴: −5.6 % / −8.3 % against the paper's N 192 (Bondi's point-mass ΔX(200) 2.86) |
| `rkfix_pair_d10_L64_N256_lev0_t200` (frames) | 1st / 1 | 144.9 | 200 | 18 u/h | 3 h, ~21:30 MSK |
| `rkfix_lone_m_L64_N128_lev0_t200` (M) | 2nd / 0 | 200, done 12:47 MSK, no NaN | 200 | 207 u/h | finished: filed in `runs/bondi/09_convergence/`, packed in `campaign/09_convergence/` |
| `rkfix_lone_m_L64_N192_lev0_t200` | 2nd / 0 | 200, done 17:49 MSK, no NaN | 200 | 49 u/h | evolution finished; consumer draining (t 136 of 200 at 18:30, 2.3 h, ~20:50 MSK), packed after |

The lone N 128 consumer lags (~80 s per plotfile against one every ~14 s; the N 192 solve holds 8 of the second
node's 12 CPUs): 183 plotfiles (66 GB, 667 GB free) drain after the run, a few hours. Its constraints stay flat
(interior Ham 2.1 → 3.4 × 10⁻⁶ over t 10–189, Mom ~3.5 × 10⁻⁷); the paper's M at N 128 grew (boundary-masked Ham
6.0 → 7.7 × 10⁻⁶ against our 3.5 → 3.3 × 10⁻⁶).

## Queued: the paper rerun (list agreed 10-23)

Each needs the go and the checkpoint question. Each run is its packed run again (`evolution_params.txt`,
`launch_config.sh`) on the fixed binary with fresh initial data (`GRTresna_bondi_fix`, the joined lapse, the fixed
converter; star tables at new frequencies are rebuilt at launch). GPU-h on one H100 alone: N 128 ≈ 200 u/h, N 192
≈ 50, N 256 ≈ 19, the L 128 box at N 256 ≈ 37. Solves: N 128 ~6 min on the first node (~25 min on the second),
N 192 ~20 min and 93 GB, N 256 and the L 128 run 68 min and 221 GB, first node only (the second's limit is 195 GB).
N 128 runs go to the first node, two per card: the second node's consumer cannot keep up with them (12 CPUs).

| runs (Table I) | for | N | stop | GPU-h | notes |
|---|---|---|---|---|---|
| PM10-t400 | constant a to t 400; Fig. trajectories (b) | 128 | 400 | 2 | frames; first, it decides the late-separation runs |
| PM8, PM12, PM16, PM20 | a ∝ d^−2.03 | 128 | 200 | 4 | |
| E0.64, E1.34, E1.57 | a ∝ M̄^0.97 | 128 | 200 | 3 | the old error ∝ ω² differed between them |
| R0.60, R0.80, R1.33 | each star follows its partner's mass | 128 | 200 | 3 | |
| MP10 | exchange reverses the motion | 128 | 200 | 1 | |
| PP10, MM10 | same-sign pairs merge, centroids at rest | 128 | 200 | 2 | MM10 with frames (its movie) |
| PP10 | the same at a second resolution | 192 | 200 | 4 | frames and slice cache (its movie; replaces N 256) |
| PM10-tol, PM10-η2 | solve tolerance, gauge | 128 | 200 | 2 | |
| PM10-L128 | domain size; Ψ4 in the near zone | 256 (L 128) | 200 | 5.5 | 221 GB solve: first node |
| S0.75, S0.80, S0.85, S0.90 | stationarity of the stars | 128 | 120 | 2.4 | no `launch_config.sh` packed: rebuild from `runs/bondi/01_star_family` |

About 29 GPU-h, ~10–12 h on the three cards. Dropped from the paper's 34 (the text changes with them):
- P: at the centre, symmetry holds it; M (off centre) carries test (v), S0.75 the isolated positive-mass star.
- PM10-AMR: no refined level is ever created (|χ − 1| stays below the 0.02 threshold); say so from PM10's own χ.
- PP10 at N 256, MM10 at N 192 and MM10's second N 128 run: a same-sign pair's centroid is held by symmetry, so
  N 128 and PP10 at N 192 suffice; Fig. same-sign (a) and the movie use PP10 at N 192.

Decided after PM10-t400: PM10-rec and PM10-off (7 GPU-h). The old runs' separation growth after t 200 shrank
eightfold per halving of Δx, so it is likely the old time error: if the fixed PM10-t400 shows none, Sec. VII
"Separation after t = 200" and both runs go.

Optional: M-t1000 (5 GPU-h; only if the text keeps "neither collapses nor disperses ... 1000 alone"), M at N 256
(11 GPU-h, the 221 GB solve on the first node; the lone star's third resolution).

## Revision

### 1. Text (workstation)

Done 10-22 (pdflatex and lualatex both build, 13 pages): every presentation point of the GRG reports, mapped to
WRITING_STANDARDS §1–7 (title, abstract, symbols defined at first use, private vocabulary out, the five tests before
the results, Table I setup / Table II results, one number per claim, conclusions with a scope paragraph, captions),
an outside-reader pass (~60 findings applied) and a redundancy pass (text 6608 → 6191 words).

- [ ] Every number, Table II and the figures from the reruns (the frames figure and movies from the new PM10 N 256,
      PP10 N 256 and MM10 N 128 frame runs).
- [ ] Convergence (Sec. VII A, App. A, Fig. 6(b) / Fig. 10): the order table, ΔX's self-convergence over t 200 with
      the rescaled differences, the lone star's drift with resolution; App. A loses the transfer explanation.
- [ ] Sec. III A, initial data as now built: the profile's exterior (field tail, isotropic Schwarzschild metric, the
      lapse joined in value and slope), and the evolution's superposed lapse α = 1 + Σ(α_k − 1) in Π = −(ω/α) φ₀.
- [ ] The separation: "constant to 1 %" held only for the net change in the old runs (it dipped 2.9 % near t 51);
      recheck on the reruns.
- [ ] Notation table (~20 symbols, WRITING_STANDARDS §2): decide whether it is worth the space.
- [ ] Strip all TODO comments before the arXiv upload.

### 2. Release and submission

- [ ] Pack the reruns into `results/bondi-dipole-runaway/` (groups as now) and update `runs_registry.tsv`.
- [ ] Merge into develop without `research/`, tag (e.g. `v1.1-bondi-dipole`), GitHub release, then Zenodo
      "Sync now" (CLAUDE.md, Publishing) and check the version DOI under concept 10.5281/zenodo.23245933.
- [ ] arXiv v2 of 2608.24577: account page → Articles You Own → Replace icon → upload the full source again (tex,
      bbl, figures, `anc/` movies) → compiler **pdflatex** → update the abstract and comments ("v2: corrected time
      integration, all simulations rerun, convergence study added") → submit. Same identifier; v1 stays visible.
      Replacements have their own limit (one per week after v5), not the monthly cap.
- [ ] Journal submission (EPJC), on the same day as the v2.

### After Bondi

The merger paper (arXiv:2610.13206), withdrawn from GRG on 2026-10-22: its runs carry the same first-order stage
re-fill (BinaryWormholeMerger), so it needs the same single-star A/B before its writing pass and replacement.
