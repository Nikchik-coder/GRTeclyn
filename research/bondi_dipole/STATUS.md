# Bondi dipole paper — status

One page, current only. Paper: [`article/bondi_dipole.tex`](article/bondi_dipole.tex), arXiv:2608.24577 (v1). Data:
[`results/bondi-dipole-runaway/`](../../results/bondi-dipole-runaway/README.md), tag `v1.0-bondi-dipole`. Code:
`Examples/RadialRecipe/`, launchers `grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh` and
`run_single_selfgrav.sh`. Runs: `runs/bondi/` (untracked): only the revision's runs on the fixed binary, filed by
question (`NN_group/`), live runs in `staging/`; every earlier run, its movies and notes in
`00_archive/superseded_2026-10-23/` (`runs/bondi/README.md`). The pack mirrors the groups, `campaign/NN_group/<run>`,
and also holds only the fixed runs: the v1 cells, guide and registry are in that archive's `results_campaign/`, and
the published v1 pack in the tag `v1.0-bondi-dipole`.
Writing rules: [`../WRITING_STANDARDS.md`](../WRITING_STANDARDS.md). Branch `feature/fix_bondi`, cut from
`feature/spinning` on 2026-10-22 (develop carries no `research/`; its code is the same).

## Journal trail

- PRD, then CQG: rejected (dates not recorded).
- GRG: sent to review, rejected 2026-10-20 on presentation (undefined symbols and lab vocabulary, too many numbers,
  no convergence test), no invitation to resubmit. The reports are kept locally only, in `referee/` (git-excluded).
- Next: EPJC (open access through SCOAP3; confirm it charges no APC), fallback IJMPD.

## Current status (2026-10-24, 08:00 MSK)

