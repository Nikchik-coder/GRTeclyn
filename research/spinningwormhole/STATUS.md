# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

**Folders by family** (decided 2026-10-13): run dirs in
`runs/spinning_wormhole/{drainhole,symmetric_massless}/` (launch with `--subdir
drainhole` or `--subdir symmetric_massless[/validation]`), packed runs in
`results/spinningwormhole/campaign/{drainhole,symmetric_massless}/NN_study/`
(`pack_run.sh <family>/NN_study <run dir>`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| A1 on L = 128: 21 t = 0 checks `t0conv_ve0XXb_L128_N{128,192,256}_ml3` (symmetric, to t = 1) | first GPU node / 0 and 1 | 2 of 21 started (14:14) | 1 | ~2–10 min each | ~1.2 h, ~15:30 |

No checkpoints (A1: asked, none). A1 runs pop `runs/spinning_wormhole/logs/a1_queue_L128.txt`
(`a1_queue_v3.sh`, one worker per card) into `symmetric_massless/validation/`; tables
`runs/spinning_p3/tables_eta2/` (ve024–085 new: `p5_A1_tables.py`, midpoint error ≤ 8.5e-8).
The first six A1 runs on L = 64 (v_e 0.24, 0.43; 13:49–14:10) are superseded by
the L = 128 set (decided 2026-10-13); their 25 GB of scratch wait for the word.
Closed out today, all in `drainhole/04_fast_spin_hold/`: v_e 0.7 (died t = 42.36,
far-side puncture), v_e 0.5 (finished; 14 movies to t = 64), J = 1 on exact data
(died t = 70.64 at the end of a collapse).

**Frames over the whole box** (decided 2026-10-13): launch with `--zoom 128
--coord 64 --center 64 64 64` and `GRTECLYN_FRAMES_BUFF_CAP=2048`, so the live frames,
the preflight's frame 0 and the slice cache cover ±64 at one pixel per finest cell
(2048² at N = 256); zooming is done later, when the frames are redrawn from the cache
(`rerender_frames.py` needs a window option for that, not yet written).

## QUEUED

**Order (decided 2026-10-13): the symmetric family first, then the drainhole.**
The symmetric family is the one Kleihaus–Kunz and CKK published and Azad et al.
analysed in full, so it validates the 3D pipeline against published values before
the drainhole, which has no published fast-spin data, is taken to high spin.

**Every run from now on is on L = 128, clean to t = 100** (decided 2026-10-13).
The sponge (extra Kreiss–Oliger dissipation in r 24–32; the merger's
`Source/Grids/SpongeZone.hpp`) removes only grid-scale noise: the outgoing gauge
pulse (λ ~ 8 ≫ Δx 0.5) passes it, reflects off the faces and is back at the
throat by t ≈ 64 on L = 64, which ends every L64 hold's trust window (in ve050a,
K enters the frame window from t ≈ 60). The layout is the merger's own
`single_hold_L128_t100`: the L64 Step 1 grid's base Δx and nested boxes
(tagging_L 64: ±16/8/4, max_level 3) in a box twice as wide, sponge 48–64, so the
return comes at t ≈ 120–128. Triplets are N = 128 / 192 / 256 (dx0 1 / 0.667 /
0.5; finest Δx 0.125 / 0.083 / 0.0625, N = 256 being the Step 1 grid's Δx
everywhere). The merger ran this layout at 13.9 t/h: ~7.2 h to t = 100 at
N = 256, ~10 GPU-h a triplet. Still open for "clean to t = 100": the far-side
puncture. In every family (b) run so far min χ falls ×8 in the first time unit
(the far side has positive mass, a black-hole-like puncture), the way the dead
ve070a's did before it hit the floor; A2's static Ellis is massless there, the
spinning ones are not.

*Phase A: symmetric, family (b) at η0 2*

| run | needs | restart from | waiting on |
|---|---|---|---|
| A2 `static_hold_L128_ml3_sym_t100` ×3 (N 128/192/256) | ~10 GPU-h; static table η0 2, M 0 (`backgrounds.py static`); L128 templates | — | A1, its go |
| A3 `spin_hold_L128_ml3_ve024b_t100` ×3 | ~10 GPU-h; table `fam_b_ve024_eta2` (built) | — | A2, its go; the far-side puncture |
| A3 `spin_hold_L128_ml3_ve043b_t100` ×3 | as above, v_e 0.43 | — | A2, its go; the far-side puncture |
| A3 `spin_hold_L128_ml3_ve067b_t100` ×3 | as above, v_e 0.67 | — | A2, its go; the far-side puncture |
| A3 `spin_hold_L128_ml3_ve085b_t100` ×3 | as above, v_e 0.85 | — | A2, its go; the far-side puncture |
| A4 `spin_hold_L128_ml3_ve090b/095b/099b_t100` ×3 | tables exist (`tables_eta2/`) | — | A3, its go |

