# Bondi dipole paper — status

One page, current only. Paper: [`article/bondi_dipole.tex`](article/bondi_dipole.tex), arXiv:2608.24577 (v1). Data:
[`results/bondi-dipole-runaway/`](../../results/bondi-dipole-runaway/README.md), tag `v1.0-bondi-dipole`. Code:
`Examples/RadialRecipe/`, launchers `grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh` and
`run_single_selfgrav.sh`. Runs: `runs/bondi/` (untracked): only the revision's runs on the fixed binary, filed by
question (`NN_group/`), live runs in `staging/`; every earlier run, its movies and notes in
`00_archive/superseded_2026-10-23/` (`runs/bondi/README.md`). The pack mirrors the groups, `campaign/NN_group/<run>`,
and also holds only the fixed runs: the v1 cells, guide and registry are in that archive's `results_campaign/`, and
the published v1 pack in the tag `v1.0-bondi-dipole`.
Writing rules: [`../WRITING_STANDARDS.md`](../WRITING_STANDARDS.md). Work is on `trunk`: `feature/fix_bondi`, cut
from `feature/spinning` on 2026-10-22, was merged into it at the v2 release and deleted on 2026-10-26.

## Journal trail

- PRD, then CQG: rejected (dates not recorded).
- GRG: sent to review, rejected 2026-10-20 on presentation (undefined symbols and lab vocabulary, too many numbers,
  no convergence test), no invitation to resubmit. The reports are kept locally only, in `referee/` (git-excluded).
- Next (decided 2026-10-26): resubmit to GRG once the paper carries the rerun numbers, with a submission message
  that every referee point is addressed and a point-by-point response to both reports; it names the earlier
  submission (its manuscript number is not recorded here; take it from the decision e-mail). Fallback EPJC, then IJMPD.
- 2026-10-26: Physics of the Dark Universe (Elsevier) considered instead of GRG; it published three of the
  negative-mass papers the article cites in 2026.

## Current status (2026-10-26)

The paper's v1 simulations carried a numerical error that changes its numbers: the evolution integrated in time at
first order instead of fourth (below). It is fixed and verified, every simulation was rerun on the fixed code and
fixed initial data (the table below), and the paper now carries the rerun numbers throughout (figures and text
10-26; both engines build, 14 pages). The constraints converge at order 3–4 (1.2–1.6 in the v1 runs) and ΔX and
a at order 4.4 / 4.2.

