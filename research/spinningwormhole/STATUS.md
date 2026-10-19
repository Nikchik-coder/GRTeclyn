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

## THE THRESHOLD AGAINST AZAD ET AL. (2026-10-19)

The claims stand on the current runs — stability at fast spin (the 0.9c triplet) and the GW signal of the
rotating collapse (the far-zone 0.2c). What is missing is the curve between them: where the instability's
growth dies with spin. The 0.6c/0.7c holds below are those missing pieces.

The background tables carry Azad et al.'s own measure (J/A as a fraction of the extremal-Kerr limit
1/(8π)), so the comparison with arXiv:2301.05243 is direct. What they actually claim:
1. The static radial mode weakens quadratically with J and, in their second-order expansion, vanishes at
   J/A ≈ 50 % of the extremal limit.
2. **The second mode**: the moment the throat rotates, a zero mode of the static wormhole becomes a second
   unstable radial mode. It grows with J and crosses the main mode at ≈ 30 % of the limit. Past the
   crossing their expansion fails, so they conjecture the two modes merge there and the instability
   disappears at ≈ 30 % — a conjecture, not a result.

Our ladder in their units: 0.2c = 12 %, 0.30c = 18 %, 0.40c = 24 %, 0.46c = 29 %, 0.5c = 33 %, then
nothing until 0.9c = 81 %. So:
- The 0.46c sits exactly on their mode crossing, and the 0.5c just **above** their conjectured threshold —
  and our 0.5c still drifts down (τ 13.4, −1 % at t 99). Nonperturbatively their 30 % conjecture already
  fails on our data (caveat: that run had the drive on; the drive-off rungs land tonight and make it clean).
- The whole 33–81 % band is unsampled, and the true threshold must sit in it — that is the point of going
  beyond 0.5c. Locating it turns claim 2 from a trend into a number and answers Azad's open question
  nonperturbatively.
- Near the crossing the departure should be **two-mode**: the τ(J) fits are single exponentials, so re-fit
  the 0.46c/0.5c deficits with two modes once tonight's holds land — free, no new runs.
- Physicality: by J/M² the family bulges in the middle — 0.5c is the worst offender (1.19), 0.7c is 1.11,
  and the fast end returns to the Kerr value (0.9c 1.013); "unphysical" does not single out the fast rungs.

