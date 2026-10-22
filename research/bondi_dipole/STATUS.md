# Bondi dipole paper — status

One page, current only. Paper: [`bondi_dipole.tex`](bondi_dipole.tex), arXiv:2608.24577 (v1). Data:
[`results/bondi-dipole-runaway/`](../../results/bondi-dipole-runaway/README.md), tag `v1.0-bondi-dipole`. Code:
`Examples/RadialRecipe/`, launcher `grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh`. Runs:
`runs/bondi/` (untracked). Writing rules: [`../WRITING_STANDARDS.md`](../WRITING_STANDARDS.md). Branch
`feature/fix_bondi`, cut from `feature/spinning` on 2026-10-22 (develop carries no `research/`; its code is the same).

## Journal trail

- PRD, then CQG: rejected (dates not recorded).
- GRG: sent to review, rejected 2026-10-20 on presentation (undefined symbols and lab vocabulary, too many numbers,
  no convergence test), no invitation to resubmit. The reports are kept locally only, in `referee/` (git-excluded).
- Next: EPJC (open access through SCOAP3; confirm it charges no APC), fallback IJMPD.

## REVISION (from 2026-10-22)

Two tracks in parallel: the text on the workstation, the convergence runs on the cluster. Tick each item as it lands.

### What the packed data say

The runs are uniform-grid (one level), so the pack's boundary-masked norms (`L2_Ham_amr`, `L2_Mom_amr` in each run's
`constraint_norms.dat`) already cover the whole grid. Order between the d₀ = 10 runs, N 128→192 / 192→256, where
the code's order is 4:

| | t 0 | t 10 | t 50 | t 100 | t 200 |
|---|---|---|---|---|---|
| Ham L0 | 1.7 / 0.3 | 0.8 / 0.4 | 1.5 / 1.1 | 1.5 / 1.2 | 1.6 / 1.3 |
| Mom L0 | −1.4 / −1.3 | 1.5 / 0.2 | 1.4 / −0.6 | 1.6 / −0.3 | 1.7 / 0.4 |
| ΔX: Q_meas (Q₂ 2.86, Q₄ 5.94) | – | −0.1 | −3.8 | −6.7 | −10.8 |

- Neither convergence test passes. The constraints converge at order 1.5 at best, and the momentum constraint stops
  converging between N 192 and 256. ΔX is non-monotone from t 50 on, so N 128 is outside the convergent regime.
- The rise of the domain-wide Hamiltonian norm at t = 0 (2.0 → 3.7 → 5.6 × 10⁻⁴), which App. A and Fig. 4(b)
  attribute to the solve-to-evolution transfer, sits in the box's outer boundary layer: the boundary-masked norm
  falls (2.1 → 1.1 → 1.0 × 10⁻⁶). That explanation goes.
- No plotfiles of these runs survive, so any new norm needs new runs.

### 1. Text (workstation)

Every presentation point of the GRG reports maps to WRITING_STANDARDS §1–7 and its Bondi open items. Done
2026-10-22 (pdflatex and lualatex both build: 13 pages, no overfull boxes, no undefined references):

- [x] Title in normal case; Nachevsky co-author; acknowledgments as in the spinning paper. Abstract rebuilt from
      WRITING_STANDARDS' draft: no undefined symbol, two result numbers, the scope at the end.
