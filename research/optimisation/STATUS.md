# Campaign M — status

What is live, what is planned, the main results — nothing else. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` and
`grteclyn-wrapper/scripts/optimisation/` (layout in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)).
The page before this compaction (the campaign diary to 2026-10-29) is
`git show 96c177ee1:research/optimisation/STATUS.md`.

Remaining work is the **D21 3+1 triplet** (Azad comparison), now running. D51
evolution is parked. Dropped 2026-10-29: rotating 2D eigenproblem, further
2D-solver work, and extra matter recipes. Evolutions wait for the go.

## Live

D21 X 1.829, L 64, max_level 3, stop 150, checkpoints off. Binary
`main3d_matter_16460fb0`. Scratch: 32 GB in the three run dirs, 440 GB free.

| run | card | t | speed | ETA |
|---|---|---|---|---|
| `D21_X1p829_L64_N096_ml3_spdrv0_t150` | — | 87.5, NaN in h11 (level 3) | dead | — |
| `D21_X1p829_L64_N128_ml3_spdrv0_t150` | 0 | 46 | 20 u/h | ~5.2 h, ~01:56 MSK 30 Oct |
| `D21_X1p829_L64_N192_ml3_spdrv0_t150` | 1 | 23 | 5.0 u/h | ~26 h, ~22:15 MSK 30 Oct |

N 96: R_eq 4.063→3.108 (−24%); MOTS R 4.034→3.489, growth τ~9 at t=50–70 then the MOTS rate died while R_eq kept falling. N 128 is now alone on card 0.

## Planned (nothing launches without the go)

D51 X 1.606 triplet stays written, not launched.

## Main results

**Symmetric family, joint bill + radial-stability CMA-ES** (2026-10-28; best
clean, screened stable unless noted), vs classical V = 0:

| v_e | X | vs V = 0 | knobs (m, q₁, q₂, q₃) |
|---|---|---|---|
| 0.27 | 1.63372 | −45.4 % | 0.855, 3.232, 3.776, −0.256 |
| 0.50 | 1.49461 | −43.1 % | 0.864, 4.606, 0.559, −0.806 |
| 0.85 | 1.09759 | −24.9 % | 0.425, 2.438, 4.267, 0.445 |

Classical X: 2.99352 / 2.62527 / 1.46184. Frontiers −47.8 / −45.6 / −27.0 %.
The v_e 0.50 loop-best (X 1.47714, −43.7 %) had an open twin and is not the
screened number. Bill-only Nelder–Mead was −32.0 / −35.4 / −26.2 %. Family-(b)
holds die at the far-side puncture at t ≈ 23, so these are not the 3+1 targets.

**Drainhole (the 3+1 family).** Classical spinning X: D21 4.64453, D51 3.39986,
D90 0.59955. D21 CMA-ES (pure kink start, 400 evals): search-best X 1.78483 (−61.6 %) did
not clear. Winner after the finer-grid check: e140 X **1.8287958015** (−60.6 %
vs $V = 0$) at m 1.023, q (0.672, 0.048, 0.310), 210×42 PASS, E19 1.6e-10.
Also clean: e5 X 2.357928 (−49.2 %). A new CMA best is kept only after it is
re-solved on the next finer grid; the 1e-8 cutoff on the search grid does not
do this (the failed 1.785 was already 1e-10 there).
Cleared for evolution: D51 smoke X **1.6061738698** (−52.8 %), unchanged to
4e-15 over 150×30 → 180×36 → 210×42 (E19 6e-9–3e-8, dense-solve floor). Not
cleared: D30 clean X 1.693 and D51 frontier X 1.505 (stalled on the first finer
grid). D90 search not run.

**Potential landscape.** Not flat. Shape + rays at m 0.3: best clean −27.3 /
−26.9 / −20.6 % at v_e 0.27 / 0.50 / 0.85 vs V = 0; no bottom found (Newton or
the monitor ceiling stopped every ray). γ to −π costs ≈ +42 % at every spin.
The 4-knob optimizer then the joint CMA-ES produced the table above.

**Radial screen** (J = 0, m = 0; two-grid match; rotating 2D dropped). Drainhole
gate λη₀ = 0.3898 vs published 0.390. Classical symmetric Ellis λη₀ = 1.182.
Every kink and winner background: no unstable radial mode up to nx 300.

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
- [ ] 9. Evolve the winners — **remaining work.** D21 X 1.829 triplet live; D51 parked.
- [ ] 10. Publish.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- CMA-ES: a point becomes the best only after a re-solve on the next finer
  grid. The search-grid residual alone does not clear it.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
