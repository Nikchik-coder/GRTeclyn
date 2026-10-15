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
| B1 `spin_hold_L128_ml3_ve050a_t100` (N 256, `drainhole/05_hold_L128/ve050a/`), relaunch from t = 0 | first GPU node, card 0 | t = 20.4 at 06:30 UTC 10-15 | 100 | ~13.9 t/h | ~5.7 h, ≈ 12:15 UTC 10-15 |
| probe `spin_hold_L128_N192_ml4_ve085b_lapse1_eta02_t100` (eta 1 → 0.2, the shift damping matched to the far puncture ~1/(2M); else the dead ml4 template) | first GPU node, card 1 (2-way share) | launched 06:55 UTC 10-15 | 100 | ~14 t/h (est., shared) | dies by t ≈ 24 in ~1.7 h ≈ 08:40 UTC, or t = 100 ≈ 14:00 UTC 10-15 |
| probe `spin_hold_L128_N192_ml4_ve085b_lapse1_minchi4_t100` (min_chi 1e-8 → 1e-4 on the ml4 grid — the FARZONE floor at compliant resolution; else the dead ml4 template) | first GPU node, card 1 (2-way share) | launched 06:57 UTC 10-15 | 100 | ~14 t/h (est., shared) | same windows |
| dt ladder `static_hold_L64_ml3_dt005_t070` (`drainhole/06_dt_ladder/`; numerics debt 1, its go 10-15) | second GPU node, card 0 | launched 05:31 UTC 10-15 | 70 | ~12 t/h (3-way card share, 88 % aggregate) | ~5.5 h, ≈ 11:00 UTC 10-15 |
| dt ladder `static_hold_L64_ml3_dt0035_t070` (same study) | second GPU node, card 0 | launched 05:34 UTC 10-15 | 70 | ~9.5 t/h (shares rise as arms finish) | ≈ 12:20 UTC 10-15 |
| dt ladder control `static_hold_L64_ml3_dt002ctl_t100` (same study; levnorm-binary regression vs the packed Step 0 hold) | second GPU node, card 0 | launched 05:35 UTC 10-15 | 100 | ~5.4 t/h now | ≈ 15:40 UTC 10-15 |

**2026-10-14 ~21:53 UTC the node container was killed externally** (and once
before, 23:44 UTC 10-13, which is what stopped B1): scratch wiped, both
first-launch runs gone, no checkpoints survived (they lived on scratch only).
What each had shown by then:

- **B1 first launch (killed, not a death): clean to t = 46.70, zero NaN.**
  MOTS R 4.9612 → 4.9573, **−0.08 % by t = 46**, where the static twin
  (`single_hold_L128_t100`) was already −1 % by t = 44 — the spin is slowing
  the collapse ~10× at mid-time, matching the L64 result. χ_min steady
  1.5e-6, lapse_min 0.17, all smooth. 47 frames + 363 MB slice cache to
  t = 46 survive on NFS (`..._t100_killed_t46/`), so movies to t ≈ 46 are
  makeable. Relaunched from t = 0 on the same template, 05:00 UTC 10-15.
- **√χ-lapse probe: a genuine physics death, not the kill** — NaN in h11 at
  **t = 22.87** (21:07 UTC 10-13): far-side χ pinned at the 1e-8 floor,
  |K|max 1.2 → 94, MOTS lost from t ≈ 20. The √χ lapse cleared the old
  t ≈ 4 window (~6× later death) but the far-side puncture still wins.
  The min_chi 1e-4 probe launched 05:00 UTC 10-15 was KILLED BY HAND at
  t = 9.13, before its verdict: the resolution check that should have run
  before the launch (BH rule dx ≲ M/40, far mass M ≈ 2.5 → dx ≤ 0.06;
  ml3 gives the puncture 0.083) says ml3 under-resolves the far side
  whatever the floor. Superseded 05:35 UTC 10-15 by the **ml4 probe**:
  min_chi back at 1e-8, √χ lapse kept, `max_level = 4` → level-4 box ±2
  (dx 0.0417) on the puncture alone
  (`params_spin_hold_L128_N192_ve085b_lapse1_ml4.txt`, two-line diff:
  max_level + the regrid_interval entry it sizes).
