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

**B1 `spin_hold_L128_ml3_ve050a_t100` FINISHED ≈ 12:15 UTC 10-15: reached
t = 100 clean, 0 NaN** — packed, registry + README + trust window (t ≤ 78)
done, movies rendering. MOTS R −1 % at t = 71 (static twin: t = 44), −3.14 %
at t = 100, no horizon; L2_Ham ×2 off plateau at t = 78.8 (the slow level-2
interface mode), far-side χ on the 1e-8 floor from t = 91.9. Final Chk10000
copied to the run's `nfs_chk/` (a t = 100 restart point if the hold is ever
extended toward the t ≈ 120 return); scratch pruned. **Card 0 is free and
stays idle — the launch freeze above holds until the σ verdict.**

| run | node/card | t | stop | speed | ETA |
|---|---|---|---|---|---|
| rescue probe `spin_hold_L64_ml3_ve070a_minchi4_t100` (`drainhole/04_fast_spin_hold/`; the old ve070a run rerun exactly, one knob: min_chi 1e-8 → 1e-4 — there χ DID clamp to the floor from t ≈ 4, unlike family (b) where a 1e-4 floor never engaged) | first GPU node, card 1 | launched 10:55 UTC 10-15 | 100 | ~17 t/h (est., card to itself) | verdict vs the old t = 42.36 death ≈ 13:30 UTC; t = 100 ≈ 16:50 UTC 10-15 |
| dt isolation `static_hold_L64_ml3_dt005_sig04_t045` (sigma 0.1 → 0.4 at dt_mult 0.05; t = 15 check: checkerboard KILLED, see debt item 1) | second GPU node, card 0 | t = 42.3 at 12:22 UTC 10-15 | 45 | ~12 t/h (3-way share) | ≈ 12:40 UTC 10-15; its share then gets the sigma-0.4 + dt 0.02 t100 arm |
| sigma ladder `static_hold_L64_ml3_dt005_sig03_t045` (one knob vs the sig04 arm: sigma 0.3 — the gentlest KO that still kills the mode?) | second GPU node, card 0 | launched 12:30 UTC 10-15 | 45 | ~12 t/h (est.) | ≈ 16:15 UTC 10-15 |
| dt ladder control `static_hold_L64_ml3_dt002ctl_t100` (same study; levnorm-binary regression vs the packed Step 0 hold) | second GPU node, card 0 | t = 35.3 at 12:22 UTC 10-15 | 100 | ~5.9 t/h | ≈ 23:00 UTC 10-15 |

