# Campaign M — status

What is live, what is planned, the main results — nothing else. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` and
`grteclyn-wrapper/scripts/optimisation/` (layout in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)).
The page before this compaction (the campaign diary to 2026-10-29) is
`git show 96c177ee1:research/optimisation/STATUS.md`.

Priority: **repair and revalidate the radial stability screen**. The 2026-10-30
audit withdraws the zero-instability labels; physical stability is unresolved.
The D21 3+1 triplet ended in NaNs at every resolution. D51 evolution remains
parked, and its exported background needs revalidation. Evolutions wait for the go.

## Live

Nothing running; audit jobs finished at 19:36 MSK on 2026-10-30. Both cards idle.
Second-node scratch: 21 GB leftover N192 (3 plotfiles), 47 MB cache, 455 GB free.
Dead N96/N128 plotfiles wiped 2026-10-30 (11 GB); frames kept.

| run | card | t | speed | ETA |
|---|---|---|---|---|
| `D21_X1p829_L64_N096_ml3_spdrv0_t150` | — | 87.5, NaN in h11 (level 3) | dead | — |
| `D21_X1p829_L64_N128_ml3_spdrv0_t150` | — | 97.7, NaN in A11 (level 3) | dead | — |
| `D21_X1p829_L64_N192_ml3_spdrv0_t150` | — | 112.2, NaN in h11 (level 3) | dead | — |
| `opt-d90` | — | 400/400, finished 16:43 MSK | done | — |
| `opt-s0` | — | 400/400, finished 18:04 MSK | done | — |

N 96 / N 128 / N 192 all died mid-plunge (R_eq −24% / −27% / −30%; MOTS R settled ~3.49, not the classical 2.52). Onset later at higher N (−1% at t=58 / 67 / 81).

## Drainhole CMA queue (card 0)

D0 finished 09:06 MSK. `opt-d30` finished 12:17 MSK. `opt-d80` finished 14:15 MSK.
`opt-d90` finished 16:43 MSK. Drainhole queue empty.
`opt-s0` finished 18:04 MSK. Symmetric queue empty.

## Planned (nothing launches without the go)

D51 X 1.606 triplet stays written, not launched. Its previous clearance is withdrawn.

## Validation audit — 2026-10-30

- **Background equations and bill:** 27 package tests pass. The independent symbolic
  Einstein/KG transcription, V = 0 reduction and N-row identity pass. D21 e140
  reproduces X = 1.828795801462 on a fresh 210×42 GPU solve, with E19 1.7e-10
  and E_c 5.3e-10; denser quadrature changes X by less than 5e-14. Off-grid
  constraint residuals remain small. The additional 220×44 solve stalled;
  240×48 exceeded GPU memory, so this audit adds no finer-grid clearance.
- **Stability labels withdrawn:** `optimize_potential.py` and `stability_screen.py`
  pass the physical potential to grid-unit backgrounds without multiplying V,
  V′ and V″ by the static solution's sigma². Restoring this factor makes the
  S0 screen return positive growth λη₀ ≈ 0.80 through nx = 300. Its mode still
  has substantial unused-constraint residuals (tt ≈ 0.11, tη ≈ 0.044 at nx 300);
  this is not yet a verified physical instability, nor evidence that every winner
  is unstable. `growth_rate` treats no matched eigenvalue as `stable=True`, and
  the optimizer ignores the static background's constraint verdict. Both must
  return an unresolved result when their checks fail.
- **Acceptance and export:** finer-grid checking is a separate script, not an
  automatic gate before `best_clean`/`best_stable` are saved. `grid_check.py`
  exports ABOVE-GATE solutions and unconditionally writes `lam_eta0 = 0` without
  a stability calculation. The D51 `evolution/verified/*smoke_210x42.npz` is such
  a file: X = 1.6061750110, E19 = 1.13e-4 and E_c = 1.56e-5. It must not be
  used as a cleared background. Newer optimizer dumps also store grid-unit
  R_e/R_A/R_pol as though physical; the radii need sigma before hand-off metadata.
- **Next:** correct the potential scaling and unresolved-mode handling; gate static
  backgrounds and eigenmodes on their unused equations; remove fabricated zero
  rates; gate exports and enforce separate grid checks; then rerun stability
  validation. Code is unchanged by this audit. Logs are under
  `runs/capped_jobs/opt-audit-*` on the second GPU node.
- **Paper blocked:** the draft's claims of eliminated radial instability, every
  model passing all four criteria, and sustained D21 throat survival are not
  supported. Revise these claims after the checks above; the exoticity reductions
  are separate measurements. Figure 1 now shows the actual search loop and the
  separate resolution/evolution checks.

## Main results

**Symmetric family, joint bill + radial-screen CMA-ES** (2026-10-28; search-grid
clean candidates, all stability labels withdrawn), vs classical V = 0:

| v_e | X | vs V = 0 | knobs (m, q₁, q₂, q₃) |
|---|---|---|---|
| 0 | 1.62676341 | −48.2 % | 1.198, 2.433, −0.046, 1.197 |
| 0.27 | 1.63372 | −45.4 % | 0.855, 3.232, 3.776, −0.256 |
| 0.50 | 1.49461 | −43.1 % | 0.864, 4.606, 0.559, −0.806 |
| 0.85 | 1.09759 | −24.9 % | 0.425, 2.438, 4.267, 0.445 |

Classical X: π / 2.99352 / 2.62527 / 1.46184. The v_e 0 search (2026-10-30, seed 111) frontier is 1.60271 (E19 5.6e-7); family 43 PASS, 142 FRONTIER. Not grid-checked. Frontiers at the three spins −47.8 / −45.6 / −27.0 %.
The v_e 0.50 loop-best (X 1.47714, −43.7 %) had an open twin and is not the
listed number. Bill-only Nelder–Mead was −32.0 / −35.4 / −26.2 %. Family-(b)
holds die at the far-side puncture at t ≈ 23, so these are not the 3+1 targets.

**Drainhole (the 3+1 family).** Classical spinning X: D21 4.64453, D51 3.39986,
D90 0.59955. Classical static (D0, J = 0) X 4.89835.
D0 CMA-ES (2026-10-30; kink x0, 400 evals, seed 101): search-best clean
X **1.83872766** (−62.5 % vs V = 0) at m 1.199, q (0.227, 0.485, 0.275),
E19 1.2e-10. Frontier 1.83854 (E19 7.9e-7). Family: 91 PASS, 54
FRONTIER (145 accepted npz). Not grid-checked.
D21 CMA-ES (pure kink start, 400 evals): search-best X 1.78483 (−61.6 %) did
not clear. Winner after the finer-grid check: e140 X **1.8287958015** (−60.6 %
vs $V = 0$) at m 1.023, q (0.672, 0.048, 0.310), 210×42 PASS, E19 1.6e-10.
Also clean: e5 X 2.357928 (−49.2 %). A new CMA best needs a separate finer-grid
re-solve before clearance; the optimizer does not enforce it. The 1e-8 cutoff
on the search grid is insufficient (the failed 1.785 was already 1e-10 there).
D21 area-pin + free-J CMA-ES (2026-10-30; 400 evals, seed 113, $J\in[0,4.13]$):
search-best clean X_A **1.78089377** (−62.0 % vs V = 0; −3.5 % vs the
4-knob D21 walk-in) at m 0.152, q (0.790, −1.199, 2.922), J 4.125,
$R_e/R_{\mathrm{pol}}$ 1.189, E19 1.2e-9. Frontier X_A 1.53867
(E19 8.2e-7). Family: 12 PASS, 146 FRONTIER. Not grid-checked.
D30 CMA-ES (2026-10-30; kink x0, 400 evals, seed 103): search-best clean
X **1.88040565** (−57.0 % vs V = 0) at m 0.740, q (0.607, 0.201, −0.664),
E19 1.3e-9. Frontier 1.84808 (E19 3.0e-9). Not grid-checked.
D80 CMA-ES (2026-10-30; kink x0, 400 evals, seed 105): search-best clean
X **1.10469483** (−22.2 % vs V = 0) at m 0.234, q (0.083, 0.504, 1.187),
E19 2.6e-10. Frontier 1.10396 (E19 1.1e-7). Family: 69 PASS, 72
FRONTIER. Not grid-checked. Classical V = 0 X 1.41924.
D90 CMA-ES (2026-10-30; kink x0, 400 evals, seed 107): search-best clean
X **0.787086131** (+31.3 % vs V = 0) at m 0.150, q (−0.337, 0.366, 0.445),
E19 8.7e-9. Frontier 0.78449 (E19 4.5e-8). Family: 71 PASS, 61
FRONTIER. Not grid-checked. Classical V = 0 X 0.59955. The kink search
did not beat V = 0.
**D51 clearance withdrawn:** the earlier smoke check reported X **1.6061738698**
(−52.8 %), unchanged to 4e-15 over 150×30 → 180×36 → 210×42, but both finer
rows took zero Newton iterations and were FRONTIER (E19 3e-8). The later
exported 210×42 file is ABOVE-GATE (audit above). Earlier D30 clean X 1.693
and D51 frontier X 1.505 also remain uncleared. Drainhole CMA queue is done.

**Potential landscape.** Not flat. Shape + rays at m 0.3: best clean −27.3 /
−26.9 / −20.6 % at v_e 0.27 / 0.50 / 0.85 vs V = 0; no bottom found (Newton or
the monitor ceiling stopped every ray). γ to −π costs ≈ +42 % at every spin.
The 4-knob optimizer then the joint CMA-ES produced the table above.

**Radial screen** (J = 0, m = 0; two-grid match; rotating 2D dropped). Drainhole
gate λη₀ = 0.3898 vs published 0.390. Classical symmetric Ellis λη₀ = 1.182.
The V = 0 drainhole gate reproduces 0.389823 in the audit. The potential-bearing
screen has the scaling and acceptance errors above; all previous zero rates
and the claim of no unstable mode up to nx 300 are withdrawn.

**Hand-off.** Seven-column table (B + `potential_coeffs`) and the kink potential
are in. N 96 / 128 / 192 t = 0 contract: Hamiltonian and momentum fourth order
after a derived-field Ham bug (plotfile `Ham` omitted V; fixed in
`main3d_matter_9c16a55b_2026-10-29.ex`). Validation holds to t = 1: throat
transfer improves with N, M to ≤ 1.2e-5, J to ≤ 1.2e-6.

## Steps

- [x] 1. Phantom unknown with a potential (V → 0 reproduces KK).
- [x] 2. Pin R_e and J; bill matches Fig. 3e; tidal gated. Transit/blueshift skipped.
- [x] 3. Potential-only science run at three spins; landscape not flat.
- [x] 4–8. Dropped 2026-10-29 except the bare-field hand-off, which is done.
- [ ] Revalidate stability and exported backgrounds — **priority; see audit above.**
- [ ] 9. Evolve the winners. D21 X 1.829 triplet dead (N 192 NaN at t 112); D51 parked and uncleared.
- [ ] 10. Publish.

## Future directions

- **Oblate throat and free spin (in, opt-in).** `optimize_potential.py --pin area` holds $A$ so $R_e/R_{\mathrm{pol}}$ can grow; `--free-J` adds $J$ as a fifth CMA-ES knob. Defaults stay the published 4-knob $R_e$+$J$ walk. Still open: $\theta$-dependent scalar profiles / equatorial focusing so the NEC violation is a ring, not a shell.
- **Driving $X \to 0$.** Topological censorship forbids $X = 0$ in classical GR, but $X$ can be pushed arbitrarily small toward the thin-shell limit ($m R_e \gg 1$) on finer spectral grids (bounded only by Chebyshev resolution and Ford–Roman quantum inequalities), or cut further by restoring canonical / winding partner fields ($\chi, \Lambda$) to carry mass and angular momentum while the phantom pays solely for the throat flare-out.
- **Pins.** Throat size ($R_e$ or $R_A$) must stay pinned, otherwise the optimizer shrinks the throat toward a black hole. $J$ stays pinned to isolate the potential's gain at each $v_e$, unless `--free-J` is on.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- CMA-ES: a search-grid best is provisional until a separate finer-grid re-solve.
  The search-grid residual alone does not clear it. A missing or rejected mode
  is unresolved stability, never a zero growth rate.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