- [x] Defined at first use: ADM, NEC, rms, CCZ4, m, λ, μ, ψ, α, K, χ, ρ / Sᵢ / Sᵢⱼ (as projections), a, d, M̄, X,
      ΔX, P, Q. Diagnostics are numbered equations (barycentre, midpoint, fit, Bondi's law, momentum).
- [x] Private vocabulary out of the text and the figure labels (`article_figures.py`): campaign, cell, run matrix,
      rung, ladder, mass-matched, repainted, bicomplex, gap, birth kick, twin, verdict, certifies, nulls, deeper
      solve, box doubling, hill / well, dressed. "Phantom" survives only in its usual meaning (cosmology, ghost
      fields); our sectors are the positive- and negative-mass fields Φ₊, Φ₋.
- [x] Sec. II: the consistency argument has its own paragraph right after the action, tied to the NEC.
- [x] The five tests (Sec. IV C) come before the results; each results subsection opens with its question.
- [x] Table I is the setup (34 simulations, labels PM10, R0.60, E1.34, …); Table II holds the results.
- [x] Results: one number per claim, the rest in Table II; no chronology, no bold sentences. Convergence moved to
      Sec. VII.
- [x] Conclusions as a passage with a scope paragraph; "What is not established" is gone.
- [x] Captions rewritten: what is plotted first, one outcome sentence last.
- [x] App. A: the transfer-residual explanation is gone (the t = 0 rise is the outer boundary layer); App. B (cost)
      folded into Sec. IV A. Fixed on the way: the L = 128 run has Δx 0.50, not 0.25.
- [x] Data availability statement (concept DOI for now).
- [ ] Notation table: about 20 symbols, so WRITING_STANDARDS §2 asks for one. Decide whether it is worth the space.
- [x] Outside-reader test (2026-10-22): a fresh agent reviewed the paper against WRITING_STANDARDS as a PRD referee;
      its ~60 findings are applied (signed mass dipole used consistently, CCZ4 / CTTK / AMR / shift defined at first
      use, a parameter table, E / R / S labels explained, one word per position diagnostic, long sentences split,
      precision matched to the error bars). Kept on purpose: British spelling (EPJC takes either, consistently) and
      the question that opens each results subsection (§6).
- [x] Redundancy pass (2026-10-22): a fresh agent listed what the paper says twice; 24 of its 25 cuts applied (the
      introduction keeps its scope sentence, §5). Abstract 234 → 182 words, text 6608 → 6191 words; still 13 pages,
      which the full-width floats set.
- [ ] After 2b: the convergence paragraph of Sec. VII A, App. A and Fig. 6(b) / Fig. 10 from the new runs (TODO
      comments in the tex; strip all comments before the arXiv upload).

### 2. Convergence (cluster)

**Live**: none. The three 2a cells ran on the first GPU node on 10-22 (done N 128 13:13, N 192 13:41, N 256 15:08
MSK; 207 / 49 / 16 units/h), all to t 20 with no NaN and their scratch cleared. Each reproduces its archived run over
t ≤ 20 to 1 % (L2 norms) and 1.5e-6 (Linf_Ham_amr). Run dirs `runs/bondi/staging/conv2a_*`, each with its `launch.sh`
(diffed against the old cell: only the stop time, frames off, the binary, solve ranks and timeout change) and its t = 0
split in `t0_constraints.log`. The solve stops at 0.002 % × (128/N)⁴ relative error (16 Newton iterations at N 256).
No checkpoints. Scratch on the node: empty (the 29 GB of two dead spinning runs' plotfiles wiped 10-22 on the word).

- [x] An interior norm in `Examples/RadialRecipe` beside the boundary-masked one: drop the outer boundary layer and
      the sponge (r > 24), as `SpinningWormhole`'s `constraint_norms_levels` does. Rebuild and record the binary.
      Code reaches the nodes only by push and pull.
      Done 10-22 (8d0771d4): `constraint_norms.dat` cols 18-19, `L2_Ham_int` and `L2_Mom_int`, are the
      boundary-masked norms (cols 12-13) restricted to r ≤ `constraint_norms_interior_radius` (default: the sponge's
      inner radius, 24). Binary `runs/bondi/bin/main3d_intnorm_37ae5be1_2026-10-22.ex` (sha256 f5ca01e5fb417458,
      AMReX 26.02-12-gd7da5045, nvcc 12.1, sm_90). It is stamped 37ae5be1, the same commit before the rebase onto
      the paper commits: Source/, the example and Tools/GNUMake are identical in 8d0771d4. `run_pair_selfgrav.sh`
      takes it as `BONDI_BINARY` (unset: the example's own build, as every archived cell ran). Source/ has changed since the archived runs' a6d9dccb, so the
      2a runs' existing columns are checked against the archived rows over t ≤ 20.
- [x] 2a. Diagnosis: short runs (t ≤ 20) of the d₀ = 10 pair at N 128/192/256 with the interior norm, plus a CPU
      check of each initial-data set's t = 0 constraints. It finds what caps the order: the second-order GRTresna
      solve, a mismatch between the matter the solver used and the matter painted on the evolution grid, or
      under-resolved stars. Without it, N 320 may only reproduce order 1.5.
      Suspects found in the code (10-22), for the CPU check to size: the solve's Im Π divides by each star's own
      lapse, the painted Im Π by the summed lapse (the companion's α − 1 enters, independent of N); the solve
      interpolates the star tables linearly and differentiates the interpolant, the evolution paints a cubic spline
      and differentiates on the grid. The gridinit and the star tables are kept for it.
      Done 10-22. Orders N 128→192 / 192→256 from
      `grteclyn-wrapper/scripts/analysis/bondi_dipole/constraint_orders.py` (r ≤ 24 is the interior norm, "box" the
      boundary-masked one):

      | | t 0 | t 5 | t 10 | t 15 | t 20 |
      |---|---|---|---|---|---|
      | Ham r ≤ 24 | 1.9 / 1.6 | 2.3 / 0.6 | 1.7 / 1.1 | 1.6 / 1.1 | 1.5 / 1.2 |
      | Mom r ≤ 24 | −1.5 / −1.4 | 1.7 / −0.8 | 2.2 / 0.2 | 2.4 / 0.9 | 2.4 / 1.4 |
      | Ham box | 1.7 / 0.3 | 0.9 / 0.3 | 0.8 / 0.4 | 1.1 / 0.6 | 1.3 / 0.7 |
      | Mom box | −1.4 / −1.3 | 0.9 / 0.3 | 1.5 / 0.2 | 1.9 / 0.4 | 1.6 / −0.3 |

      The t = 0 split (`t0_constraints.py`, L2 over r ≤ 24, N 128 / 192 / 256): total 4.1 / 1.9 / 1.2 × 10⁻⁶; the
      solve's second-order truncation error 3.5 / 1.6 / 0.94 × 10⁻⁶ (order 1.9); the Im Π lapse 4.55 × 10⁻⁷ and the
      table derivative 3.5 × 10⁻⁷ at every N (order 0); the grid gradient of the painted stars 7.4 / 1.7 / 0.57 × 10⁻⁷
      (order 3.6–3.8: the stars are resolved). The solve's own residual comes out at 10⁻⁹–10⁻¹⁰, so the split
      reproduces the solve's matter.
      Verdict: the solve caps the order at 2. The two fixed mismatches are half the t = 0 total by N 256, which fits
      the interior order falling to about 1 between N 192 and 256. The momentum constraint's first-step jump grows
      with N (r ≤ 24 at t = dt: 0.6 / 1.1 / 1.7 × 10⁻⁶, from 10⁻⁸ at t = 0), so something injects grid-scale error;
      the likeliest source is the table derivative, whose error is a sawtooth at the table's spacing sampled at the
      grid points. The box norms are held down by the region outside r 24, where the sponge acts; the order is read
      inside r ≤ 24.
- [ ] 2a-fix (proposed 10-22, waiting for the go). In the GRTresna solve's matter: Im Π with the summed lapse
      1 + Σ(α_k − 1), as painted, and |∇φ|² from the profile's exact (spline) derivative. Then re-solve N 128/192/256
      and rerun the t = 0 split: the two terms must vanish and the total keep order 1.9. Before 2b, which otherwise
      inherits the fall to order 1.
- [ ] 2b. The resolution study N 192/256/320 (Δx 0.33/0.25/0.20) at L 64 to t 200. A rerun is its old run: start
      from `campaign/runaway_pair_d10_L64_N256_lev0` (`evolution_params.txt`, `launch_config.sh`) and change only N,
      the Δx-scaled solve tolerance and the diagnostics. N 320 needs about 94 GB, so it runs on both cards of the
      two-H100 node; its 640³ GRTresna solve takes about 10 h on 24 CPUs and runs under a per-process memory cap
      (CLAUDE.md, the OOM rule). Roughly 2 days and 50 GPU-h in all. Expected Q₂ 2.16, Q₃ 2.81, Q₄ 3.66.
- [ ] Paper: a convergence appendix with the rescaled ΔX differences and the rescaled Hamiltonian and momentum norms,
      the order stated in words. The N 128 scans stay, quoted as ratios with the base-grid offset stated.

### 3. Release and submission

- [ ] Merge into develop without `research/`, tag (e.g. `v1.1-bondi-dipole`), GitHub release, then Zenodo
      "Sync now" (CLAUDE.md, Publishing) and check the version DOI under concept 10.5281/zenodo.23245933.
- [ ] arXiv v2 of 2608.24577: account page → Articles You Own → Replace icon → upload the full source again (tex,
      bbl, figures, `anc/` movies) → compiler **pdflatex** → update the abstract and comments ("v2: presentation
      revised, convergence study added") → submit. Same identifier; v1 stays visible. The monthly cap counts new
      submissions only (two per calendar month, three active); replacements have their own limit, one per week
      after v5.
- [ ] Journal submission (EPJC), on the same day as the v2.

### After Bondi

The merger paper (arXiv:2610.13206), withdrawn from GRG on 2026-10-22: the same writing pass, then its own arXiv
replacement and the next journal.