dt ladder arms closed 10-15: `dt005_t070` stopped by plan at t = 45 (packed);
`dt0035_t070` **stopped by hand at t = 62.1, verdict in hand: UNSTABLE TOO** —
on the dt002 reference to 5 digits through t = 40, max|K| leaves the track at
t ≈ 43 and is ×41 by t = 55 (0.74 vs 0.018), same level-2 signature. At
sigma 0.1 only dt_mult 0.02 is safe; the speed-up must come through sigma
(debt item 1). Queued on the sig04 share (its go 12:00 UTC): **sigma-default
test `static_hold_L64_ml3_dt002_sig04_t100`** (sigma 0.4 at the production
dt 0.02, one knob vs the live control) — does the KO raise flatten the slow
level-2 growth (e-fold ~9 at sigma 0.1, ALSO in the dt 0.02 control — the
very growth that ends every trust window, cf. B1's ×2 at t = 78.8) and
extend the window?

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
- The family (b) probe ladder died the same morning — the full story is in
  **CAMPAIGN A — DROPPED** at the bottom; it no longer gates the plan.

The B1 production member (its go 2026-10-13): the v_e 0.513 drainhole on plain
L128 N256 ml3 (`params_spin_hold_ve050a_L128_N256.txt`), full-box frames
(zoom 128, cache 2048), rolling checkpoints every t = 10 keep 3 (asked). Its
static twin on this exact layout is the merger's `single_hold_L128_t100`:
the question is whether the L64 result (collapse slows with spin) holds with
the clean t = 100 baseline. Earlier today (final packing 19:50 UTC): every previous run packed,
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

**LAUNCH FREEZE (2026-10-15, ~12:00 UTC): no new run starts until the
slow-interface-mode / sigma question on the second node is settled** (the
σ = 0.4 + dt 0.02 head-to-head vs the σ = 0.1 control, verdict expected
tomorrow morning). The triplet members would otherwise bake today's σ = 0.1
into the production curve while the fix is being measured. Cards freed by
finishing runs (B1 ≈ 12:15 UTC, the ve070a rescue probe ≈ 13:20 UTC) stay
idle; systematics passes still run.

**SCOPE (decided 2026-10-15, supersedes the 10-13 order): the paper is the
drainhole's.** Campaign A (the symmetric family (b) evolutions A2–A4) is
DROPPED: four one-knob probes all die at t ≈ 23–24 at the far-side
positive-mass end, knob-independently (the postmortem at the bottom), and a
paper that introduces the symmetric case only to abandon it mid-story is
worse than one that never promises it. Family (b) stays in the paper as
theory and as the solver's validation only — the Step 2 gates, the A1
t = 0 ladder (21 runs, every quantity against Kleihaus–Kunz/CKK) and the
t = 0 convergence figures. No family (b) evolution is queued; the
postmortem section keeps everything needed to return to it.

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

*Phase B: drainhole, family (a) — THE HEADLINE*

**The spin ladder (agreed 2026-10-15): five rungs in v_e, every rung a
triplet, one τ(v_e) curve.** Rationale per rung — 0 is the anchor every
"spin slows collapse by X" divides by; ≈ 0.2 sits inside the source
paper's perturbative O(J²) domain, the one rung where the nonlinear rate
checks against a published number (the validation that licenses the fast
rungs, which have none) — and the J = 1 exact point (v_e 0.2100) IS that
rung (L64 already measured τ 6.8 vs static 5.8 there, i.e. where the
slowdown turns on); 0.5 is the production line; 0.7 and 0.9 (then
0.95/0.99 stretch) are the fast end, behind the far-side rescue.
Intermediate rungs (0.35, 0.6) only if the curve bends oddly between
neighbours. ~25 GPU-h a triplet (junk-shell N 384) → ~100 GPU-h for the
four new rungs, ~2–2.5 days on both cards.

| rung | run | needs | waiting on |
|---|---|---|---|
| v_e = 0 | static ×3: N 256 EXISTS (the merger's `single_hold_L128_t100`), run N 192 / 384 | templates written (`params_static_hold_L128_N*.txt`) | its go |
| v_e ≈ 0.2 (the published-domain rung) | `spin_hold_L128_ml3_J100_full_t100` ×3 — **the J = 1 exact point IS this rung**: its table meta reads v_e = 0.2100 (eta0 2, family a), and the freshly built `fam_a_ve020` came out at v_e 0.1984, J 0.936 — the same background twice (found 2026-10-15, one triplet saved) | table + templates exist (`params_spin_hold_J100_full_L128_N*.txt`); L64 run already measured τ 6.8 here. `fam_a_ve020.spinbg` (2049×129, err 3.9e-8) stays on disk as an optional same-rung cross-check from a different solver leg | its go |
| v_e = 0.5 | **N 256 DONE** (reached t = 100 clean 12:15 UTC 10-15, trust window 78, packed); next N 192, then N 384 | templates written (`params_spin_hold_ve050a_L128_N{192,384}.txt`); N 384 needs the junk-shell layout (below) or both cards | the launch freeze (σ verdict), then its go + checkpoint policy per member (N 256 ran every t = 10 keep 3 + NFS keeper) |
| v_e = 0.7 | B2 `spin_hold_L128_ml3_ve070a_t100` ×3 | the far side to clear t = 100: the min_chi 1e-4 rescue probe is LIVE on card 1 (the drainhole's χ does clamp to the floor, so the knob engages here — unlike family (b)) | the probe's verdict (≈ 13:30 UTC vs the old t = 42.36 death), its go |
| v_e = 0.9 (stretch 0.95 / 0.99) | B3 ×3 per spin | tables exist; expect a resolution wall before 0.99 and say so | B2, its go |

**Junk-shell layout for the N = 384-class members** (agreed 2026-10-13, not yet
templated): same L = 128 box, but the outer r > 32 shell stays one level
coarser (tagging_L 128, max_level 4, base dx0 = 2× the interior) — the
wormhole keeps its full resolution, the startup pulse dies in the 48–64 sponge,
return still t ≈ 128. Params-only (no code change). It cuts the finest triplet
member from ~36 h / 155 GB (impossible on one card) to ~16 h / ~70 GB, a
triplet to ~25 GPU-h. The production N = 256 member gains little (~7 h either
way), so it runs plain.

**Every quoted run is a triplet** (decided 2026-10-13; the stability protocol in
`SpinningWormhole.md`, after Evstafyeva, Siemonsen & East, arXiv:2508.11527):
L128 ml3 at N = 192 / 256 / 384 (finest Δx 0.0833 / 0.0625 / 0.0417; dx0 never
1). A growth is physical only if its τ converges to a nonzero value, the
finest-level constraints converge while it grows, and the throat's areal radii
or MOTS grow with it. N 192 / 384 costs are N⁴ estimates from the measured
14.1 t/h at N = 256.

**Per-level masked constraint norms are wired into every queued triplet
member** (2026-10-15): all six templates (`params_spin_hold_ve050a_L128_N*`,
`params_spin_hold_J100_full_L128_N*`) now carry `constraint_norms_levels = 1`
+ `constraint_norms_mask_radius = 0.125` (commit 73793542), so each run writes
`constraint_norms_levels.dat` — one Ham/Mom pair per AMR level plus a
hierarchy-wide pair, masked outside r = 0.125. The keys need the levnorm
binary: these launches pass `--binary
runs/spinning_wormhole/bin/main3d_levnorm_73793542_2026-10-15.ex` (the smoke
pin does not read them; preflight would refuse). Why: B1's level-0 norms grow
late (Ham 5.0e-4 → 6.3e-3 by t = 91, doubling ~5 units), and the dt-ladder
analysis identified it as the SLOW interface mode near level 2 (e-fold ~9 at
dt 0.02 in the control — the fast dt ≥ 0.035 checkerboard's quiet sibling),
not the throat and not the far-end floor. The per-level file makes that
attribution native to every triplet member. **Sigma stays 0.1 in the queued
templates for now**: the σ = 0.4 + dt 0.02 head-to-head vs the σ = 0.1
control (launching ≈ 13:00 UTC on the second node, verdict tomorrow morning)
directly measures whether a default σ raise flattens the late growth and
extends the trust window; if it does, raising σ in these templates is the
one-knob follow-up.


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
5. **The family (b) holds died at the far-side puncture** at every knob
   setting — campaign A dropped 2026-10-15 (the postmortem below).

## NUMERICS DEBT (Step 0 of `SpinningWormhole.md`; items 1 + 2 in work 2026-10-15, second node's card)

This file carried the list until ca71ceed compacted it away; restored because
every item is still open:
1. **Why Δt = 0.02 Δx — MECHANISM LOCALIZED 2026-10-15** (dt ladder,
   breakout measured at t = 42.5): a grid-scale checkerboard pinned to the
   fixed nested coarse–fine interfaces — a weak AMR interface-mode
   instability, NOT hard CFL (local coordinate speeds ≤ 0.95; the KO+RK4
   real-axis bound allows dt_mult ~0.23 at sigma 0.1), not the sponge,
   boundary or puncture. The evidence, dt_mult 0.05 vs the 0.02 control:
   - WHICH level: the new per-level norms see it long before max|K| —
     level-2 Ham ×7.5 at t = 10, ×61 at t = 15 (level 1 ×14, level 3 ×3,
     level 0 at 1.000). The composite Ham_all/ctl stays 1.000 throughout
     (level-0 volume dominates), which is exactly why the historic
     level-0-only norm was blind to it until breakout.
   - WHERE: K frames show square halos on the level-3 box edges; shells
     r ≈ 5–7.5 grow fastest (×75–160 over t 5→15; box corners at 4√3 ≈ 6.9).
   - Radiated early: wave-zone ψ4 P_total ×373 at t = 10, ×8,600 at t = 15,
     2.0e-3 absolute by t = 30 (background ~1e-13).
   - Breakout in max|K|: leaves the control track t ≈ 28–30, e-fold 4.2 →
     1.2 (t ~27 → 35), max|K| 0.56 at t = 35, 1.37 at t = 40.
   - dt_mult 0.035: max|K| on the control to 5 digits through t = 25, but
     the SAME mode grows weakly (level-2 Ham ×4.1 at t = 15, ψ4 ×20 at
     t = 14) — the threshold is a growth-rate ladder, not on/off; clean-to-70
     verdict pending (≈ 12:20 UTC).
   - Control: bit-exact vs the packed Step 0 hold (ψ4 ratio 1.000) —
     levnorm-binary regression clean so far.
   dt005 stopped by plan at t = 45 (09:00 UTC 10-15, zero NaN, clean exit;
   nothing new after saturation, every extra hour was control-share); its
   scratch pruned and logged. The one-knob isolation arm
   `static_hold_L64_ml3_dt005_sig04_t045` (sigma 0.1 → 0.4, dt_mult 0.05
   kept, live since 09:12 UTC) **CONFIRMS THE MECHANISM at its t = 15
   check (~10:35 UTC)**: where the sigma-0.1 dt005 arm had level-2 Ham ×61
   and ψ4 ×8,600 vs control at t = 15, the sigma-0.4 arm sits at level-2
   Ham 0.85–0.98 (slightly BELOW control) and ψ4 0.45× — the interface
   checkerboard is dissipation-starved and KO 0.4 kills it outright.
   Not free: max|K| carries a flat ×1.55–1.68 offset (e-folds 6.7 → 13.2,
   DECELERATING — background offset, not growth) and level-3 Ham sits at a
   flat ×2.7; sigma 0.4 measurably perturbs the hold. Verdicts still owed:
   this arm clean to t = 45 (≈ 13:00 UTC), dt0035 clean to 70 (≈ 12:20),
   control to 100 (regression + τ). Then "sigma ≈ 0.3–0.4 + dt_mult
   0.035–0.05" is the production speed-up candidate (1.75–2.5×), sigma
   tuned down if the ×1.55 K offset matters at production resolution.
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

## CAMPAIGN A — DROPPED 2026-10-15 (postmortem, kept in case we return)

Not part of any evolution plan; nothing here is queued. The record of why
the symmetric family (b) holds cannot run, and what was already tried, so a
return does not repeat it.

**The wall.** Family (b) is mirror-symmetric: its compactified far end is a
genuine positive-mass puncture (M ≈ 2.5) at the grid centre. Every hold dies
there in a K runaway (χ → floor, |K|max explodes ~30× in one coarse step,
NaN in h11 or K on the finest level), with the throat unmoved. The drainhole
differs in kind: its far end is the repulsive/negative-mass side (stationary
lapse 0.21 ≈ gauge equilibrium), which is why B-campaign runs are not behind
this wall (the slow v_e ≤ 0.51 holds ran clean; the fast ve070a death is a
different, floor-engaged variant under its own rescue probe).

**The probe ladder — four one-knob probes, N ≥ 192, all ve085b, all dead at
t ≈ 23–24** (templates `params_spin_hold_L128_N192_ve085b_lapse1*.txt`; runs
kept in `symmetric_massless/03_spin_hold/ve085b/`, frames + slice caches on
NFS):
1. √χ initial lapse (pre-collapsed punctures), ml3: died t = 22.87 —
   cleared the old t ≈ 4 window (~6×), insufficient.
2. max_level 4 on the puncture (dx 0.0417, satisfying the BH rule
   dx ≲ M/40): died t = 23.76 — +0.9 units for 2× resolution. Resolution
   ruled out.
3. eta 1 → 0.2 (shift damping ~1/(2M_punc)): died t = 23.24 — EARLIER.
   Gauge-parameter tuning ruled out.
4. min_chi 1e-4 on the ml4 grid: died t = 23.76, the parent's time to the
   step, with χ_min 2.2e-3 the whole run — the floor never engaged. Floor
   ruled out.
   (A fifth, min_chi 1e-4 on ml3, was killed by hand at t = 9.13
   pre-verdict — under-resolved, no information.)

**Conclusion.** The death time is knob-independent across lapse, resolution,
shift damping and floor: it tracks the initial data, not the numerics. The
far-side positive-mass end collapses on its own timescale (~23 at N192-class
grids) and the moving-puncture gauge family cannot ride through THIS
puncture (plausibly because it is a compactified image of infinity carrying
the scalar field, not a vacuum Schwarzschild end). What a return would need:
excision/turducken at the far puncture, a qualitatively different gauge, or
different data (a family (b) slice whose far end is regularized) — code or
theory work, not params.

**What the paper keeps from A** (validation, not evolution): Step 2 solver
gates (both families to v_e 0.99, CKK eq. (12) corrected); A1 t = 0 ladder
— 21 runs, v_e 0.24–0.99 × N 128/192/256, every Kleihaus–Kunz Fig. 1
quantity and M/J against the tables (`L128_A1/`); the t = 0 convergence
figures. The clean t < 23 windows of the probes exist on NFS if ever needed,
but are quoted nowhere.

**Shelved rationale** (for a return): Azad et al.'s mode-crossing test lived
on family (b) — second mode and crossing only for C ≤ 0.2, spins at
10/20/33/50 % of limiting J/A, crossing predicted at J/A ≈ 0.013 (33 %),
static Ellis anchor τ ≈ 1.7 at η0 = 2. The A2 static (massless far side,
NOT behind the wall) ×3, A3 ×4 spins ×3, A4 ×3 ×3 run lists and templates
are in git history at 2998819f.

## RULES

Merger launch discipline: go first, checkpoints asked per run, full frame set,
STATUS pushed at every launch/stop. Ψ4 radii in the box's wave zone (L = 64:
12 / 16 / 20, decided 2026-10-12; L = 128: inside r 48, set with the A2
templates).