The runs: two drive-off holds, 0.6c (40 %) and 0.7c (51 %, right on Azad's quadratic J_c), tables
fam_a_ve060/ve070, L 64 N 128, the FAST recipe (σ 0.4, min_chi 1e-4, dt 0.02, stop 150 — the 1e-4 floor is
what carries >0.5c: at 1e-8 the 0.7c died t 42.6, floored from t 2.3; rescued clean with 1e-4). If the
0.6c drifts and the 0.7c holds, the threshold is bracketed at 40–51 % against their 30 % conjecture. Kicks
then go only on the rung that holds — the ring-back test. PENDING in the matrix below.

## THE PAPER'S CLAIMS (decided 2026-10-18)

1. **Stability**: the fast-spinning throat is stable (the 0.9c farfix triplet holds to t 150). The kicks moved to the
   low spins (10-18): does a push bring the 0.2c's collapse earlier?
2. **Stability grows with spin**: the collapse slows as the spin grows and the fast throats hold (the ladder static →
   0.2c → 0.3c / 0.4c / 0.45c → 0.5c → 0.9c; τ(J) against Azad et al.'s second-order rate, FOR THE ARTICLE).
3. **A GW signal with no nonspherical perturbation**: the rotating collapse radiates (l 2, m 0) from unperturbed data,
   where the static wormhole needed a nonspherical perturbation to radiate at all. The far-zone waveform is the 0.2c
   on L 128 N 256 (FINISHED 10-19): r·ψ4 2.0–2.3e-4, one waveform in t − R at R 14–45, flat in R (LIVE notes); the
   L 64 runs' ψ4 at R 14/18 matches it to ≤ 2 % through t 100.

## STATE (2026-10-19 ≈ 09:15 MSK)

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
(orders under LIVE), throat areal radius flat to ≤ 7e-5, no MOTS. The 0.2c L 64 triplet ran with the same fixes: the
N 96 died in its collapse, the N 128 and N 192 went through it to t 100 with no NaN (10-18 / 10-19); the far-zone
0.2c on L 128 finished t 150 and the 0.5c N 192 t 100 (10-19); the slow runs' t ≈ 80 constraint knee is gone on
the fixed binary (LIVE notes). Live: the four holds (first node, since 10-19 08:48 MSK) and the 0.2c push-in and push-out kicks (second node, since 09:12 and 10:51 MSK). The Weyl4 frames blank the box's outer 2 cells (`--frames-blank-edge 2`, point 7).

## CODEBASE DIAGNOSTIC (2026-10-19)

**Throat radii, second check (10-19 afternoon).** Two reviewers checked the radius measurements: one audited the radius
code and the data streams, the other recomputed the radii independently from the four holds' plotfiles.

The radii are measured correctly:
- every t 0 row reproduces from the tables (≤ 4e-10);
- the 0.9c flatness, the 0.2c onsets and τ, and the holds' t 42 deficits and spin ordering all hold;
- each stream's error is about 1e-4, and streams differ from each other by about 2e-4.

Changes:
- **Use one τ definition.**
  - STATUS uses −1 → −10 % for the 0.2c and −0.1 → −1 % for the 0.5c. `plot_instability_curve` fits whatever part of
    0.2–10 % a run reaches.
  - At 0.5c the choice of radius matters too: 13.4 from the equatorial radius, 11.7 from the areal radius.
  - So the 0.2c reads 6.10 in the figure and 6.57 here, and the 0.5c 15.7 and 13.4. "Dies at 41 %" moves between 40 and
    48 %.
  - The N 96's τ of 6.72 uses a crossing at t 57.7, past its trust window (55).
- **The holds' e-folds at t 40–46 are transient.** They are still rising with t, and the 0.46c shrinks fastest: 4.0
  against the static's 4.8 at t 42. Compare τ with Azad only once the holds reach a common band.
- **The push-in kick's throat left the finest box (r 5) at t ≈ 61.4.**
  - After that, `throat_geometry` reads the box edge, not the throat. Read `throat_spheres` instead.
  - The throat is now evolving at dx 0.125. Its +92 % at t 57.5 stands.
- **The push-out's −1 % at t 24 is measured against its own kicked t 0,** which sits 0.2 % above the hold. Against the
  unperturbed throat it passes −1 % at t 25.3, which is 21.6 before the hold.
- **Which streams to quote.**
  - Never quote R_pol_min: it depends on the coordinates, and the 0.9c's late growth in it is gauge.
  - `throat_spheres` is too coarse for the small rungs: it reads the 0.46c deficit 20 % high. At dx = 1/6 it also sits
    half a cell off centre, which is why the 0.9c reads 18.409 / 18.480 / 18.477, not monotone in N.
  - The MOTS stream is the most accurate, to 3e-6.

**The codebase review (five reviewers, 10-19 morning).** The codebase checks out: none of the five reviewers found a defect that changes any of the three claims. Each part was
confirmed by re-deriving it independently:
- **Solver:** its equations match an independent Ricci computation to 1e-50, and the eq. (12) finding about CKK holds.
- **Tables:** they solve Einstein's equations to between 1e-10 (0.2c) and 1e-8 (0.9c).
- **C++ initial data:** it matches the runs' own t 0 output to float32 precision.
- **The three 10-17 fixes:** all are correct.
- **Diagnostics:** τ, the collapse onsets, the wave amplitudes and the 0.2c orders all recompute from the data.

**One physics question is open.** The settled 0.2c horizon (M_irr 1.262) comes out heavier than the exterior mass fitted
from χ at r 26–58 (about 1.16 at t 150). The field near the hole can't account for the gap. Settle it with a proper mass
integral before the paper quotes a horizon mass.

**Worth fixing (none of these moves a claim):**
- **ψ4 has no matter term in any run.** It reads the key `G_newton`, which no run sets, so it defaults to 0. The effect is
  ≤ 0.4 % at R ≥ 30, but up to 17 % at R 10.
- **The throat-sphere areal radius is read slightly low.** The interpolation is linear, so the 0.9c reads 18.41 / 18.48
  against the true 18.499. The flatness claim still holds.
- **μ₋ is read too close to the end on the log-stretched map.** That puts the Smarr check at 8e-7, against the 1e-10 the
  paper states.
- **`article/research.tex`:**
  - it drops a 1/η₀ in ψ (line 106);
  - it double-rounds two Table I digits;
  - it describes solver features the code doesn't have.
- **Some STATUS numbers don't reproduce:**
  - the 0.9c minimum orders;
  - the troughs' flatness in R;
  - the N 192 ring lapse (0.508, not 0.529);
  - the order of τ_proper (about 2, not 3).
- **The 0.9c polar radius grows by 1e-3 after t 110, at every N.** The areal radius stays flat, so it's a coordinate
  effect, but STATUS doesn't mention it.

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
  (a physics-neutral absorber; makes L64 viable past t ≈ 64), dt_multiplier 0.02. **Since 10-18 every new run
  has the drive off** (`sponge_drive_strength = 0`, the KO sponge kept): the sponge test (`10_sponge_test`) found the
  drive making the face junk once a wave reaches the shell, with the throat unchanged. The runs made with it stand:
  their throats and ψ4 inside R 18 are the same, and the far-zone waves come from the big box (no drive).
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
| ✓ | 0.2c triplet on L 64, N 96 `spin_hold_L64_N96_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | 3.3 h | FINISHED 10-18 12:12 MSK: died 62.59 mid-collapse, the result (trust 55) |
| ✓ | 0.2c triplet on L 64, N 128 (= the paper 0.2c) `spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | 9.3 h | FINISHED 10-18 18:12 MSK: through the collapse to t 100, horizon settled, (2,0) wave out (trust 100) |
| ✓ | 0.2c triplet on L 64, N 192 `spin_hold_L64_N192_ml3_J100_full_spdrv1_farfix_t100` | slow | 100 | 19.8 h | FINISHED 10-19 04:58 MSK: through the collapse to t 100 (trust 100) |
| ✓ | 0.2c on L 128, N 256, the far-zone GW run (claim 3) `spin_hold_L128_ml3_J100_full_farfix_t150` | slow | 150 | 9.7 h | FINISHED 10-19 05:06 MSK: the (2,0) wave passes R 14–45 at c, r·ψ4 flat in R (trust 150) |
| ✓ | 0c static anchor `static_hold_L64_ml3_spdrv1_t100` (in `00_archive/superseded_2026-10-17/`; pre-fix, rerun next row) | slow | 100 | 5.7 h | FINISHED 10-16 04:19 MSK |
| ☐ | 0c static rerun on the fixed binary `static_hold_L64_ml3_spdrv0_farfix_t100` (the anchor's packed params + the numerics and far-zone fix keys, drive off; diffed) | slow | 100 | ~11 h, 22 GB | LIVE since 10-19 08:48 MSK, 1st node card 0 (with the 0.30c; no checkpoints) |
| ✓ | 0.5c on L 64, N 192 `spin_hold_L64_N192_ml3_ve050a_spdrv1_farfix_t100` | slow | 100 | 20.0 h | FINISHED 10-19 05:47 MSK: clean t 100, no constraint knee, throat −1.3 % (trust 100) |
| ☐ | 0.30c on L 64, N 128 `spin_hold_L64_ml3_ve030a_spdrv0_farfix_t100` (table `fam_a_ve030`: v_e 0.304, J 1.61; Azad's τ 6.1) | slow | 100 | ~11 h, 22 GB | LIVE since 10-19 08:48 MSK, 1st node card 0 (with the static; no checkpoints) |
| ☐ | 0.40c on L 64, N 128 `spin_hold_L64_ml3_ve040a_spdrv0_farfix_t100` (table `fam_a_ve040`: v_e 0.395, J 2.41; Azad's τ 8.0) | slow | 100 | ~11 h, 22 GB | LIVE since 10-19 08:48 MSK, 1st node card 1 (with the 0.46c; no checkpoints) |
| ☐ | 0.46c on L 64, N 128 `spin_hold_L64_ml3_ve045a_spdrv0_farfix_t100` (table `fam_a_ve045`: v_e 0.456, J 3.15; Azad's τ 13) | slow | 100 | ~11 h, 22 GB | LIVE since 10-19 08:48 MSK, 1st node card 1 (with the 0.40c; no checkpoints) |
| ☐ | kicks 0.2c on L 64, N 128 `spin_kick_L64_ml3_J100_full_{l0_eps_m1e3, l0_eps_p1e3, m2_eps_p1e3}_spdrv0_farfix_t100` (push in, out, bar; drive off) | slow + kick | 100 | ~10 h, 23 GB each | push in (`l0_eps_m1e3`) LIVE since 10-19 09:12 MSK and push out (`l0_eps_p1e3`) since 10:51 MSK, both on the 2nd node's card (no checkpoints); the bar PENDING (go 10-18; card not chosen): does a push bring the collapse earlier? The push in inflates, as the merger paper's sign rule says |
| ☐ | kicks 0.30c on L 64, N 128 `spin_kick_L64_ml3_ve030a_{l0_eps_m1e3, l0_eps_p1e3, m2_eps_p1e3}_spdrv0_farfix_t100` (push in, out, bar; drive off) | slow + kick | 100 | ~10 h, 23 GB each | PENDING (go 10-18, no checkpoints; card not chosen; templates ready): the same at the black-hole spin limit (J/M² 1.03) |
| ☐ | 0.6c on L 64, N 128 `spin_hold_L64_ml3_ve060a_spdrv0_mc4_sig04_farfix_t150` (table `fam_a_ve060`: v_e 0.592, J 6.19, J/A 40 % of extremal; never run) | fast + drive off | 150 | ~15 h shared, 22 GB | QUEUED (go 10-19 ≈ 11:20 MSK, template written and diffed; no checkpoints): on the 2nd node's card when the kicks end ≈ 19:30 MSK, with the 0.7c |
| ☐ | 0.7c rerun on L 64, N 128 `spin_hold_L64_ml3_ve070a_spdrv0_mc4_sig04_farfix_t150` (the archived fast 0.7c's params + the fix/far-zone keys, drive off; J/A 51 %, Azad's quadratic J_c; old run: throat flat t 0–83, slicing broke 102) | fast + drive off | 150 | ~15 h shared, 22 GB | QUEUED (go 10-19 ≈ 11:20 MSK, template written and diffed; no checkpoints): on the 2nd node's card when the kicks end ≈ 19:30 MSK, with the 0.6c; shared ≈ 10 t/h, ETA ≈ 10:30 10-20 |

Middle rungs (10-18): tables in `runs/spinning_p3/tables/` (script `p5_mid_tables.py`, the saved fam_a_r1 solutions
nearest 0.3/0.4/0.45, f error ≤ 1e-7); templates (`templates/params_spin_hold_L64_ml3_ve0{30,40,45}a_spdrv0_farfix_t100.txt`)
= the paper 0.2c's with the table swapped and the drive off (the sponge test's result).

Kick study (planned 10-16; the kick built 10-18; **moved to the low spins 10-18 ≈ 17:15**: the 0.9c is too far from
physical spins, so the kicks go on the 0.2c first, to see whether a push brings the collapse earlier, and one more rung;
the 0.9c records below stay as the kick's t 0 validation): as Evstafyeva–Siemonsen–East (arXiv:2508.11527), kicked
holds of the stable 0.9c (A1 = 1e-3, the merger's smallest seed arm; A2 = ×10), fast recipe,
stop 150. The kick (`spinning_kick_amplitude/l/m/radius/width`, commit af28ad29; binary
`main3d_kick_af28ad29_2026-10-18.ex` = farfix + kick, the old data bit for bit at 0) is the merger's
single-throat seed on the spinning throat: ψ → ψ (1 + ε e^{−((η−η_c)/w)²} S), S = 1 (l 0: ΔR/R ≈ 2ε, the
radial branch), P2 (l 2, m 0) or sin^m θ cos mφ (m 1 pushes the throat off centre; m 2 is the bar, which the
holds seed only at round-off), with A_ij × ψ_k^−6 so the momentum constraint stays exact; the Hamiltonian
constraint is violated at O(ε), declared and measured (decided 10-18: no constraint solve, as the merger seeds
and ESE's kicks). Throat η_c (minimal coordinate sphere of each table): 0.9c 1.237, 0.7c 1.117, 0.5c 1.054,
0.2c 1.008 (the middle tables' `eta_throat`: 0.30c 1.017, 0.40c 1.030, 0.46c 1.041). Discriminators: ring-down back to the hold or a triggered collapse; R_throat, ψ4 (2,0) and
(2,±2) at R 14/18, the per-level constraints. t 0 probes (10-18, 1st node card 1, `--preflight-only` PASS, all
75 keys read, 14 frames): l 0 at +1e-3 moves R_pol +1.9989e-3 (table +1.9993e-3) and R_eq +1.707e-3 (table
+1.65e-3: the flat equatorial minimum moves out); m 2 moves R_eq +1.706e-3 (the +x ray, S = 1) and R_pol by 0
(S = 0 on the axis). The throat level's L2_Ham goes 4.4e-8 → 2.0e-4 (l 0) / 1.2e-4 (m 2), the declared violation;
its L2_Mom moves +0.2 %; levels 0–2 identical in both.

## LIVE

| run | node/card | t | stop | speed | ETA (MSK) |
|---|---|---|---|---|---|
| 0c static rerun `00_paper_runs/static_hold_L64_ml3_spdrv0_farfix_t100` | 1st, card 0 (with the 0.30c), 22 GB | 17.7 @ 10:48 | 100 | 9.02 t/h | ≈ 10-19 19:55 |
| 0.30c hold `00_paper_runs/spin_hold_L64_ml3_ve030a_spdrv0_farfix_t100` | 1st, card 0 (with the static), 22 GB | 17.7 @ 10:48 | 100 | 9.00 t/h | ≈ 10-19 19:55 |
| 0.40c hold `00_paper_runs/spin_hold_L64_ml3_ve040a_spdrv0_farfix_t100` | 1st, card 1 (with the 0.46c), 22 GB | 17.8 @ 10:48 | 100 | 9.05 t/h | ≈ 10-19 19:55 |
| 0.46c hold `00_paper_runs/spin_hold_L64_ml3_ve045a_spdrv0_farfix_t100` | 1st, card 1 (with the 0.40c), 22 GB | 17.8 @ 10:48 | 100 | 9.03 t/h | ≈ 10-19 19:55 |
| 0.2c kick, push in `00_paper_runs/spin_kick_L64_ml3_J100_full_l0_eps_m1e3_spdrv0_farfix_t100` | 2nd, card 0 (with the push out), 22 GB | 32.1 @ 10:48 | 100 | ≈ 10 t/h shared (20.3 alone) | ≈ 10-19 17:20 |
| 0.2c kick, push out `00_paper_runs/spin_kick_L64_ml3_J100_full_l0_eps_p1e3_spdrv0_farfix_t100` | 2nd, card 0 (with the push in), 22 GB | 0 @ 10:51 | 100 | ≈ 10 t/h shared | ≈ 10-19 19:05 |
| 0.2c L 64 N 192 farfix `00_paper_runs/spin_hold_L64_N192_ml3_J100_full_spdrv1_farfix_t100` | 1st, card 0 | 100.01 | 100 | – | FINISHED 10-19 04:58 |
| 0.2c L 128 N 256 far-zone GW run `00_paper_runs/spin_hold_L128_ml3_J100_full_farfix_t150` | 1st, card 1 | 150.00 | 150 | – | FINISHED 10-19 05:06 |
| 0.5c L 64 N 192 farfix `00_paper_runs/spin_hold_L64_N192_ml3_ve050a_spdrv1_farfix_t100` | 2nd, card 0 | 100.01 | 100 | – | FINISHED 10-19 05:47 |

The four holds (go 10-18, confirmed 10-19 ≈ 08:45 MSK; no checkpoints) started 10-19 08:48 MSK, two per card on the
first node; the second node's card is idle. Start checks: preflights PASS; the static's t 0 L2_Ham 2.0955094722e-3 and
L2_Mom 0 equal its archived anchor's, and its frame 0 is the anchor's (identical outside r 3); t 0 L2_Ham / L2_Mom
2.0120e-3 / 7.43e-5 (0.30c), 2.0120e-3 / 9.73e-5 (0.40c), 2.0528e-3 / 1.132e-4 (0.46c), the 0.2c's 2.0448e-3 / 5.10e-5;
level boxes ±20 / 10 / 5 in every run, so R 14 and 18 sit wholly on level 1, R 10 is inscribed in level 2's cube and
R 30 is on level 0 inside the KO sponge (reference only), as in the paper 0.2c; 22 GB per run, 45 GB per card. The ψ4
header and the first MOTS rows come with the consumers' t 0 pass (a cold MOTS search). At t 1.9 (09:02 MSK): no NaN; each
consumer takes 1.5 min a plotfile against one every 6.6 min; MOTS R flat to 1e-8 (3.8860 / 4.1889 / 4.4378 / 4.6719);
the static's L2_Ham 2.509e-3 equals its anchor's at t 0.5–1.9.

The 0.2c push-in kick (l 0, ε −1e-3 at η_c 1.0079, width 0.5; go 10-18) started alone on the second node 10-19
09:12 MSK as the first kick evolution (decided 10-19: one kick first, the other five after it), binary kick af28ad29,
the paper 0.2c's params plus the kick keys with the drive off (diffed), no checkpoints. Start checks: preflight
PASS; t 0 R_eq / R_pol 4.05145 / 4.01865, both −1.986e-3 against the hold's (2ε); levels 0–2 identical to the
hold's; the throat level's L2_Ham 2.31e-3 (hold 8.0e-6), the declared O(ε) violation; 22 GB; 20.3 t/h. At t 3 (09:21
MSK): keep-last pruning runs (3 plotfiles, 7.1 GB); the consumer takes 1.4 min a plotfile against one every 3.0 min;
the throat springs back, R_eq −1.99e-3 → −1.26e-3 against the hold (R_pol −1.30e-3). **No collapse at t 32
(10:48 MSK): the throat goes the other way.** It passes the hold's radius at t 12.8 and then grows exponentially,
R_eq +3.3 % and R_pol +3.6 % above the hold at t 32, e-folding every ≈ 5 (4.0 over t 16–24, 5.2 over 24–32); the
MOTS is lost from t ≈ 23; no NaN; the throat level's L2_Ham 4.7e-4 (hold 6.2e-5), level 0's 3e-6 (the kick's
violation travelling out). This is the merger paper's sign rule (`research/merger/article/research.tex`, Sec.
single:branching): a lone drainhole's fate is opposite to the push, squeezed it inflates and pushed outward it
collapses (ε ±1e-2, ±1e-3), and the constraint defect does not pick the branch (a constraint-solved push gives the
same). The spinning 0.2c keeps the rule.

The 0.2c push-out kick (l 0, ε +1e-3, the collapse sign; go 10-19) started 10:51 MSK on the same card as the push in
(no checkpoints). Start checks: preflight PASS; t 0 R_eq / R_pol 4.06758 / 4.03465, both +1.988e-3 against the hold
(2ε); levels 0–2 identical to the hold's, the throat level's L2_Ham 2.29e-3 (the push in's 2.31e-3); 46 GB on the card.
The consumer's t 0 pass: ψ4 header R 10 14 18 30, MOTS R 4.0303 (+1.99e-3), 14 frames; the t 0 slices equal the
hold's except χ out to r 3.3 and Ψ4 out to r 4.1.

**The far-zone run FINISHED t 150** (L 128 N 256, 10-19 05:06 MSK, no NaN). Its throat is the L 64 N 128's to 4
digits (R_eq −1 / −10 / −20 % at 46.86 / 61.99 / 66.95, τ 6.57; χ on the floor at 66.2–68.4 in the four central
cells only; the MOTS R 2.522, M_MS 1.261, over t 138–150): the box and the sponge never reach the throat. Levels 0–1
Ham 3.1e-7 / 1.7e-7 at t 80, 600–1000× below the driven L 64's. **The wave (claim 3):** r·Δψ4 (2,0) has one waveform
in t − R at R 14 / 18 / 30 / 40 / 45: trough −1.47e-4 at t − R 75, peak 2.27e-4 / 2.15e-4 / 2.05e-4 / 2.03e-4 /
2.02e-4 at t − R 86–88, trough −1.53e-4 to −1.56e-4 at t − R 99–100, then a ring-down (period ≈ 24). It is flat in
R to 11 % over R 14–45 and to 1.3 % over R 30–45 (a 1/r radiative field), 10⁴–10⁵× the pre-collapse level at
R 30–45, and R 14 / 18 match the L 64 N 128's to ≤ 2 % through t 100 (the drive's face junk does not reach them).
The pre-fix run's R 30 burst (r ψ4 up to 0.9 by t 94) was junk. Trust 150; packed.

**The 0.5c N 192 FINISHED t 100** (10-19 05:47 MSK, second node, no NaN): no floor, max|K| 1.0e-2, no horizon. The
throat shrinks slowly from t ≈ 55 (R_eq −0.1 % at 68.5, −1.0 % at 99.4: τ 13.4 over that window, the 0.2c's 4.7–5.1;
MOTS R 4.962 → 4.898, −1.3 % at t 100; the pre-fix L 64 0.5c was −1.6 % at t 80). No constraint knee: L2_Ham flat
(2.32e-3 → 2.34e-3), L2_Mom ×2 at 83 with the shrinking throat (level 3), levels 0–1 the drive's shell junk (Ham
8e-5 at t 100), level 2 9e-7. **The slow recipe now quotes to t 100.** Trust 100; packed.

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
1.2e-6 / 3.8e-7 / 7.8e-8 at t 6 (≈ 4th order). **N 128 FINISHED t 100** (18:12 MSK, no NaN) through the collapse into
a settled horizon: R_eq −1 % at 46.9, −10 % at 62.0, −20 % at 67.0 (τ 6.6 over −1 → −10 %; the N 96 6.7); the MOTS
leaves the throat at t ≈ 60 (θ_in −0.09), the throat's minimal sphere is gone from 75, and the MOTS settles at R 2.524
(M_MS 1.262) over t 88–100; χ on the floor at 66.2 (the central cell only, inside the horizon, t 66–67; χ back to 1e-3
there), max|K| > 0.1 at 67.5; trust 100 (raised from 66 for the waves, 10-18); the pre-fix N 128's sequence within
0.2. Packed, scratch pruned. **The (2,0) wave** (r·ψ4 minus its t 0 value, the static part of the rotating
background; the consumer's stream already carries the factor r): r·Δψ4 1.2e-4 in the first lobe at R 10 (t 74),
3.0e-4 at R 10 (t 96) and 2.3e-4 at R 14 (t 100); outgoing at ≈ c (R 14 → 18: 1.00 c on the features that passed
both; the equatorial Weyl4 lobe r 10 → 22: 1.0 / 1.0 / 0.89 c); about 10× below the merger's 5 % quadrupole-kicked
static collapse (r ψ4 2.9e-3 at R 10, `results/merger/figures/08_waves/psi4_gallery.png` (a)). **Corrected 10-19:**
the first quote (1.2e-3, ≈ 3e-3, "the size of the merger's kick") multiplied the stream by R a second time. Still a
wave, not junk (the far-zone run above). Figure: `<run>/waves/psi4_l2m0_radiated_N128.png` (plot_extracted_psi4.py on
the background-subtracted file; its r·Re axis is right).

**N 192 FINISHED t 100** (10-19 04:58 MSK, no NaN) through the collapse: R_eq −1 % at 57.8, −10 % at 71.9, −20 % at
76.6 (about 10 after the N 128: the resolution-seeded onset); the MOTS leaves the throat at t ≈ 70 and reads R 2.533
(M_MS 1.266) at t 100, still settling; χ on the floor at 78.3–79.9 in the four central cells only (inside the
horizon), max|K| > 0.1 at 79.2; trust 100. τ(−1 → −10 %) 6.72 / 6.57 / 6.12 (N 96 / 128 / 192) in coordinate time,
3.57 / 3.28 / 3.13 in the proper time of the throat's equatorial ring (∫α dt): each member collapses at a different
throat lapse (0.549 / 0.518 / 0.529 at −1 %), so the coordinate rate does not converge and the proper one does
(≈ 3rd order). Its wave, shifted by the collapse delay (9.9), matches the N 128's at R 10 / 14 / 18 to 6–9 %. Packed.

**Triplet convergence to t 50** (10-18 ≈ 19:30, the N 192 at t 51; orders 96→128 / 128→192 from
`constraint_norms_levels.dat`): every level converges in both pairs. Ham L0 2.8/2.8 at t 10 → 4.2/4.5 at t 50; Mom L0
2.3/2.4 → 4.4/4.4; Ham L1 2.1/2.4 → 4.7/4.9; Mom L1 1.8/2.1 → 4.6/4.8; Ham L2 2.2/2.4 → 1.9/1.9; Mom L2 2.0/2.3 →
3.7/4.0; Ham L3 4.0/4.3 → 3.4/4.0; Mom L3 3.0/4.1 → 4.3/4.3 (levels 0–1 jump to 4–5 from t ≈ 30, where the drive's
shell junk takes over their error). The throat's pre-collapse drift converges at 4th order (t 5–10: 3.6–4.2). The
collapse onset is resolution-seeded (R_eq −0.1 % at 30.7 / 36.1 / 46.1: shifts that fit a seed shrinking at 4th–5th
order); the N 192's collapse came where expected (−1 % at 57.8, −10 % at 71.9; τ above). **Through the collapse
(10-19, figure `results/spinningwormhole/figures/convergence_02c.png`, `plot_convergence --spin 0.2c`):** past t ≈ 45 the
members sit at different collapse stages, so equal-t orders mean nothing; at equal R_eq deficit (−0.1 % … −10 %) the
throat level converges at 3.3–4.0 (Ham) and 3.4–4.2 (Mom). Aligned at −10 %, the collapse curves, the R 14 wave
(N 128 / 192 within 6 %) and the horizons overlap. Why the constraints still grow after the collapse: the note below.

**Constraint growth: the slow runs' t ≈ 80 knee is gone** (the N 128 to t 100, 10-18). The pre-fix "Ham ×2 at 78–85"
was levels 1–2 growing exponentially (e-fold 5–7) from t ≈ 30 until they dominated the whole-box norm (pre-fix 0.2c
N 128: level 1 Ham 1.6e-5 at t 30, 1.6e-1 at 80; the static and the 0.5c alike). On the fixed binary at t 80: level 1
1.8e-4, level 2 5.9e-6 (900× / 8000× lower); level 2 flat at ~5e-6 over t 75–100. Still growing: the throat level
through the collapse (Mom 3.1e-4 at 60 → 5.4e-3 at 80, flat to 100), and levels 0–1 from t 31 at every N, the drive's
shell junk (the drive-off sponge test: level 1 1100× lower at t 55; order +4.1 to +5.1 across N 96/128/192 at
t 35–45), to 2e-4 at 80 and 7e-4 at 100. The whole-box L2_Ham never doubles. The 0.2c's throat quotes stop at its collapse;
its exterior and waves hold to t 100; the 0.5c N 192 settles whether the slow recipe quotes past 80: yes (no knee to
t 100, above).

**Why the constraints grow after the collapse** (10-19). Two separate causes:
- **Levels 0–1: the sponge drive.** Once the collapse's outgoing pulse reaches the sponge shell, the drive keeps
  pulling the shell back to the t = 0 data, and that breaks the constraints. The far-zone run has no drive, and its
  levels 0–1 are 600–2000× lower at t 80–100 (3e-7 against 2e-4).
- **Level 3: the collapse itself.** It jumps while the throat pinches into a black hole, then stays flat inside the
  horizon: 3.5e-4 (Ham) and 5.4e-3 (Mom) from t 80 to 150 in the far-zone run.

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
**Result** (both FINISHED t 55, no NaN, 17:03 / 17:10 MSK; packed to `10_sponge_test`, scratch pruned): the drive made the
junk. Drive off, at t 55 against the N 96: Weyl4 change at r 28–32 5.8e-7 vs 2.8e-5 (48× lower), r 24–28 1.6e-7 vs
1.5e-6; level 0 Ham 6.6e-6 vs 9.3e-5, level 1 9.0e-8 vs 1.0e-4; r < 24, ψ4 at R 10/14/18 and the throat identical
(R_eq to 1e-8 at t 45, 9e-7 at t 55). The wider absorber cuts the face junk too (1.0e-6) but its drive reaches into
level 1's box (from r 20; level 1 to 21.3) and raises levels 1–2 (Ham 1.8e-4 / 2.0e-5 vs 1.0e-4 / 2.9e-7). Decided
10-18: new L 64 runs (the middle rungs, the low-spin kicks) run with the drive off; the live runs keep theirs.

## NEXT

- The four holds (static, 0.30c, 0.40c, 0.46c) LIVE on the first node since 10-19 08:48 MSK, two per card, ETA ≈ 19:55
  MSK. The 0.2c push-in (inflating, the sign rule) and push-out (the collapse sign, since 10:51 MSK) kicks LIVE on
  the second node's card, ETA ≈ 17:20 / 19:05 MSK; the other four kicks PENDING.
- The 0.2c triplet, the far-zone run and the 0.5c N 192 are done and packed (10-19); the first node's scratch pruned
  (41 GB, 10-19 ≈ 08:10 MSK); the second node's (the 0.5c N 192's last plotfiles, 21 GB) pruned 10-19 ≈ 09:35 MSK. Movies
  to the trust windows (`logs/rerender_{0p2c_N192_farfix_t100,0p2c_L128_farzone_t150,0p5c_N192_farfix_t100}*.log`):
  14 full-box + 14 core for each of the three (the N 192s 10-19 08:28, the far-zone run 09:07 MSK), all checked on
  contact sheets (fixed bars).
- Card sharing (measured 10-18 on the 0.2c N 128, L 64): 20.6 t/h alone, 10.2 with one more run on the card, 7.0 with
  two more: one card does ≈ 20 t/h of L 64 N 128 however it is split, so a 100-unit hold takes ≈ 4.9 h alone or
  ≈ 14.5 h three to a card.
- Claim 3's figure (10-19): `results/spinningwormhole/figures/farzone_wave_02c.png` (`plot_farzone_wave`; a copy in the
  run's `figures/`): the throat against the L 64 hold, r·Δψ4 (2,0) at R 14–45 against t − R, the extrema against
  R (over R 30–45 the peak holds to 1.5 %, the troughs to 7.2 % / 2.4 %), and their speed between neighbouring spheres
  against light's over the same stretch (α√χ − β^r on the equator: 0.86 at R 14–18, 0.95 at 40–45): within 1 % of
  light over R 40–45 and 2.5 % over 30–40, ahead of it further in (4–15 %) while the near field fades. The static
  rerun (LIVE) is the no-radiation control on the fixed binary.
- CANCELLED 10-18 ≈ 17:15 MSK: the five 0.9c kicks (the 0.9c is too far from physical spins; their templates stay in
  `templates/`). PENDING instead (go 10-18 ≈ 17:30 MSK, no checkpoints; cards not chosen): six kicks at the low
  spins, the 0.2c and the 0.30c (the black-hole spin limit, J/M² 1.03), each a push in (l 0 −1e-3), out (l 0 +1e-3)
  and a bar (m 2 +1e-3): does a push bring the collapse earlier? Templates ready
  (`templates/params_spin_kick_L64_ml3_{J100_full,ve030a}_*_spdrv0_farfix_t100.txt`): the hold's L 64 N 128 params
  with the drive off plus the kick keys (η_c 1.0079 / 1.0171 from the tables, width 0.5), binary
  `main3d_kick_af28ad29_2026-10-18.ex`, `--subdir drainhole/00_paper_runs`, the hold's consumer flags; ~10 h and
  23 GB each, three per card. Start checks: R_pol/R_eq at t 0 (+/−2e-3 for l 0), frame 0 against the hold's, ψ4
  header R 10 14 18 30. The 0.9c triplet's convergence figure: `results/spinningwormhole/figures/` (10-18).
- Second node (one card): the 0.2c push-in and push-out kicks since 10-19 09:12 / 10:51 MSK; the 0.5c N 192's last plotfiles pruned from
  its scratch (21 GB, 10-19 ≈ 09:35 MSK); 854 GB free.

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

**The ladder against Azad, Blázquez-Salcedo, Khoo & Kunz (arXiv:2301.05243; 10-18).** Their second-order radial
mode ω_I = ω_I⁽⁰⁾ + J² Δω_I⁽²⁾ (r₀ = 1) for our drainhole (η₀ = 2, M = 1: their C = 1 row, ω_I⁽⁰⁾ = −0.390,
Δω_I⁽²⁾ = +0.384) gives τ = η₀ / (0.390 − 0.384 (J/η₀²)²): static 5.13, 0.2c 5.46 (+6.6 %), 0.3c 6.1, 0.4c 8.0,
0.45c 13.2, and stability at J/η₀² = 1.008 (J 4.03, v_e ≈ 0.51c): our 0.5c (J 4.13) sits on it. Measured (pre-fix,
ΔR 1–30 %): static 5.8, 0.2c 6.8 (+17 %), the same slowing with a J² coefficient 0.81 against their 0.384; that
would move the threshold to J ≈ 2.6, v_e ≈ 0.41c, in line with their conjecture that the full instability ends
below the second-order value (≈ 30 % of the extremal J/A = 1/8π). On their J/A scale (area from the t 0 MOTS):
0.2c 12 %, 0.5c 34 %, 0.9c 81 %. Astrophysically only J/M² < 1 is realistic: v_e < 0.29c on this family.
Caveat (10-18): our τ is a coordinate-time fit over a window, not their mode, and it drifts with the window even
for the static throat: 4.1 / 5.1 / 5.8 for deficits 0.1–1 / 0.3–3 / 1–30 % (the 0.2c 4.7 / 5.8 / 6.8, the same in
the farfix N 128), bracketing their 5.13; the spin's slowing grows as the throat shrinks (+13 % early, +17 % late,
against their +6.6 %). Like for like needs the linear mode in Killing time, e.g. small l 0 kicks of both holds.

**The rotating collapse emits a real gravitational wave (10-16).** At R = 30 the 0.21c collapse
(`spin_hold_L128_ml3_J100_full_t100`) shows an l = 2, m = 0 burst |ψ₄| = 3.0e-2 arriving at t = 81 (horizon
formation t ≈ 64 plus ~17 of light travel). The static collapse at the same radius reads 6.0e-5, the
numerical floor (spherical collapse cannot radiate): the spinning burst is 500× above it and 10⁴× above the
run's quiet-phase noise; B1 (0.5c, no collapse) stays quiet. Measurable per spin alongside τ
(`psi4_mode_l2m0.dat` in every pack). **Re-measured on the fixed binary (10-19, the far-zone run, LIVE notes):** r·ψ4
2.0e-4 at R 30–45, flat in R and outgoing at c; the pre-fix burst above was junk; the static control is the pending
static rerun.

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
  not cure it. The knee was levels 1–2's coarse–fine growth: gone on the fixed binary (the 0.2c N 128 farfix).
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
- 10-18: the 0.7c wiped (hold, slow-recipe extra, kicks): above the Kerr bound (J/M² 1.11), not astrophysical; the
  0.9c stays the one stable anchor. The ladder fills 0.2c–0.5c instead, against Azad et al. (FOR THE ARTICLE).
- 10-18: the drive off for all new runs (the sponge test: the drive made the face junk; the throat is the same).
  No reruns for it: the runs with the drive keep their throats and their ψ4 inside R 18.
  The 0.9c kicks dropped (too far from physical spins): the kick study moves to the low spins, the 0.2c first.
- 10-19: the 0.99c, the 0.95c stretch, the clamp validation and the cancelled 0.9c kicks taken off the run matrix.

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
