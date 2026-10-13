# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

**Folders** (decided 2026-10-13; no flat folders): `runs/spinning_wormhole/<family>/<NN_study>/`
mirrors `results/spinningwormhole/campaign/<family>/<NN_study>/`; a triplet sits in a per-spin
folder; superseded runs go to `<family>/00_archive/`. Shared: `backgrounds/ bin/ logs/
manifests/ smoke/ templates/`. Now:
- `drainhole/`: `01_static_hold/`, `02_spin_hold/` (the O(J²) holds), `03_t0_checks/`
  (v_e 0.5, N 96/128/192), `04_fast_spin_hold/` (v_e 0.5, 0.7, J = 1);
- `symmetric_massless/`: `00_archive/L64_A1_superseded/`, `01_t0_checks/L64_ladder/` (the
  morning's v_e 0.5–0.99 checks) and `01_t0_checks/L128_A1/<spin>/` (A1: N 128/192/256
  per spin), `03_spin_hold/<spin>/` (the A3 holds; the probes first).

Launch through `logs/queue_worker.sh <gpu> logs/spin_queue.txt` (each line: template, name,
target folder, fg|bg) or `launch.sh --subdir <family>/<NN_study>[/<spin>]`; pack with
`pack_run.sh <family>/<NN_study> <run dir>`.

## LIVE