- **ml4 probe DIED at t = 23.76** (06:25 UTC 10-15): NaN in h11 on level 4,
  far-side χ pinned on the 1e-8 floor, lapse_min 2.2e-4 (collapsed at the
  puncture, as it should), |K|max 64 → 2009 in one coarse step — the same
  K-runaway death as ml3's t = 22.87, **+0.9 time units for 2× resolution**.
  The BH-rule dx (0.0417 ≤ M/40) is satisfied and changes nothing:
  RESOLUTION IS RULED OUT as the far-side fix. The gauge is already full
  moving-puncture (advective 1+log + Gamma-driver), so the surviving
  suspects are its parameters at the heavy puncture — eta = 1 is set by
  M_ADM = 1, while the BH rule of thumb eta ≈ 1/(2M_punc) with
  M_punc ≈ 2.5 wants ~0.2 — and the initial data itself (whether the
  compactified far end is evolvable at all). Both remaining knobs went
  live in parallel on card 1 (the go 06:50 UTC 10-15): the **eta02
  probe** (eta 0.2, one-line diff) and the **minchi4-ml4 probe**
  (min_chi 1e-4 on the ml4 grid — the floor retried at compliant
  resolution, its ml3 test never got a verdict). One-line-diff templates
  `..._ml4_eta02.txt` / `..._ml4_minchi4.txt`; frame 0 of both is
  byte-identical to the dead ml4 probe's, both floors confirmed in
  `collapse_diagnostics.dat` (1e-8 vs 1e-4). No checkpoints (per-run
  call, none asked).

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
(type 1) cleared the t ≈ 4 window but DIED at t = 22.87 (NaN in h11, far-side
χ on the 1e-8 floor, |K|max → 94) — it helps, it does not win; the ml4
probe on top of it (level-4 box ±2, dx 0.0417, BH rule satisfied) DIED THE
SAME WAY at t = 23.76 (06:25 UTC 10-15), +0.9 time units for 2× resolution:
resolution is ruled out, the puncture K-runaway is gauge- or data-level.
A control at N = 192 with the original stationary lapse, to split the lapse
from the resolution, waits for its go. Agreed 2026-10-15: if min_chi does
not win, the next knob is DEEPER CENTRE REFINEMENT — the far side is a
genuine positive-mass puncture and likely needs BH-class resolution at r = 0.
(Both tried 10-15: the min_chi 1e-4 probe was killed pre-verdict for the
missed resolution check, and ml4 then failed on its own — see above.)
Params-only: raising max_level to 4 (or 5) under the same tagging_L 64 adds
nested boxes ±2 (±1) on the puncture alone, finest dx 0.0417 (0.0208) at
N 192 — the BH rule of thumb dx ≲ M/40 with the far mass M ≈ 2.5 wants
≤ 0.06, so ml3's 0.083 is under-resolved there and ml4 is the first
compliant level. Each added level carries about the level-3 box's cell
count at 2× the substeps; measure the real cost on the probe grid before
sizing production. The throat keeps its ml3 structure either way.

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

## NUMERICS DEBT (Step 0 of `SpinningWormhole.md`; items 1 + 2 in work 2026-10-15, second node's card)

This file carried the list until ca71ceed compacted it away; restored because
every item is still open:
1. **Why Δt = 0.02 Δx — MEASUREMENT LIVE** (the dt ladder above; its go
   2026-10-15, "use this gpu for testing"). The evidence re-read 10-15 from the
   merger's packs: it is a dt-dependent WEAK INSTABILITY growing from t = 0,
   visible when it crosses the background, NOT a hard CFL blow-up and NOT the
   hold's physical mode — `single_hold_dt01_t070` (dt_mult 0.1): max|K| bump
   visible t ≈ 10, e-fold ~0.8, NaN at t = 16; `single_hold_dt005_t070`
   (0.05): visible t ≈ 28, e-fold ~1.5, K SATURATES ~1.9 while min_lapse
   stays on the control to 4 digits until t = 40, then the collapse runs away
   (L2_Ham ×35); 0.02 clean to 100. Threshold sits in (0.02, 0.05]. The
   ladder reruns the spinning static hold (same numbers verbatim) at 0.05 /
   0.035 / 0.02 with the new per-level norms (WHICH level) and the radial
   profile to r = 34 (WHERE: throat / AMR interfaces ±4/8/16 / sponge 24–32 /
   boundary). Then one-knob isolation arms at 0.05 (sigma, sponge) as the
   location dictates.
2. **Constraint norms level 0 only — DONE 2026-10-15** (commit 73793542,
   binary `main3d_levnorm_73793542_2026-10-15.ex`): `constraint_norms_levels
   = 1` writes `constraint_norms_levels.dat` — one masked L2_Ham/L2_Mom pair
   per level (cells no finer level covers, `makeFineMask`) plus a
   hierarchy-wide pair, puncture excluded inside `constraint_norms_mask_radius`
   (default 0.125, t0_checks.py's innermost shell edge). Historic level-0
   file untouched; smoke-tested on the ml3 grid (t = 0 value bit-identical to
   the packed Step 0 hold, speed unchanged 17.8 t/h). Adopt in production
   templates at the next binary bump.
3. **Constraint-solved seeds.** The Π shell seed violates the constraints in
   proportion to its amplitude (`SimulationParameters.hpp:50`); perturb Π,
   then re-solve the constraints. Dormant until a seeded spinning run is
   queued: every current hold runs seed_amplitude 0.
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
