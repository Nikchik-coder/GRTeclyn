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

Every presentation point of the GRG reports maps to WRITING_STANDARDS §1–7 and its Bondi open items.

- [ ] Title in normal case. Abstract rebuilt from WRITING_STANDARDS' draft: at most three numbers, every symbol
      defined, the scope at the end.
- [ ] Define at first use, in the abstract and again in the body: a, d, M±, M̄, m, ψ, α, ρ / Sᵢ / Sᵢⱼ (the
      projections of the stress-energy tensor that source the Einstein equations), rms, NEC, CCZ4, ADM, Q, ℓ.
- [ ] Private vocabulary out (WRITING_STANDARDS §1): campaign, campaign pair, run matrix, cell, rung, ladder,
      mass-matched, repainted, bicomplex, gap, birth kick, twin, verdict, certifies, nulls / signal, deeper solve,
      box doubling; hill / well defined once. "Phantom" renamed, or defined once against its usual meaning.
- [ ] Sec. II: the consistency argument (negating the stress tensor is the only choice compatible with conservation
      of the total stress tensor and with field equations derived from the action) gets its own paragraph right
      after the action, tied to the NEC violation.
- [ ] The criteria before the results: what counts as the runaway, and what would falsify it.
- [ ] Table I split in two: the simulations (model label, d₀, masses, L, N or Δx, final t, role) and the results.
- [ ] Results: one number per claim, the rest into the results table or an appendix; no debugging chronology, no
      bold sentences, verbs scaled to the evidence. Every number that remains is printed by `article_figures.py`.
- [ ] Conclusions as a passage; "What is not established" becomes scope stated early.
- [ ] Captions: what is plotted first, one outcome sentence last, five lines or fewer.
- [ ] App. A: drop the transfer-residual explanation; show the boundary-masked norms.
- [ ] Data and code availability statement, citing the new release's Zenodo DOI.
- [ ] The WRITING_STANDARDS checklist and outside-reader test; both engines build.

### 2. Convergence (cluster)

- [ ] An interior norm in `Examples/RadialRecipe` beside the boundary-masked one: drop the outer boundary layer and
      the sponge (r > 24), as `SpinningWormhole`'s `constraint_norms_levels` does. Rebuild and record the binary.
      Code reaches the nodes only by push and pull.
- [ ] 2a. Diagnosis: short runs (t ≤ 20) of the d₀ = 10 pair at N 128/192/256 with the interior norm, plus a CPU
      check of each initial-data set's t = 0 constraints. It finds what caps the order: the second-order GRTresna
      solve, a mismatch between the matter the solver used and the matter painted on the evolution grid, or
      under-resolved stars. Without it, N 320 may only reproduce order 1.5.
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