| run | node/card | t | stop | speed | ETA |
|---|---|---|---|---|---|
| B1 `spin_hold_L128_ml3_ve050a_t100` (N 256, `drainhole/05_hold_L128/ve050a/`) | first GPU node, card 0 | launched 20:22 UTC | 100 | ~14 t/h (A1's measure) | ~7.2 h, ≈ 03:30 UTC 10-14 |
| probe `spin_hold_L128_N192_ml3_ve085b_lapse1_t100` (`symmetric_massless/03_spin_hold/ve085b/`) | first GPU node, card 1 | launched 20:54 UTC | 100 | ~45 t/h (N⁴) | dies by t ≈ 4 in ~10 min, or t = 100 in ~2.2 h ≈ 23:10 UTC |

**The far-side fix probe** (its go 2026-10-13, no checkpoints; N = 192 —
dx0 = 1 is retired): the A3 ve085b hold with one knob,
`spinning_initial_lapse_type = 1` (lapse = √χ at t = 0, pre-collapsed at the
punctures) instead of the stationary lapse that died there at t ≈ 4. If it
dies too, the agreed next probe on this card is min_chi 1e-4 (the merger's
FARZONE knob), same grid. A survivor then reruns ve070a (drainhole) with the
winning knob — that one still waits for its go.

The B1 production member (its go 2026-10-13): the v_e 0.513 drainhole on plain
L128 N256 ml3 (`params_spin_hold_ve050a_L128_N256.txt`), full-box frames
(zoom 128, cache 2048), rolling checkpoints every t = 10 keep 3 (asked). Its
static twin on this exact layout is the merger's `single_hold_L128_t100`:
the question is whether the L64 result (collapse slows with spin) holds with
the clean t = 100 baseline. Card 1 stays free; nothing else launches without
its go. Earlier today (final packing 19:50 UTC): every previous run packed,
scratch empty. Closed out: in `drainhole/04_fast_spin_hold/` v_e 0.7
(died t = 42.36, far-side puncture), v_e 0.5 (finished; 14 movies to t = 64) and
J = 1 on exact data (died t = 70.64 at the end of a collapse); in
`symmetric_massless/` the 21 A1 runs (`01_t0_checks/L128_A1/`) and the three puncture
probes (`03_spin_hold/`). The six L = 64 A1 runs are superseded
(`symmetric_massless/00_archive/`, not packed).

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
return comes at t ≈ 120–128. **Triplets are N = 192 / 256 / 384** (dx0 0.667 /
0.5 / 0.333; finest Δx 0.0833 / 0.0625 / 0.0417): dx0 = 1 is too coarse for any
evolution, so the coarsest member keeps dx0 ≤ 2/3 and the production grid is
dx0 = 0.5 (corrected 2026-10-13; the A1 N = 128 members stand as t = 0 checks
only, and the old L = 64 at N = 128 was this same dx0 0.5). From the measured
14.1 t/h and 46 GB at N = 256: ~2.2 / 7.1 / ~36 h to t = 100 (N⁴), ~45 GPU-h a
triplet; N = 384 scales to ~155 GB, over the 81.5 GB card, so those members
need both cards (MPI) or their own decision.

**BLOCKER: the far-side puncture.** The valid evidence is the drainhole's
v_e 0.7 hold (L64, dx0 0.5): died at t = 42.36 at the centre (the compactified
far end), lapse/χ to the floor, K runaway, throat unmoved. The three first
probes (v_e 0.43 / 0.67 / 0.85) died at t ≈ 4 the same way but were SUPERSEDED
2026-10-13: they ran N = 128 on L = 128 (dx0 = 1, below the floor), so grid and
physics are confounded there (archived in
`00_archive/L128_N128_probes_superseded/`, ve085b wiped; packs removed). No
spinning family (b) hold (A3, A4) and no fast drainhole hold (B2, B3) runs
until the far side is handled; A2's static Ellis is massless there and the
slow drainhole (v_e ≤ 0.51) held. Probes at N ≥ 192: the √χ initial lapse
(type 1, LIVE on card 1 — cleared the t ≈ 4 window, χ recovered off the
floor); if it dies later, min_chi 1e-4 (its go given); a control at N = 192
with the original stationary lapse, to split the lapse from the resolution,
waits for its go.

*Phase A: symmetric, family (b) at η0 2*

| run | needs | restart from | waiting on |
|---|---|---|---|
| A2 `static_hold_L128_ml3_sym_t100` ×3 (N 192/256/384) | ~45 GPU-h; static table η0 2, M 0 (`backgrounds.py static`); L128 templates | — | its go |
| A3 `spin_hold_L128_ml3_ve024b_t100` ×3 | ~45 GPU-h; table `fam_b_ve024_eta2` (built) | — | the far-side puncture fix, its go |
| A3 `spin_hold_L128_ml3_ve043b/067b/085b_t100` ×3 | as above (the N = 128 probe templates sit below the ladder now) | — | the far-side puncture fix, its go |
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
| B1 the rest: ve050a N 192 / 384, static ×3, J = 1 ×3 | templates written (`params_{static_hold,spin_hold_ve050a,spin_hold_J100_full}_L128_N{192,256,384}.txt`); the static L128 N256 anchor already exists (the merger's `single_hold_L128_t100`) | — | its go; the N = 384 members on the junk-shell layout (below) |

**Junk-shell layout for the N = 384-class members** (agreed 2026-10-13, not yet
templated): same L = 128 box, but the outer r > 32 shell stays one level
coarser (tagging_L 128, max_level 4, base dx0 = 2× the interior) — the
wormhole keeps its full resolution, the startup pulse dies in the 48–64 sponge,
return still t ≈ 128. Params-only (no code change). It cuts the finest triplet
member from ~36 h / 155 GB (impossible on one card) to ~16 h / ~70 GB, a
triplet to ~25 GPU-h. The production N = 256 member gains little (~7 h either
way), so it runs plain.
| B2 `spin_hold_L128_ml3_ve070a_t100` ×3 | the far-side puncture fix | — | the fix, its go |
| B3 higher spin ×3 (v_e 0.9 / 0.95 / 0.99), L128 | tables exist | — | B2, its go |

**Every quoted run is a triplet** (decided 2026-10-13; the stability protocol in
`SpinningWormhole.md`, after Evstafyeva, Siemonsen & East, arXiv:2508.11527):
L128 ml3 at N = 192 / 256 / 384 (finest Δx 0.0833 / 0.0625 / 0.0417; dx0 never
1). A growth is physical only if its τ converges to a nonzero value, the
finest-level constraints converge while it grows, and the throat's areal radii
or MOTS grow with it. N 192 / 384 costs are N⁴ estimates from the measured
14.1 t/h at N = 256.

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
1. **t = 0 checks: PASS** (07:03–07:50; `*/0N_t0_checks/`, `t0_checks.py`).
   v_e 0.5, 3 grids: constraints converge at 4th order
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
4. **A1, family (b) on L = 128: PASS** (21 runs, v_e 0.24–0.99 × N 128/192/256;
   `L128_A1/<spin>/t0conv_<spin>_L128_checks.txt`). Throat radii converge to the
   table (R_eq −7e-5 to −9e-4 at N = 256); Ham/Mom 4th order inside the throat,
   1/dx² and 1/dx outside (the tables' interpolation); the 3D ADM mass integral
   equals the table metric's on the same grid to ≤ 1e-12, extrapolated M within
   2e-5–7e-4 of the table's (0.7 % at 0.99), J within 2e-3 (0.24) to 2e-5 (0.99).
5. **The first family (b) hold probes died at the far-side puncture** by
   t ≈ 4, but on a dx0 = 1 grid — SUPERSEDED; the N ≥ 192 retests (the
   BLOCKER above) are what counts now.

## NUMERICS DEBT (Step 0 of `SpinningWormhole.md`, none done; re-noted 2026-10-13)

This file carried the list until ca71ceed compacted it away; restored because
every item is still open:
1. **Why Δt = 0.02 Δx.** The only evidence is the merger's
   `single_hold_dt005_t070`: at 0.05 it matched to t ≈ 30, then drifted to a
   different solution (max|K| ×30 by t = 35, L2_Ham ×35 by t = 40, lapse
   floored at t = 61). A measured limit, cause unknown; every hold pays it
   (~7 h to t = 100 at N = 256).
2. **Constraint norms are level 0 only**
   (`Examples/SpinningWormhole/SpinningWormholeLevel.cpp:336`); the triplet
   protocol wants the finest levels with the punctures masked (today the
   plotfiles' derived constraints cover this offline, in `t0_checks.py`).
3. **Constraint-solved seeds.** The Π shell seed violates the constraints in
   proportion to its amplitude (`SimulationParameters.hpp:50`); perturb Π,
   then re-solve the constraints.
4. **Waveform extrapolation in 1/R**: absent; matters least under the
   stability-only plan.

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