- **A1, what it validates:** the Kleihaus–Kunz 2014 Fig. 1 quantities (M/M0,
  J/J0, R_p/R, R_A/R, ΩJ), read off the 3D grid at t = 0 and compared with the
  table and the digitized KK curves, converging across N.
- **A2:** the static Ellis growth against Azad et al.'s C = 0 rate (τ ≈ 1.7 at
  η0 = 2).
- **A3:** their two modes and the crossing.
- **A4:** beyond any published stability result.

*Phase B: drainhole, family (a), after Phase A*

| run | needs | restart from | waiting on |
|---|---|---|---|
| B1 the three drainhole holds again as L128 triplets: static, v_e 0.51, J = 1 | ~10 GPU-h each; replaces the L64 N 64 / 96 partners, which would stop at t = 64 too | — | Phase A, its go |
| B2 `spin_hold_L128_ml3_ve070a_t100` ×3 | the far-side puncture fix | — | Phase A, the fix, its go |
| B3 higher spin ×3 (v_e 0.9 / 0.95 / 0.99), L128 | tables exist | — | B2, its go |

**Every quoted run is a triplet** (decided 2026-10-13; the stability protocol in
`SpinningWormhole.md`, after Evstafyeva, Siemonsen & East, arXiv:2508.11527):
L128 ml3 at N = 128 / 192 / 256 (finest Δx 0.125 / 0.083 / 0.0625). A growth is
physical only if its τ converges to a nonzero value, the finest-level constraints
converge while it grows, and the throat's areal radii or MOTS grow with it. N 128 /
192 costs are N⁴ estimates from the merger's 13.9 t/h at N = 256.

**Why a symmetric ladder** (decided 2026-10-13: the paper carries both
families). Azad et al. computed the second unstable mode, and its crossing
with the main one, only for C ≤ 0.2 (near-symmetric). For our drainhole
(C = 1) they give the main mode alone (τ ≈ 5.1 at η0 = 2). So the paper's
mode-merger test runs on family (b): spins at 10 / 20 / 33 / 50 % of the
limiting J/A, where 33 % is their predicted crossing (J/A ≈ 0.013) and 50 %
is where their O(J²) main mode reaches zero. The static Ellis anchor comes
first (their C = 0 rate gives τ ≈ 1.7 at η0 = 2). Same gauge and η0 1 → 2
rescale as the family (b) t = 0 ladder; no checkpoints unless asked.

## NOW: STEP 3, TEST THE FAST-SPIN TABLES

The question the solver was built for: **does fast spin fix the instability?**
The O(J²) holds could not tell (their push was the data's own J⁴ error); the
full tables are exact to ~1e-10.
1. **t = 0 checks: PASS** (07:03–07:50; `runs/spinning_wormhole/*/validation/`,
   `t0_checks.py`). v_e 0.5, 3 grids: constraints converge at 4th order
   inside the throat; outside they grow as 1/dx² (Ham) and 1/dx (Mom), the
   fingerprint of the tables' fixed ~2e-7 bilinear error, 10⁴× below the
   O(J²) holds' push; throat radii converge to the table (R_eq −5e-5 at
   N = 192). Family (b) to v_e 0.99: throat radii within 0.1 %, constraints
   at the static hold's level.
2. **The drainhole at v_e 0.5 and 0.7** (the earlier holds' L64 grid, to
   t = 100). 0.7: died at its far-side puncture (t = 42.36), throat frozen.
   0.5: the throat shrinks, the static hold's sign, but slowly (MOTS R
   −0.61 % at t = 64, −2.9 % at 100; e-fold time ~5 at t 40–50, then a
   steady rate); no horizon, where the static hold's detached at t ≈ 61.
   Both are cut by the L64 boundary return (t ≈ 64), hence L = 128 above.
3. **J = 1 on exact data: the push vanishes.** The throat collapses on the
   static hold's mode (R_eq −1 % at t = 46.9, −10 % at 61.8; τ 6.8 against the
   static hold's 5.8 by the same measure) and the run dies inside the collapse
   at t = 70.64. The O(J²) hold's inflation was its data's error. With 0.5
   (−0.5 % by t = 64) the collapse slows with spin: the headline to confirm on
   L = 128 (B1).

## DONE

- **Step 0** (2026-10-11): the static hold twins the merger's `single_hold`:
  collapse, τ 5.27, trust window t ≤ 64.
- **Step 1** (2026-10-12): the O(J²) holds at J = 0.25 / 1 inflate (τ 5.8 / 5.6);
  their push grew as J⁴, the data's error, not the spin.
- **Step 2** (2026-10-13): full solver, both families to v_e 0.99, every gate
  green; CKK's eq. (12) is wrong; tables in `runs/spinning_p3/tables/`
  (error ≤ 1e-7 to v_e 0.9).

## RULES

Merger launch discipline: go first, checkpoints asked per run, full frame set,
STATUS pushed at every launch/stop. Ψ4 radii in the box's wave zone (L = 64:
12 / 16 / 20, decided 2026-10-12; L = 128: inside r 48, set with the A2
templates).