The paper's simulations carry a numerical error that changes its numbers: the evolution integrated in time at first
order instead of fourth (below). It is fixed and verified, and the paper is being rerun on the fixed code and fixed
initial data (the table below). The constraints now converge at order 3–4 (1.2–1.6 in the paper's runs) and ΔX and
a at about order 4.

The headline changes: the paper's Table II gives ΔX(200) = 3.00 ± 0.01 and a = 1.55 × 10⁻⁴ (N 256), 5 % and 8 %
above Bondi's point-mass 2.86 and 1.43 × 10⁻⁴; the fixed N 256 gives ΔX(200) = 2.874 ± 0.029 and
a = (1.451 ± 0.024) × 10⁻⁴ (error: the N 192 − 256 difference), on the point-mass values. Over N 128, 192, 256 they
converge at order 4.4 and 4.2 (the paper's runs did not converge after t 50) and extrapolate to 2.886 and
1.461 × 10⁻⁴. The separation is unchanged (0.1 %). The model, the tests and the qualitative result are untouched;
every number changes.

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

## Runs for the revision

Each run is its v1 cell again (`evolution_params.txt`, `launch_config.sh` in
`runs/bondi/00_archive/superseded_2026-10-23/results_campaign/<group>/<cell>/`) on the fixed binary with fresh initial
data (`GRTresna_bondi_fix`, the joined lapse, the fixed converter; star tables at new frequencies are rebuilt at
launch); each needs the go and the checkpoint question. Finished runs are filed in `runs/bondi/NN_group/` and packed
in `campaign/NN_group/`. Names: the Table I label, the box and the cells (`PM10_L64_N128`), a stop time other than the
paper's appended (`PM10_L64_N128_t400`); the initial data as `<name>_initial_data` in `runs/bondi/11_initial_data/`. Runs
launched before the renaming keep their launch names (`rkfix_*`) in `staging/` until close-out. GPU-h on one H100 alone: N 128 ≈ 200 u/h, N 192 ≈ 50, N 256 ≈ 19, the L 128 box at N 256
≈ 37. Solves: N 128 ~6 min on the first node (~25 min on the second), N 192 ~20 min and 93 GB, N 256 and the L 128
run 68 min and 221 GB, first node only (the second's limit is 195 GB). N 128 runs go to the first node, two per
card: the second node's consumer cannot keep up with them (12 CPUs).

| runs (Table I) | for | L | N | stop | GPU-h | status |
|---|---|---|---|---|---|---|
| `PM10_L64_N128` | the runaway; convergence | 64 | 128 | 200 | 1 | **done**: ΔX(200) 2.648, a(5–200) 1.274 × 10⁻⁴; `09_convergence/` |
| `PM10_L64_N192` | convergence | 64 | 192 | 200 | 4 | **done**: ΔX(200) 2.846, a(5–200) 1.427 × 10⁻⁴; `09_convergence/` |
| `PM10_L64_N256` | the headline; frames, figure and movie | 64 | 256 | 200 | 11 | **done**: ΔX(200) 2.874, a(5–200) 1.451 × 10⁻⁴ (order 4.4 / 4.2 with N 128, 192); `09_convergence/` |
| `M_L64_N128` | the lone star sits still; convergence | 64 | 128 | 200 | 1 | **done**: `09_convergence/` |
| `M_L64_N192` | convergence | 64 | 192 | 200 | 4 | **done**: the minimum lapse moves −1.48 × 10⁻⁴ by t 200 (N 128 −1.47), the peak field +0.001 % (N 128's −0.13 % was numerical); constraints at order 2.8–2.9 inside r < 24 (N 128→192); `09_convergence/` |
| `M_L64_N256` | convergence | 64 | 256 | 200 | 11 | **done** (from its rejected solve's data, `11_initial_data/M_L64_N256_initial_data`: the solve stopped at its floor, Ham 2.51 × 10⁻⁴ %): the minimum lapse moves −1.49 × 10⁻⁴ by t 200 (N 192 −1.48), the peak field +0.003 %, the core 2.83 × 10⁻³ (N 192 2.84); around the star (r < 12) Ham converges at order 3.4 / 3.7 and Mom at 3.0 / 3.8 (medians, N 128→192 / 192→256); in 12 ≤ r < 24 Ham is the same at all three N after t 30, so over r < 24 the 192→256 Ham order falls from 3.7 at t 10 to 0.8 at t 200; no NaN; `09_convergence/` |
| `PM10_L64_N128_t400` (PM10-t400) | PM10 carried to t 400: constant a; Fig. trajectories (b) | 64 | 128 | 400 | 2 | **done**: d 9.98 at t 200, 10.84 at t 400 (the paper's run 10.00, 11.74); a 1.06 × 10⁻⁴ over 133–266 and 0.82 × 10⁻⁴ over 300–400 (the paper's 1.45, 1.42), falling as the stars lose 5.9 % of their matter by t 400, which is numerical (at t 200: −2.6 % at N 128, within 1 % at N 192 and 256); no NaN; frames; `04_runaway/` |
| PM8, PM12, PM16, PM20 (`PM8_L64_N128`, …) | a ∝ d^−2.03 (the old −2.03 ± 0.01 sat 3σ from −2) | 64 | 128 | 200 | 4 | PM8, PM12 **done**: a d0² is 0.994 and 1.009 of PM10's (a ∝ d0^−1.97 over d0 8–12, N 128); `05_separation/`; PM16, PM20 running (Live) |
| E0.64, E1.34, E1.57 (d0 20; `E0.64_L64_N128`, …) | a ∝ M̄^0.97 | 64 | 128 | 200 | 3 | running (Live), launched 10-24 08:58 MSK on card 1, no checkpoints; the old error ∝ ω² differed between them |
| MP10 (`MP10_L64_N128`) | test iv: the motion reverses when the two stars are swapped | 64 | 128 | 200 | 1 | running (Live), launched 10-24 12:25 MSK on card 0, no checkpoints |
| PP10 (`PP10_L64_N128`) | test v: a same-sign pair stays at rest; Fig. same-sign (with frames, its movie), Fig. constraints | 64 | 128 | 200 | 1 | running (Live), launched 10-24 12:25 MSK on card 0, no checkpoints; N 192 and 256 dropped 10-24 (a check, not a convergence study) |
| MM10 (`MM10_L64_N128`) | test v; Fig. same-sign (with frames, its movie) | 64 | 128 | 200 | 1 | running (Live), launched 10-24 12:25 MSK on card 0, no checkpoints; one run with frames for the paper's two N 128 runs; N 192 dropped 10-24 |
| PM10-tol, PM10-AMR, PM10-η2 | Table II: ΔX(200) against a tighter solve tolerance, one refinement level, doubled shift damping | 64 | 128 | 200 | 4 | dropped 2026-10-24: numerics checks (in v1 each moved ΔX(200) by < 0.01 %) |
| R0.60, R0.80, R1.33 (`R0.60_L64_N128`, …) | each star follows its partner's mass | 64 | 128 | 200 | 3 | R0.60, R0.80 **done**: the positive star's pull C (its partner changed) is 0.610 and 0.806 of PM10's at N 128 (predicted 0.600, 0.803; the paper's runs 0.618, 0.810), the negative star's (partner unchanged) 1.034 and 1.006 (1.028, 1.011); d(200) − d0 −1.20 and −0.56 (−1.38, −0.59); no NaN; `06_mass/`. R1.33 running (Live) |
| `P_L64_N128` (P) | the isolated positive-mass star (ω 0.75) at the centre: test v, Sec. III A | 64 | 128 | 200 | 1 | running (Live), launched 10-24 08:28 MSK, no checkpoints; dry run matched the paper's run |
| S0.75, S0.80, S0.85, S0.90 | stationarity of the stars | 64 | 128 | 120 | 2.4 | dropped 2026-10-24: P backs the positive star instead (the M convergence covers the negative one) |
| `PM10_L128_N256` (PM10-L128) | domain size, the box doubled at the same Δx 0.5 (the old one moved ΔX by 4 %); Ψ4 in the near zone | 128 | 256 | 200 | 5.5 | **done**: the stars move as in the L 64 box: the cores' ΔX(200) is +0.2 % from PM10 N 128 and their separation the same (10.07); the whole-domain barycentres' ΔX moves −4.8 % (the paper's −4.2 %) because they take in the field the stars shed, which the larger box keeps; |Ψ4|ₗ₌₂ ∝ R^−4.7 (the paper's −4.8), R|Ψ4| falls ×30 over R 16–40 (31); no NaN; frames; `04_runaway/` |
| PM10-rec, PM10-off | the separation after t 200 | 64 | 128 | 600–784 | 7 | dropped 2026-10-23: for the pair only the large box remains |
| M-t1000 | "neither collapses nor disperses ... 1000 alone" | 64 | 128 | 1000 | 5 | dropped 2026-10-24; its text is out of the article |

Queue empty: MP10, PP10 and MM10 launched 10-24 12:25 MSK on card 0, when M N 256 and R0.60 / R0.80 landed.
Decided 2026-10-23: the pair ends with PM10-t400 and the large box (PM10-rec / -off dropped). **Decided 2026-10-24:
every simulation the paper keeps is rerun**, no checkpoints, as the cards free; the same-sign pairs and the numerics
are checks, not a convergence study. Dropped from the paper: S0.75–S0.90, M-t1000, PM10-rec / -off, PM10-tol / -AMR /
-η2, and PP10 / MM10 at N 192 and 256. Launch scripts in `staging/`, each from its v1 cell; the dropped ones in
`runs/bondi/00_archive/dropped_2026-10-24/`.

Extra, not for the paper (10-24): `PM10-rec_L64_N192_t1000`, the recentring chase (v1 PM10-rec) at N 192 to t 1000,
v ~ 0.14 c after ~71 units; no solve (PM10 N 192's data, so it repeats PM10_L64_N192 until the first shift, t ~ 170);
frames, no checkpoints; ~20 h on one H100. Launched 10-24 09:22 MSK on the second node, card 0 (Live); dry run: only
stop, plot interval and treadmill keys differ from PM10 N 192.

## Live

No checkpoints (on the word); frames only on PP10, MM10 and the chase.

| run | node / card | t (12:44 MSK 10-24) | stop | speed | ETA |
|---|---|---|---|---|---|
| `PM16_L64_N128` | 1st / 1 | 154 (solve converged at iteration 12, Ham 9.0 × 10⁻⁴ %; params and t 0 as the paper's run) | 200 | ~27 u/h each with seven on the card | ~1.7 h, ~14:25 MSK |
| `PM20_L64_N128` | 1st / 1 | 156 (as PM16: Ham 9.3 × 10⁻⁴ %) | 200 | ~30 u/h | ~1.5 h, ~14:15 MSK |
| `R1.33_L64_N128`, `P_L64_N128` | 1st / 1 | 124 / 126 (solves converged at iteration 12, Ham 8.8 / 10.6 × 10⁻⁴ %) | 200 | ~28 u/h | ~2.8 h, ~15:30 MSK |
| `E0.64_L64_N128`, `E1.34_L64_N128`, `E1.57_L64_N128` | 1st / 1 | 99 / 100 / 100 (solves converged at iteration 12, Ham 9.1 / 9.5 / 9.7 × 10⁻⁴ %) | 200 | ~28–31 u/h | ~3.5 h, ~16:15 MSK |
| `MP10_L64_N128`, `PP10_L64_N128`, `MM10_L64_N128` | 1st / 0 | 3 / 8 / 5 (launched 12:25 MSK; solves converged at iteration 12, Ham 8.6 / 12.7 / 13.3 × 10⁻⁴ %; evolving from 12:40 MSK; frame 0 of PP10 and MM10 as the paper's runs; consumers keep up, 2–3 plotfiles on scratch; 20 GB on the card) | 200 | ~66 u/h each | ~3 h, ~15:45 MSK |
| `PM10-rec_L64_N192_t1000` | 2nd / 0 | 167 (PM10 N 192's data, no solve; launched 09:22 MSK; 20 GB on the card) | 1000 | ~51 u/h | ~16.4 h, ~05:10 MSK 10-25 |

## Revision

### 1. Text (workstation)

Done 10-22 (pdflatex and lualatex both build, 13 pages): every presentation point of the GRG reports, mapped to
WRITING_STANDARDS §1–7 (title, abstract, symbols defined at first use, private vocabulary out, the five tests before
the results, Table I setup / Table II results, one number per claim, conclusions with a scope paragraph, captions),
an outside-reader pass (~60 findings applied) and a redundancy pass (text 6608 → 6191 words).

- [ ] Every number, Table II and the figures from the reruns (the frames figure and movies from the new PM10 N 256
      and PM10-t400); Tables I and II and the text keep only the simulations in "Runs for the revision".
      `article_figures.py` and `results/.../analysis/` still read the v1 cells (archived 10-23): re-point them.
- [ ] Convergence (Sec. VII A, App. A, Fig. 6(b) / Fig. 10): the order table, ΔX's self-convergence over t 200 with
      the rescaled differences, the lone star's drift with resolution; App. A loses the transfer explanation.
- [ ] Sec. III A, initial data as now built: the profile's exterior (field tail, isotropic Schwarzschild metric, the
      lapse joined in value and slope), and the evolution's superposed lapse α = 1 + Σ(α_k − 1) in Π = −(ω/α) φ₀.
- [ ] The separation: "constant to 1 %" held only for the net change in the old runs (it dipped 2.9 % near t 51);
      recheck on the reruns.
- [ ] PM10-L128, the domain size (Table II, the line "PM10-L128; -tol; …"; Sec. II on the two trackers): the box
      does not move the stars. By the cores ΔX(200) changes +0.2 % from PM10 at N 128 and the separation is 10.07
      in both boxes; by the whole-domain barycentres ΔX(200) changes −4.8 % (v1 −4.2 %), because in the L 128 box
      they keep the field the stars shed, which the L 64 box's absorbing layer removes from r 24 (sector rms radius
      16.9 against 5.8 at t 100). Table II's −4.2 % becomes +0.2 % by the cores (or the text says why the
      barycentres move), and "the two ways of tracking agree on ΔX to 1 %" holds only in the L 64 box.
- [ ] Same-sign controls at N 128 only, numerics checks out (10-24): Table I's rows (PP10 128; MM10 128, one run; no
      PM10-tol / -AMR / -η2), Table II's "PP10, all N; MM10, all N" and "PM10-L128; -tol; -AMR; -η2" rows, Fig.
      same-sign (a) and its movie from PP10 at N 128, the grey PP10 line of Fig. constraints, Fig. convergence (a)'s
      PM10-tol / -AMR markers, Sec. VII's numerical-choices paragraph, and the same-sign merger time (t 33.6).
- [ ] PM10-L128, Ψ4 (Fig. wavezone, Table II, the wave-extraction paragraph): |Ψ4|ₗ₌₂ falls as R^−4.7 (text −4.8)
      and R|Ψ4| drops ×30 across the four spheres (text 31); the near-zone conclusion stands. The consumer stores
      R Ψ4; `article_figures.py` divides by R, which is right.
- [ ] Sec. VII, the separation after t 200: PM10-rec and PM10-off are dropped (decided 2026-10-23), so the paragraph
      rests on PM10-t400 alone: at N 128 d is 9.98 at t 200 and 10.84 at t 400 (text: 11.8), a falls from
      1.06 × 10⁻⁴ (133–266) to 0.82 × 10⁻⁴ (300–400), and the stars lose 5.9 % of their matter by t 400, a
      numerical loss (at t 200: −2.6 % at N 128, within 1 % at N 192 and 256).
- [ ] S0.75–S0.90 leave Table I (dropped 2026-10-24); Sec. III A's stationarity of the stars and test v rest on P
      (the positive star at the centre) and M (the negative star off centre).
- [x] M-t1000 out of the article (2026-10-24): the introduction's longer runs, Table I's M row, Table II's decay
      row, its results paragraph, and the conclusions' "1000 alone, although it slowly relaxes outward".
- [ ] Table I's caption "The 34 simulations": recount when the reruns land (S0.75–S0.90, M-t1000, PM10-rec / -off
      dropped; M at N 192 and 256 added; MM10 at N 128 is one run).
- [ ] Notation table (~20 symbols, WRITING_STANDARDS §2): decide whether it is worth the space.
- [ ] Strip all TODO comments before the arXiv upload.

### 2. Release and submission

- [ ] Pack the reruns into `results/bondi-dipole-runaway/` (groups as now; the v1 cells there leave as their reruns
      land) and update `runs_registry.tsv`.
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
