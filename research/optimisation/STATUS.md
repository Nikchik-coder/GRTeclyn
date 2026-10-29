# Campaign M — status

What is live, what is planned, the main results — nothing else. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` and
`grteclyn-wrapper/scripts/optimisation/` (layout in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)).
The page before this compaction (the campaign diary to 2026-10-29) is
`git show 96c177ee1:research/optimisation/STATUS.md`.

Remaining work is a **D21 table then its 3+1 triplet** (Azad comparison). D51
evolution is parked. Dropped 2026-10-29: rotating 2D eigenproblem, further
2D-solver work, and extra matter recipes. Evolutions wait for the go.

## Live

None. Both cards idle. Scratch: 47 MB cache, 482 GB free.

**Last finished:** `grid-d21-a` and `grid-d21-b` (2026-10-29 12:58 UTC, exit 0).
Cleared: e140 X **1.8287958015** (PASS on 180 and 210, X frozen) and e5
X **2.3579280305** (PASS on all three grids). Champion X 1.785 still not cleared.

## Planned (nothing launches without the go)

Ask before a D21 table at e140, then its 3+1. D51 X 1.606 triplet stays written,
not launched.

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
not clear. Cleared on the finer grids: e140 X **1.8287958015** (−60.6 % vs
$V = 0$) at m 1.023, q (0.672, 0.048, 0.310); e5 X **2.3579280305** (−49.2 %)
at m 0.355, q (0.037, 0.082, −0.458).
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
- [ ] 9. Evolve the winners — **remaining work.** D21 e140 cleared, 3+1 not launched; D51 parked.
- [ ] 10. Publish.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
