# Campaign M — status

What is live, what is planned, the main results — nothing else. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` and
`grteclyn-wrapper/scripts/optimisation/` (layout in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)).
The page before this compaction (the campaign diary to 2026-10-29) is
`git show 96c177ee1:research/optimisation/STATUS.md`.

Remaining work is **3+1 GRTeclyn evolutions** of the cleared bare-field tables.
Dropped 2026-10-29: rotating 2D eigenproblem, further 2D-solver work, and extra
matter recipes (layers, winding, focusing, onions, corridor, double throat,
charge). Every evolution waits for the go.

## Live

No run is live. Cards idle. Scratch: 47 MB cache, 482 GB free; D51 plotfiles wiped
(frames kept).

**Last finished:** `D51_X1p606_smoke_t005` (card 0, 2026-10-29 08:12 UTC, exit 0,
no checkpoints, no NaN). t 5.01 at 20.0 u/h. After startup Ham/Mom +0.007 % /
+0.047 %, throat +3e-6, max |K| 3.0e-4. t = 5 is too short to claim physical
stability (classical D51 inflates ~t 70–100). 98 frames + 98 slice-cache npz kept.
Binary `main3d_matter_9c16a55b_2026-10-29.ex`.

## Planned (nothing launches without the go)

**D51 X 1.606 3+1 triplet**, the spinning 0.2c / D51 recipe (templates written,
not launched). L 64, max_level 3, σ 0.1, min_chi 1e-8, drive off, farfix keys,
stop 150, plot every t = 1.0 (interval 75 / 100 / 150). Same table as the t = 5
smoke. Binary `main3d_matter_9c16a55b_2026-10-29.ex`. Profile `hold` (not the
smoke profile: need MOTS + ψ4 + throat spheres). `--subdir convergence`. N 192
adds `--mots-spectral-steps 150`. Checkpoints off unless asked. Do not start
from the t = 0 templates (`shift_advec_coeff = 1`, missing farfix).

```
LAUNCH=grteclyn-wrapper/scripts/campaigns/optimisation/launch_evolution.sh
BIN=runs/spinning_wormhole/bin/main3d_matter_9c16a55b_2026-10-29.ex
# N 96 / 128: --template params_D51_X1p606_L64_N096_ml3_spdrv0_t150.txt
#             --name D51_X1p606_L64_N096_ml3_spdrv0_t150 --gpu N --profile hold
#             --zoom 32 --center 32 32 32 --subdir convergence --binary $BIN
# N 192: same, plus --consume-args with the hold flags and --mots-spectral-steps 150
```

Classical D51 comparison is the packed spinning run (N 128 died inflating at
t 100, trust 95). No other tables: D30 X 1.693 and D51 X 1.505 did not clear
the finer grid.

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

**Drainhole (the 3+1 family).** Classical spinning X: D51 3.39986, D90 0.59955.
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
- [ ] 9. Evolve the winners — **remaining work.** D51 t = 5 smoke finished.
- [ ] 10. Publish.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