The headline changes: the paper's Table II gives ΔX(200) = 3.00 ± 0.01 and a = 1.55 × 10⁻⁴ (N 256), 5 % and 8 %
above Bondi's point-mass 2.86 and 1.43 × 10⁻⁴; the fixed N 256 gives ΔX(200) = 2.874 ± 0.029 and
a = (1.451 ± 0.024) × 10⁻⁴ (error: the N 192 − 256 difference), on the point-mass values. Over N 128, 192, 256 they
converge at order 4.4 and 4.2 (the paper's runs did not converge after t 50) and extrapolate to 2.886 and
1.461 × 10⁻⁴. The separation is unchanged (0.1 %). The model, the tests and the qualitative result are untouched;
every number changes.

Figures (2026-10-26): every article figure is drawn from the reruns by `python -m
grteclyn_wrapper.visualisation.bondi_dipole` into `results/bondi-dipole-runaway/figures/<group>/` (PDF + PNG, one
folder per campaign group, index `FIGURES.md`); the old Fig. 10 is replaced by the two resolution sets,
`09_convergence/convergence_pair` / `convergence_lone` (constraints by region with the order-2 / order-4 rescaled
curves, and the motion), now Figs. 8 and 9 of Appendix A on one float page before the appendix text. Decided 10-26:
the main-text resolution figure and the star-family plot leave the article (the appendix sets carry the first, the
text the family's two facts); every key sits above its panel, no blue (orange the one accent). Text pass 10-26:
every number, both tables and every caption carry the rerun values (the checklist below).
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
| PM8, PM12, PM16, PM20 (`PM8_L64_N128`, …) | a ∝ d^−2.03 (the old −2.03 ± 0.01 sat 3σ from −2) | 64 | 128 | 200 | 4 | **done**: a ∝ d0^−1.953 ± 0.003 over d0 8–20 (the paper's runs −2.028 ± 0.011 by the same estimator: barycentre midpoint, t ≥ 5, N 128); a d0² is 0.994, 1.009, 1.025 and 1.036 of PM10's for PM8, PM12, PM16, PM20 (the paper's runs 1.020, 0.992, 0.990, 0.991); PM16 a 5.10 × 10⁻⁵, ΔX(200) 1.043; PM20 3.30 × 10⁻⁵, 0.664; no NaN; `05_separation/` |
| E0.64, E1.34, E1.57 (d0 20; `E0.64_L64_N128`, …) | a ∝ M̄^0.97 | 64 | 128 | 200 | 3 | **done**: a ∝ M̄^0.967 ± 0.013 over E0.64, PM20, E1.34, E1.57 (the paper's runs 0.957 ± 0.007 by the same unweighted fit; the paper quotes 0.97 ± 0.06), core midpoint, t ≥ 5, the paper's masses; relative to PM20, a d0²/M̄ is 1.030, 0.999, 1.000 (the paper's 1.027, 0.992, 0.990); its absolute value is 0.92, 0.90 (PM20), 0.90, 0.90 at N 128 (the paper's 1.024, 0.997, 0.989, 0.987), low because N 128 is under-resolved: PM10 gives 0.89 at N 128 and 1.01 at N 256; no NaN; `06_mass/` |
| MP10 (`MP10_L64_N128`) | test iv: the motion reverses when the two stars are swapped | 64 | 128 | 200 | 1 | **done**: ΔX(200) −2.648 against PM10's +2.648 at N 128, drift ratio −0.99997, a ratio −1.00010 (the paper's −1.00002, −1.00001); no NaN; `03_same_sign/` |
| PP10 (`PP10_L64_N128`) | test v: a same-sign pair stays at rest; Fig. same-sign (with frames, its movie), Fig. constraints | 64 | 128 | 200 | 1 | **done**: the centroid stays at its start to round-off, max \|ΔX\| 4 × 10⁻¹³ over t ≤ 200 (the paper's run 7.8 × 10⁻⁴): the fixed code keeps the pair's mirror symmetry exactly; frames with the slice cache; no NaN; `03_same_sign/`; N 192 and 256 dropped 10-24 (a check, not a convergence study) |
| MM10 (`MM10_L64_N128`) | test v; Fig. same-sign (with frames, its movie) | 64 | 128 | 200 | 1 | **done**: centroid max \|ΔX\| 3 × 10⁻¹³ over t ≤ 200 (the paper's run 4.9 × 10⁻⁴); frames with the slice cache; no NaN; `03_same_sign/`; N 192 dropped 10-24 |
| PM10-tol, PM10-AMR, PM10-η2 | Table II: ΔX(200) against a tighter solve tolerance, one refinement level, doubled shift damping | 64 | 128 | 200 | 4 | dropped 2026-10-24: numerics checks (in v1 each moved ΔX(200) by < 0.01 %) |
| R0.60, R0.80, R1.33 (`R0.60_L64_N128`, …) | each star follows its partner's mass | 64 | 128 | 200 | 3 | **done**: the changed partner's pull C is 0.610, 0.806 and 0.751 of PM10's at N 128 (predicted 0.600, 0.803, 0.747; the paper's runs 0.618, 0.810, 0.756), the unchanged partner's 1.034, 1.006 and 0.994 (1.028, 1.011, 1.001); d(200) − d0 −1.20, −0.56 and +0.57 (−1.38, −0.59, +0.60), and with PM10's −0.02 it crosses zero at \|M₋\|/M₊ = 1.008 (barycentres; the paper's 1.00 ± 0.03); no NaN; `06_mass/` |
| `P_L64_N128` (P) | the isolated positive-mass star (ω 0.75) at the centre: test v, Sec. III A | 64 | 128 | 200 | 1 | **done**: the star sits at the box centre and its core stays there to round-off, 3 × 10⁻¹³ on any axis over t ≤ 200 (the paper's run 1.8 × 10⁻³); the peak field −0.14 % by t 200 (−0.48 %); no NaN; `02_lone_star/` |
| S0.75, S0.80, S0.85, S0.90 | stationarity of the stars | 64 | 128 | 120 | 2.4 | dropped 2026-10-24: P backs the positive star instead (the M convergence covers the negative one) |
| `PM10_L128_N256` (PM10-L128) | domain size, the box doubled at the same Δx 0.5 (the old one moved ΔX by 4 %); Ψ4 in the near zone | 128 | 256 | 200 | 5.5 | **done**: the stars move as in the L 64 box: the cores' ΔX(200) is +0.2 % from PM10 N 128 and their separation the same (10.07); the whole-domain barycentres' ΔX moves −4.8 % (the paper's −4.2 %) because they take in the field the stars shed, which the larger box keeps; |Ψ4|ₗ₌₂ ∝ R^−4.7 (the paper's −4.8), R|Ψ4| falls ×30 over R 16–40 (31); no NaN; frames; `04_runaway/` |
| PM10-rec, PM10-off | the separation after t 200 | 64 | 128 | 600–784 | 7 | dropped 2026-10-23: for the pair only the large box remains |
| M-t1000 (`M_L64_N192_t1000`) | "neither collapses nor disperses ... 1000 alone" | 64 | 192 | 1000 | 20 | **done** 10-25 11:07 MSK, back at N 192 (the paper's N 128 run lost 5.4 % of its peak field by t 1000): the peak field +0.11 % by t 1000, the star's matter −2.3 %; the core moves 0.12 toward the centre, almost all after t 400 (N 128: 0.14); Ham (r < 24) ×3 to t 400, then falling (1.35 × 10⁻⁶ at t 1000), Mom flat; identical to M N 192 to t 200; no NaN; frames and movies in the run tree, not packed; `02_lone_star/` |

Queue empty: every run for the paper is done (the last, M-t1000, at 11:07 MSK 10-25), filed and packed.
Decided 2026-10-23: the pair ends with PM10-t400 and the large box (PM10-rec / -off dropped). **Decided 2026-10-24:
every simulation the paper keeps is rerun**, no checkpoints, as the cards free; the same-sign pairs and the numerics
are checks, not a convergence study. Dropped from the paper: S0.75–S0.90, PM10-rec / -off, PM10-tol / -AMR /
-η2, and PP10 / MM10 at N 192 and 256. Launch scripts in `staging/`, each from its v1 cell; the dropped ones in
`runs/bondi/00_archive/dropped_2026-10-24/`.

Extra (10-24), in the paper since 10-26 (Sec. V G, Table I row PM10-rec): `PM10-rec_L64_N192_t1000`, the
recentring chase (v1 PM10-rec) at N 192 to t 1000;
no solve (PM10 N 192's data, identical to PM10_L64_N192 until the first shift, t 167); frames, no checkpoints.
**Done** 10-25 05:41 MSK on the second node (`04_runaway/`): both stars accelerate forward to t 1000 (v1 at N 128:
the trailing star turned back near t 530 and d reached 24 by t 700, while its matter doubled). d 10.02 at t 200,
10.24 at 400, 10.91 at 600, 12.04 at 800, 13.47 at 1000: after t 400 the trailing star accelerates ~9 % less than the
leader (0.62 against 0.68 × 10⁻⁴ over 900–1000), numerical (d(200) − 10 is 0.071 / 0.016 / 0.005 at N 128 / 192 /
256). Final v 0.115 c (leader) and 0.108 c (trailer), γ 1.006; the pair 63 units on (31 shifts); matter −2.7 %.
Ham (r < 24) ×3.9 over t 10–1000, flat after t 600 (r < 12 ×2.9 to t 600, then flat; 12–24 still growing), Mom flat,
the worst point flat at 4–5 × 10⁻⁵; no NaN. Frames and movies in the run tree, not packed.

## Live

No runs live (10-25): card 0 of both nodes is free; scratch clean on the second node.

## Revision

### 1. Text (workstation)

Done 10-22 (pdflatex and lualatex both build, 13 pages): every presentation point of the GRG reports, mapped to
WRITING_STANDARDS §1–7 (title, abstract, symbols defined at first use, private vocabulary out, the five tests before
the results, Table I setup / Table II results, one number per claim, conclusions with a scope paragraph, captions),
an outside-reader pass (~60 findings applied) and a redundancy pass (text 6608 → 6191 words).

Rerun-numbers pass done 10-26 (both engines build, 14 pages): every number, Table I (24 simulations) and Table II,
and the captions of Figs. 3–9 carry the rerun values; Tables I and II keep only the kept runs (no -tol / -AMR /
-η2 / -off / S0.75–S0.90; PP10 / MM10 at N 128, merger t 34.4 / 33.6, centroids at round-off). Sec. VII A quotes
Q_meas = 6.9 between Q₄ = 5.9 and Q₅ = 8.7 (ΔX order 4.4, a 4.2; Richardson 2.89 and 1.46 × 10⁻⁴, inside the
192–256 error bars), which closes WRITING_STANDARDS' open item on the non-convergent v1 base grid. App. A is
rebuilt around Figs. 10–11 (the boundary-transient explanation is gone). Sec. III A describes the profile's
analytic exterior (isotropic Schwarzschild, lapse joined in value and slope, the 1.9 % field tail) and the
superposed lapse in Π. The separation is quoted by the cores (0.05 %; proper 0.15 %; Sec. V A says the barycentre
gap dips 2.5 % near t 50 as the stars shed field). PM10-L128 is quoted by cores (+0.3 %) and barycentres (−4.8 %)
with the shed-field reading; Ψ4 is R^−4.7, ×30. New Sec. V G "Evolution to t = 1000": PM10-rec is in the paper
(0.115 c / 0.107 c at t 1000 from the treadmill odometer, a 1.42 → 0.70 × 10⁻⁴, d 10.0 → 13.5, read as truncation
error) beside M-t1000 (peak +0.11 %); the abstract notes the tenth of c, and momentum is 0.1 % (N 256).
Decided 10-26: no notation table — every symbol is defined at first use, and a table would repeat Secs. II–IV.
Setup-fix notes 10-26 (from "What was wrong", as the pitfall notes WRITING_STANDARDS §3.6 allows; 15 pages now):
Sec. IV carries the per-stage FillPatch pitfall (first order in Δt, amplified oscillation, shows only in the
constraint orders); Sec. III A why the lapse join must be smooth (a 5 × 10⁻⁵ step passes every t = 0 check and
becomes a growing momentum violation); Sec. III B the solver–painter matter agreement (a mismatch is a t = 0
floor no resolution removes), the face-layer copy, and that the corrected data enter at the solve's order 2.0.
Audit pass 10-26 (four checks: numbers against the pack, figure provenance, WRITING_STANDARDS, repetition; 13 pages,
both engines; GRG's Declarations block, funding, competing interests, data and code availability, replaces the Data
availability section; the appendix float sits in Sec. VII A, so it prints before the references): the August star-table M₋ and M₊+M₋ become the solver's −0.014293 and 5.7 × 10⁻⁵; the signed momentum
is below 0.5 % for t ≥ 5 (not 0.1 %), the residual falls ×49 from N 128 to 256, P's central lapse moves 7 × 10⁻⁴,
the peak field < 0.3 %, the separation 0.05 % everywhere, the trailing star 0.108c, the zero crossing 0.99 ± 0.02
(the code had hard-coded the v1 centre); the setup notes are stated as the final setup (no chronology), CTTK, κ, η,
σ, α∞, Δx, ℓ and r defined, captions end with their outcome, about 170 words trimmed.

- [x] The five videos are on YouTube (links in `movies/youtube/README.md`, 310bddff); the captions carry them and
      Video 5 (the t 1000 chase) is linked in Sec. V G (10-26).

Referee-style audit, second pass (10-26, a simulated PRD referee; GRG-irrelevant items skipped): Pi_s defined with
its imaginary t = 0 value and S_i = 0 stated; Box, delta_ij, body ADM, the norm symbols ||H||_2 / ||M||_2 defined;
Q_meas/Q_n displayed as Eq. (11); d redefined as the core separation, and Fig. 8(k) and the massscale curves now
plot the cores (the barycentre d hid the fourteenfold convergence behind shed field); E/R frequencies in Table II;
Sec. V G: Eq. (9) at the measured late-window d and matter predicts 0.87e-4, three quarters of the fall; Sec. VI
ref V A -> V B; forcelaw axes d_0, fit label Mbar; frames tag w_+ + w_-; wavezone/massscale 2.55 in, forcelaw 3.62,
samesign 2.78; captions and p. 12 text trimmed so the references end on page 13. Skipped: the full radial ODEs, a
notation table, the absorbing-layer loss sentence (the d_0 = 20 runs lose no more matter than PM10 at N 128).
- [x] Strip the one remaining TODO comment (the release's version DOI, Data availability): done 10-26.

### 2. Release and submission

- [x] Pack the reruns into `results/bondi-dipole-runaway/` (10-26): the 24 runs by group, the registry; the pack's
      README, LAUNCH.md, MATTER_MODEL.md and binaries.tsv rewritten for v2, and the GRTresna fix 9a85e6a in
      `patches/grtresna-solve-matches-painter.diff` (GRTresna is not in this repository; the paper's Code
      availability now names the fork). Bibliography (10-26): Bičák et al. Part II (self-accelerating, 390, 411;
      Part I as see also) and five preprints now published (Clough et al. OJAp, Nojiri-Odintsov, Trivedi-Loeb and
      Manfredi et al. Phys. Dark Univ., GRTresna JOSS), each checked on Crossref; still 13 pages.
- [x] Released 10-26: `feature/fix_bondi` into trunk (3b4117b0), trunk into develop without `research/` (3ba44705),
      release metadata (658bb941), tag and GitHub release `v2.0-bondi-dipole`; Zenodo ingested it within a minute:
      version DOI 10.5281/zenodo.23662692 under concept 10.5281/zenodo.23245933, which the paper's Data
      availability now cites.
- [x] arXiv v2 of 2608.24577 submitted 2026-10-26 as submit/8283157 (replacement), built from 7675b824: the package
      and form text in `arxiv_submission/` (local, excluded from git); 13 pages, five videos in `anc/`, both authors,
      comments ending with the v2 reason. Due for announcement Mon 26 Oct 20:00 ET (Tue 03:00 MSK).
- [ ] Journal submission: the GRG resubmission (full LaTeX source and PDF; the message and the point-by-point
      response above), on the same day as the v2.

### After Bondi

The merger paper (arXiv:2610.13206), withdrawn from GRG on 2026-10-22: its runs carry the same first-order stage
re-fill (BinaryWormholeMerger), so it needs the same single-star A/B before its writing pass and replacement.
