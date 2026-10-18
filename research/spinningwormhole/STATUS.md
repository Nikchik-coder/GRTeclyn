# Spinning-wormhole campaign — status

The current state, the main results so far and the paper notes (packed 2026-10-17; the full pre-pack text
is `git show ab899cc5:research/spinningwormhole/STATUS.md`). Plans:
[`SpinningWormhole.md`](SpinningWormhole.md) (paper), [`SpinningSolver.md`](SpinningSolver.md) (solver,
done). Code: `Examples/SpinningWormhole/` + `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed:
`results/spinningwormhole/` (one outcome line per run in `runs_registry.tsv`, trust windows in
`trust_windows.tsv`). Branch `feature/spinning` (pushes to `myfork`).

**Folders** (decided 2026-10-13): `runs/spinning_wormhole/<family>/<NN_study>/` mirrors
`results/spinningwormhole/campaign/<family>/<NN_study>/`; superseded runs go to `<family>/00_archive/`.
Shared: `backgrounds/ bin/ logs/ manifests/ smoke/ templates/`. Launch with
`launch.sh --subdir <family>/<NN_study>`; pack with `research/spinningwormhole/pack_run.sh <family>/<NN_study> <run dir>`.

## THE PAPER'S CLAIMS (decided 2026-10-18)

1. **Stability**: the fast-spinning throat is stable (the 0.9c farfix triplet holds to t 150; the kicks test it).
2. **Stability grows with spin**: the collapse slows as the spin grows and the fast throats hold (the ladder static →
   0.2c → 0.5c → 0.7c → 0.9c; onset times and τ from the reruns).
3. **A GW signal with no nonspherical perturbation**: the rotating collapse radiates (l 2, m 0) from unperturbed data,
   where the static wormhole needed a nonspherical perturbation to radiate at all. The far-zone waveform comes from
   one big-box run, the 0.2c on L 128 N 256 (PAPER RUN MATRIX); the L 64 runs' ψ4 at R 14/18 carries face junk
   from t ≈ 45 (below).

## STATE (2026-10-18 ≈ 13:05 MSK)

**Every run before 10-17 carries three numerics bugs, all found and fixed 10-17** (how: CONVERGENCE below),
so every paper run reruns on binary rkfix 0661dac4:
1. The background table was interpolated bilinearly. Fix: C2 spline (faadc95e, the default).
2. AMReX's `cell_quartic_interp` stores rounded weights: every coarse–fine ghost 6e-8 low. Fix:
   `CellQuarticExact`, key `exact_quartic_interp = 1` (1380067f, 16228dcd). Candidate upstream AMReX PR.
3. The example's `specificEvalRHS` re-filled the whole RK stage from StateData. Fix: key
   `rk_stage_refill = 0` (0661dac4). The merger, RadialRecipe and SupportedWormholeCollapse examples carry
   the same re-fill (other campaigns' code, not changed here).

**Verified with all three fixes** (t 0.5 checks, N 128 → 192 at t 0.49): the 0.2c converges on levels 1–3
(levels 1–2 +2.0 to +2.2, throat level +3.8); the 0.9c on levels 1–3 with `constraint_norms_mask_radius =
0.75` (levels 1–2 +2.3 to +3.1, level 3 +3.7 to +3.8). Both triplets are clear to rerun. Still not
converging, outside the measured physics: level 0's outer ~4 units (the box face, inside the sponge shell).
The pre-fix paper runs are archived (`drainhole/00_archive/superseded_2026-10-17/`); their results stay
below as the pre-fix record, to be requoted from the reruns.

**The far-zone junk is fixed** (FAR-ZONE JUNK below). Two causes, two fixes, both tested on the 0.9c L 128 N 128 to
t 10: the Γ-driver advected the rotating background shift (`shift_advec_coeff = 0`), and the flat-space Sommerfeld
faces sat at 5.5 M_ADM (`sommerfeld_relative_to_background = 1`). With both, the far zone is quieter than the inside.
The 0.9c L 128 triplet reran with both (`_farfix_t150`, binary farfix 891d817d, whose per-level norms also skip the
box's outer 3 cells: `constraint_norms_edge_cells = 3`) and PASSES: all three clean to t 150, every level converging
(orders under LIVE), throat areal radius flat to ≤ 7e-5, no MOTS. The 0.2c L 64 triplet runs with the same fixes
since 08:56 / 09:13 MSK 10-18. The Weyl4 frames blank the box's outer 2 cells (`--frames-blank-edge 2`, point 7).

## CONVERGENCE: HOW THE BUGS WERE FOUND (10-17)

1. **Symptom** (`constraint_norms_levels.dat`, r < 0.125 masked). 0.2c triplet: only the finest level
   (|x| < 4, around the throat) converged (order 3–4 from t ≈ 1; Ham 3.7/2.7, Mom 3.5/3.7 at t 20); levels
   0–2 grew with N (order −0.4 to −4). 0.9c: no level converged (−0.3 to −1.8 at t ≤ 2.4; N 96 → 128 at
   most +1 through t 150). Until fixed, the triplets rested on the throat size and the lapse only.
2. **Bug 1, the table** (≈ 13:45, CPU check on both tables, equatorial row). 4th-order FD second
   derivatives of the bilinearly interpolated f and nu_bar got WORSE with N on every level (−0.8 to −2.8):
   the atan map thins the table points at large radius, and FD second derivatives of a piecewise-bilinear
   field grow like (Δ_table/h)². A C2 cubic spline converges (+4.2 near the throat; +4.0 on levels 1–3 in
   xx, zz, xz of f, nu_bar, phi). The solver family is not at fault (the 0.9c table's spline FD: +4.0).
3. **Spline checks** (13:47, `03_t0_checks/t0spline_*`, both tables × N 96/128/192 to t 0.5). At t = 0 Mom
   converged on levels 1–3 (+2.2 to +3.7; bilinear −0.7 to −1.2 on levels 1–2), Ham on levels 1–2 5–100×
   lower; but Ham there still grew with N at t = 0 (−1.4 to −1.6, both tables) and Mom from the first step
   (≈ −2): a second, table-independent source on levels 1–2. Level 0 identical both ways (−0.4).
4. **Bug 2, AMReX's interpolation weights** (16:30, `t0cst_*`, Ham/Mom in the plotfiles, layer split). The
   growing level-1/2 Ham at t = 0 sat 100 % in the 3-cell layer along each fine level's outer boundary,
   where the ghosts are interpolated from the coarser level; bulk, equator, axis and the inner layer
   converged at +2.4 to +3.6; the 0.2c level-3 flattening at N 192 was the same layer (94 %). Cause:
   `amrex::cell_quartic_interp` stores its weights rounded to 8 decimals (0.01708984, −0.12304688,
   0.92285156, 0.20507812, −0.02197266), sum 1 − 2e-8, so every ghost is (1 − 2e-8)³ ≈ 1 − 6e-8 times the
   field, constants included: under the second derivatives a fixed jump 6e-8/h², order −1.5. Fix: the
   exact Lagrange weights (35, −252, 1890, 420, −45)/2048 (exact in binary), on the state and every derive.
5. **Exact weights verified** (17:00, `t0exq_*`). Every level converged at t = 0 (level 1 Ham up to 230×
   lower at N 192), the 0.2c throat level at +3.6 to t 0.5; but in the evolution levels 1–2 still grew
   (0.9c Mom unchanged, order ≈ −2; 0.2c 6–70× lower but growing), in the layers either side of the
   coarse–fine boundaries.
6. **Sponge drive cleared** (17:16, `t0spoff_*`): drive off is identical on levels 1–3 (level 2 to 4 digits).
7. **Bug 3, the RK stage re-fill** (17:23 0.9c `t0rk0_*`, 17:41 0.2c `t0rk0_J100_*`). The example's
   `specificEvalRHS` called `FillPatch` on the whole stage (valid cells too): RK4 keeps the stage in the new
   data, so the half-step stages saw (Uⁿ + U_stage)/2 (first order in time on paper), and AmrLevel::RK's
   stage-consistent ghosts were overwritten. Upstream BinaryBH has no re-fill. With `rk_stage_refill = 0`
   the 0.9c levels 1–2 converge in every layer (+2.3 to +3.1, 30–900× lower at N 192) and the 0.2c levels
   1–3 (levels 1–2 +2.0 to +2.2, 7–50× lower; throat +3.8).
8. **0.9c level 3** (17:58, `t0mask_*`): with the mask at r 0.75 it converges at +3.7/+3.8; its Ham_3 falls
   from 3.5e-4 to 1.4e-8 at N 192 — the χ-floored core (r < 0.6, the 1e-4 floor) was the whole 0.125-mask norm.
9. **Level 0, the box face** (`logs/t0rk0_layers_2026-10-17.log`, `t0rk0_level0_bins_2026-10-17.log`): at
   t = 0 only the outer 2 cells (Sommerfeld boundary, order −0.4); by t 0.5 spread ~12 cells in (r ≥ 24,
   inside the sponge shell; Mom −1.5 to −2 there); level 0 inside r 24 converges (+2.0/+2.5). Not fixed.
   Explained ≈ 21:00: FAR-ZONE JUNK below.

## FAR-ZONE JUNK: THE ADVECTED ROTATING SHIFT (found 10-17 ≈ 21:00)

From the stopped L 128 0.9c triplet's slice caches (z = 64, the full box; `frames/_slice_cache/` in the archived
run dirs):
1. **Symptom.** Π shows a ring at r ≈ 44–58 (the drive shell is 48–64), RMS 1.4e-11 at t 3, 1.2e-9 at t 9,
   ≈ 4e-8 peak by t 25, plus blobs on the box faces from t 1; K on the faces reaches 1.7e-4 RMS by t 9 (the
   throat's: 4.4e-4). Both are the same at N 128 / 192 / 256 (a continuum effect, not truncation), and level 0's
   constraints never converge. Inside r ≈ 44, Π and K converge at 3rd–4th order, and the stripes on the
   refinement-box edges shrink with N. The single-wormhole and merger runs never showed it.
2. **Cause 1, the gauge.** The 0.9c background shift rotates (|β| 0.17 at r 10, 0.04 at the face). With
   `shift_advec_coeff = 1` the Γ-driver's advection term β·∇β = −ω²(x, y), the centripetal term, is nonzero at
   t 0, so the shift moves inward everywhere from the first step, linearly in t. The measured change over t 0→1
   equals −ω²r at r 10, 30 and 46 to 1 %, at every N; χ and the lapse follow as t². By t 12 the shift near the
   throat has moved 2.3e-2 (≈ 25 %). A zero-shift background (the single wormhole, the merger) has β·∇β = 0. The
   sponge drive holds r 48–64 at the t 0 state while the inside drifts: the ring.
3. **Cause 2, the box.** M_ADM = 11.7, so the face at r 64 is ≈ 5.5 M: χ 0.71 and lapse 0.83 at the face centre
   (0.78 / 0.88 at the corner). The flat-space Sommerfeld condition is far off there and pushes junk in from t 1
   (χ in the outer 4 units moves 2.7e-4 by t 1, against 6e-7 just inside).
4. **Reach.** All 146 spinning templates carry `shift_advec_coeff = 1`: every hold with a rotating background,
   pre-fix ones included, drifted this way.
5. **Gauge fix: `shift_advec_coeff = 0`** (test `08_gauge_fix/advtest_L128_N128_ml3_ve090a_adv0_t10`, the stopped
   N 128 with only that knob, finished t 10.02, no NaN, packed). Against the stopped run at t 10: the shift drift
   is 3000× lower at the throat (6.7e-6 vs 2.1e-2) and 10⁵× at r 24–36, the χ drift 1000× lower; the constraint
   norms are unchanged on every level (the drift was pure gauge). The Π ring at r 48–52 fell 8× at t 3, but
   by t 10 the faces' junk fills the drive shell (Π at r 52–56 3.5e-9 in both runs, K at r ≥ 48 identical): the
   frames still show it. Adopt `shift_advec_coeff = 0` for every rotating hold.
6. **Face fix** (go 10-17; code f01991c8, binary `main3d_somref_f01991c8_2026-10-17.ex`): the Sommerfeld condition
   acts on (state − t 0 background), zero for the unperturbed wormhole, outgoing for perturbations. An optional
   reference state in `apply_sommerfeld_boundaries` via the virtual `GRAMRLevel::sommerfeld_reference()` (default
   none: other examples bit-identical); the spinning key `sommerfeld_relative_to_background = 1` returns the
   drive's `m_sponge_ref` (built for either knob, its ghosts filled across box edges). Test: the gauge test plus
   the key (`09_boundary_fix/bctest_L128_N128_ml3_ve090a_adv0_somref_t10`, finished t 10.02, no NaN, packed):
   **PASS**. Against the gauge test at t 10: K at r 60–64 4.8e-11 vs 1.9e-4, Π 5.2e-13 vs 1.7e-9, the shift drift
   3.8e-10 vs 2.3e-4, χ and the lapse there exactly constant; the drive shell (r 48–56) Π 100–1000× and K 10⁴×
   lower; the inside identical. Level 0's constraint norms stay at their t 0 values (Ham 1.15e-3, Mom 1.78e-6; the
   gauge test's Mom grew 7× by t 10): what is left there is the outer 2 cells' t 0 diagnostic (their derivative
   stencils reach the extrapolated ghosts, as Weyl4's do), not evolution.
7. **Weyl4 frames: the box's outer 2 cells blank** (decided 2026-10-17). Weyl4's 4th-order stencil reaches two cells
   beyond the box there, into first-order extrapolated ghosts: 2.4e-4 in the outermost cell and 1.8e-5 in the next,
   against 5.5e-7 further in, from t 0 in every run; it never feeds back into the evolution, but it set the Weyl4
   colour scale. The consumer flag `--frames-blank-edge CELLS` (frames/edge.py; default 0) draws those cells blank
   and caches them as NaN, so redraws and movies from the cache match; it is in every spinning profile
   (`_SWH_FRAME_TAIL`) and goes into every `--consume-args` launch. On the boundary test's t 10 plotfile the Weyl4
   colour scale fell from 2.6e-4 (the strip) to 6e-5 (the throat's field).

## PAPER-RUN SETTINGS (decided 2026-10-16; fix keys 2026-10-17)

- Grid: L 64, N 128, max_level 3 (dx 0.5 → 0.0625), sponge 24–32 (KO) + `sponge_drive_strength = 1.0`
  (a physics-neutral absorber; makes L64 viable past t ≈ 64), dt_multiplier 0.02.
- **SLOW (≤ 0.5c)**: σ 0.1, min_chi 1e-8, stop 85 (brackets the 78–85 knee; quotes t ≤ 80). Everything that
  collapses does so by t ≈ 64, and the throat stays unclamped for the quoted τ.
- **FAST (0.7c+)**: σ 0.4, min_chi 1e-4, stop 150. The claim is long-time stability; σ 0.1 recipes NaN
  there, and floor + σ 0.4 holds the 0.9c flat. σ 0.4 is safe because the floor forbids the χ depth it kills.
- Binary `main3d_rkfix_0661dac4_2026-10-17.ex` with `exact_quartic_interp = 1`, `rk_stage_refill = 0`;
  the fast runs also `constraint_norms_mask_radius = 0.75`.
- A rerun is its old run: the old packed params
  (`drainhole/00_archive/superseded_2026-10-17/<run>_pack/evolution_params.txt`) plus the fix keys, diffed
  before launch.
- ψ4 radii 14/18/30 (30 sits in the drive shell: reference only; 14 is the trusted waveform on this grid);
  full frame set; consumer keep-last 3; hold profile (throat spheres per plotfile); checkpoints asked per
  run; movies and quotes cut at each run's trust window.
- Stability protocol (adopted 10-13, after Evstafyeva–Siemonsen–East, arXiv:2508.11527): every quoted run
  is a triplet member or licensed by one; a growth is physical only if its τ converges to a nonzero value,
  the finest-level constraints converge while it grows, and the throat's areal radius or MOTS grows with it.

## PAPER RUN MATRIX — fresh campaign since 2026-10-17

New runs launch with `--subdir drainhole/00_paper_runs`. The triplets first; no kick run before both
triplets pass (decided 10-17).

| ✓ | run | recipe | stop | cost | status |
|---|---|---|---|---|---|
| ✓ | 0.9c triplet on L 128, N 128 `spin_hold_L128_N128_ml3_ve090a_spdrv1_sig04_farfix_t150` | fast | 150 | 3.4 h | FINISHED 10-18 02:55 MSK |
| ✓ | 0.9c triplet on L 128, N 192 `spin_hold_L128_N192_ml3_ve090a_spdrv1_sig04_farfix_t150` | fast | 150 | 5.4 h | FINISHED 10-18 04:52 MSK |
| ✓ | 0.9c triplet on L 128, N 256 (= the paper 0.9c) `spin_hold_L128_ml3_ve090a_spdrv1_sig04_farfix_t150` | fast | 150 | 9.7 h | FINISHED 10-18 09:08 MSK |
| ✓ | 0.2c triplet on L 64, N 96 `spin_hold_L64_N96_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | 3.3 h | DIED 62.59 10-18 12:12 MSK: the collapse (trust 55) |
| ☐ | 0.2c triplet on L 64, N 128 (= the paper 0.2c) `spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | ~10 h | LIVE |
| ☐ | 0.2c triplet on L 64, N 192 `spin_hold_L64_N192_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | ~20 h | LIVE |
| ☐ | 0.2c on L 128, N 256, the far-zone GW run (claim 3) `spin_hold_L128_ml3_J100_full_farfix_t100` | slow | 100 | ~7.5 h, 51 GB | PENDING (planned 10-18): go and checkpoints to ask; template ready |
| ✓ | 0c static anchor `static_hold_L64_ml3_spdrv1_t100` (in `00_archive/superseded_2026-10-17/`) | slow | 100 | 5.7 h | FINISHED 10-16 04:19 MSK |
| ☐ | 0.5c on L 64, N 192 `spin_hold_L64_N192_ml3_ve050a_spdrv1_farfix_t100` | slow | 100 | ~20 h | LIVE |
| ☐ | 0.7c on L 64, N 192 `spin_hold_L64_N192_ml3_ve070a_spdrv1_sig04_farfix_t150` | fast | 150 | ~30 h | PENDING: 1st node card 1 after the L 128 0.2c (≈ 10-19 04:00 MSK) |
| ☐ | 0.7c on the slow recipe (extra) | slow | 100 | ~9 h | |
| ☐ | 0.99c | fast | 150 | ~9 h | |
| ☐ | clamp validation (methods): σ 0.4 + min_chi 1e-4 + dt 0.05 at 0.5c | – | 100 | ~4 h | |
| ☐ | kicks 0.9c on L 128, N 256 `spin_kick_L128_ml3_ve090a_{l0_eps_p1e3, l0_eps_m1e3, l0_eps_p1e2, m2_eps_p1e3, m1_eps_p1e3}_spdrv1_sig04_farfix_t150` | fast + kick | 150 | 9.7 h each | QUEUED (go 10-18, no checkpoints): from ≈ 05:00 MSK 10-19, two at a time; t 0 probes PASS |
| ☐ | kicks 0.7c (l 0, m 2 at 1e-3) | fast + kick | 150 | ~30 h each on L 64 N 192 | |
| ☐ | 0.95c stretch (optional) | fast | 150 | ~9 h | |

