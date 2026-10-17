# Spinning-wormhole campaign — status

One page, current only (packed 2026-10-17; everything before is in
`git show ab899cc5:research/spinningwormhole/STATUS.md`). Plans:
[`SpinningWormhole.md`](SpinningWormhole.md) (paper; its §6 holds the article notes that lived here),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`
(one outcome line per run in `runs_registry.tsv`). Branch `feature/spinning` (pushes to `myfork`).

**Folders** (decided 2026-10-13): `runs/spinning_wormhole/<family>/<NN_study>/` mirrors
`results/spinningwormhole/campaign/<family>/<NN_study>/`; superseded runs go to `<family>/00_archive/`.
Shared: `backgrounds/ bin/ logs/ manifests/ smoke/ templates/`. Launch with
`launch.sh --subdir <family>/<NN_study>`; pack with `research/spinningwormhole/pack_run.sh <family>/<NN_study> <run dir>`.

## STATE (2026-10-17 ≈ 18:00 MSK)

**Every run before 10-17 carries three numerics bugs, all found and fixed 10-17**, so every paper run reruns:
1. The background table was interpolated bilinearly, so its 4th-order second derivatives grew with N.
   Fix: C2 spline (faadc95e, the default).
2. AMReX's `cell_quartic_interp` stores its weights rounded (sum 1 − 2e-8): every coarse–fine ghost came out
   6e-8 low, 6e-8/h² under the second derivatives (order −1.5 on levels 1–2). Fix: `CellQuarticExact`, the
   exact weights (35, −252, 1890, 420, −45)/2048, key `exact_quartic_interp = 1` (1380067f, 16228dcd).
   Candidate for an upstream AMReX PR.
3. The example's `specificEvalRHS` re-filled the whole RK stage from StateData: the half-step stages saw the
   average of the old state and the stage, and AmrLevel::RK's stage-consistent ghosts were overwritten
   (first order in time at the coarse–fine edges; Mom order ≈ −2 on levels 1–2). Fix: key
   `rk_stage_refill = 0` (0661dac4); upstream BinaryBH has no re-fill. The merger, RadialRecipe and
   SupportedWormholeCollapse examples carry the same re-fill (other campaigns' code, not changed here).

**Verified with all three fixes** (t 0.5 checks, `03_t0_checks/t0rk0_*`, `t0mask_*`; N 128 → 192 at t 0.49):
the 0.2c converges on levels 1–3 (levels 1–2 +2.0 to +2.2, throat level +3.8); the 0.9c on levels 1–3 with
`constraint_norms_mask_radius = 0.75` (levels 1–2 +2.3 to +3.1, level 3 +3.7 to +3.8; its Ham_3 drops from
3.5e-4 to 1.4e-8, the χ-floored core r < 0.6 was the whole 0.125-mask norm). The sponge drive is not involved
(drive off = identical). Still not converging, outside the measured physics: level 0's outer ~4 units (the
Sommerfeld box face, inside the sponge shell; level 0 inside r 24 converges).

**Open**: does the drive keep the border clean late (the pair below, pre-fix binary; the face error does not
depend on the fixes)? The dt 0.02 ceiling and the σ choices came from an "interface mode" on the coarse–fine
box edges measured with bugs 2–3 in place — retest dt 0.05 on the fixed binary after the triplets. The
pre-fix 0.9c N 96 throat measure read +13–17 % after t ≈ 79 — settle it on the fixed triplet.

## PAPER-RUN SETTINGS (decided 2026-10-16; fix keys 2026-10-17)

- Grid: L 64, N 128, max_level 3 (dx 0.5 → 0.0625), sponge 24–32 (KO) + drive 1.0, dt_multiplier 0.02.
- **SLOW (≤ 0.5c)**: σ 0.1, min_chi 1e-8, stop 85. **FAST (0.7c+)**: σ 0.4, min_chi 1e-4, stop 150.
- Binary `main3d_rkfix_0661dac4_2026-10-17.ex` with `exact_quartic_interp = 1`, `rk_stage_refill = 0`;
  the fast runs also `constraint_norms_mask_radius = 0.75`.
- A rerun is its old run: the old packed params
  (`drainhole/00_archive/superseded_2026-10-17/<run>_pack/evolution_params.txt`) plus the fix keys, diffed
  before launch.
- ψ4 radii 14/18/30 (30 sits in the drive shell: reference only); full frame set; consumer keep-last 3; hold
  profile (throat spheres per plotfile); checkpoints asked per run; movies and quotes cut at each run's trust
  window. On the fast runs `throat_geometry.dat` is not a throat measure (its rays start inside the χ-floored
  core): use MOTS or `throat_spheres.dat`.
- Why this recipe (pre-fix runs): σ ≥ 0.2 kills the far-side puncture on the 1e-8 floor, the 1e-4 floor
  removes that failure, σ 0.1 slow runs hit Ham ×2 at t 78–85, dt 0.05 died on L128 spin data.

## PAPER RUN MATRIX — reset 2026-10-17: all NOT STARTED

The pre-fix runs (run dirs with frames, slice caches, movies, and their packs) are in
`runs/spinning_wormhole/drainhole/00_archive/superseded_2026-10-17/`. New runs launch with
`--subdir drainhole/00_paper_runs`. The triplets first; no kick run before both triplets pass (decided 10-17).

| ✓ | run | recipe | stop | cost | status |
|---|---|---|---|---|---|
| ☐ | 0.2c triplet N 96 | slow | 85 | ~4 h | NOT STARTED |
| ☐ | 0.2c triplet N 128 (= the paper 0.2c) | slow | 85 | ~9 h | NOT STARTED |
| ☐ | 0.2c triplet N 192 | slow | 85 | ~20 h, ~60 GB (a card alone) | NOT STARTED |
| ☐ | 0.9c triplet N 96 | fast | 150 | ~4 h | NOT STARTED |
| ☐ | 0.9c triplet N 128 (= the paper 0.9c) | fast | 150 | ~9 h | NOT STARTED |
| ☐ | 0.9c triplet N 192 | fast | 150 | ~34 h, ~67 GB (a card alone) | NOT STARTED |
| ☐ | 0c static anchor | slow | 85 | ~9 h | NOT STARTED |
| ☐ | 0.5c | slow | 85 | ~9 h | NOT STARTED |
| ☐ | 0.7c | fast | 150 | ~9 h | NOT STARTED |
| ☐ | 0.7c on the slow recipe (extra) | slow | 100 | ~9 h | NOT STARTED |
| ☐ | 0.99c | fast | 150 | ~9 h | NOT STARTED |
| ☐ | clamp validation (methods): σ 0.4 + min_chi 1e-4 + dt 0.05 at 0.5c | – | 100 | ~4 h | NOT STARTED |
| ☐ | kick 0.9c A1, kick 0.9c A2 (×10), kick 0.7c A1 | fast + seed | 150 | ~9 h each | BLOCKED until both triplets pass; templates not built |
| ☐ | 0.95c stretch | fast | 150 | ~9 h | optional, only if the 0.99c curve wants it |

Kick study (planned 10-16): as Evstafyeva–Siemonsen–East (arXiv 2508.11527), the stable 0.9c (A1 = the
merger seed's scale, A2 = ×10) and 0.7c (A1) with the Gaussian scalar seed (`spinning_seed_amplitude/width/
radius`), fast recipe, stop 150; discriminators: ring-down back to the hold or a triggered collapse, ψ4 at
R 14/18. The Π shell seed violates the constraints in proportion to its amplitude: decide on a
constraint-solved seed before templating.

## LIVE

| run | node/card | t | stop | speed | ETA (MSK) |
|---|---|---|---|---|---|
| sponge drive pair `07_sponge_fix/sptest_L64_N96_ml3_ve090a_drv{1,0}_t60` (pre-fix binary exq 16228dcd, no checkpoints): does the drive shell corrupt the border? | 1st, card 0 | 10.3 @ 17:54 | 60 | ~16.5 t/h | ≈ 10-17 20:50 (~3 h) |

## NEXT

- The two triplet reruns: waiting for the go and the checkpoint answer. Each N 192 needs a card alone (the
  0.9c on card 1; the 0.2c on the second node's card, from a session there, or after); the N 96 + N 128 pair
  of each spin takes ~39 GB on card 0.
- Second node (one card): idle since ≈ 12:19 MSK; its scratch still holds the 0.99c σ 0.4 run's 7.1 GB
  (prune needs a session there).

## DONE

- **Step 0** (10-11): the static hold twins the merger's `single_hold` (collapse, τ 5.27, trust t ≤ 64).
- **Step 1** (10-12): the O(J²) holds inflate; their push grew as J⁴, the data's error, not the spin.
- **Step 2** (10-13): full solver, both families to v_e 0.99, every gate green; CKK's eq. (12) is wrong;
  tables in `runs/spinning_p3/tables/` (error ≤ 1e-7 to v_e 0.9).
- **Step 3 t = 0 checks** (10-13 to 10-15): v_e 0.5 drainhole and the A1 family (b) ladder (21 runs,
  v_e 0.24–0.99 × N 128/192/256): throat radii, M and J against the tables.
- **10-17**: the three numerics bugs above, found by per-level constraint convergence and fixed.

**Campaign A (family (b) evolutions), dropped 2026-10-15.** Its compactified far end is a positive-mass
puncture; every hold died at t ≈ 23–24 whatever the lapse (√χ), resolution (max_level 4), shift damping
(η 0.2) or χ floor (1e-4): the death tracks the data, not the numerics (pre-fix runs). A return needs
excision at the far puncture, another gauge, or regularized data. Family (b) stays as theory and solver
validation (Step 2 gates, the A1 ladder). The full postmortem is in the STATUS above at ab899cc5; the A2–A4
run lists and templates at 2998819f.

## RULES

CLAUDE.md's launch discipline: go first, checkpoints asked per run, full frame set, STATUS pushed at every
launch, stop or wipe. ψ4 radii 14/18/30 on every spinning launch. Kick runs wait for both triplets.