Kick study (planned 10-16; the kick built 10-18): as Evstafyeva–Siemonsen–East (arXiv:2508.11527), kicked
holds of the stable 0.9c (A1 = 1e-3, the merger's smallest seed arm; A2 = ×10) and the 0.7c, fast recipe,
stop 150. The kick (`spinning_kick_amplitude/l/m/radius/width`, commit af28ad29; binary
`main3d_kick_af28ad29_2026-10-18.ex` = farfix + kick, the old data bit for bit at 0) is the merger's
single-throat seed on the spinning throat: ψ → ψ (1 + ε e^{−((η−η_c)/w)²} S), S = 1 (l 0: ΔR/R ≈ 2ε, the
radial branch), P2 (l 2, m 0) or sin^m θ cos mφ (m 1 pushes the throat off centre; m 2 is the bar, which the
holds seed only at round-off), with A_ij × ψ_k^−6 so the momentum constraint stays exact; the Hamiltonian
constraint is violated at O(ε), declared and measured (decided 10-18: no constraint solve, as the merger seeds
and ESE's kicks). Throat η_c (minimal coordinate sphere of each table): 0.9c 1.237, 0.7c 1.117, 0.5c 1.054,
0.2c 1.008. Discriminators: ring-down back to the hold or a triggered collapse; R_throat, ψ4 (2,0) and
(2,±2) at R 14/18, the per-level constraints. t 0 probes (10-18, 1st node card 1, `--preflight-only` PASS, all
75 keys read, 14 frames): l 0 at +1e-3 moves R_pol +1.9989e-3 (table +1.9993e-3) and R_eq +1.707e-3 (table
+1.65e-3: the flat equatorial minimum moves out); m 2 moves R_eq +1.706e-3 (the +x ray, S = 1) and R_pol by 0
(S = 0 on the axis). The throat level's L2_Ham goes 4.4e-8 → 2.0e-4 (l 0) / 1.2e-4 (m 2), the declared violation;
its L2_Mom moves +0.2 %; levels 0–2 identical in both.

## LIVE

| run | node/card | t | stop | speed | ETA (MSK) |
|---|---|---|---|---|---|
| 0.2c L 64 N 128 farfix `00_paper_runs/spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100` | 1st, card 1, 22.9 GB (+ the two sponge tests) | 71.1 @ 16:07 | 100 | 7.0 t/h shared | ≈ 20:15 (or its collapse death) |
| sponge test, drive off `10_sponge_test/spin_hold_L64_N96_ml3_J100_full_spdrv0_farfix_t055` | 1st, card 1, 12 GB | 42.5 @ 16:07 | 55 | 13.6 t/h shared | ≈ 17:00 |
| sponge test, wider absorber `10_sponge_test/spin_hold_L64_N96_ml3_J100_full_spdrv1w20p2_farfix_t055` | 1st, card 1, 12 GB | 40.6 @ 16:07 | 55 | 13.0 t/h shared | ≈ 17:15 |
| 0.2c L 64 N 192 farfix `00_paper_runs/spin_hold_L64_N192_ml3_J100_full_spdrv1_farfix_t100` | 1st, card 0 (solo), 59.7 GB | 34.9 @ 16:07 | 100 | 5.1 t/h | ≈ 10-19 04:55 |
| 0.5c L 64 N 192 farfix `00_paper_runs/spin_hold_L64_N192_ml3_ve050a_spdrv1_farfix_t100` | 2nd, card 0 (solo), 59.9 GB | 31.5 @ 16:07 | 100 | 5.0 t/h | ≈ 10-19 05:50 |

0.2c settings (go 10-18 ≈ 08:50; the N 192's ≈ 09:10): the fix_t100 templates (slow recipe: σ 0.1, min_chi 1e-8,
dt 0.02, stop 100, L 64, centre 32, sponge 24–32 with drive 1.0) plus `shift_advec_coeff = 0`,
`sommerfeld_relative_to_background = 1`, `constraint_norms_edge_cells = 3` on binary farfix 891d817d; ψ4 at R 10 14 18
(each wholly on level 1, whose box reaches ±21.3 / 20 / 18.7 at N 96 / 128 / 192) and 30 (in the drive shell: reference
only); full-box frames (zoom 64, centre 32) with the Weyl4 edge blanked; default MOTS search; no checkpoints. Start
checks: preflights PASS, t 0 constraints identical to the fix_t100 launches (N 192 L2_Ham 1.5234e-3); level 0's
per-level Ham at t 0 8.5e-11 / 3.5e-11 (+3.1); ψ4 header R 10 14 18 30; t 0 MOTS R 4.022 / 4.022 / 4.023; consumers
keep pace (≈ 1 / 1.5 / 2.5 min per plotfile against one every 3 / 6 / 12 min at N 96 / 128 / 192; the N 192's t 0
pass, a cold MOTS search, 9.4 min). **N 96 DIED 62.59** (12:12 MSK; NaN in h11, level 3) mid-collapse, after
its horizon formed (the MOTS left the throat at t ≈ 55 and was 0.13 outside it at 62, θ_in −0.26), the 0.2c result,
with `shift_advec_coeff = 0` all the way: R_eq −3.1 % at 50, −10.4 % at 58, −20.5 % at
the end; χ on the 1e-8 floor at 55.4, max|K| > 0.1 at 56.5, L2_Mom ×2 at 59.0; trust 55 (the pre-fix N 96 ran the same
sequence ~3 later: floor 58.0, NaN 64.83); packed, scratch pruned. Orders at t 6 (the N 192's t at 10:23): level 0 Ham
+2.6–2.7, Mom +2.1–2.5; levels 1–2 +1.8–2.4; level 3 +3.0–4.3; 96→128 the same to t 14.8; the throat's R_eq drift
1.2e-6 / 3.8e-7 / 7.8e-8 at t 6 (≈ 4th order).

0.5c settings (go 10-18 ≈ 09:45, second node): the archived pre-fix 0.5c `spin_hold_L64_ml3_ve050a_spdrv1_t150`
(slow recipe: σ 0.1, min_chi 1e-8, dt 0.02, sponge 24–32 with drive 1.0) with N 128 → 192 and stop 150 → 100, plus
the far-zone and numerics fixes; otherwise the live 0.2c N 192's template with the ve050a table (M_ADM 1.86, R_A
4.97: the box face at 17 M). Same binary and consumer flags as the 0.2c; no checkpoints. Start checks: preflight PASS,
t 0 L2_Ham 2.32e-3; ψ4 header R 10 14 18 30; t 0 MOTS R 4.962 (table R_A 4.966); first consumer pass ≤ 7 min against
one plotfile every 12 min.

**The 0.9c farfix triplet** (FINISHED 10-18: N 128 02:55, N 192 04:52, N 256 09:08 MSK; packed, scratch pruned).
Settings (go 10-17 ≈ 23:20): the stopped L 128 triplet's (records below) plus `shift_advec_coeff = 0`,
`sommerfeld_relative_to_background = 1` and `constraint_norms_edge_cells = 3` on binary
`main3d_farfix_891d817d_2026-10-17.ex`; consumer flags plus `--frames-blank-edge 2`; no checkpoints. Start checked
23:30: preflights PASS, N 128 frame 0 identical to the stopped run's in all 14 fields (Weyl4 with the blank border),
ψ4 header R 14 18 30 40 45, MOTS rows nan; level 0's per-level Ham at t 0 1.6e-9 / 5.4e-10 / 2.3e-10 (+2.7 / +3.0).
Per-level orders t 1–150 (128→192 / 192→256), steady over the whole run: level 0 +2.3 to +3.7 / +2.5 to +3.4,
level 1 +1.9 to +2.3 / +2.2 to +2.6, level 2 +1.8 to +2.5 / +1.9 to +2.8; level 3 Mom +3.2 to +4.3 / +0.8 to +3.9,
Ham +1.7 to +3.4 / +1.0 to +4.4 (192→256 Ham3 ≈ +1.0–1.5 from t 100; level 3's boxes shrink with N). One late
exception: 192→256 level-0 Mom falls from +2.9 at t 140 to +1.2 at t 150, as every member's level-0 Mom grows from
t 140 (at ~5e-9). Throat areal radius flat (18.410 / 18.480 / 18.478, drift ≤ 7e-5); no MOTS; min lapse 0.083 →
~0.001 at the far-side puncture, the same at every N.

Records of the two 0.9c triplets stopped 10-17 (run dirs in `drainhole/00_archive/aborted_2026-10-17/`):

- **L 128** (stopped 21:09 at t 33.95 / 16.34 / 11.99, no NaN; far-zone junk: FAR-ZONE JUNK above). Orders at t 7
  (128→192 / 192→256): level 0 Ham −0.5/−0.5, Mom −0.6/−0.9; level 1 +2.0/+2.3, +1.9/+2.2; level 2 +2.0/+2.3,
  +1.7/+2.1; level 3 +2.1/+1.2, +3.5/+0.8 (level 3 from about +4 at t 1). Each level's boxes shrink with N (the
  same ±16/8/4 tags rounded to each grid: level 3 is 12 / 10.7 / 10 wide), so per-level orders compare slightly
  different regions. Consumers kept pace (one plotfile per t 1). Settings (go 10-17 20:15), the base for the rerun:
  the L 64 N 128 rerun's params with only the box changed: L 128, centre 64, sponge 48–64 (strength 4, drive 1.0),
  N 128 / 192 / 256 (dx 1 → 0.125, 0.667 → 0.083, 0.5 → 0.0625; refined boxes ±16/8/4 via tagging_L 64); σ 0.4,
  min_chi 1e-4, dt 0.02, stop 150, a plotfile every t 1, mask 0.75, `exact_quartic_interp = 1`, `rk_stage_refill = 0`,
  binary rkfix 0661dac4, no checkpoints. Consumer (hold flags via `--consume-args`): ψ4 at R 14 18 30 40 45, throat
  spheres, MOTS 150 steps, frames and slice cache of the full box (zoom 128, centre 64) at the finest dx
  (`GRTECLYN_FRAMES_BUFF_CAP=2048`: 1024 / 1536 / 2048 px). Card memory: N 256 51.1 GB alone, N 192 + N 128 33.8 GB
  together; speeds 15.6 / 21.2 / 44 t/h.
- **L 64** (stopped 20:07): orders at t 7.0 (96→128 / 128→192): level 0 Ham −0.3/−0.4, Mom
  −0.8/−0.8; level 1 +0.7/+0.9, +1.0/+1.1 (from +3 at t 1); level 2 +2.3/+2.4, +2.1/+2.3; level 3 +1.2/+3.2,
  +0.8/+2.5 (96→128 to t 13.3: level 2 +2.5/+2.2, level 3 +1.9/+1.8). Frames: all 14 fields, t 0 identical, values
  = the plotfile; the old run's coarse–fine stripes in K and Pi gone. Its consumers had run `--mots-spectral-steps
  150` since 19:13–19:40 (`restart_consumer.sh --busy`): the N 192's 400-step MOTS search took 22 min per plotfile
  against one every 12 min (the 0.9c never has a MOTS).

**ψ4 junk at the box faces in the collapse (found 10-18).** In the 0.2c farfix runs Weyl4 grows at the faces
(r 28–32) once the outgoing K pulse reaches them (t ≈ 30–40): Re ψ4 change 2.8e-5 there at t 55 on N 96, 4× less
on N 128 at equal t (numerical), creeping inward at ~0.4 c (r 20–24: 1.3e-6 at t 62); r < 20 (R 14, 18) still
≤ 4e-7 at t 55. The 0.9c on L 128 (nothing leaves its interior) shows none. Suspect: the drive — its quartic ramp
bites only in the last 2–3 units (∫ ≈ 1.6 e-folds across the shell) and its pull to the t 0 state is not Einstein
evolution once a pulse is in the shell. The pre-fix runs were far worse (1e-4–1e-2 in every shell by t 46–85), so
the pre-fix 0.21c GW-burst number needs a farfix re-measurement. Test (go 10-18, L stays 64): `10_sponge_test`,
the N 96 to t 55 with the drive off, and with a wider, gentler absorber (20–32, ramp power 2: ∫ 4.0 e-folds);
start checks 13:00: preflights PASS, t 0 L2_Ham/Mom identical to the N 96's (3.4707e-3 / 1.2619e-4); no checkpoints.

## NEXT

- The 0.2c triplet (N 96 done, N 128 + N 192 LIVE): close out each member as it finishes; then its per-level
  convergence and the collapse τ across N.
- PENDING (planned 10-18; go and checkpoints to ask): the far-zone GW run `spin_hold_L128_ml3_J100_full_farfix_t100`,
  a rerun of the pre-fix `05_hold_L128/J100_full/spin_hold_L128_ml3_J100_full_t100` (through the collapse to t 100
  with 0 NaN, horizon at t ≈ 64, the R 30 burst; 7.5 h): its template plus the farfix keys (`exact_quartic_interp
  1`, `rk_stage_refill 0`, `shift_advec_coeff 0`, `sommerfeld_relative_to_background 1`, `constraint_norms_edge_cells
  3`) on binary farfix 891d817d; L 128, N 256, boxes ±16/8/4 (`tagging_L 64`, the L 64 N 128 grid inside), KO
  sponge 48–64 with no drive, as the old run; slow recipe, stop 100, a plotfile every t 1. Consumer: the 0.9c
  N 256's flags with the default MOTS search and `--radii 14 18 30 40 45`, `GRTECLYN_FRAMES_BUFF_CAP=2048`,
  `--subdir drainhole/00_paper_runs`. Card: the first node's card 1 once the 0.2c N 128 ends (≈ 20:15 MSK),
  before the 0.7c. Start checks: frame 0 and the t 0 constraints against the old run's (L2_Ham 6.2029e-4), ψ4
  header R 14 18 30 40 45, the consumer's pace (a plotfile every ≈ 4 min).
- QUEUED (go 10-18, no checkpoints): the five 0.9c kicks (templates ready in `templates/`: the paper 0.9c's
  params plus the kick keys; binary `main3d_kick_af28ad29_2026-10-18.ex`; the N 256's launch line with its
  consumer flags, `--subdir drainhole/00_paper_runs`; 51 GB, 9.7 h each). Order: l 0 +1e-3, m 2, l 0 −1e-3, m 1,
  l 0 +1e-2. First node card 0 after the 0.2c N 192 (≈ 05:00 MSK 10-19), second node after the 0.5c (≈ 05:45);
  two at a time, all done ≈ 10-20 11:00 MSK. Start checks: R_pol/R_eq at t 0 as the probes, frame 0 against the
  hold's, ψ4 header R 14 18 30 40 45. The 0.9c triplet's convergence figure: `results/spinningwormhole/figures/` (10-18).
- PENDING: the 0.7c `spin_hold_L64_N192_ml3_ve070a_spdrv1_sig04_farfix_t150` (template ready; ~60 GB, ~30 h to t 150)
  on the first node's card 1 after the L 128 0.2c (≈ 10-19 04:00 MSK; neither fits beside the N 128, 24 + 51/60 GB).
  Same launch line as the 0.5c with `--gpu 1`; needs a session on the first node.
- Second node (one card): the 0.5c live since 09:48 MSK 10-18 (ETA ≈ 05:40 MSK 10-19); scratch clean (the 0.99c σ 0.4
  run's 7.1 GB of leftovers pruned 10-18).

## MAIN RESULTS SO FAR — PRE-FIX (requote every evolution number from the reruns)

**The physics picture by spin (throat check 10-17).** Static and 0.21c collapse (τ ≈ 5–6); 0.5c shrinks
slowly (MOTS R 4.961 → 4.881 at t 80, −1.6 %, from t ≈ 45; 4.79 at 110); 0.7c holds its size (MOTS R
6.873 → 6.871 to t 83, ≤ 0.05 %) but its slicing breaks from t ≈ 102 (NaN 135.85); 0.9c holds (R 18.476 at
t 24–31, equatorial circumference 23.82 flat to t 40); 0.99c holds (MOTS R 181.76 → 181.72 at 150; sphere
measure 181.76 → 182.4 at t 120, a long marginal tube, R within 2 % from r 2.4 to 8). Stable spins radiate
nothing (0.5c/0.7c ψ4 at the noise floor, no R 14 → 30 propagation). **Open: the 0.9c may inflate after
t ≈ 40** — the N 96 sphere measure read R 20.98 at t 79 → 21.68 at 103 (+13 → +17 % over 18.49; the
minimum moved out r 1.76 → 6.7, R ≈ 28 at r ≈ 2); this measure overestimates a deformed throat (up to 9 %
on the 0.7c) and reads the 0.99c flat; settle it on the fixed triplet with a surface finder.

**Paper runs (all archived 10-17):**
- 0c static anchor `static_hold_L64_ml3_spdrv1_t100`: clean t 100; throat and interior identical to the
  undriven hold to 4 digits while |K| falls two decades across the shell — the drive is a clean absorber
  and the t ≈ 60+ growth is collapse-sourced, not a boundary echo; trust 64.
- 0.21c triplet (J = 1, slow): N 96 died 64.83 at the collapse end (failed, in `00_archive/failed_2026-10-17/`);
  N 128 through the collapse to 85 (MOTS R −1 % at 47, 2.53 at 85; trust 66); N 192 died 78.66 late in the
  collapse (R −1 % at 56, 2.98 at 78; χ on the floor at 75.7, K > 0.1 at 76.4; trust 75). Onset later with N
  (R −1 % at t 43/47/56), growth time similar (τ ≈ 5–6.5 from the MOTS deficit): a resolution-seeded onset,
  the rate set by the physics; members agree on R to 0.1 % only to t 30 (N 96) / 37 (N 128).
- 0.5c `ve050a_spdrv1_t150`: died 130.0 (NaN h11): clean through the Ham ×2 knee (~83), then Ham 0.157 at
  110 → 0.367 at 120, max|K| > 0.1 at 110, lapse pinned 1e-10 by 128 (the slow recipe going unphysical
  long); trust 80.
- 0.7c `ve070a_spdrv1_sig04_t150`: died 135.85 (NaN in K, level 3): lapse to its 1e-10 floor at 102.4,
  K > 0.1 at 105.8, Ham ×2 at 127.5; the throat holds (MOTS R 6.870–6.873 over t 0–83): the slicing
  breaks, not the throat; trust 102.
- 0.7c on the slow recipe `ve070a_spdrv1_t100`: died 42.6 at the far side (χ on the 1e-8 floor from 2.3,
  level-3 Mom ×8 by 20 and ×400 by 30, K > 0.1 at 22.7): the 1e-4 floor is what carries the 0.7c; trust 15.
- 0.9c `ve090a_spdrv1_sig04_t150`: clean t 150, Ham flat (1.07e-2 → 1.17e-2 over 60 → 150), max|K| flat
  2.0e-2 — the stability claim; no throat-size record (its plotfiles were gone before the throat measure).
  Triplet N 96 `_t150`: clean t 150 (Ham 5.5e-3 → 1.04e-2, Mom 2.0e-4 → 1.6e-3, lapse 1.1e-3 at 150);
  N 192 never ran on the fixed data.
- 0.99c `ve099a_spdrv1_sig04_t150`: clean t 150 (Ham 3.93e-2 flat, Mom 1.50e-3, lapse 8.1e-3, K 2.2e-3).
- Clamp validation `06_dt_ladder/…ve050a_spdrv1_sig04_mc4_dt005_t100`: died 81.1 (the dt 0.05 K
  instability, delayed 22 → 64 by σ 0.4 + floor, not cured); the clamp validated in the clean window (ψ4 at
  R 14 within 0.9 %, throat R within 0.3 % of the unclamped parent).

**L128 production box (`05_hold_L128/`, 10-15/16):**
- Model check PASSES: `spin_hold_L128_ml3_J100_full_t100` (0.21c, N 256): τ(ΔR ∈ [0.01, 0.3]) = 6.78 vs
  L64's 6.8 (static 5.8); R_eq −1 % / −10 % at t 46.85 / 61.82 vs L64's 46.9 / 61.8; detached horizon at
  t ≈ 64; trust 67.
- B1 `spin_hold_L128_ml3_ve050a_t100` (0.5c, N 256): clean t 100; MOTS R −1 % at t 71 where the static twin
  took t 44, −3.14 % at t 100, no horizon; Ham ×2 at 78.8 (the slow level-2 interface mode); trust 78.

**Step 3 (10-13 → 10-15):**
- t = 0 checks PASS (v_e 0.5, three grids): constraints 4th order inside the throat; outside they grew as
  1/dx² (Ham) and 1/dx (Mom), the bilinear table's fingerprint (later bug 1); throat radii converge to the
  table (R_eq −5e-5 at N 192).
- J = 1 on exact data: the O(J²) holds' push vanishes; the throat collapses on the static mode (R_eq −1 % at
  46.9, −10 % at 61.8; τ 6.8 against the static 5.8): spin slows the collapse.
- A1, family (b) on L128: PASS (21 runs, v_e 0.24–0.99 × N 128/192/256, `L128_A1/`): throat radii converge
  to the table (R_eq −7e-5 to −9e-4 at N 256); the 3D ADM mass integral equals the table metric's to
  ≤ 1e-12, extrapolated M within 2e-5–7e-4 (0.7 % at 0.99), J within 2e-3 (0.24) to 2e-5 (0.99).

**Measurement notes.** On the fast runs `throat_geometry.dat` is not a throat measure (its rays start at
r 0.6, inside the χ-floored core; the "0.9c 23.8 → 5.9 / 0.99c 101 → 76" readings and the lapse → 0.001
were that core). The consumer writes `small_data/throat_spheres.dat` per plotfile (`--throat-spheres`, in
the hold profile since 10-17). The fast throats need the MOTS flags `--mots-spectral-untrapped
--mots-spectral-warm-flow --mots-spectral-steps 1500` (the 0.9c needs 700–1200 steps; the default 400
found nothing). The pre-fix N 96 frames are 2× the data (yt summed both sides of a cell face at z = 32;
renderer fixed 10-17 ≈ 13:00 MSK; the data are unaffected).

## FOR THE ARTICLE (paper notes and additions; evolution numbers pre-fix)

**The rotating collapse emits a real gravitational wave (10-16).** At R = 30 the 0.21c collapse
(`spin_hold_L128_ml3_J100_full_t100`) shows an l = 2, m = 0 burst |ψ₄| = 3.0e-2 arriving at t = 81 (horizon
formation t ≈ 64 plus ~17 of light travel). The static collapse at the same radius reads 6.0e-5, the
numerical floor (spherical collapse cannot radiate): the spinning burst is 500× above it and 10⁴× above the
run's quiet-phase noise; B1 (0.5c, no collapse) stays quiet. Measurable per spin alongside τ
(`psi4_mode_l2m0.dat` in every pack). Its farfix re-measurement is the L 128 N 256 0.2c (claim 3, PAPER RUN MATRIX).

**The exotic-matter trend is the physics behind the ladder (10-15): plot τ(v_e) against D/M(v_e).** From
the family (a) tables (D = the phantom scalar charge; `results/spinningwormhole/solutions/<leg>/<leg>.tsv`):

| v_e | D (scalar charge) | M_ADM | D/M |
|---|---|---|---|
| 0.06 | 2.23 | 1.01 | 2.22 |
| 0.51 | 2.00 | 1.87 | 1.07 |
| 0.70 | 1.72 | 3.31 | 0.52 |
| 0.90 | 1.07 | 11.7 | 0.09 |
| 0.96 | 0.67 | 32.0 | 0.02 |

D shrinks with spin while M grows, so the exotic fraction falls a hundred-fold across the family; at
extremality the family approaches extremal Kerr with the scalar switched off. Rotation progressively
replaces exotic matter as what holds the throat open: the phantom field both sustains the throat and drives
its collapse, and the faster the spin, the less of it there is.

**The exotic matter is measured on the grid (10-16).** The scalar charge is fit from the equatorial φ frame
slices (φ = D/(η₀√4π)·[arctan(η/η₀) − π/2], annulus r = 4–22). At t = 0 the grid reproduces the solver's D to
~2×10⁻⁴ at four spins (static 2.2358/√5, 0.21c 2.2014, 0.51c 2.0010, 0.70c 1.7194). In time, to each trust
window: the static hold drains D 2.24 → 1.39 (−38 %) by t = 64 and the 0.21c collapse 2.20 → 1.61 (−27 %)
by t = 67, max|φ| falling with it (the horizon swallows the phantom); B1 (0.51c) and the 0.70c stay flat
(max|φ| −2.5 % over 78 units, −6 % settled by t = 40; the ±15–20 % wobble of the fitted D there is the
coordinate annulus feeling the gauge). Figure when wanted: D(t), max|φ|, max|Π| per hold, cut at trust; it
reads only the frame slice caches (phi_z, Pi_z), so no plotfile retention is needed.

**Speed-up research (dt × σ, closed 10-16; "goes fully to the article").** The dt ceiling was never hard
CFL (local speeds ≤ 0.95; KO + RK4 allow dt_mult ~0.23 at σ 0.1): it was a weak AMR interface-mode
instability, a grid-scale checkerboard pinned to the fixed nested coarse–fine box edges (square halos in K,
shells r ≈ 5–7.5 fastest), dissipation-starved at σ 0.1 and radiating into the wave zone long before
breakout (ψ4 ×373 at t = 10 at dt_mult 0.05). One mode at every dt, a growth-rate ladder: e-fold ~0.8 at
dt_mult 0.1, breakout t ≈ 28–30 at 0.05 and t ≈ 43 at 0.035, e-fold ~9 at the production 0.02. Verdicts:
(1) L64 static σ 0.3 + dt 0.05 ran clean, 2.5× faster (σ 0.2 only postponed the mode); (2) σ 0.4 at dt 0.02
erases the late constraint growth (masked Ham 2.4e-5 / 4.1e-5 / 7.9e-4 of the σ 0.1 control on levels
1/2/3 at t = 100; the collapse comes ~4 units earlier, so collapse times compare only at matched σ); (3) the
levnorm binary is bit-exact; (4) dt 0.05 and 0.035 died on L128 spin data (χ to the 1e-8 floor from
t ≈ 20), so production stayed at dt 0.02. **The mode lived exactly where bugs 2 and 3 acted** (the
coarse–fine edges): retest dt 0.05 on the fixed binary before quoting any of this. Arms:
`drainhole/06_dt_ladder/` and the ledger below.

## RUN LEDGER — every arm before the fixes

All N 128 base, max_level 3. drv = sponge_drive_strength. Outcomes frozen in `runs_registry.tsv` /
`trust_windows.tsv`.

| run | data | L | sigma | dt | floor | drv | outcome | trust |
|---|---|---|---|---|---|---|---|---|
| `static_hold_L64_ml3_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | – | Step 0 anchor, clean t 100 | 64 |
| `static_hold_L64_ml3_dt002ctl_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | – | bit-exact twin of Step 0 | 100 |
| `static_hold_L64_ml3_dt005_t070` | static | 64 | 0.1 | 0.05 | 1e-8 | – | interface mode ×61 by t 15; stopped 45 | – |
| `static_hold_L64_ml3_dt0035_t070` | static | 64 | 0.1 | 0.035 | 1e-8 | – | same mode, later; stopped 62 | – |
| `static_hold_L64_ml3_dt005_sig02_t045` | static | 64 | 0.2 | 0.05 | 1e-8 | – | FAIL: mode only postponed | – |
| `static_hold_L64_ml3_dt005_sig03_t045` | static | 64 | 0.3 | 0.05 | 1e-8 | – | clean 45, gentlest working KO | – |
| `static_hold_L64_ml3_dt005_sig04_t045` | static | 64 | 0.4 | 0.05 | 1e-8 | – | clean 45, mode killed | – |
| `static_hold_L64_ml3_dt002_sig04_t100` | static | 64 | 0.4 | 0.02 | 1e-8 | – | constraints 400–40,000× below ctl; collapse 4 u early | 100 |
| `static_hold_L64_ml3_spdrv1_t100` | static | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | drive is a clean absorber; echo story falsified | 64 |
| `spin_hold_L64_ml3_J025_t100` | 0.1c | 64 | 0.1 | 0.02 | 1e-8 | – | clean t 100 | 64 |
| `spin_hold_L64_ml3_J100_t100` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | – | collapse; tau 6.8 vs static 5.8 | 57 |
| `spin_hold_L64_ml3_J100_full_t100` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | – | exact-data collapse; died 70.64 at its end | 64 |
| `spin_hold_L64_ml3_ve050a_t100` | 0.5c | 64 | 0.1 | 0.02 | 1e-8 | – | clean t 100; Ham ×2 at 84.5 | 64 |
| `spin_hold_L64_ml3_ve070a_t100` | 0.7c | 64 | 0.1 | 0.02 | 1e-8 | – | DIED 42.36, far-side puncture | 40 |
| `spin_hold_L128_ml3_ve050a_t100` (B1) | 0.5c | 128 | 0.1 | 0.02 | 1e-8 | – | clean t 100; Ham ×2 at 78.8 | 78 |
| `spin_hold_L128_ml3_J100_full_t100` (N 256) | 0.21c | 128 | 0.1 | 0.02 | 1e-8 | – | model check PASSES (tau 6.78 = L64's); GW burst 500× floor | 67 |
| `spin_hold_L128_ml3_ve050a_sig04_dt005_t100` | 0.5c | 128 | 0.4 | 0.05 | 1e-8 | – | DIED 47.85, puncture floored from t 20 | 20 |
| `spin_hold_L128_ml3_ve050a_sig04_dt0035_t060` | 0.5c | 128 | 0.4 | 0.035 | 1e-8 | – | floored 22.3; stopped 26.4 | – |
| `spin_hold_L128_ml3_ve050a_sig04_t100` | 0.5c | 128 | 0.4 | 0.02 | 1e-8 | – | DIED 46.47: sigma kills at ANY dt | 15 |
| `spin_hold_L64_ml3_ve070a_minchi4_t100` | 0.7c | 64 | 0.1 | 0.02 | 1e-4 | – | RESCUE PASS, clean t 100, chi heals | 64 |
| `spin_hold_L64_ml3_ve050a_spdrv1_t150` | 0.5c | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | DIED 130.0 (NaN h11): K > 0.1 at 110, lapse pinned 128; quotes t ≤ 80 | 80 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig02_t100` | 0.5c | 64 | 0.2 | 0.02 | 1e-8 | 1.0 | stopped 23.9 (two-regime decision; chi on the dt005 decay curve) | 25 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig02_dt005_t100` | 0.5c | 64 | 0.2 | 0.05 | 1e-8 | 1.0 | stopped 44.5: slow puncture decay | 20 |
| `spin_hold_L64_ml3_ve050a_spdrv1_sig04_mc4_dt005_t100` | 0.5c | 64 | 0.4 | 0.05 | 1e-4 | 1.0 | DIED 81.1 (NaN in K): dt 0.05 K instability delayed, not cured; clamp validated t ≤ 70 | 70 |
| `spin_hold_L64_ml3_ve090a_spdrv1_sig04_t150` | 0.9c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | CLEAN t 150, Ham flat; the paper 0.9c (archived) | 150 |
| `spin_hold_L64_ml3_ve070a_spdrv1_sig04_t150` | 0.7c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | DIED 135.85 (NaN in K; lapse floor 102.4); the paper 0.7c (archived) | 102 |
| `spin_hold_L64_ml3_ve070a_spdrv1_t100` | 0.7c | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | DIED 42.6 at the far side (slow recipe; archived) | 15 |
| `spin_hold_L64_N96_ml3_J100_full_spdrv1_t85` | 0.21c | 64 (N 96) | 0.1 | 0.02 | 1e-8 | 1.0 | J=1 triplet N 96: FAILED 64.83 at the collapse end; R −1 % at 43 | 58 |
| `spin_hold_L64_ml3_J100_full_spdrv1_t85` | 0.21c | 64 | 0.1 | 0.02 | 1e-8 | 1.0 | J=1 triplet N 128: through the collapse to 85 (archived) | 66 |
| `spin_hold_L64_N192_ml3_J100_full_spdrv1_t85` | 0.21c | 64 (N 192) | 0.1 | 0.02 | 1e-8 | 1.0 | J=1 triplet N 192: DIED 78.66 late in the collapse (archived) | 75 |
| `spin_hold_L64_N96_ml3_ve090a_spdrv1_sig04_t100` | 0.9c | 64 (N 96) | 0.4 | 0.02 | 1e-4 | 1.0 | fast triplet N 96 to 100, superseded by `_t150` (archived) | 100 |
| `spin_hold_L64_N96_ml3_ve090a_spdrv1_sig04_t150` | 0.9c | 64 (N 96) | 0.4 | 0.02 | 1e-4 | 1.0 | fast triplet N 96: CLEAN t 150 (archived) | 150 |
| `spin_hold_L64_ml3_ve099a_spdrv1_t150` | 0.99c | 64 | 0.1 | 0.02 | 1e-4 | 1.0 | stopped 50.4 (feasibility answered: Ham flat, chi on the floor) | 50 |
| `spin_hold_L64_ml3_ve099a_spdrv1_sig04_t150` | 0.99c | 64 | 0.4 | 0.02 | 1e-4 | 1.0 | the paper 0.99c: clean t 150 (archived) | 150 |

What the ledger says (pre-fix):
- σ ≥ 0.2 kills the spin far-side puncture on the 1e-8 floor at any dt (0.4 by t ≈ 22, 0.2 slowly); the
  min_chi 1e-4 floor removes that failure mode.
- σ 0.1 caps every slow run at the interior interface knee, Ham ×2 at 78–85, box-independent; the drive does
  not cure it.
- σ 0.4 + floor 1e-4 do NOT cure the dt 0.05 K instability at 0.5c, only delay it (K > 0.1 at 64.5 vs 22):
  dt 0.02 everywhere; the two-regime recipe is final.
- dt alone never killed a spin run; dt 0.05 needs σ ≥ 0.3 (static) and the floor (spin).

## OPEN

- Level 0's box face (Sommerfeld on a non-flat background): a better outer condition or a bigger box, only
  on decision.
- The sponge drive (pair `07_sponge_fix/sptest_*`, pre-fix binary, stopped by decision at t 14.5, 10-17):
  levels 2–3 identical drive on/off; level 1 grows with the drive (×8 by t 14.5, ×1.1 at t 2), the drive
  acting directly on the level-1 corners inside the shell (r 24–27.7). The drive pulls every field to the
  t = 0 data, which is not constraint-preserving: watch the triplets' level-1 norms (it does not converge
  away); the throat levels 2–3 had seen nothing by t 14.5.
- Retest dt 0.05 / σ on the fixed binary after the triplets (the interface mode sat on the coarse–fine edges).
- Upstream AMReX PR for the rounded `cell_quartic_interp` weights (later, on decision).
- The RK stage re-fill in the merger, RadialRecipe and SupportedWormholeCollapse examples (their campaigns'
  call).
- Waveform extrapolation in 1/R: absent; matters least under the stability-only plan.

## DECISIONS (compact history)

- 10-13: every quoted run is a triplet (the stability protocol above); per-level masked constraint norms
  (`constraint_norms_levels = 1`, levnorm binary 73793542) in every member.
- 10-13: every run on L = 128 with triplets N 192/256/384 — superseded 10-16 by the L64 two-regime recipe;
  the L128 N 192/384 members dropped; the L128 N 256 runs keep the model-check and box-independence roles.
- 10-15: the paper is the drainhole's alone; campaign A dropped (below).
- 10-13: full-box frames on L128 (`--zoom 128 --coord 64 --center 64 64 64`, `GRTECLYN_FRAMES_BUFF_CAP=2048`).
- 10-16: two regimes (slow ≤ 0.5c, fast 0.7c+), drive 1.0, dt 0.02; ψ4 radii 14/18/30 baked into the hold
  profile.
- 10-17: the three numerics fixes; every paper run reruns; the pre-fix paper runs archived; kicks wait for
  both triplets.
- 10-18: the kick is the merger's unsolved conformal-factor shell, momentum-exact (af28ad29); no constraint
  solve.

## DONE

- **Step 0** (10-11): the static hold twins the merger's `single_hold` (collapse, τ 5.27, trust t ≤ 64).
- **Step 1** (10-12): the O(J²) holds inflate (τ 5.8 / 5.6 at J = 0.25 / 1); their push grew as J⁴, the
  data's error, not the spin.
- **Step 2** (10-13): full solver, both families to v_e 0.99, every gate green; CKK's eq. (12) is wrong;
  tables in `runs/spinning_p3/tables/` (error ≤ 1e-7 to v_e 0.9).
- **Step 3** (10-13 → 10-15): t = 0 checks, the L64 holds, the A1 ladder (MAIN RESULTS above).
- **10-17**: the three numerics bugs found by per-level constraint convergence and fixed (CONVERGENCE above).

**Campaign A (family (b) evolutions), dropped 2026-10-15.** Its compactified far end is a positive-mass
puncture (M ≈ 2.5) at the grid centre; every hold died there in a K runaway at t ≈ 23–24 with the throat
unmoved, whatever the lapse (√χ initial lapse: 22.87), resolution (max_level 4: 23.76), shift damping
(η 0.2: 23.24, earlier) or χ floor (1e-4: 23.76, never engaged): the death tracks the data, not the
numerics (pre-fix runs). A return needs excision at the far puncture, another gauge, or regularized data.
Family (b) stays as theory and solver validation (Step 2 gates, the A1 ladder, the t = 0 convergence
figures). Runs in `symmetric_massless/03_spin_hold/ve085b/`; the A2–A4 run lists and templates at 2998819f.

## ASSETS

- B1's final Chk10000 sits in its `nfs_chk/` (t = 100 restart point).
- `fam_a_ve020.spinbg` (2049×129, err 3.9e-8): an optional same-rung cross-check of the J = 1 point
  (v_e 0.1984 vs 0.2100) from a different solver leg.
- The pre-fix paper runs, frames and packs: `runs/spinning_wormhole/drainhole/00_archive/superseded_2026-10-17/`.

## RULES

CLAUDE.md's launch discipline: go first, checkpoints asked per run, full frame set, STATUS pushed at every
launch, stop or wipe. ψ4 radii 14/18/30 on every spinning launch. Kick runs wait for both triplets.
